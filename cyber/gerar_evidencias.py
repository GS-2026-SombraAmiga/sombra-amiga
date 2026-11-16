"""Gera as evidências da auditoria em cyber/evidencias/.

  1. Roda a Sentinela Cidadã no protótipo real e nos dois exemplos (com vazamento e corrigido),
     guardando os relatórios (.json e .md) e a saída do terminal de cada execução (.txt).
  2. Gera o painel de Risco Cidadão com as três análises.
  3. Se o Microsoft Edge estiver instalado, tira um print de cada aba do painel.

Uso, na pasta cyber/:  python gerar_evidencias.py [--sem-llm]
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CYBER = Path(__file__).resolve().parent
EVIDENCIAS = CYBER / "evidencias"
ANALISES = [
    ("Protótipo Sombra Amiga", ["../api/src", "../servico-soa/src", "../api/tests"], "prototipo-sombra-amiga"),
    ("Exemplo com vazamento", ["exemplos/com-vazamento"], "exemplo-com-vazamento"),
    ("Exemplo corrigido", ["exemplos/corrigido"], "exemplo-corrigido"),
]
EDGE = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def rodar(argumentos: list[str]) -> subprocess.CompletedProcess:
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-m", "sentinela", *argumentos], cwd=CYBER, env=ambiente,
                          capture_output=True, text=True, encoding="utf-8")


def main() -> int:
    extra = ["--sem-llm"] if "--sem-llm" in sys.argv else []
    EVIDENCIAS.mkdir(exist_ok=True)

    for nome, alvos, slug in ANALISES:
        r = rodar(["analisar", *alvos, "--nome", nome, "--saida", "evidencias", "--bloquear", *extra])
        comando = "python -m sentinela analisar " + " ".join(alvos) + f' --nome "{nome}" --bloquear'
        texto = f"$ {comando}\n{r.stdout}{r.stderr}(código de saída: {r.returncode})\n"
        (EVIDENCIAS / f"terminal-{slug}.txt").write_text(texto, encoding="utf-8")
        print(texto)

    jsons = [f"evidencias/{slug}.json" for _, _, slug in ANALISES]
    print(rodar(["painel", *jsons, "--saida", "evidencias/painel-risco-cidadao.html"]).stdout)

    edge = next((e for e in EDGE if Path(e).exists()), shutil.which("msedge"))
    if not edge:
        print("Edge não encontrado: os prints do painel não foram gerados.")
        return 0
    painel = (EVIDENCIAS / "painel-risco-cidadao.html").read_text(encoding="utf-8")
    for indice, (_, _, slug) in enumerate(ANALISES):
        # Uma cópia do painel que abre direto na aba desejada.
        copia = EVIDENCIAS / f"_aba-{indice}.html"
        copia.write_text(painel.replace("mostrar(0);", f"mostrar({indice});"), encoding="utf-8")
        destino = EVIDENCIAS / f"painel-{slug}.png"
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,1700",
                        f"--screenshot={destino}", copia.as_uri()], capture_output=True)
        copia.unlink()
        print(f"Print: {destino.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
