"""Prevê se a máxima de amanhã chega a 32 °C ou mais e publica o alerta na API.

Uso:
    python publicar_previsao.py                       # último dia disponível, envia para a API local
    python publicar_previsao.py --data 2024-11-13 --simular
    python publicar_previsao.py --api http://localhost:5080

O modelo é o Random Forest escolhido no notebook, retreinado só com os dias
anteriores à data informada, para que nada do futuro entre no treino.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from preparar_dados import LIMITE_C, carregar_horario, diario, montar_base, montar_variaveis

PASTA_DADOS = Path(__file__).resolve().parent / "dados" / "a701"
PARAMETROS = dict(n_estimators=200, max_depth=12, min_samples_leaf=20,
                  class_weight="balanced", random_state=42, n_jobs=-1)
LIMIAR = 0.50
HORAS_MINIMAS = 20


def ler_argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Publica na API a previsão de calor para amanhã.")
    p.add_argument("--data", type=pd.Timestamp,
                   help='o "hoje" da previsão, no formato AAAA-MM-DD (padrão: último dia disponível)')
    p.add_argument("--api", default="http://localhost:5080",
                   help="endereço da API (padrão: http://localhost:5080)")
    p.add_argument("--simular", action="store_true",
                   help="mostra o resultado sem enviar para a API")
    return p.parse_args()


def carregar_dias() -> pd.DataFrame:
    """Mesma preparação do notebook: dias com pelo menos 20 horas de leitura, em frequência diária."""
    dias = diario(carregar_horario(PASTA_DADOS))
    return dias[dias["horas"] >= HORAS_MINIMAS].asfreq("D")


def prever(dias: pd.DataFrame, hoje: pd.Timestamp) -> float:
    # Exemplos de treino: só dias anteriores a hoje. O alvo do último deles é a máxima de hoje,
    # que já é conhecida na noite em que a previsão é feita.
    X, y = montar_base(dias.loc[:hoje])
    X_treino, y_treino = X[X.index < hoje], y[y.index < hoje]

    # As variáveis de hoje são montadas sem o filtro de alvo, porque o amanhã ainda não aconteceu.
    variaveis_hoje = montar_variaveis(dias.loc[:hoje]).loc[[hoje]]
    if variaveis_hoje.isna().any(axis=None):
        faltando = ", ".join(variaveis_hoje.columns[variaveis_hoje.isna().iloc[0]])
        sys.exit(f"Erro: faltam dados em {hoje:%d/%m/%Y} para montar as variáveis ({faltando}).")

    modelo = RandomForestClassifier(**PARAMETROS)
    modelo.fit(X_treino, y_treino)
    print(f"Treino: {len(X_treino):,} dias, de {X_treino.index.min():%d/%m/%Y} a {X_treino.index.max():%d/%m/%Y}")
    return float(modelo.predict_proba(variaveis_hoje)[0, 1])


def publicar(api: str, corpo: dict) -> dict:
    requisicao = urllib.request.Request(
        api.rstrip("/") + "/api/alertas/previsao",
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=10) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        sys.exit(f"Erro: a API respondeu {erro.code}: {erro.read().decode('utf-8', 'replace')}")
    except urllib.error.URLError as erro:
        sys.exit(f"Erro: não foi possível conectar à API em {api} ({erro.reason}). Ela está rodando?")


def main() -> None:
    args = ler_argumentos()
    dias = carregar_dias()

    # Último dia disponível: o mais recente com todas as variáveis preenchidas.
    completos = montar_variaveis(dias).notna().all(axis=1)
    ultimo = completos[completos].index.max()
    hoje = (args.data or ultimo).normalize()
    if hoje > ultimo or hoje < dias.index.min():
        sys.exit(f"Erro: a data precisa estar entre {dias.index.min():%d/%m/%Y} e {ultimo:%d/%m/%Y}.")
    amanha = hoje + pd.Timedelta(days=1)

    print(f"Hoje: {hoje:%d/%m/%Y}, máxima de {dias.at[hoje, 'tmax']:.1f} °C")
    probabilidade = prever(dias, hoje)
    print(f"Probabilidade de máxima de {LIMITE_C} °C ou mais em {amanha:%d/%m/%Y}: {probabilidade:.0%}")

    # Em datas do histórico, mostra o que aconteceu de fato, para conferir a previsão.
    if amanha in dias.index and pd.notna(dias.at[amanha, "tmax"]):
        print(f"Real em {amanha:%d/%m/%Y}: máxima de {dias.at[amanha, 'tmax']:.1f} °C")

    if probabilidade < LIMIAR:
        print(f"Sem alerta (probabilidade de {probabilidade:.0%}, abaixo de {LIMIAR:.0%}).")
        return

    corpo = {
        "nivel": "Alto",
        "mensagem": (f"Previsão para amanhã ({amanha:%d/%m}): máxima de {LIMITE_C} °C ou mais. "
                     f"Probabilidade de {probabilidade:.0%}."),
    }
    if args.simular:
        print("Simulação: o alerta abaixo NÃO foi enviado.")
        print(json.dumps(corpo, ensure_ascii=False, indent=2))
        return

    alerta = publicar(args.api, corpo)
    print(f"Alerta publicado na API: id {alerta.get('id')}")
    print(json.dumps(alerta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
