# Testing: Features e Test Cases

Material da disciplina Testing, Compliance & Quality Assurance, para importar no Azure DevOps.

| Arquivo | Uso |
|---|---|
| [features-e-testes.md](features-e-testes.md) | Leitura completa das 15 Features e dos 46 Test Cases. Serve também de contingência para o PDF |
| `features.csv` | Importação das Features no Azure Boards |
| `test-cases.csv` | Importação dos Test Cases no Azure Test Plans |
| `test-cases-amostra.csv` | Um único Test Case, para testar a importação antes |
| `conteudo.py` | Fonte única do conteúdo. Edite aqui e rode `python gerar_azure.py` |

## Situação

- **F01 a F09 e F15:** descrevem a API, que já está pronta. Todos os resultados esperados foram conferidos contra a API real, com banco limpo e na ordem do documento.
- **F10 a F14:** descrevem partes ainda em construção (Rede de Apoio, app, ESP32 e painel). Os Test Cases delas serão revisados quando cada parte ficar pronta.

## Como importar

**Features:**
1. No projeto, abra **Boards > Work items > Import Work Items**.
2. Escolha `features.csv`.
3. Confira o mapeamento de colunas e salve os itens.

Se o processo do projeto não tiver o campo **Acceptance Criteria** para Feature, o assistente vai avisar. Nesse caso, me avise para eu juntar os critérios na descrição.

**Test Cases:**
1. Abra **Test Plans** e crie um plano, por exemplo "Homologação Sombra Amiga".
2. No menu da suíte, use a opção de importar casos de teste de um CSV.
3. Importe primeiro `test-cases-amostra.csv` e confira se objetivo, passos e resultados esperados apareceram certos.
4. Se estiver tudo certo, apague o caso de amostra e importe `test-cases.csv`.

Cada Test Case tem no título o código da Feature (por exemplo `F01-TC01`) e as tags da Feature e do tipo (Positivo ou Negativo). Isso permite filtrar os casos por Feature.

## Para a entrega

A entrega pede o professor como Admin, o link do projeto no PDF e prints das Features e dos Test Cases como contingência.
