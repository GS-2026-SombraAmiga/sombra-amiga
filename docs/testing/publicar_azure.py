"""Sincroniza as Features e os Test Cases de conteudo.py com o Azure DevOps.

Pré-requisito: Azure CLI instalado e login feito com
    az login --allow-no-subscriptions

Uso:
    python publicar_azure.py --org https://dev.azure.com/<organizacao> --projeto "<projeto>" --simular
    python publicar_azure.py --org https://dev.azure.com/<organizacao> --projeto "<projeto>"

- Cada item é reconhecido pelo código no título (F-01, TC-01.01, e também o formato
  antigo F01 e F01-TC01). Itens existentes são atualizados no lugar; os que faltam são criados.
- Cada Test Case novo é ligado à sua Feature pelo vínculo "Tests".
- Executar de novo não duplica nada: se não houver mudança, nada é alterado.
- O token de acesso vem da sessão do Azure CLI e não é exibido nem gravado.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from xml.sax.saxutils import escape

from conteudo import FEATURES, tags_feature, tags_teste, titulo_feature, titulo_teste
from gerar_azure import criterios_html, descricao_feature_html, descricao_teste_html

RECURSO_AZURE_DEVOPS = "499b84ac-1321-427f-aa17-267ca6975798"
VERSAO_API = "7.1"
CAMPO_CRITERIOS = "Microsoft.VSTS.Common.AcceptanceCriteria"
CAMPO_PASSOS = "Microsoft.VSTS.TCM.Steps"
CAMPOS_LIDOS = ["System.WorkItemType", "System.Title", "System.Description", "System.Tags", CAMPO_CRITERIOS, CAMPO_PASSOS]


def passos_xml(passos):
    """Formato do campo Microsoft.VSTS.TCM.Steps: HTML escapado dentro de XML."""
    def celula(texto):
        return f'<parameterizedString isformatted="true">{escape("<DIV><P>" + html.escape(texto) + "</P></DIV>")}</parameterizedString>'

    corpo = "".join(
        f'<step id="{i + 1}" type="ValidateStep">{celula(acao)}{celula(esperado)}<description/></step>'
        for i, (acao, esperado) in enumerate(passos)
    )
    return f'<steps id="0" last="{len(passos)}">{corpo}</steps>'


def chave(titulo):
    """Código estável do item, aceitando o formato novo e o antigo dos títulos."""
    if m := re.match(r"^(?:TC-(\d{2})\.(\d{2})|F(\d{2})-TC(\d{2}))\b", titulo):
        return ("TC", m.group(1) or m.group(3), m.group(2) or m.group(4))
    if m := re.match(r"^F-?(\d{2})\b", titulo):
        return ("F", m.group(1))
    return None


def normalizar(valor):
    """Compara pelo texto visível, porque o Azure reescreve o HTML ao salvar."""
    texto = html.unescape(html.unescape(valor or ""))
    texto = re.sub(r"<[^>]+>", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


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

    def existentes(self):
        """Features e Test Cases do projeto, indexados pelo código do título."""
        consulta = {"query": "SELECT [System.Id] FROM workitems WHERE [System.TeamProject] = @project "
                             "AND [System.WorkItemType] IN ('Feature', 'Test Case')"}
        ids = [w["id"] for w in self.chamar("POST", "wit/wiql", consulta)["workItems"]]
        itens = {}
        for i in range(0, len(ids), 200):
            lote = ",".join(map(str, ids[i:i + 200]))
            for item in self.chamar("GET", f"wit/workitems?ids={lote}&fields={','.join(CAMPOS_LIDOS)}")["value"]:
                if (k := chave(item["fields"]["System.Title"])) is not None:
                    item["url"] = f"{self.org}/_apis/wit/workItems/{item['id']}"
                    itens[k] = item
        return itens

    def criar(self, tipo, campos, relacoes=()):
        corpo = [{"op": "add", "path": f"/fields/{nome}", "value": valor} for nome, valor in campos.items()]
        corpo += [{"op": "add", "path": "/relations/-", "value": r} for r in relacoes]
        return self.chamar("POST", f"wit/workitems/${urllib.parse.quote(tipo)}", corpo, "application/json-patch+json")

    def atualizar(self, id_item, campos):
        # Em tags, "add" soma às existentes; "replace" troca a lista inteira.
        corpo = [{"op": "replace" if nome == "System.Tags" else "add", "path": f"/fields/{nome}", "value": valor}
                 for nome, valor in campos.items()]
        return self.chamar("PATCH", f"wit/workitems/{id_item}", corpo, "application/json-patch+json")


def diferencas(item, desejado):
    atuais = item["fields"]
    return {nome: valor for nome, valor in desejado.items() if normalizar(atuais.get(nome)) != normalizar(valor)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--org", required=True, help="Ex.: https://dev.azure.com/minha-organizacao")
    parser.add_argument("--projeto", required=True)
    parser.add_argument("--simular", action="store_true", help="Mostra o que mudaria, sem alterar nada")
    args = parser.parse_args()

    azure = AzureDevOps(args.org, args.projeto)
    faltando = {"Feature", "Test Case"} - azure.tipos()
    if faltando:
        sys.exit(f"O projeto não tem os tipos {sorted(faltando)}. Use um processo Agile, Scrum ou CMMI, não o Basic.")

    criterios_em_campo = azure.tem_campo("Feature", CAMPO_CRITERIOS)
    itens = azure.existentes()
    print(f"Projeto encontrado. Critérios de aceite {'no campo próprio' if criterios_em_campo else 'na descrição'}. "
          f"{len(itens)} itens reconhecidos.")

    contagem = {"criados": 0, "atualizados": 0, "iguais": 0}
    verbo = "seria" if args.simular else "foi"

    def sincronizar(k, tipo, desejado, relacoes=()):
        existente = itens.get(k)
        if existente is None:
            contagem["criados"] += 1
            if args.simular:
                print(f"  criar      {desejado['System.Title']}")
                return None
            novo = azure.criar(tipo, desejado, relacoes)
            print(f"  criado     #{novo['id']} {desejado['System.Title']}")
            return novo
        mudar = diferencas(existente, desejado)
        if not mudar:
            contagem["iguais"] += 1
            return existente
        contagem["atualizados"] += 1
        print(f"  atualizar  #{existente['id']} {desejado['System.Title']}  ({', '.join(n.split('.')[-1] for n in mudar)})")
        if not args.simular:
            azure.atualizar(existente["id"], mudar)
        return existente

    for f in FEATURES:
        numero = f["id"][1:]
        descricao = descricao_feature_html(f)
        desejado = {"System.Title": titulo_feature(f), "System.Tags": tags_feature(f)}
        if criterios_em_campo:
            desejado["System.Description"] = descricao
            desejado[CAMPO_CRITERIOS] = criterios_html(f)
        else:
            desejado["System.Description"] = descricao + "<p><b>Critérios de aceite</b></p>" + criterios_html(f)
        feature = sincronizar(("F", numero), "Feature", desejado)

        for n, t in enumerate(f["testes"], start=1):
            desejado_tc = {"System.Title": titulo_teste(f, n, t), "System.Description": descricao_teste_html(t),
                           CAMPO_PASSOS: passos_xml(t["passos"]), "System.Tags": tags_teste(f, t)}
            relacoes = [{"rel": "Microsoft.VSTS.Common.TestedBy-Reverse", "url": feature["url"]}] if feature else []
            sincronizar(("TC", numero, f"{n:02d}"), "Test Case", desejado_tc, relacoes)

    print(f"\n{contagem['criados']} a criar, {contagem['atualizados']} a atualizar e {contagem['iguais']} já iguais."
          if args.simular else
          f"\n{contagem['criados']} criados, {contagem['atualizados']} atualizados e {contagem['iguais']} já iguais.")
    if not args.simular:
        print(f"Veja em: {args.org.rstrip('/')}/{urllib.parse.quote(args.projeto)}/_workitems")


if __name__ == "__main__":
    main()
