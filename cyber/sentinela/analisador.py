"""Análise estática do protótipo: inventário de PII, dados e segredos escritos no código e Taint Analysis.

O Taint Analysis segue o dado sensível dentro de cada método (C# e Java):
  1. Fontes: parâmetros com nome sensível (cpf, condicaoSaude...) e acessos a membros sensíveis (dados.Cpf).
  2. Propagação: atribuições (var texto = $"... {cpf}") contaminam a variável da esquerda.
  3. Proteção: chamadas e membros sanitizadores (Mascarar(cpf), cpf.Mascarado, Hash(senha)) limpam o dado.
  4. Saídas: logs, console, exceções, arquivos, respostas da API e envio a outros sistemas.
Um dado sensível que chega a uma saída sem proteção vira um achado do tipo "vazamento".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .regras import Categoria, Regras, Saida, cpf_valido

EXTENSOES_CODIGO = {".cs": "cs", ".java": "java"}
EXTENSOES_CONFIG = {".json", ".properties", ".yml", ".yaml", ".env"}
PASTAS_IGNORADAS = {"bin", "obj", "node_modules", ".git", "target", "Migracoes", "Migrations", ".venv", "__pycache__"}
PALAVRAS_DEV = re.compile(r"(?i)(desenvolvimento|development|\bdev\b|teste|test|exemplo|example|local)")

METODO = re.compile(
    r"(?:^|(?<=[{};]))[ \t]*(?:(?:public|private|protected|internal|static|async|override|virtual|sealed|final|"
    r"synchronized|abstract|partial|new)\s+)+[\w<>\[\],.?\s]*?\b(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w.,\s]+)?",
    re.MULTILINE,
)
DECLARACAO_TIPO = re.compile(r"\b(class|record|interface|struct|enum)\b")
IDENTIFICADOR = re.compile(r"(?<![\w.])([A-Za-z_]\w*)")
MEMBRO = re.compile(r"\.\s*([A-Za-z_]\w*)")
ATRIBUICAO = re.compile(r"^\s*(?:(?:var|final|let|[\w<>\[\]?,.]+)\s+)?([A-Za-z_]\w*)\s*(?:\+)?=(?!=)\s*(.+)$", re.DOTALL)


@dataclass
class Passo:
    linha: int
    texto: str


@dataclass
class Achado:
    tipo: str                 # vazamento | pii_literal | segredo
    categoria: Categoria
    arquivo: str
    linha: int
    trecho: str
    exposicao: int
    saida_id: str
    saida_descricao: str
    metodo: str = ""
    caminho: list[Passo] = field(default_factory=list)
    alerta: str = ""
    alerta_fonte: str = ""    # "llm" ou "texto padrao"

    @property
    def peso(self) -> int:
        return self.categoria.sensibilidade * self.exposicao

    @property
    def gravidade(self) -> str:
        if self.peso >= 20:
            return "critica"
        if self.peso >= 12:
            return "alta"
        if self.peso >= 6:
            return "media"
        return "baixa"


@dataclass
class ItemInventario:
    arquivo: str
    linha: int
    identificador: str
    categoria: Categoria


@dataclass
class Resultado:
    alvo: str
    arquivos_analisados: int = 0
    metodos_analisados: int = 0
    achados: list[Achado] = field(default_factory=list)
    inventario: list[ItemInventario] = field(default_factory=list)


# ---------------------------------------------------------------- utilidades de texto

def _sem_comentarios(codigo: str) -> str:
    """Troca comentários por espaços, preservando as quebras de linha (os números de linha continuam certos)."""
    def branco(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))
    padrao = re.compile(r'//[^\n]*|/\*.*?\*/|@?\$?"(?:\\.|[^"\\\n])*"', re.DOTALL)
    return padrao.sub(lambda m: m.group(0) if m.group(0).lstrip("@$").startswith('"') else branco(m), codigo)


def _so_codigo(expr: str) -> str:
    """Remove o texto fixo das strings, mas mantém o que está dentro de {...} nas strings interpoladas do C#."""
    def trocar(m: re.Match) -> str:
        literal = m.group(0)
        if literal.startswith("$") or literal.startswith("@$") or literal.startswith("$@"):
            return " " + " ".join(re.findall(r"\{([^{}]*)\}", literal)) + " "
        return '""'
    return re.sub(r'(?:\$@|@\$|\$|@)?"(?:\\.|[^"\\\n])*"', trocar, expr)


