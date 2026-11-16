"""Carrega as regras de PII e de saídas inseguras dos arquivos TOML em cyber/regras/."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PASTA_REGRAS = Path(__file__).resolve().parent.parent / "regras"


@dataclass(frozen=True)
class Categoria:
    id: str
    nome: str
    sensibilidade: int
    campos: tuple[re.Pattern, ...]
    valores: tuple[re.Pattern, ...]
    validar: str | None
    alerta: str

    def casa_nome(self, nome: str) -> bool:
        return any(p.search(nome) for p in self.campos)


@dataclass(frozen=True)
class Saida:
    id: str
    linguagens: tuple[str, ...]
    exposicao: int
    descricao: str
    padrao: re.Pattern


@dataclass
class Regras:
    categorias: list[Categoria]
    saidas: list[Saida]
    nomes_protegidos: re.Pattern
    sanitizadores: re.Pattern
    derivacoes_seguras: re.Pattern
    chamadas_que_propagam: re.Pattern
    exposicao_estatica: dict[str, int] = field(default_factory=dict)

    def categoria_do_nome(self, nome: str) -> Categoria | None:
        """Categoria de um identificador (Cpf, contatoFamiliar...), ou None se não for dado sensível."""
        if self.nomes_protegidos.search(nome):
            return None
        for categoria in self.categorias:
            if categoria.casa_nome(nome):
                return categoria
        return None

    def saidas_da_linguagem(self, linguagem: str) -> list[Saida]:
        return [s for s in self.saidas if linguagem in s.linguagens]

    def por_id(self, id_categoria: str) -> Categoria:
        return next(c for c in self.categorias if c.id == id_categoria)


def carregar(pasta: Path = PASTA_REGRAS) -> Regras:
    with open(pasta / "regras_pii.toml", "rb") as f:
        pii = tomllib.load(f)
    with open(pasta / "saidas.toml", "rb") as f:
        saidas = tomllib.load(f)

    categorias = [
        Categoria(
            id=c["id"],
            nome=c["nome"],
            sensibilidade=int(c["sensibilidade"]),
            campos=tuple(re.compile(p) for p in c.get("campos", [])),
            valores=tuple(re.compile(p) for p in c.get("valores", [])),
            validar=c.get("validar"),
            alerta=c["alerta"],
        )
        for c in pii["categoria"]
    ]
    lista_saidas = [
        Saida(
            id=s["id"],
            linguagens=tuple(s["linguagens"]),
            exposicao=int(s["exposicao"]),
            descricao=s["descricao"],
            padrao=re.compile(s["padrao"]),
        )
        for s in saidas["saida"]
    ]
    return Regras(
        categorias=categorias,
        saidas=lista_saidas,
        nomes_protegidos=re.compile(pii["protecao"]["nomes_protegidos"]),
        sanitizadores=re.compile(pii["protecao"]["sanitizadores"]),
        derivacoes_seguras=re.compile(pii["protecao"]["derivacoes_seguras"]),
        chamadas_que_propagam=re.compile(pii["protecao"]["chamadas_que_propagam"]),
        exposicao_estatica=dict(saidas.get("exposicao_estatica", {})),
    )


def cpf_valido(texto: str) -> bool:
    """Confere os dígitos verificadores, para não confundir qualquer número de 11 dígitos com CPF."""
    d = [int(c) for c in texto if c.isdigit()]
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for pos in (9, 10):
        soma = sum(d[i] * (pos + 1 - i) for i in range(pos))
        digito = (soma * 10 % 11) % 10
        if d[pos] != digito:
            return False
    return True
