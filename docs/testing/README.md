# Testing: Features e Test Cases

Material da disciplina Testing, Compliance & Quality Assurance, para importar no Azure DevOps.

| Arquivo | Uso |
|---|---|
| [features-e-testes.md](features-e-testes.md) | Leitura completa das 15 Features e dos 46 Test Cases. Serve também de contingência para o PDF |
| `features.csv` | Importação das Features no Azure Boards |
| `test-cases.csv` | Importação dos Test Cases no Azure Test Plans |
| `test-cases-amostra.csv` | Um único Test Case, para testar a importação antes |
| `conteudo.py` | Fonte única do conteúdo. Edite aqui e rode `python gerar_azure.py` |
| `publicar_azure.py` | Cria tudo no Azure DevOps pelo script |

## Situação

- **F01 a F09 e F15:** descrevem a API, que já está pronta. Todos os resultados esperados foram conferidos contra a API real, com banco limpo e na ordem do documento.
- **F10 a F14:** descrevem partes ainda em construção (Rede de Apoio, app, ESP32 e painel). Os Test Cases delas serão revisados quando cada parte ficar pronta.

## Como publicar (recomendado: script)

O script [publicar_azure.py](publicar_azure.py) sincroniza o projeto com `conteudo.py`: cria o que falta, atualiza no lugar o que mudou e liga cada Test Case novo à sua Feature. Pode ser executado de novo sem duplicar nada.

**Publicado em:** [RM556278 / GS-26](https://dev.azure.com/RM556278/GS-26/_workitems), com 15 Features e 46 Test Cases.

**Onde demonstrar:** em **Boards > Queries > Shared Queries**, o script também cria duas consultas:
- [GS — Features e Test Cases](https://dev.azure.com/RM556278/web/qr.aspx?pguid=650b5e8c-62cf-4ee6-b2ef-ed11c5570706&qid=c33e23e2-02b4-4077-a4c9-b3faa1d25ab9): cada Feature, de F-01 a F-15, com seus Test Cases logo abaixo.
- [GS — Test Cases](https://dev.azure.com/RM556278/web/qr.aspx?pguid=650b5e8c-62cf-4ee6-b2ef-ed11c5570706&qid=c43c9011-0219-41bd-9823-62cddec1a460): os 46 casos, de TC-01.01 a TC-15.01.

A lista das Features também aparece em **Boards > Backlogs > Features**. Os Test Cases não aparecem no Board nem no Backlog, porque o Azure não os trata como itens de backlog.

1. Faça login uma vez. O navegador abre para você entrar com a conta do Azure DevOps:
   ```bash
   az login --allow-no-subscriptions
   ```
2. Confira sem criar nada:
   ```bash
   cd docs/testing
   python publicar_azure.py --org https://dev.azure.com/<organizacao> --projeto "<projeto>" --simular
   ```
3. Rode sem `--simular` para aplicar.

**Padrão dos itens** (o mesmo do projeto Ford-VINSight):
- **Títulos:** `F-01 — Nome` para Features e `TC-01.01 — [Positivo] Nome` para Test Cases.
- **Critérios de aceite:** em Gherkin, com um `Cenário:` seguido de `Dado`, `Quando`, `Então` e `E`.

Requisitos:
- A conta precisa ter acesso **Basic** ao projeto.
- O processo do projeto precisa ser Agile, Scrum ou CMMI, porque o Basic não tem o tipo Feature.

## Como importar (alternativa: CSV)

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

Cada Test Case tem no título o código da Feature (por exemplo `TC-01.01` pertence à `F-01`) e as tags da Feature e do tipo (Positivo ou Negativo). Isso permite filtrar os casos por Feature.

## Para a entrega

A entrega pede o professor como Admin, o link do projeto no PDF e prints das Features e dos Test Cases como contingência.