def _fora_de_strings(texto: str, inicio: int = 0):
    """Percorre o texto devolvendo (posição, caractere) só para o que está fora de strings e caracteres literais."""
    i, n = inicio, len(texto)
    while i < n:
        c = texto[i]
        if c == '"':
            i += 1
            while i < n and texto[i] != '"':
                i += 2 if texto[i] == "\\" else 1
            i += 1
            continue
        if c == "'" and i + 2 < n and (texto[i + 2] == "'" or (texto[i + 1] == "\\" and i + 3 < n and texto[i + 3] == "'")):
            i += 4 if texto[i + 1] == "\\" else 3
            continue
        yield i, c
        i += 1


def _fechamento(texto: str, abre: int, a: str = "(", f: str = ")") -> int:
    """Posição do caractere que fecha o par aberto em texto[abre], ignorando o conteúdo de strings."""
    nivel = 0
    for i, c in _fora_de_strings(texto, abre):
        if c == a:
            nivel += 1
        elif c == f:
            nivel -= 1
            if nivel == 0:
                return i
    return len(texto) - 1


def _linha(texto: str, pos: int, base: int) -> int:
    return base + texto.count("\n", 0, pos)


# ---------------------------------------------------------------- Taint Analysis

class _Taint:
    def __init__(self, regras: Regras, linguagem: str):
        self.regras = regras
        self.saidas = regras.saidas_da_linguagem(linguagem)

    def _proteger(self, expr: str) -> str:
        """Apaga da expressão as partes já protegidas por um sanitizador."""
        # Chamadas: Mascarar(cpf), HashSenha(x) -> o argumento inteiro fica protegido.
        saida, i = [], 0
        for m in self.regras.sanitizadores.finditer(expr):
            fim_nome = m.end()
            depois = expr[fim_nome:].lstrip()
            if depois.startswith("("):
                abre = expr.index("(", fim_nome)
                fecha = _fechamento(expr, abre)
                inicio = m.start()
                # cadeia antes do sanitizador (ex.: dados.Cpf.Mascarar()) também fica protegida
                while inicio > 0 and (expr[inicio - 1].isalnum() or expr[inicio - 1] in "._"):
                    inicio -= 1
                saida.append(expr[i:inicio])
                i = fecha + 1
            elif m.start() > 0 and expr[m.start() - 1] == ".":
                # Membro: cidadao.Cpf.Mascarado -> apaga a cadeia toda
                inicio = m.start() - 1
                while inicio > 0 and (expr[inicio - 1].isalnum() or expr[inicio - 1] in "._"):
                    inicio -= 1
                saida.append(expr[i:inicio])
                i = m.end()
        saida.append(expr[i:])
        return "".join(saida)

    def _so_o_que_propaga(self, expr: str) -> str:
        """Numa atribuição, apaga os argumentos de chamadas e construtores que não montam texto a partir do dado."""
        codigo = _so_codigo(expr)
        partes, i = [], 0
        for m in re.finditer(r"([A-Za-z_]\w*)\s*\(", codigo):
            if m.start() < i or self.regras.chamadas_que_propagam.match(m.group(1)):
                continue
            abre = m.end() - 1
            fecha = _fechamento(codigo, abre)
            partes.append(codigo[i:abre + 1])
            i = fecha
        partes.append(codigo[i:])
        return "".join(partes)

    def contaminacao(self, expr: str, contaminadas: dict[str, tuple[Categoria, Passo]]) -> tuple[Categoria, Passo | None] | None:
        """Devolve a categoria do dado sensível que a expressão carrega (ou None)."""
        codigo = self._proteger(_so_codigo(expr))
        for m in IDENTIFICADOR.finditer(codigo):
            nome = m.group(1)
            if nome in contaminadas:
                return contaminadas[nome]
        for m in MEMBRO.finditer(codigo):
            categoria = self.regras.categoria_do_nome(m.group(1))
            if categoria:
                return categoria, None
        for m in IDENTIFICADOR.finditer(codigo):
            categoria = self.regras.categoria_do_nome(m.group(1))
            if categoria:
                return categoria, None
        return None

    def metodo(self, arquivo: str, nome: str, parametros: str, corpo: str, linha_corpo: int, linha_cab: int) -> list[Achado]:
        achados: list[Achado] = []
        contaminadas: dict[str, tuple[Categoria, Passo]] = {}

        for parametro in filter(None, (p.strip() for p in parametros.split(","))):
            nome_param = re.sub(r"\[.*?\]|=.*$", "", parametro).split()[-1] if parametro.split() else ""
            categoria = self.regras.categoria_do_nome(nome_param)
            if categoria:
                contaminadas[nome_param] = (categoria, Passo(linha_cab, f"parâmetro {nome_param} ({categoria.nome})"))

        # Divide o corpo em comandos (terminados em ; { ou }), guardando a posição de cada um.
        inicio = 0
        nivel_parenteses = 0
        for i, c in _fora_de_strings(corpo + ";"):
            if c == "(":
                nivel_parenteses += 1
            elif c == ")":
                nivel_parenteses -= 1
            if c in ";{}" and nivel_parenteses <= 0:
                comando = corpo[inicio:i]
                if comando.strip():
                    achados += self._comando(arquivo, nome, comando, _linha(corpo, inicio, linha_corpo), contaminadas)
                inicio = i + 1
                nivel_parenteses = 0
        return achados

    def _comando(self, arquivo: str, metodo: str, comando: str, linha_bruta: int, contaminadas: dict) -> list[Achado]:
        """linha_bruta é a linha onde o texto do comando começa (pode ser o fim da linha anterior)."""
        achados = []
        texto = " ".join(comando.split())
        linha = _linha(comando, len(comando) - len(comando.lstrip()), linha_bruta)
        linha_de = lambda pos: _linha(comando, pos, linha_bruta)  # noqa: E731

        for saida in self.saidas:
            for m in saida.padrao.finditer(comando):
                abre = m.end() - 1
                argumentos = comando[abre:_fechamento(comando, abre) + 1]
                origem = self.contaminacao(argumentos, contaminadas)
                if origem:
                    categoria, passo = origem
                    caminho = []
                    if passo:
                        caminho.append(passo)
                    caminho.append(Passo(linha_de(m.start()), texto[:160]))
                    achados.append(Achado(
                        tipo="vazamento", categoria=categoria, arquivo=arquivo,
                        linha=linha_de(m.start()), trecho=texto[:200],
                        exposicao=saida.exposicao, saida_id=saida.id, saida_descricao=saida.descricao,
                        metodo=metodo, caminho=caminho,
                    ))

        atribuicao = ATRIBUICAO.match(comando)
        if atribuicao and not achados:
            destino, valor = atribuicao.group(1), atribuicao.group(2)
            derivado_seguro = (self.regras.nomes_protegidos.search(destino)
                               or self.regras.derivacoes_seguras.search(_so_codigo(valor)))
            origem = None if derivado_seguro else self.contaminacao(self._so_o_que_propaga(valor), contaminadas)
            if origem:
                categoria, passo_anterior = origem
                descricao = f"{destino} recebe {categoria.nome}: {texto[:120]}"
                contaminadas[destino] = (categoria, Passo(linha, descricao) if passo_anterior is None
                                         else Passo(passo_anterior.linha, passo_anterior.texto + f" → {descricao}"))
            elif destino in contaminadas:
                del contaminadas[destino]   # reatribuído com valor limpo
        return achados


