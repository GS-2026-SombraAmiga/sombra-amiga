"""Painel executivo de Risco Cidadão: uma página HTML única, sem dependências, que reúne uma ou mais análises."""

from __future__ import annotations

import html
import json
from pathlib import Path

MODELO = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Risco Cidadão · Sombra Amiga</title>
<style>
:root {
  --fundo: #f4f3ef; --superficie: #fcfcfb; --texto: #0b0b0b; --texto-2: #52514e; --texto-3: #74736e;
  --linha: #e1e0d9; --borda: rgba(11,11,11,0.10); --acento: #b3410e;
  --bom: #0ca30c; --aviso: #fab219; --serio: #ec835a; --critico: #d03b3b; --trilha: #ecebe6;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --fundo: #121211; --superficie: #1a1a19; --texto: #f0efec; --texto-2: #c3c2b7; --texto-3: #9a998f;
    --linha: #2c2c2a; --borda: rgba(255,255,255,0.10); --acento: #f08a4b; --trilha: #2c2c2a; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --fundo: #121211; --superficie: #1a1a19; --texto: #f0efec; --texto-2: #c3c2b7; --texto-3: #9a998f;
  --linha: #2c2c2a; --borda: rgba(255,255,255,0.10); --acento: #f08a4b; --trilha: #2c2c2a; color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--fundo); color: var(--texto); font: 15px/1.45 "Segoe UI", system-ui, sans-serif; }
main { max-width: 1120px; margin: 0 auto; padding: 24px 16px 48px; }
header { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; }
h1 { margin: 0; font-size: 24px; }
h1 small { display: block; font-size: 14px; font-weight: 400; color: var(--texto-2); }
h2 { font-size: 17px; margin: 0 0 10px; }
.abas { display: flex; flex-wrap: wrap; gap: 6px; }
.abas button { border: 1px solid var(--borda); background: var(--superficie); color: var(--texto); padding: 7px 12px; border-radius: 8px; cursor: pointer; font: inherit; font-size: 14px; }
.abas button[aria-selected="true"] { border-color: var(--acento); box-shadow: inset 0 0 0 1px var(--acento); font-weight: 600; }
.cartao { background: var(--superficie); border: 1px solid var(--borda); border-radius: 12px; padding: 18px; }
.grade { display: grid; gap: 14px; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); margin-bottom: 14px; }
@media (max-width: 760px) { .grade { grid-template-columns: 1fr; } }
.rotulo { color: var(--texto-2); font-size: 13px; }
.heroi { display: flex; align-items: baseline; gap: 10px; margin: 4px 0 2px; }
.heroi strong { font-size: 64px; line-height: 1; font-weight: 600; letter-spacing: -1px; }
.heroi span { color: var(--texto-2); font-size: 18px; }
.faixa-atual { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; font-size: 15px; }
.icone { width: 14px; height: 14px; border-radius: 50%; display: inline-grid; place-items: center; color: #fff; font-size: 10px; font-weight: 700; flex: none; }
.medidor { position: relative; margin: 16px 0 6px; }
.trilho { display: flex; gap: 2px; height: 10px; }
.trilho div { border-radius: 2px; }
.trilho div:first-child { border-radius: 5px 2px 2px 5px; }
.trilho div:last-child { border-radius: 2px 5px 5px 2px; }
.marcador { position: absolute; top: -5px; width: 4px; height: 20px; background: var(--texto); border-radius: 2px; box-shadow: 0 0 0 2px var(--superficie); transform: translateX(-2px); }
.escala { display: flex; justify-content: space-between; color: var(--texto-3); font-size: 12px; }
.faixas { display: flex; flex-wrap: wrap; gap: 4px 14px; margin-top: 8px; font-size: 12px; color: var(--texto-2); }
.faixas span { display: inline-flex; align-items: center; gap: 5px; }
.formula { margin-top: 12px; font-size: 12.5px; color: var(--texto-2); }
.tiles { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.tile { border: 1px solid var(--borda); border-radius: 10px; padding: 10px 12px; }
.tile .valor { font-size: 28px; font-weight: 600; line-height: 1.1; }
.tile .nome { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--texto-2); }
.meta { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 12px; font-size: 13px; color: var(--texto-2); }
.meta b { color: var(--texto); }
.alertas { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.alertas li { border: 1px solid var(--borda); border-left-width: 4px; border-radius: 8px; padding: 10px 12px; }
.alertas .topo { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; font-size: 13px; color: var(--texto-2); margin-bottom: 4px; }
.alertas .texto { font-size: 15px; }
.fonte { font-size: 11.5px; border: 1px solid var(--borda); border-radius: 999px; padding: 1px 8px; color: var(--texto-2); }
details { margin-top: 6px; font-size: 13px; color: var(--texto-2); }
summary { cursor: pointer; }
code { font-family: Consolas, ui-monospace, monospace; font-size: 12.5px; background: var(--fundo); padding: 1px 4px; border-radius: 4px; word-break: break-word; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--linha); vertical-align: top; }
th { color: var(--texto-2); font-weight: 600; }
.vazio { color: var(--texto-2); padding: 8px 0; }
.secao { margin-top: 14px; }
.rolagem { overflow-x: auto; }
</style>
</head>
<body>
<main>
  <header>
    <h1>Risco Cidadão <small>Sentinela Cidadã · análise de privacidade do protótipo Sombra Amiga</small></h1>
    <div class="abas" role="tablist" id="abas"></div>
  </header>

  <div class="grade">
    <section class="cartao" aria-labelledby="t-indice">
      <div class="rotulo" id="t-indice">Índice de Risco Cidadão</div>
      <div class="heroi"><strong id="valor">0</strong><span>/ 100</span></div>
      <div class="faixa-atual" id="faixa"></div>
      <div class="medidor" role="img" id="medidor">
        <div class="trilho">
          <div style="flex:30;background:var(--bom)"></div>
          <div style="flex:30;background:var(--aviso)"></div>
          <div style="flex:25;background:var(--serio)"></div>
          <div style="flex:15;background:var(--critico)"></div>
        </div>
        <div class="marcador" id="marcador"></div>
      </div>
      <div class="escala"><span>0</span><span>30</span><span>60</span><span>85</span><span>100</span></div>
      <div class="faixas" id="legenda-faixas"></div>
      <div class="formula">Cada falha tem peso = sensibilidade do dado × exposição da saída (1 a 25). O índice é a chance de pelo menos uma falha causar dano: 100 × (1 − Π(1 − (peso/25)³)).</div>
    </section>

    <section class="cartao" aria-labelledby="t-grav">
      <h2 id="t-grav">Falhas por gravidade</h2>
      <div class="tiles" id="tiles"></div>
      <div class="meta" id="meta"></div>
    </section>
  </div>

  <section class="cartao" aria-labelledby="t-alertas">
    <h2 id="t-alertas">Alertas para o cidadão</h2>
    <ul class="alertas" id="alertas"></ul>
  </section>

  <section class="cartao secao" aria-labelledby="t-tabela">
    <h2 id="t-tabela">Detalhe técnico dos achados</h2>
    <div class="rolagem"><table>
      <thead><tr><th>Gravidade</th><th>Tipo</th><th>Dado</th><th>Saída</th><th>Onde</th><th>Peso</th></tr></thead>
      <tbody id="tabela"></tbody>
    </table></div>
  </section>

  <section class="cartao secao" aria-labelledby="t-inv">
    <h2 id="t-inv">Inventário de dados pessoais no código</h2>
    <div class="meta" id="inventario"></div>
  </section>
</main>
<script>
const ANALISES = __DADOS__;
const FAIXAS = [
  { id: "baixo", nome: "Baixo", cor: "var(--bom)", icone: "✓", texto: "#fff" },
  { id: "moderado", nome: "Moderado", cor: "var(--aviso)", icone: "!", texto: "#0b0b0b" },
  { id: "alto", nome: "Alto", cor: "var(--serio)", icone: "!", texto: "#fff" },
  { id: "critico", nome: "Crítico", cor: "var(--critico)", icone: "×", texto: "#fff" },
];
const GRAV = [
  { id: "critica", nome: "Crítica", cor: "var(--critico)", icone: "×", texto: "#fff" },
  { id: "alta", nome: "Alta", cor: "var(--serio)", icone: "!", texto: "#fff" },
  { id: "media", nome: "Média", cor: "var(--aviso)", icone: "!", texto: "#0b0b0b" },
  { id: "baixa", nome: "Baixa", cor: "var(--bom)", icone: "i", texto: "#fff" },
];
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const icone = g => `<span class="icone" aria-hidden="true" style="background:${g.cor};color:${g.texto}">${g.icone}</span>`;
const grav = id => GRAV.find(g => g.id === id);

document.getElementById("legenda-faixas").innerHTML = FAIXAS.map(f => `<span>${icone(f)}${f.nome}</span>`).join("");

function mostrar(i) {
  const d = ANALISES[i], r = d.resumo;
  document.querySelectorAll("#abas button").forEach((b, j) => b.setAttribute("aria-selected", j === i));
  const f = FAIXAS.find(x => x.id === r.faixa);
  document.getElementById("valor").textContent = r.risco_cidadao;
  document.getElementById("faixa").innerHTML = `${icone(f)} Risco ${f.nome.toLowerCase()}`;
  document.getElementById("marcador").style.left = r.risco_cidadao + "%";
  document.getElementById("medidor").setAttribute("aria-label", `Risco Cidadão ${r.risco_cidadao} de 100, faixa ${f.nome}`);
  document.getElementById("tiles").innerHTML = GRAV.map(g =>
    `<div class="tile"><div class="valor">${r.por_gravidade[g.id]}</div><div class="nome">${icone(g)}${g.nome}</div></div>`).join("");
  const fonte = { "llm": "LLM (Claude)", "texto padrao": "texto padrão das regras", "misto": "LLM e texto padrão" }[d.fonte_alertas];
  document.getElementById("meta").innerHTML =
    `<span>Vazamentos que bloqueiam a entrega: <b>${r.vazamentos_bloqueantes}</b></span>` +
    `<span>Arquivos: <b>${d.arquivos_analisados}</b></span><span>Métodos seguidos: <b>${d.metodos_analisados}</b></span>` +
    `<span>Alertas por: <b>${fonte}</b></span><span>Gerado em: <b>${esc(d.gerado_em.replace("T", " ").slice(0, 16))}</b></span>`;

  const vistos = new Set();
  const alertas = d.achados.filter(a => { const k = a.alerta + a.gravidade; if (vistos.has(k)) return false; vistos.add(k); return true; });
  document.getElementById("alertas").innerHTML = alertas.length ? alertas.map(a => {
    const g = grav(a.gravidade);
    const iguais = d.achados.filter(x => x.alerta === a.alerta && x.gravidade === a.gravidade).length;
    const caminho = a.caminho.length ? `<br>Caminho do dado: ${a.caminho.map(p => `linha ${p.linha}: <code>${esc(p.texto)}</code>`).join(" → ")}` : "";
    return `<li style="border-left-color:${g.cor}">
      <div class="topo">${icone(g)}<b>${g.nome}</b><span>${esc(a.categoria)} · ${esc(a.tipo_rotulo)}</span>${iguais > 1 ? `<span>${iguais} ocorrências</span>` : ""}<span class="fonte">${a.alerta_fonte === "llm" ? "texto do LLM" : "texto padrão"}</span></div>
      <div class="texto">${esc(a.alerta)}</div>
      <details><summary>Detalhe técnico</summary><code>${esc(a.arquivo)}</code>, linha ${a.linha}${a.metodo ? `, método <code>${esc(a.metodo)}</code>` : ""}<br>Trecho: <code>${esc(a.trecho)}</code>${caminho}</details>
    </li>`;
  }).join("") : `<li class="vazio" style="border-left-color:var(--bom)">Nenhum dado pessoal chega a uma saída insegura nesta análise.</li>`;

  document.getElementById("tabela").innerHTML = d.achados.length ? d.achados.map(a => {
    const g = grav(a.gravidade);
    return `<tr><td><span class="faixa-atual" style="font-weight:400">${icone(g)}${g.nome}</span></td><td>${esc(a.tipo_rotulo)}</td><td>${esc(a.categoria)}</td><td>${esc(a.saida)}</td><td><code>${esc(a.arquivo)}:${a.linha}</code></td><td>${a.sensibilidade} × ${a.exposicao} = <b>${a.peso}</b></td></tr>`;
  }).join("") : `<tr><td colspan="6" class="vazio">Nenhum achado.</td></tr>`;

  const porCategoria = {};
  d.inventario.forEach(i => { porCategoria[i.categoria] = (porCategoria[i.categoria] || 0) + 1; });
  const itens = Object.entries(porCategoria);
  document.getElementById("inventario").innerHTML = itens.length
    ? itens.map(([c, n]) => `<span>${esc(c)}: <b>${n}</b> declaração(ões)</span>`).join("") + `<span>Total: <b>${d.inventario.length}</b></span>`
    : `<span>Nenhuma declaração de dado pessoal encontrada.</span>`;
}

document.getElementById("abas").innerHTML = ANALISES.map((d, i) => `<button role="tab" type="button">${esc(d.alvo)}</button>`).join("");
document.querySelectorAll("#abas button").forEach((b, i) => b.addEventListener("click", () => mostrar(i)));
mostrar(0);
</script>
</body>
</html>
"""


def gerar(analises: list[dict], destino: Path) -> None:
    dados = json.dumps(analises, ensure_ascii=False).replace("</", "<\\/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(MODELO.replace("__DADOS__", dados), encoding="utf-8")
