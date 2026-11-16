"""Tradução das falhas técnicas em alertas claros de risco real ao cidadão.

Usa o Claude (SDK oficial `anthropic`) quando o pacote está instalado e há credencial
(ANTHROPIC_API_KEY ou perfil do `ant auth login`). Sem isso, ou se a chamada falhar,
usa o texto de reserva da categoria definido em regras_pii.toml. O relatório sempre
indica qual das duas fontes gerou cada alerta.
"""

from __future__ import annotations

import os

from .analisador import Achado

MODELO = os.environ.get("SENTINELA_MODELO", "claude-opus-5-5")

INSTRUCOES = (
    "Você traduz falhas de segurança de software em alertas para cidadãos leigos, em português do Brasil. "
    "O sistema é a Sombra Amiga, que protege idosos e trabalhadores de rua da Brasilândia (São Paulo) "
    "contra o calor extremo. Escreva no máximo duas frases curtas, sem jargão técnico: "
    "diga qual dado da pessoa fica exposto, quem poderia vê-lo e que mal isso pode causar. "
    "Não invente fatos além da descrição recebida e não use alarmismo."
)


def _descricao_tecnica(achado: Achado) -> str:
    caminho = " | ".join(f"linha {p.linha}: {p.texto}" for p in achado.caminho)
    return (
        f"Tipo: {achado.tipo}. Dado: {achado.categoria.nome}. Saída: {achado.saida_descricao}. "
        f"Arquivo: {achado.arquivo}, linha {achado.linha}. Trecho: {achado.trecho}. Caminho do dado: {caminho or 'n/a'}."
    )


def _texto_padrao(achado: Achado) -> str:
    return achado.categoria.alerta.format(saida=achado.saida_descricao)


def _cliente():
    if os.environ.get("SENTINELA_SEM_LLM"):
        return None
    try:
        import anthropic
    except ImportError:
        return None
    try:
        return anthropic.Anthropic()
    except Exception:  # sem credencial configurada
        return None


def traduzir(achados: list[Achado]) -> str:
    """Preenche achado.alerta e achado.alerta_fonte. Devolve a fonte usada ("llm", "texto padrao" ou "misto")."""
    cliente = _cliente()
    fontes = set()
    cache: dict[tuple, tuple[str, str]] = {}

    for achado in achados:
        chave = (achado.tipo, achado.categoria.id, achado.saida_id)
        if chave in cache:
            achado.alerta, achado.alerta_fonte = cache[chave]
            fontes.add(achado.alerta_fonte)
            continue

        texto, fonte = _texto_padrao(achado), "texto padrao"
        if cliente is not None:
            texto_llm = _perguntar(cliente, achado)
            if texto_llm:
                texto, fonte = texto_llm, "llm"
        achado.alerta, achado.alerta_fonte = texto, fonte
        cache[chave] = (texto, fonte)
        fontes.add(fonte)

    if len(fontes) > 1:
        return "misto"
    return fontes.pop() if fontes else "texto padrao"


def _perguntar(cliente, achado: Achado) -> str | None:
    import anthropic

    try:
        resposta = cliente.beta.messages.create(
            model=MODELO,
            max_tokens=1024,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low"},
            system=INSTRUCOES,
            messages=[{"role": "user", "content": _descricao_tecnica(achado)}],
        )
    except (anthropic.APIConnectionError, anthropic.APIStatusError):
        return None
    if resposta.stop_reason == "refusal":
        return None
    partes = [bloco.text for bloco in resposta.content if bloco.type == "text"]
    texto = " ".join(" ".join(partes).split())
    return texto or None