def _metodos(codigo: str):
    """Encontra os métodos do arquivo: (nome, parâmetros, corpo, linha do corpo, linha do cabeçalho)."""
    for m in METODO.finditer(codigo):
        if DECLARACAO_TIPO.search(m.group(0)):
            continue
        resto = codigo[m.end():]
        posicao = m.end() + (len(resto) - len(resto.lstrip()))
        linha_cab = codigo.count("\n", 0, m.start()) + 1
        if codigo.startswith("=>", posicao):
            fim = codigo.find(";", posicao)
            corpo = codigo[posicao + 2:fim]
            yield m.group(1), m.group(2), corpo, codigo.count("\n", 0, posicao) + 1, linha_cab
        elif codigo.startswith("{", posicao):
            fecha = _fechamento(codigo, posicao, "{", "}")
            yield m.group(1), m.group(2), codigo[posicao + 1:fecha], codigo.count("\n", 0, posicao + 1) + 1, linha_cab


# ---------------------------------------------------------------- varreduras estáticas

def _eh_teste(caminho: Path) -> bool:
    return any(re.search(r"(?i)test", parte) for parte in caminho.parts)


def _literais_pii(regras: Regras, arquivo: str, texto: str, teste: bool) -> list[Achado]:
    achados = []
    vistos = set()
    exposicao = regras.exposicao_estatica["literal_teste" if teste else "literal_codigo"]
    for numero, linha in enumerate(texto.splitlines(), 1):
        for categoria in regras.categorias:
            for padrao in categoria.valores:
                for m in padrao.finditer(linha):
                    valor = m.group(0)
                    if categoria.validar == "cpf" and not cpf_valido(valor):
                        continue
                    if (categoria.id, valor) in vistos:
                        continue
                    vistos.add((categoria.id, valor))
                    achados.append(Achado(
                        tipo="pii_literal", categoria=categoria, arquivo=arquivo, linha=numero,
                        trecho=linha.strip()[:200], exposicao=exposicao,
                        saida_id="codigo_fonte",
                        saida_descricao="o código-fonte, que fica no repositório" + (" (dado de teste)" if teste else ""),
                    ))
    return achados


