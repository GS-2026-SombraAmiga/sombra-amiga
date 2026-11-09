# To-Do de ML

Responsável: Pedro Henrique Junqueira

O notebook, o relatório e os dados já estão no repositório. Os CSVs da estação A701 ficam em `dados/a701/`, então tudo roda a partir de um clone, sem baixar nada do INMET.

## Antes de começar

- [ ] Aceitar o convite da organização `GS-2026-SombraAmiga` no GitHub e conferir se tem permissão de escrita
- [ ] Clonar o repositório e criar uma branch, por exemplo `pedro/publicar-previsao`
- [ ] Rodar o notebook e conferir que os números batem com o [RELATORIO_ML.md](RELATORIO_ML.md) (instruções no [README](README.md))

## 1. Script `ml/publicar_previsao.py`

**Objetivo:** levar a previsão do modelo para a API, que hoje só existe dentro do notebook.

**O que o script faz:**

1. Recebe três argumentos:
   - `--data AAAA-MM-DD`: o "hoje" da previsão. O padrão é o último dia disponível.
   - `--api`: o endereço da API. O padrão é `http://localhost:5080`.
   - `--simular`: mostra o resultado sem enviar para a API.
2. Carrega os dados com `carregar_horario` e `diario`, de [preparar_dados.py](preparar_dados.py).
3. Treina o Random Forest com os parâmetros escolhidos no notebook, usando só os dias **anteriores** à data informada: `n_estimators=200`, `max_depth=12`, `min_samples_leaf=20`, `class_weight="balanced"` e `random_state=42`.
4. Calcula a probabilidade de a máxima de amanhã chegar a 32 °C ou mais.
5. Se a probabilidade for de 0,50 ou mais, envia o alerta para `POST /api/alertas/previsao`:

   ```json
   {
     "nivel": "Alto",
     "mensagem": "Previsão para amanhã (dd/mm): máxima de 32 °C ou mais. Probabilidade de 78%."
   }
   ```

   Se for menor, só imprime "sem alerta" e a probabilidade.

**Cuidados:**

- **Reaproveitar as variáveis do notebook:** mova a função `montar_base` do notebook para `preparar_dados.py` e importe-a nos dois lugares, para não existirem duas versões.
- **O dia da previsão não tem alvo:** `montar_base` descarta as linhas em que ainda não se sabe o dia seguinte, e é exatamente esse o dia que queremos prever. As variáveis do dia da previsão precisam ser montadas sem esse filtro.
- **Nada do futuro entra no treino:** só dias anteriores à data informada.
- **Sem dependência nova:** use `urllib.request`, que já vem com o Python, para fazer o POST.

**Como testar:**

1. Suba a API:
   ```bash
   cd api
   dotnet run --project src/SombraAmiga.Api --urls http://localhost:5080
   ```
2. Rode o script com `--simular` em um dia de 2024 ou 2025 seguido de um dia quente.
3. Rode sem `--simular` e confira o alerta em http://localhost:5080/api/alertas/ativos.

**Pronto quando:**

- [ ] O script funciona nos dois modos, com e sem `--simular`
- [ ] O notebook continua executando sem erros depois de mover `montar_base`
- [ ] O [README](README.md) tem uma seção "Publicar previsão" explicando como usar
- [ ] Pull request aberto para a `main`

## 2. Vídeo de ML

Até 5 minutos, no YouTube como **não listado**. O link vai para o Teams junto com o do repositório.

| Tempo | Conteúdo |
|---|---|
| 0:00 a 0:30 | O problema: calor extremo, idosos e trabalhadores de rua |
| 0:30 a 1:15 | Os dados reais do INMET e o gráfico de dias quentes por ano |
| 1:15 a 2:00 | A pergunta de ML, as variáveis e a divisão temporal |
| 2:00 a 3:00 | Os 24 testes de hiperparâmetros e o gráfico de overfitting |
| 3:00 a 4:15 | Treino x teste e a comparação com a persistência, incluindo o que o modelo **não** melhora |
| 4:15 a 5:00 | O que isso significa para o cidadão e o script publicando o alerta na API |

- [ ] Vídeo gravado e publicado
- [ ] Link adicionado ao [README](README.md)
