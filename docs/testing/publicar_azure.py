"""Cria as Features e os Test Cases de conteudo.py no Azure DevOps.

Pré-requisito: Azure CLI instalado e login feito com
    az login --allow-no-subscriptions

Uso:
    python publicar_azure.py --org https://dev.azure.com/<organizacao> --projeto "<projeto>" --simular
    python publicar_azure.py --org https://dev.azure.com/<organizacao> --projeto "<projeto>"

- Cada Test Case é ligado à sua Feature pelo vínculo "Tests".
- Itens com o mesmo título já existentes no projeto são ignorados, então o script
  pode ser executado de novo sem duplicar nada.
- O token de acesso vem da sessão do Azure CLI e não é exibido nem gravado.
"""
import argparse
import html
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from xml.sax.saxutils import escape

from conteudo import FEATURES

RECURSO_AZURE_DEVOPS = "499b84ac-1321-427f-aa17-267ca6975798"
VERSAO_API = "7.1"
CAMPO_CRITERIOS = "Microsoft.VSTS.Common.AcceptanceCriteria"


# ---------- conteúdo ----------

def html_lista(itens):
    return "<ol>" + "".join(f"<li>{html.escape(i)}</li>" for i in itens) + "</ol>"


def descricao_feature(f, incluir_criterios):
    texto = f"<p><b>{html.escape(f['historia'])}</b></p><p>{html.escape(f['descricao'])}</p>"
    if incluir_criterios:
        texto += "<p><b>Critérios de aceite</b></p>" + html_lista(f["criterios"])
    return texto


def titulo_teste(f, n, t):
    return f"{f['id']}-TC{n:02d} [{t['tipo']}] {t['titulo']}"


def passos_xml(passos):
    """Formato do campo Microsoft.VSTS.TCM.Steps: HTML escapado dentro de XML."""
    def celula(texto):
        return f'<parameterizedString isformatted="true">{escape("<DIV><P>" + html.escape(texto) + "</P></DIV>")}</parameterizedString>'

    corpo = "".join(
        f'<step id="{i + 1}" type="ValidateStep">{celula(acao)}{celula(esperado)}<description/></step>'
        for i, (acao, esperado) in enumerate(passos)
    )
    return f'<steps id="0" last="{len(passos)}">{corpo}</steps>'


def descricao_teste(t):
    return (f"<p><b>Objetivo:</b> {html.escape(t['objetivo'])}</p>"
            f"<p><b>Preparação:</b> {html.escape(t['preparacao'])}</p>"
            f"<p><b>Tipo:</b> {t['tipo']} (caixa-preta, funcional)</p>")


# ---------- acesso à API ----------

