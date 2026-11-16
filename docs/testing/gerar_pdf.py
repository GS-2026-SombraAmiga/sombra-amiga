"""Gera o PDF de entrega de Testing a partir do que está publicado no Azure DevOps.

O PDF traz o link do projeto, as consultas compartilhadas, os prints das telas (pasta prints/, se houver)
e, como contingência, a relação e o detalhe de todas as Features e de todos os Test Cases,
lidos do Azure pela API no momento da geração.

Uso (na pasta docs/testing, com login no Azure CLI):
    python gerar_pdf.py
Saída: docs/testing/entrega/GS_Testing_SombraAmiga.pdf (e o .html de origem)
"""
import base64
import html
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from publicar_azure import AzureDevOps, chave

ORG = "https://dev.azure.com/RM556278"
PROJETO = "GS-26"
CONSULTAS = {
    "GS — Features e Test Cases": "https://dev.azure.com/RM556278/web/qr.aspx?pguid=650b5e8c-62cf-4ee6-b2ef-ed11c5570706&qid=c33e23e2-02b4-4077-a4c9-b3faa1d25ab9",
    "GS — Test Cases": "https://dev.azure.com/RM556278/web/qr.aspx?pguid=650b5e8c-62cf-4ee6-b2ef-ed11c5570706&qid=c43c9011-0219-41bd-9823-62cddec1a460",
}
CAMPOS = ["System.Title", "System.State", "System.Tags", "System.Description",
          "Microsoft.VSTS.Common.AcceptanceCriteria", "Microsoft.VSTS.TCM.Steps"]
PASTA = Path(__file__).resolve().parent
PRINTS = PASTA / "prints"
SAIDA = PASTA / "entrega"
EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]


def texto_limpo(valor: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(valor or ""))).strip()


def passos(xml_passos: str) -> list[tuple[str, str]]:
    if not xml_passos:
        return []
    raiz = ET.fromstring(xml_passos)
    resultado = []
    for passo in raiz.iter("step"):
        partes = [texto_limpo(p.text or "") for p in passo.findall("parameterizedString")]
        resultado.append((partes[0] if partes else "", partes[1] if len(partes) > 1 else ""))
    return resultado


def ler_itens():
    azure = AzureDevOps(ORG, PROJETO)
    consulta = {"query": "SELECT [System.Id] FROM workitems WHERE [System.TeamProject] = @project "
                         "AND [System.WorkItemType] IN ('Feature', 'Test Case')"}
    ids = [w["id"] for w in azure.chamar("POST", "wit/wiql", consulta)["workItems"]]
    features, testes = {}, {}
    for i in range(0, len(ids), 200):
        lote = ",".join(map(str, ids[i:i + 200]))
        for item in azure.chamar("GET", f"wit/workitems?ids={lote}&fields={','.join(CAMPOS)}")["value"]:
            k = chave(item["fields"]["System.Title"])
            if k is None:
                continue
            item["link"] = f"{ORG}/{PROJETO}/_workitems/edit/{item['id']}"
            (features if k[0] == "F" else testes)[k] = item
    return dict(sorted(features.items())), dict(sorted(testes.items()))


