# Machine Learning

Previsão de dia de calor perigoso (máxima de 32 °C ou mais) no dia seguinte, com dados reais do INMET.

| Arquivo | Conteúdo |
|---|---|
| [previsao_calor.ipynb](previsao_calor.ipynb) | Notebook executado: dados, preparação, treino, resultados e conclusão |
| [RELATORIO_ML.md](RELATORIO_ML.md) | Relatório do problema à conclusão |
| [preparar_dados.py](preparar_dados.py) | Leitura dos CSVs do INMET e agregação diária |
| [dados/README.md](dados/README.md) | Fonte, período e qualidade dos dados |
| `figuras/` | Gráficos gerados pelo notebook |

## Como rodar

Requisito: Python 3.12.

```bash
cd ml
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace previsao_calor.ipynb
```

A execução leva cerca de 1 minuto e meio.
