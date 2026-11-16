"""Relatórios da análise: JSON (para o painel e para máquinas) e Markdown (para pessoas)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .analisador import Resultado
from .risco import resumo

ROTULO_GRAVIDADE = {"critica": "Crítica", "alta": "Alta", "media": "Média", "baixa": "Baixa"}
ROTULO_TIPO = {"vazamento": "Vazamento (Taint Analysis)", "pii_literal": "Dado pessoal no código", "segredo": "Segredo na configuração"}


def para_dict(resultado: Resultado, fonte_alertas: str) -> dict:
    return {
        "alvo": resultado.alvo,
        "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "arquivos_analisados": resultado.arquivos_analisados,
        "metodos_analisados": resultado.metodos_analisados,
        "fonte_alertas": fonte_alertas,
        "resumo": resumo(resultado.achados),
        "achados": [
            {
                "tipo": a.tipo,
                "tipo_rotulo": ROTULO_TIPO[a.tipo],
                "categoria": a.categoria.nome,
                "categoria_id": a.categoria.id,
                "sensibilidade": a.categoria.sensibilidade,
                "exposicao": a.exposicao,
                "peso": a.peso,
                "gravidade": a.gravidade,
                "arquivo": a.arquivo,
                "linha": a.linha,
                "metodo": a.metodo,
                "saida": a.saida_id,
                "saida_descricao": a.saida_descricao,
                "trecho": a.trecho,
                "caminho": [{"linha": p.linha, "texto": p.texto} for p in a.caminho],
                "alerta": a.alerta,
                "alerta_fonte": a.alerta_fonte,
            }
            for a in resultado.achados
        ],
        "inventario": [
            {"arquivo": i.arquivo, "linha": i.linha, "identificador": i.identificador, "categoria": i.categoria.nome}
            for i in resultado.inventario
        ],
    }


def salvar_json(dados: dict, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def markdown(dados: dict) -> str:
    r = dados["resumo"]
    linhas = [
        f"# Sentinela Cidadã: {dados['alvo']}",
        "",
        f"- **Risco Cidadão:** {r['risco_cidadao']}/100 ({r['faixa_rotulo']})",
        f"- **Arquivos analisados:** {dados['arquivos_analisados']} · **métodos seguidos pelo Taint Analysis:** {dados['metodos_analisados']}",
        f"- **Achados por gravidade:** " + ", ".join(f"{ROTULO_GRAVIDADE[g]} {n}" for g, n in r["por_gravidade"].items()),
        f"- **Vazamentos que bloqueiam a entrega:** {r['vazamentos_bloqueantes']}",
        f"- **Alertas gerados por:** {'LLM (Claude)' if dados['fonte_alertas'] == 'llm' else 'texto padrão das regras' if dados['fonte_alertas'] == 'texto padrao' else 'LLM e texto padrão'}",
        f"- **Gerado em:** {dados['gerado_em']}",
        "",
    ]
    if not dados["achados"]:
        linhas += ["Nenhum achado.", ""]
    for i, a in enumerate(dados["achados"], 1):
        linhas += [
            f"## {i}. {ROTULO_GRAVIDADE[a['gravidade']]}: {a['categoria']} em {a['saida']} ({a['tipo_rotulo']})",
            "",
            f"> **Para o cidadão:** {a['alerta']}",
            "",
            f"- **Onde:** `{a['arquivo']}`, linha {a['linha']}" + (f", método `{a['metodo']}`" if a["metodo"] else ""),
            f"- **Peso:** sensibilidade {a['sensibilidade']} × exposição {a['exposicao']} = {a['peso']}",
            f"- **Trecho:** `{a['trecho']}`",
        ]
        if a["caminho"]:
            linhas.append("- **Caminho do dado:**")
            linhas += [f"  - linha {p['linha']}: {p['texto']}" for p in a["caminho"]]
        linhas.append("")
    if dados["inventario"]:
        linhas += ["## Inventário de dados pessoais declarados no código", "", "| Arquivo | Linha | Identificador | Categoria |", "|---|---|---|---|"]
        linhas += [f"| `{i['arquivo']}` | {i['linha']} | `{i['identificador']}` | {i['categoria']} |" for i in dados["inventario"]]
        linhas.append("")
    return "\n".join(linhas)
