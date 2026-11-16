"""Linha de comando da Sentinela Cidadã.

  python -m sentinela analisar <pastas ou arquivos...> [--nome NOME] [--saida PASTA] [--bloquear]
      Analisa o código, traduz os achados em alertas e grava <saida>/<nome>.json e .md.
      Com --bloquear, termina com código 1 se algum dado pessoal vazar para uma saída insegura
      (gravidade alta ou crítica). É o que trava a entrega no GitHub Actions.

  python -m sentinela painel <relatorios.json...> [--saida painel.html]
      Junta uma ou mais análises no painel de Risco Cidadão.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

from . import analisador, llm, painel, regras, relatorio

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]


def _slug(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-") or "analise"


def cmd_analisar(args) -> int:
    alvos = [Path(a) for a in args.alvos]
    faltando = [a for a in alvos if not a.exists()]
    if faltando:
        print(f"Não encontrado: {', '.join(map(str, faltando))}", file=sys.stderr)
        return 2

    resultado = analisador.analisar(alvos, regras.carregar(), raiz=RAIZ_REPOSITORIO, nome=args.nome)
    fonte = llm.traduzir(resultado.achados) if not args.sem_llm else "texto padrao"
    if args.sem_llm:
        for a in resultado.achados:
            a.alerta, a.alerta_fonte = a.categoria.alerta.format(saida=a.saida_descricao), "texto padrao"
    dados = relatorio.para_dict(resultado, fonte)

    saida = Path(args.saida)
    base = saida / _slug(resultado.alvo)
    relatorio.salvar_json(dados, base.with_suffix(".json"))
    base.with_suffix(".md").write_text(relatorio.markdown(dados), encoding="utf-8")

    r = dados["resumo"]
    print(f"Sentinela Cidadã · {resultado.alvo}")
    print(f"  Arquivos: {dados['arquivos_analisados']} · métodos seguidos: {dados['metodos_analisados']}")
    print(f"  Risco Cidadão: {r['risco_cidadao']}/100 ({r['faixa_rotulo']})")
    print("  Achados: " + ", ".join(f"{relatorio.ROTULO_GRAVIDADE[g]} {n}" for g, n in r["por_gravidade"].items()))
    for a in dados["achados"]:
        if a["tipo"] == "vazamento":
            print(f"  [VAZAMENTO {relatorio.ROTULO_GRAVIDADE[a['gravidade']].upper()}] {a['categoria']} -> {a['saida']} "
                  f"em {a['arquivo']}:{a['linha']} ({a['metodo']})")
    print(f"  Relatórios: {base.with_suffix('.json')} e .md")

    if args.bloquear and r["vazamentos_bloqueantes"]:
        print(f"BLOQUEADO: {r['vazamentos_bloqueantes']} vazamento(s) de dado pessoal para saída insegura.", file=sys.stderr)
        return 1
    if args.bloquear:
        print("LIBERADO: nenhum dado pessoal chega a uma saída insegura.")
    return 0


def cmd_painel(args) -> int:
    analises = [json.loads(Path(a).read_text(encoding="utf-8")) for a in args.relatorios]
    painel.gerar(analises, Path(args.saida))
    print(f"Painel gerado: {args.saida}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sentinela", description="Sentinela Cidadã: PII, Taint Analysis e Risco Cidadão.")
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("analisar", help="analisa pastas ou arquivos de código")
    p.add_argument("alvos", nargs="+")
    p.add_argument("--nome", help="nome da análise no relatório e no painel")
    p.add_argument("--saida", default="saida", help="pasta dos relatórios (padrão: saida)")
    p.add_argument("--bloquear", action="store_true", help="código de saída 1 se houver vazamento grave")
    p.add_argument("--sem-llm", action="store_true", help="usa só os textos padrão das regras")
    p.set_defaults(func=cmd_analisar)

    p = sub.add_parser("painel", help="gera o painel de Risco Cidadão")
    p.add_argument("relatorios", nargs="+")
    p.add_argument("--saida", default="saida/painel.html")
    p.set_defaults(func=cmd_painel)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
