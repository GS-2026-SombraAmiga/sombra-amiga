"""Índice de Risco Cidadão (0 a 100).

Cada achado tem um peso = sensibilidade do dado (1-5) x exposição da saída (1-5), de 1 a 25.
A chance de esse achado causar dano a um cidadão é estimada por p = (peso / 25)^3:
  - um CPF numa resposta da API (5 x 5 = 25) vale p = 1;
  - um CPF no log (5 x 3 = 15) vale p = 0,22;
  - um segredo de desenvolvimento no repositório (5 x 2 = 10) vale p = 0,06;
  - um CPF fictício num teste (5 x 1 = 5) vale p = 0,008.

O índice é a chance de pelo menos um achado causar dano:
    Risco Cidadão = 100 x (1 - produto(1 - p))
Assim o índice cresce com cada falha, mas nunca passa de 100, e o cubo faz poucas falhas graves
pesarem muito mais que muitas falhas leves.
"""

from __future__ import annotations

from collections import Counter

from .analisador import Achado

FAIXAS = [(85, "critico", "Crítico"), (60, "alto", "Alto"), (30, "moderado", "Moderado"), (0, "baixo", "Baixo")]


def indice(achados: list[Achado]) -> int:
    chance_sem_dano = 1.0
    for achado in achados:
        chance_sem_dano *= 1 - (achado.peso / 25) ** 3
    return round(100 * (1 - chance_sem_dano))


def faixa(valor: int) -> tuple[str, str]:
    for minimo, codigo, rotulo in FAIXAS:
        if valor >= minimo:
            return codigo, rotulo
    return FAIXAS[-1][1], FAIXAS[-1][2]


def resumo(achados: list[Achado]) -> dict:
    valor = indice(achados)
    codigo, rotulo = faixa(valor)
    return {
        "risco_cidadao": valor,
        "faixa": codigo,
        "faixa_rotulo": rotulo,
        "por_gravidade": {g: sum(1 for a in achados if a.gravidade == g) for g in ("critica", "alta", "media", "baixa")},
        "por_tipo": dict(Counter(a.tipo for a in achados)),
        "por_categoria": dict(Counter(a.categoria.nome for a in achados)),
        "vazamentos_bloqueantes": sum(1 for a in achados if a.tipo == "vazamento" and a.peso >= 12),
    }
