"""Gera os arquivos de importação do Azure DevOps e o documento legível.

Uso: python gerar_azure.py
Saída: features.csv, test-cases.csv, test-cases-amostra.csv e features-e-testes.md nesta pasta.
"""
import csv
import html
from pathlib import Path

from conteudo import FEATURES, cenario_linhas, tags_feature, tags_teste, titulo_feature, titulo_teste

PASTA = Path(__file__).parent


def criterios_html(f):
    """Cada cenário em um parágrafo, com as palavras-chave do Gherkin em negrito."""
    blocos = []
    for cenario in f["criterios"]:
        linhas = []
        for linha in cenario_linhas(cenario):
            chave, _, resto = linha.partition(" ")
            linhas.append(f"<b>{html.escape(chave)}</b> {html.escape(resto)}")
        blocos.append("<p>" + "<br>".join(linhas) + "</p>")
    return "".join(blocos)


def descricao_feature_html(f):
    return f"<p><b>{html.escape(f['historia'])}</b></p><p>{html.escape(f['descricao'])}</p>"


def descricao_teste_html(t):
    return (f"<p><b>Objetivo:</b> {html.escape(t['objetivo'])}</p>"
            f"<p><b>Preparação:</b> {html.escape(t['preparacao'])}</p>"
            f"<p><b>Tipo:</b> {t['tipo']} (caixa-preta, funcional)</p>")


def gerar_features():
    with open(PASTA / "features.csv", "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["ID", "Work Item Type", "Title", "Description", "Acceptance Criteria", "Tags"])
        for f in FEATURES:
            escritor.writerow(["", "Feature", titulo_feature(f), descricao_feature_html(f), criterios_html(f), tags_feature(f)])


def gerar_test_cases(nome="test-cases.csv", limite=None):
    with open(PASTA / nome, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["ID", "Work Item Type", "Title", "Test Step", "Step Action", "Step Expected", "Assigned To", "State", "Tags"])
        for f in FEATURES[:1] if limite else FEATURES:
            for n, t in enumerate(f["testes"][:limite], start=1):
                passos = [(f"Objetivo: {t['objetivo']} Preparação: {t['preparacao']}", "Ambiente pronto conforme a preparação.")] + t["passos"]
                for numero, (acao, esperado) in enumerate(passos, start=1):
                    if numero == 1:
                        escritor.writerow(["", "Test Case", titulo_teste(f, n, t), numero, acao, esperado, "", "Design", tags_teste(f, t)])
                    else:
                        escritor.writerow(["", "", "", numero, acao, esperado, "", "", ""])


def gerar_documento():
    linhas = [
        "# Features e Test Cases",
        "",
        "Gerado por `gerar_azure.py` a partir de `conteudo.py`. Não edite à mão.",
        "",
        "| Feature | Test Cases | Positivos | Negativos |",
        "|---|---|---|---|",
    ]
    for f in FEATURES:
        pos = sum(t["tipo"] == "Positivo" for t in f["testes"])
        linhas.append(f"| {titulo_feature(f)} | {len(f['testes'])} | {pos} | {len(f['testes']) - pos} |")
    total = sum(len(f["testes"]) for f in FEATURES)
    linhas += ["", f"**Total:** {len(FEATURES)} Features e {total} Test Cases.", ""]

    for f in FEATURES:
        linhas += [f"## {titulo_feature(f)}", "", f"**{f['historia']}**", "", f["descricao"], "", "### Critérios de aceite", ""]
        for cenario in f["criterios"]:
            primeira, *demais = cenario_linhas(cenario)
            linhas += [f"**{primeira}**  "] + [f"{l}  " for l in demais] + [""]
        for n, t in enumerate(f["testes"], start=1):
            linhas += [
                f"### {titulo_teste(f, n, t)}",
                "",
                f"- **Objetivo:** {t['objetivo']}",
                f"- **Preparação:** {t['preparacao']}",
                "",
                "| # | Ação e entradas | Resultado esperado |",
                "|---|---|---|",
            ]
            for numero, (acao, esperado) in enumerate(t["passos"], start=1):
                linhas.append(f"| {numero} | {acao.replace('|', '/')} | {esperado.replace('|', '/')} |")
            linhas.append("")
    (PASTA / "features-e-testes.md").write_text("\n".join(linhas), encoding="utf-8")
    return total


if __name__ == "__main__":
    gerar_features()
    gerar_test_cases()
    gerar_test_cases("test-cases-amostra.csv", limite=1)
    total = gerar_documento()
    print(f"{len(FEATURES)} Features e {total} Test Cases gerados.")
