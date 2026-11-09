"""Gera os arquivos de importação do Azure DevOps e o documento legível.

Uso: python gerar_azure.py
Saída: features.csv, test-cases.csv, test-cases-amostra.csv e features-e-testes.md nesta pasta.
"""
import csv
import html
from pathlib import Path

from conteudo import FEATURES

PASTA = Path(__file__).parent


def lista_html(itens):
    return "<ol>" + "".join(f"<li>{html.escape(i)}</li>" for i in itens) + "</ol>"


def gerar_features():
    with open(PASTA / "features.csv", "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["ID", "Work Item Type", "Title", "Description", "Acceptance Criteria", "Tags"])
        for f in FEATURES:
            descricao = f"<p><b>{html.escape(f['historia'])}</b></p><p>{html.escape(f['descricao'])}</p>"
            escritor.writerow(["", "Feature", f"{f['id']} - {f['titulo']}", descricao, lista_html(f["criterios"]), f["id"]])


def gerar_test_cases(nome="test-cases.csv", limite=None):
    with open(PASTA / nome, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["ID", "Work Item Type", "Title", "Test Step", "Step Action", "Step Expected", "Assigned To", "State", "Tags"])
        for f in FEATURES[:1] if limite else FEATURES:
            for n, t in enumerate(f["testes"][:limite], start=1):
                titulo = f"{f['id']}-TC{n:02d} [{t['tipo']}] {t['titulo']}"
                passos = [(f"Objetivo: {t['objetivo']} Preparação: {t['preparacao']}", "Ambiente pronto conforme a preparação.")] + t["passos"]
                for numero, (acao, esperado) in enumerate(passos, start=1):
                    if numero == 1:
                        escritor.writerow(["", "Test Case", titulo, numero, acao, esperado, "", "Design", f"{f['id']}; {t['tipo']}"])
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
        linhas.append(f"| {f['id']} {f['titulo']} | {len(f['testes'])} | {pos} | {len(f['testes']) - pos} |")
    total = sum(len(f["testes"]) for f in FEATURES)
    linhas += ["", f"**Total:** {len(FEATURES)} Features e {total} Test Cases.", ""]

    for f in FEATURES:
        linhas += [f"## {f['id']} - {f['titulo']}", "", f"**{f['historia']}**", "", f["descricao"], "", "**Critérios de aceite**", ""]
        linhas += [f"{i}. {c}" for i, c in enumerate(f["criterios"], start=1)]
        linhas.append("")
        for n, t in enumerate(f["testes"], start=1):
            linhas += [
                f"### {f['id']}-TC{n:02d} [{t['tipo']}] {t['titulo']}",
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