class AzureDevOps:
    def __init__(self, org, projeto):
        self.org = org.rstrip("/")
        self.projeto = projeto
        self._token = self._obter_token()

    @staticmethod
    def _obter_token():
        az = shutil.which("az") or r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        resultado = subprocess.run(
            [az, "account", "get-access-token", "--resource", RECURSO_AZURE_DEVOPS, "--query", "accessToken", "-o", "tsv"],
            capture_output=True, text=True)
        if resultado.returncode != 0 or not resultado.stdout.strip():
            sys.exit("Não foi possível obter acesso. Faça login com: az login --allow-no-subscriptions")
        return resultado.stdout.strip()

    def chamar(self, metodo, caminho, corpo=None, tipo="application/json"):
        url = f"{self.org}/{urllib.parse.quote(self.projeto)}/_apis/{caminho}"
        url += ("&" if "?" in url else "?") + f"api-version={VERSAO_API}"
        dados = json.dumps(corpo).encode() if corpo is not None else None
        pedido = urllib.request.Request(url, data=dados, method=metodo, headers={
            "Authorization": f"Bearer {self._token}", "Content-Type": tipo, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(pedido) as resposta:
                return json.loads(resposta.read().decode() or "{}")
        except urllib.error.HTTPError as erro:
            detalhe = erro.read().decode(errors="replace")[:400]
            raise RuntimeError(f"{metodo} {caminho} falhou com HTTP {erro.code}: {detalhe}") from None

    def tipos(self):
        return {t["name"] for t in self.chamar("GET", "wit/workitemtypes")["value"]}

    def tem_campo(self, tipo, campo):
        campos = self.chamar("GET", f"wit/workitemtypes/{urllib.parse.quote(tipo)}/fields")["value"]
        return any(c["referenceName"] == campo for c in campos)

    def titulos_existentes(self):
        consulta = {"query": "SELECT [System.Id] FROM workitems WHERE [System.TeamProject] = @project "
                             "AND [System.WorkItemType] IN ('Feature', 'Test Case')"}
        ids = [w["id"] for w in self.chamar("POST", "wit/wiql", consulta)["workItems"]]
        existentes = {}
        for i in range(0, len(ids), 200):
            lote = ",".join(map(str, ids[i:i + 200]))
            for item in self.chamar("GET", f"wit/workitems?ids={lote}&fields=System.Title")["value"]:
                existentes[item["fields"]["System.Title"]] = item
        return existentes

    def criar(self, tipo, campos, relacoes=()):
        corpo = [{"op": "add", "path": f"/fields/{nome}", "value": valor} for nome, valor in campos.items()]
        corpo += [{"op": "add", "path": "/relations/-", "value": r} for r in relacoes]
        return self.chamar("POST", f"wit/workitems/${urllib.parse.quote(tipo)}", corpo, "application/json-patch+json")


# ---------- execução ----------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--org", required=True, help="Ex.: https://dev.azure.com/minha-organizacao")
    parser.add_argument("--projeto", required=True)
    parser.add_argument("--simular", action="store_true", help="Confere o projeto e mostra o que seria criado, sem criar nada")
    args = parser.parse_args()

    azure = AzureDevOps(args.org, args.projeto)

    tipos = azure.tipos()
    faltando = {"Feature", "Test Case"} - tipos
    if faltando:
        sys.exit(f"O projeto não tem os tipos {sorted(faltando)}. Use um processo Agile, Scrum ou CMMI, não o Basic.")

    criterios_em_campo = azure.tem_campo("Feature", CAMPO_CRITERIOS)
    existentes = azure.titulos_existentes()
    print(f"Projeto encontrado. Critérios de aceite {'no campo próprio' if criterios_em_campo else 'na descrição'}. "
          f"{len(existentes)} itens já existem.")

    criadas = pulados = testes_criados = 0
    for f in FEATURES:
        titulo = f"{f['id']} - {f['titulo']}"
        if titulo in existentes:
            feature = existentes[titulo]
            pulados += 1
        elif args.simular:
            feature = None
            criadas += 1
        else:
            campos = {"System.Title": titulo, "System.Description": descricao_feature(f, not criterios_em_campo),
                      "System.Tags": f["id"]}
            if criterios_em_campo:
                campos[CAMPO_CRITERIOS] = html_lista(f["criterios"])
            feature = azure.criar("Feature", campos)
            criadas += 1
            print(f"  Feature #{feature['id']} {titulo}")

        for n, t in enumerate(f["testes"], start=1):
            titulo_tc = titulo_teste(f, n, t)
            if titulo_tc in existentes:
                pulados += 1
                continue
            testes_criados += 1
            if args.simular:
                continue
            campos = {"System.Title": titulo_tc, "System.Description": descricao_teste(t),
                      "Microsoft.VSTS.TCM.Steps": passos_xml(t["passos"]), "System.Tags": f"{f['id']}; {t['tipo']}"}
            relacao = {"rel": "Microsoft.VSTS.Common.TestedBy-Reverse", "url": feature["url"]}
            caso = azure.criar("Test Case", campos, [relacao])
            print(f"    Test Case #{caso['id']} {titulo_tc}")

    acao = "seriam criados" if args.simular else "criados"
    print(f"\n{criadas} Features e {testes_criados} Test Cases {acao}. {pulados} já existiam e foram ignorados.")
    if not args.simular:
        print(f"Veja em: {args.org.rstrip('/')}/{urllib.parse.quote(args.projeto)}/_workitems")


if __name__ == "__main__":
    main()
