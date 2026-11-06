"""Carrega os CSVs horários da estação A701 (INMET) e gera a série diária local.

Os arquivos mudam de formato entre os anos:
- data: 2015-01-01 ou 2015/01/01
- hora: 00:00 ou 0000 UTC
- ausente: -9999 ou campo vazio
A hora vem em UTC, e o dia é calculado em horário local (UTC-3).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

COLUNAS = {
    2: "chuva_mm", 3: "pressao_mb", 6: "radiacao_kj", 7: "temp_c",
    8: "orvalho_c", 9: "temp_max_c", 10: "temp_min_c",
    15: "umidade_pct", 16: "vento_dir", 18: "vento_ms",
}


def ler_arquivo(caminho: Path) -> pd.DataFrame:
    bruto = pd.read_csv(caminho, sep=";", skiprows=8, encoding="latin-1",
                        decimal=",", dtype=str, index_col=False)
    data = bruto.iloc[:, 0].str.replace("/", "-", regex=False)
    hora = bruto.iloc[:, 1].str.replace(" UTC", "", regex=False).str.replace(":", "", regex=False).str.zfill(4).str[:4]
    saida = pd.DataFrame({"utc": pd.to_datetime(data + " " + hora, format="%Y-%m-%d %H%M")})
    for indice, nome in COLUNAS.items():
        valores = pd.to_numeric(bruto.iloc[:, indice].str.replace(",", ".", regex=False), errors="coerce")
        saida[nome] = valores.where(valores > -9000)
    return saida


def carregar_horario(pasta: Path) -> pd.DataFrame:
    arquivos = sorted(pasta.glob("*.CSV"))
    df = pd.concat([ler_arquivo(a) for a in arquivos], ignore_index=True)
    df = df.drop_duplicates("utc").sort_values("utc").reset_index(drop=True)
    df["local"] = df["utc"] - pd.Timedelta(hours=3)
    return df


def indice_calor(temp_c, umidade):
    """Índice de calor (fórmula de Rothfusz, NWS), em Celsius."""
    t = np.asarray(temp_c, dtype=float) * 9 / 5 + 32
    r = np.asarray(umidade, dtype=float)
    hi = (-42.379 + 2.04901523 * t + 10.14333127 * r - 0.22475541 * t * r
          - 6.83783e-3 * t ** 2 - 5.481717e-2 * r ** 2 + 1.22874e-3 * t ** 2 * r
          + 8.5282e-4 * t * r ** 2 - 1.99e-6 * t ** 2 * r ** 2)
    simples = 0.5 * (t + 61 + (t - 68) * 1.2 + r * 0.094)
    hi = np.where(t >= 80, hi, simples)
    return (hi - 32) * 5 / 9


def diario(horario: pd.DataFrame) -> pd.DataFrame:
    h = horario.copy()
    h["ic_c"] = indice_calor(h["temp_c"], h["umidade_pct"])
    h["dia"] = h["local"].dt.normalize()
    d = h.groupby("dia").agg(
        horas=("temp_c", "count"), tmax=("temp_max_c", "max"), tmin=("temp_min_c", "min"),
        tmed=("temp_c", "mean"), umid_med=("umidade_pct", "mean"), umid_min=("umidade_pct", "min"),
        chuva=("chuva_mm", "sum"), pressao=("pressao_mb", "mean"), vento=("vento_ms", "mean"),
        radiacao=("radiacao_kj", "sum"), ic_max=("ic_c", "max"),
    )
    return d


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    d = diario(carregar_horario(pasta))
    d.to_csv(sys.argv[2])
    print("dias", len(d), d.index.min().date(), d.index.max().date())