def montar_html(features, testes) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    e = html.escape
    por_feature = {}
    for k, t in testes.items():
        por_feature.setdefault(k[1], []).append(t)

    prints = sorted(p for p in PRINTS.glob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg"}) if PRINTS.exists() else []
    def imagem(p: Path) -> str:
        tipo = "png" if p.suffix.lower() == ".png" else "jpeg"
        return f"data:image/{tipo};base64,{base64.b64encode(p.read_bytes()).decode()}"

    bloco_prints = "".join(
        f'<figure><img src="{imagem(p)}"><figcaption>{e(p.stem.split("_", 1)[-1].replace("-", " "))}</figcaption></figure>'
        for p in prints) or "<p><i>Os prints das telas estão na pasta prints/.</i></p>"

    lista_f = "".join(
        f"<tr><td>#{f['id']}</td><td><a href='{f['link']}'>{e(f['fields']['System.Title'])}</a></td>"
        f"<td>{e(f['fields']['System.State'])}</td><td>{len(por_feature.get(k[1], []))}</td></tr>"
        for k, f in features.items())

    detalhe_f = ""
    for k, f in features.items():
        campos = f["fields"]
        casos = "".join(f"<li>#{t['id']} {e(t['fields']['System.Title'])}</li>" for t in por_feature.get(k[1], []))
        detalhe_f += f"""
        <section class="item">
          <h3><a href="{f['link']}">#{f['id']} · {e(campos['System.Title'])}</a></h3>
          <p class="meta">Tipo: Feature · Estado: {e(campos['System.State'])} · Tags: {e(campos.get('System.Tags', ''))}</p>
          <h4>Descrição</h4><div class="html">{campos.get('System.Description', '')}</div>
          <h4>Critérios de aceite</h4><div class="html">{campos.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')}</div>
          <h4>Test Cases ligados</h4><ul>{casos}</ul>
        </section>"""

    lista_t = "".join(
        f"<tr><td>#{t['id']}</td><td><a href='{t['link']}'>{e(t['fields']['System.Title'])}</a></td>"
        f"<td>{e(t['fields']['System.State'])}</td></tr>"
        for t in testes.values())

    detalhe_t = ""
    for k, t in testes.items():
        campos = t["fields"]
        linhas = "".join(f"<tr><td>{i}</td><td>{e(a)}</td><td>{e(r)}</td></tr>"
                         for i, (a, r) in enumerate(passos(campos.get("Microsoft.VSTS.TCM.Steps", "")), 1))
        detalhe_t += f"""
        <section class="item">
          <h3><a href="{t['link']}">#{t['id']} · {e(campos['System.Title'])}</a></h3>
          <p class="meta">Tipo: Test Case · Estado: {e(campos['System.State'])} · Tags: {e(campos.get('System.Tags', ''))}</p>
          <div class="html">{campos.get('System.Description', '')}</div>
          <table class="passos"><thead><tr><th>#</th><th>Ação</th><th>Resultado esperado</th></tr></thead><tbody>{linhas}</tbody></table>
        </section>"""

    consultas = "".join(f"<li><a href='{u}'>{e(n)}</a></li>" for n, u in CONSULTAS.items())
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>GS Testing - Sombra Amiga</title>
<style>
@page {{ size: A4; margin: 15mm 14mm; }}
body {{ font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; color: #1d1d1f; line-height: 1.4; }}
h1 {{ font-size: 20pt; color: #b3410e; margin: 0 0 4px; }}
h2 {{ font-size: 14pt; border-bottom: 2px solid #e8742a; padding-bottom: 3px; margin: 20px 0 8px; page-break-after: avoid; }}
h3 {{ font-size: 11pt; margin: 0 0 2px; }} h4 {{ font-size: 9.5pt; margin: 8px 0 2px; color: #444; }}
a {{ color: #1a5fb4; text-decoration: none; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; }}
th, td {{ border: 1px solid #ccc; padding: 3px 6px; text-align: left; vertical-align: top; }}
th {{ background: #f6e7dc; }}
.capa {{ border: 2px solid #e8742a; border-radius: 8px; padding: 14px 18px; }}
.item {{ border: 1px solid #ddd; border-radius: 6px; padding: 8px 10px; margin: 0 0 10px; page-break-inside: avoid; }}
.meta {{ color: #666; font-size: 8.5pt; margin: 0 0 4px; }}
.html p {{ margin: 2px 0; }} .html ul {{ margin: 2px 0; padding-left: 18px; }}
.passos {{ margin-top: 6px; }} .passos td:first-child {{ width: 18px; }}
figure {{ margin: 8px 0 14px; page-break-inside: avoid; }} figure img {{ width: 100%; border: 1px solid #bbb; }}
figcaption {{ font-size: 8.5pt; color: #555; }}
.quebra {{ page-break-before: always; }}
</style></head><body>
<div class="capa">
  <h1>Sombra Amiga</h1>
  <p style="font-size:12pt;margin:0 0 8px">Global Solution 2026.2 · <b>Testing, Compliance &amp; Quality Assurance</b> · Features e Test Cases</p>
  <p><b>Turma:</b> 3ESPG · <b>Integrantes:</b> Glauco Heitor Gonçalves (RM 555978) e Pedro Henrique Junqueira (RM 556278)</p>
  <p><b>Projeto no Azure DevOps:</b> <a href="{ORG}/{PROJETO}">{ORG}/{PROJETO}</a> · Work items: <a href="{ORG}/{PROJETO}/_workitems">{ORG}/{PROJETO}/_workitems</a></p>
  <p><b>Consultas compartilhadas</b> (Boards &gt; Queries &gt; Shared Queries):</p><ul>{consultas}</ul>
  <p><b>Conteúdo:</b> {len(features)} Features e {len(testes)} Test Cases (positivos e negativos, caixa-preta). Exportado do Azure DevOps em {agora}.</p>
</div>

<h2>1. Telas do Azure DevOps</h2>
<p class="meta">Prints das consultas compartilhadas e de um exemplo de cada tipo de item. O conteúdo completo de cada Feature e de cada Test Case está nas seções 3 e 5.</p>
{bloco_prints}

<h2 class="quebra">2. Relação de Features</h2>
<table><thead><tr><th>ID</th><th>Feature</th><th>Estado</th><th>Test Cases</th></tr></thead><tbody>{lista_f}</tbody></table>

<h2>3. Detalhe de cada Feature</h2>
<p class="meta">Contingência: conteúdo de cada Feature lido do Azure DevOps (descrição com a história de usuário e critérios de aceite no formato Cenário / Dado / Quando / Então).</p>
{detalhe_f}

<h2 class="quebra">4. Relação de Test Cases</h2>
<table><thead><tr><th>ID</th><th>Test Case</th><th>Estado</th></tr></thead><tbody>{lista_t}</tbody></table>

<h2>5. Definição de cada Test Case</h2>
<p class="meta">Contingência: objetivo, preparação, passos e resultados esperados de cada Test Case, lidos do Azure DevOps.</p>
{detalhe_t}
</body></html>"""


def main() -> int:
    features, testes = ler_itens()
    SAIDA.mkdir(exist_ok=True)
    origem = SAIDA / "GS_Testing_SombraAmiga.html"
    origem.write_text(montar_html(features, testes), encoding="utf-8")
    pdf = SAIDA / "GS_Testing_SombraAmiga.pdf"
    edge = next((e for e in EDGE if Path(e).exists()), shutil.which("msedge"))
    if not edge:
        print(f"HTML gerado em {origem}. Edge não encontrado: imprima o HTML em PDF pelo navegador.")
        return 0
    subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", origem.as_uri()], capture_output=True)
    print(f"{len(features)} Features e {len(testes)} Test Cases · PDF: {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
