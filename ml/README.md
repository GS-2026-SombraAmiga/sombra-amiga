# Machine Learning

Previsão de dia de calor perigoso (máxima de 32 °C ou mais) no dia seguinte, com dados reais do INMET.

**Vídeo de demonstração:** https://youtu.be/0q5JtlM2ivk

| Arquivo | Conteúdo |
|---|---|
| [previsao_calor.ipynb](previsao_calor.ipynb) | Notebook executado: dados, preparação, treino, resultados e conclusão |
| [RELATORIO_ML.md](RELATORIO_ML.md) | Relatório do problema à conclusão |
| [preparar_dados.py](preparar_dados.py) | Leitura dos CSVs do INMET, agregação diária e variáveis do modelo (`montar_base`) |
| [publicar_previsao.py](publicar_previsao.py) | Treina o modelo e publica na API o alerta de calor para amanhã |
| [dados/README.md](dados/README.md) | Fonte, período e qualidade dos dados |
| `figuras/` | Gráficos gerados pelo notebook |
| [TODO.md](TODO.md) | Tarefas pendentes: script de publicação da previsão e vídeo |

## Como rodar

Requisito: Python 3.12.

```bash
cd ml
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace previsao_calor.ipynb
```

A execução leva cerca de 1 minuto e meio.

## Publicar previsão

O script [publicar_previsao.py](publicar_previsao.py) leva a previsão do notebook para a API. Ele treina o Random Forest escolhido no notebook (`n_estimators=200`, `max_depth=12`, `min_samples_leaf=20`, `class_weight="balanced"`) usando **só os dias anteriores** à data da previsão, calcula a probabilidade de a máxima de amanhã chegar a 32 °C ou mais e, se ela for de 50% ou mais, envia o alerta para `POST /api/alertas/previsao`. As variáveis vêm da mesma função `montar_base` usada no notebook, em [preparar_dados.py](preparar_dados.py).

| Argumento | Padrão | O que faz |
|---|---|---|
| `--data AAAA-MM-DD` | último dia disponível | O "hoje" da previsão. O alerta é para o dia seguinte |
| `--api URL` | `http://localhost:5080` | Endereço da API |
| `--simular` | desligado | Mostra o resultado sem enviar para a API |

O último dia disponível é o mais recente com todas as variáveis preenchidas. Nos dados atuais é 20/10/2026, porque 21/10 e 26/10 têm menos de 20 horas de leitura e são descartados, como no notebook, e isso deixa a média de 7 dias vazia até o fim do mês.

**1. Simular** (não precisa da API):

```bash
cd ml
python publicar_previsao.py --data 2024-02-07 --simular
```

```
Hoje: 07/02/2024, máxima de 31.7 °C
Treino: 3,218 dias, de 07/01/2015 a 06/02/2024
Probabilidade de máxima de 32 °C ou mais em 08/02/2024: 81%
Real em 08/02/2024: máxima de 33.1 °C
Simulação: o alerta abaixo NÃO foi enviado.
{
  "nivel": "Alto",
  "mensagem": "Previsão para amanhã (08/02): máxima de 32 °C ou mais. Probabilidade de 81%."
}
```

Em datas do histórico, a linha "Real em" mostra o que aconteceu de fato no dia seguinte. Abaixo de 50%, o script só imprime "Sem alerta" e a probabilidade.

**2. Publicar na API:**

```bash
cd api
dotnet run --project src/SombraAmiga.Api --urls http://localhost:5080
```

Em outro terminal:

```bash
cd ml
python publicar_previsao.py --data 2024-02-07
```

O alerta aparece em http://localhost:5080/api/alertas/ativos, com origem `Previsao`. O script não usa dependência nova: o envio é feito com `urllib.request`, da biblioteca padrão do Python.