def _segredos(regras: Regras, arquivo: str, texto: str, extensao: str, teste: bool) -> list[Achado]:
    senha = regras.por_id("senha")
    achados = []
    if extensao == ".json":
        padrao = re.compile(r'"([\w.:-]+)"\s*:\s*"([^"]*)"')
    elif extensao in {".properties", ".env"}:
        padrao = re.compile(r"^\s*([\w.\-]+)\s*[=:]\s*(.+?)\s*$")
    elif extensao in {".yml", ".yaml"}:
        padrao = re.compile(r"^\s*([\w.\-]+)\s*:\s*['\"]?([^'\"#\n]+)")
    else:  # código: constante = "valor"
        padrao = re.compile(r'\b([A-Za-z_]\w*)\s*=\s*"([^"]{4,})"')
    for numero, linha in enumerate(texto.splitlines(), 1):
        for m in padrao.finditer(linha):
            chave, valor = m.group(1).split(".")[-1].split(":")[-1], m.group(2).strip()
            if not valor or regras.categoria_do_nome(chave) is not senha:
                continue
            if re.sub(r"[\W_]", "", valor).lower() == re.sub(r"[\W_]", "", chave).lower():
                continue  # rótulo, não segredo (ex.: CHAVE_SERVICO = "chave-servico")
            variavel = re.fullmatch(r"\$\{(\w+)(?::(.*))?\}", valor)
            if variavel and variavel.group(2) is None:
                continue  # só lê de variável de ambiente: correto
            padrao_dev = bool(variavel) or bool(PALAVRAS_DEV.search(valor)) or "appsettings" in arquivo.lower()
            if teste:
                tipo_exposicao, nota = "literal_teste", " (segredo fictício de teste)"
            elif padrao_dev:
                tipo_exposicao, nota = "segredo_padrao_dev", " (valor de desenvolvimento, trocável por variável de ambiente)"
            else:
                tipo_exposicao, nota = "segredo_fixo", ""
            achados.append(Achado(
                tipo="segredo", categoria=senha, arquivo=arquivo, linha=numero, trecho=linha.strip()[:200],
                exposicao=regras.exposicao_estatica[tipo_exposicao],
                saida_id="configuracao",
                saida_descricao="o código e a configuração guardados no repositório" + nota,
            ))
    return achados


def _inventario(regras: Regras, arquivo: str, codigo: str) -> list[ItemInventario]:
    itens = []
    declaracao = re.compile(r"\b(?:string|String|int|long|Cpf|bool|[\w<>?]+)\??\s+([A-Za-z_]\w*)\s*(?=[{;=,)])")
    vistos = set()
    for numero, linha in enumerate(codigo.splitlines(), 1):
        for m in declaracao.finditer(linha):
            nome = m.group(1)
            categoria = regras.categoria_do_nome(nome)
            if categoria and (nome.lower(), categoria.id) not in vistos:
                vistos.add((nome.lower(), categoria.id))
                itens.append(ItemInventario(arquivo, numero, nome, categoria))
    return itens


# ---------------------------------------------------------------- ponto de entrada

def analisar(alvos: list[Path], regras: Regras, raiz: Path | None = None, nome: str | None = None) -> Resultado:
    raiz = raiz or Path.cwd()
    resultado = Resultado(alvo=nome or ", ".join(str(a) for a in alvos))
    arquivos = []
    for alvo in alvos:
        if alvo.is_file():
            arquivos.append(alvo)
            continue
        for caminho in sorted(alvo.rglob("*")):
            if caminho.is_file() and not (set(caminho.parts) & PASTAS_IGNORADAS) and not caminho.name.endswith(".Designer.cs"):
                arquivos.append(caminho)

    for caminho in arquivos:
        extensao = caminho.suffix.lower()
        if extensao not in EXTENSOES_CODIGO and extensao not in EXTENSOES_CONFIG:
            continue
        try:
            texto = caminho.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            relativo = caminho.resolve().relative_to(raiz.resolve()).as_posix()
        except ValueError:
            relativo = caminho.as_posix()
        teste = _eh_teste(caminho)
        resultado.arquivos_analisados += 1

        resultado.achados += _literais_pii(regras, relativo, texto, teste)
        resultado.achados += _segredos(regras, relativo, texto, extensao, teste)

        if extensao in EXTENSOES_CODIGO:
            codigo = _sem_comentarios(texto)
            resultado.inventario += _inventario(regras, relativo, codigo)
            if teste:
                continue  # código de teste não é saída de produção
            taint = _Taint(regras, EXTENSOES_CODIGO[extensao])
            for nome_metodo, parametros, corpo, linha_corpo, linha_cab in _metodos(codigo):
                resultado.metodos_analisados += 1
                resultado.achados += taint.metodo(relativo, nome_metodo, parametros, corpo, linha_corpo, linha_cab)

    resultado.achados.sort(key=lambda a: (-a.peso, a.arquivo, a.linha))
    return resultado
