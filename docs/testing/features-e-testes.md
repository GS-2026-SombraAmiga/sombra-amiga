# Features e Test Cases

Gerado por `gerar_azure.py` a partir de `conteudo.py`. Não edite à mão.

| Feature | Test Cases | Positivos | Negativos |
|---|---|---|---|
| F01 Cadastro e manutenção do cidadão | 5 | 2 | 3 |
| F02 Risco de calor personalizado | 4 | 2 | 2 |
| F03 Pontos de sombra e água próximos | 2 | 1 | 1 |
| F04 Check-in "estou bem" | 3 | 1 | 2 |
| F05 Recebimento das leituras dos sensores | 4 | 1 | 3 |
| F06 Alertas automáticos de calor | 3 | 2 | 1 |
| F07 Previsão de calor da véspera | 4 | 2 | 2 |
| F08 Indicador de impacto | 2 | 1 | 1 |
| F09 Gestão dos pontos de hidratação | 3 | 2 | 1 |
| F10 Rede de Apoio: acesso dos agentes | 3 | 1 | 2 |
| F11 Rede de Apoio: atendimento de pedidos de ajuda | 3 | 2 | 1 |
| F12 App do cidadão | 4 | 2 | 2 |
| F13 Estação de monitoramento no ponto (ESP32) | 3 | 2 | 1 |
| F14 Painel web de acompanhamento | 2 | 1 | 1 |
| F15 Proteção de dados pessoais | 1 | 1 | 0 |

**Total:** 15 Features e 46 Test Cases.

## F01 - Cadastro e manutenção do cidadão

**Como idoso ou trabalhador de rua, quero me cadastrar informando meu perfil, para receber alertas de calor adequados à minha vulnerabilidade.**

O cadastro guarda nome, CPF, contato de um familiar, condição de saúde (opcional) e, para trabalhadores de rua, a ocupação. O cidadão pode atualizar os dados ou remover o cadastro.

**Critérios de aceite**

1. Dado que informo perfil, nome, CPF válido e contato de um familiar, quando envio o cadastro, então ele é criado e recebo um identificador.
2. Dado que sou trabalhador de rua, quando não informo a ocupação, então o cadastro é recusado com a mensagem "Ocupação é obrigatória.".
3. Dado que o CPF é inválido, quando envio o cadastro, então ele é recusado com a mensagem "CPF inválido.".
4. Dado que o CPF já está cadastrado, quando envio o cadastro, então ele é recusado com a mensagem "Já existe um cadastro com este CPF.".
5. Dado que estou cadastrado, quando atualizo meus dados ou removo o cadastro, então a alteração é aplicada.

### F01-TC01 [Positivo] Cadastrar idoso com dados válidos

- **Objetivo:** Verificar que um idoso consegue se cadastrar com dados válidos.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. CPF 529.982.247-25 ainda não cadastrado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Abrir POST /api/cidadaos e clicar em Try it out. | O campo de requisição fica editável. |
| 2 | Informar {"perfil": "Idoso", "nome": "Lurdes Teste", "cpf": "52998224725", "contatoFamiliar": "Filha Teste", "condicaoSaude": "Hipertensão"} e clicar em Execute. | Resposta HTTP 201. |
| 3 | Conferir o corpo da resposta. | Contém id, nome "Lurdes Teste", cpfMascarado "***.***.***-25", perfil "Idoso" e temCondicaoSaude true. |

### F01-TC02 [Negativo] Recusar trabalhador de rua sem ocupação

- **Objetivo:** Verificar que o cadastro de trabalhador de rua exige a ocupação.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. CPF 111.444.777-35 ainda não cadastrado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Abrir POST /api/cidadaos e clicar em Try it out. | O campo de requisição fica editável. |
| 2 | Informar {"perfil": "TrabalhadorDeRua", "nome": "Rafael Teste", "cpf": "11144477735", "contatoFamiliar": "Irmão Teste"} e clicar em Execute. | Resposta HTTP 400 com title "Ocupação é obrigatória.". |
| 3 | Consultar GET /api/cidadaos. | O nome "Rafael Teste" não aparece na lista. |

### F01-TC03 [Negativo] Recusar CPF inválido sem repetir o valor enviado

- **Objetivo:** Verificar que um CPF inválido é recusado e que a mensagem de erro não expõe o número.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Abrir POST /api/cidadaos e clicar em Try it out. | O campo de requisição fica editável. |
| 2 | Informar {"perfil": "Idoso", "nome": "Teste", "cpf": "12345678900", "contatoFamiliar": "Contato"} e clicar em Execute. | Resposta HTTP 400 com title "CPF inválido.". |
| 3 | Conferir o corpo da resposta. | O número 12345678900 não aparece no corpo. |

### F01-TC04 [Negativo] Recusar CPF já cadastrado

- **Objetivo:** Verificar que não é possível cadastrar duas pessoas com o mesmo CPF.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Caso de teste "Cadastrar idoso com dados válidos" executado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Abrir POST /api/cidadaos e clicar em Try it out. | O campo de requisição fica editável. |
| 2 | Informar {"perfil": "Idoso", "nome": "Outra Pessoa", "cpf": "529.982.247-25", "contatoFamiliar": "Contato"} e clicar em Execute. | Resposta HTTP 409 com title "Já existe um cadastro com este CPF.". |

### F01-TC05 [Positivo] Atualizar e remover o cadastro

- **Objetivo:** Verificar que o cidadão consegue atualizar os dados e remover o cadastro.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Um cidadão cadastrado, com o id anotado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em PUT /api/cidadaos/{id}, informar {"nome": "Nome Atualizado", "contatoFamiliar": "Contato"} e clicar em Execute. | Resposta HTTP 204. |
| 2 | Consultar GET /api/cidadaos/{id}. | Resposta HTTP 200 com nome "Nome Atualizado". |
| 3 | Executar DELETE /api/cidadaos/{id}. | Resposta HTTP 204. |
| 4 | Consultar GET /api/cidadaos/{id} novamente. | Resposta HTTP 404 com title "Cidadão não encontrado.". |

## F02 - Risco de calor personalizado

**Como cidadão, quero ver o risco de calor de agora ajustado ao meu perfil, com uma orientação simples, para saber como me proteger.**

O risco usa a maior sensação térmica medida pelos sensores nas últimas 3 horas. As faixas são: baixo (abaixo de 27 °C), atenção (27 °C), alto (32 °C) e extremo (41 °C). Para refletir a vulnerabilidade, somam-se 3 °C para idosos, 2 °C para trabalhadores de rua e 1 °C para quem informou condição de saúde.

**Critérios de aceite**

1. Dado que há leituras nas últimas 3 horas, quando consulto o risco geral, então vejo a sensação térmica e o nível.
2. Dado que sou idoso com condição de saúde, quando consulto meu risco, então o nível considera os ajustes do meu perfil e a orientação é própria para idosos.
3. Dado que não há leituras nas últimas 3 horas, quando consulto o risco, então vejo "Sem leituras recentes dos sensores.".
4. Dado um cidadão inexistente, quando consulto o risco dele, então recebo "Cidadão não encontrado.".

### F02-TC01 [Negativo] Consultar risco geral sem leituras recentes

- **Objetivo:** Verificar a resposta quando os sensores não enviaram dados nas últimas 3 horas.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/risco/atual sem parâmetros. | Resposta HTTP 200 com nivel null e orientacao "Sem leituras recentes dos sensores.". |

### F02-TC02 [Positivo] Consultar risco geral com calor de atenção

- **Objetivo:** Verificar o cálculo do risco geral a partir de uma leitura recente.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 29, "umidadePct": 50} e clicar em Execute. | Resposta HTTP 201 com indiceCalorC 29.7 e nivel "Atencao". |
| 2 | Executar GET /api/risco/atual sem parâmetros. | Resposta HTTP 200 com nivel "Atencao" e orientacao "Risco geral: atenção.". |

### F02-TC03 [Positivo] Consultar risco personalizado de idoso com hipertensão

- **Objetivo:** Verificar que o mesmo calor tem risco maior para um idoso com condição de saúde.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Executados, nesta ordem, os casos "Consultar risco geral com calor de atenção" e "Cadastrar idoso com dados válidos", com o id do idoso anotado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/risco/atual com cidadaoId igual ao id do idoso. | Resposta HTTP 200 com nivel "Alto". |
| 2 | Conferir a orientação. | orientacao "Evite sair entre 11h e 16h. Beba água mesmo sem sede.". |

### F02-TC04 [Negativo] Consultar risco de cidadão inexistente

- **Objetivo:** Verificar que um identificador desconhecido é recusado.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/risco/atual com cidadaoId 00000000-0000-0000-0000-000000000001. | Resposta HTTP 404 com title "Cidadão não encontrado.". |

## F03 - Pontos de sombra e água próximos

**Como trabalhador de rua, quero ver os pontos de sombra e água mais próximos de onde estou, para parar e me hidratar sem perder tempo.**

A busca considera apenas pontos ativos dentro de um raio, de 2 km por padrão, e mostra tipo e distância, do mais próximo ao mais distante.

**Critérios de aceite**

1. Dado que informo minha localização, quando busco pontos próximos, então vejo os pontos ativos dentro do raio, ordenados pela distância.
2. Dado que não há pontos dentro do raio, quando busco, então recebo uma lista vazia, sem erro.
3. Pontos desativados não aparecem na busca.

### F03-TC01 [Positivo] Buscar pontos próximos ordenados pela distância

- **Objetivo:** Verificar a ordenação e a distância dos pontos retornados.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API. Os 3 pontos simulados de demonstração estão ativos.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/pontos/proximos com latitude -23.4620, longitude -46.6810 e raioKm 5. | Resposta HTTP 200 com 3 pontos. |
| 2 | Conferir o primeiro ponto e a ordem. | O primeiro é "Praça da Sombra (simulado)" com distanciaKm 0, e as distâncias seguintes são crescentes. |

### F03-TC02 [Negativo] Buscar pontos longe de qualquer ponto cadastrado

- **Objetivo:** Verificar a resposta quando não há pontos dentro do raio.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/pontos/proximos com latitude -23.5505, longitude -46.6333 e raioKm 2. | Resposta HTTP 200 com lista vazia []. |

## F04 - Check-in "estou bem"

**Como idoso, quero avisar com um toque que estou bem ou que preciso de ajuda, para minha família ficar tranquila sem precisar me ligar.**

O check-in registra o status e o horário. O histórico fica disponível para a família, do mais recente ao mais antigo. Um check-in "preciso de ajuda" abre um pedido na Rede de Apoio (F11).

**Critérios de aceite**

1. Dado que estou cadastrado, quando faço um check-in "estou bem", então ele é registrado com data e hora.
2. Dado que fiz check-ins, quando a família consulta meu histórico, então os vê do mais recente ao mais antigo.
3. Dado um cidadão inexistente, quando o check-in é enviado, então ele é recusado.
4. Dado um status diferente de "EstouBem" ou "PrecisoDeAjuda", quando o check-in é enviado, então ele é recusado.

### F04-TC01 [Positivo] Registrar check-in e consultar o histórico

- **Objetivo:** Verificar o registro do check-in e sua exibição no histórico.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Um cidadão cadastrado, com o id anotado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "EstouBem"} e clicar em Execute. | Resposta HTTP 201 com status "EstouBem" e dataHoraUtc preenchida. |
| 2 | Executar GET /api/cidadaos/{id}/checkins. | O check-in registrado aparece em primeiro lugar. |

### F04-TC02 [Negativo] Recusar check-in de cidadão inexistente

- **Objetivo:** Verificar que não é possível registrar check-in para quem não está cadastrado.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/checkins, informar {"cidadaoId": "00000000-0000-0000-0000-000000000001", "status": "EstouBem"} e clicar em Execute. | Resposta HTTP 404 com title "Cidadão não encontrado.". |

### F04-TC03 [Negativo] Recusar check-in com status inválido

- **Objetivo:** Verificar que só os status previstos são aceitos.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Um cidadão cadastrado, com o id anotado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "Talvez"} e clicar em Execute. | Resposta HTTP 400. |
| 2 | Executar GET /api/cidadaos/{id}/checkins. | Nenhum check-in novo aparece. |

## F05 - Recebimento das leituras dos sensores

**Como responsável pelos pontos de hidratação, quero que cada ponto envie temperatura e umidade, para o sistema saber a sensação térmica real em cada lugar.**

A API recebe a leitura do ESP32, calcula o índice de calor pela fórmula de Rothfusz (NWS) e classifica o nível de risco. Leituras fora da faixa do sensor são recusadas.

**Critérios de aceite**

1. Dado uma leitura com temperatura entre -10 °C e 60 °C e umidade entre 0% e 100%, quando ela é enviada, então é registrada com a sensação térmica e o nível.
2. Dado uma temperatura fora da faixa, quando a leitura é enviada, então ela é recusada com "Temperatura fora da faixa do sensor.".
3. Dado uma umidade fora da faixa, quando a leitura é enviada, então ela é recusada com "Umidade deve estar entre 0 e 100.".
4. Dado um ponto inexistente, quando a leitura é enviada, então ela é recusada com "Ponto não encontrado.".

### F05-TC01 [Positivo] Registrar leitura de calor extremo

- **Objetivo:** Verificar o cálculo da sensação térmica e do nível de uma leitura válida.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 38, "umidadePct": 50} e clicar em Execute. | Resposta HTTP 201 com indiceCalorC 48.6 e nivel "Extremo". |

### F05-TC02 [Negativo] Recusar umidade acima de 100%

- **Objetivo:** Verificar que leituras impossíveis de umidade são recusadas.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 30, "umidadePct": 150} e clicar em Execute. | Resposta HTTP 400 com title "Umidade deve estar entre 0 e 100.". |

### F05-TC03 [Negativo] Recusar temperatura fora da faixa do sensor

- **Objetivo:** Verificar que leituras impossíveis de temperatura são recusadas.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 99, "umidadePct": 50} e clicar em Execute. | Resposta HTTP 400 com title "Temperatura fora da faixa do sensor.". |

### F05-TC04 [Negativo] Recusar leitura de ponto inexistente

- **Objetivo:** Verificar que só pontos cadastrados podem enviar leituras.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "00000000-0000-0000-0000-000000000001", "temperaturaC": 30, "umidadePct": 50} e clicar em Execute. | Resposta HTTP 404 com title "Ponto não encontrado.". |

## F06 - Alertas automáticos de calor

**Como cidadão, quero ser avisado quando um ponto do meu bairro estiver com calor perigoso, para evitar me expor naquele momento.**

Uma leitura com sensação térmica de 32 °C ou mais abre um alerta para o ponto. Se o calor piorar, o mesmo alerta é atualizado, sem duplicar. Quando a sensação cai abaixo de 32 °C, o alerta é encerrado.

**Critérios de aceite**

1. Dado uma leitura de risco alto ou extremo, quando ela é registrada, então um alerta ativo é aberto para o ponto.
2. Dado um alerta já aberto, quando o calor piora, então o mesmo alerta passa a mostrar o novo nível, sem criar outro.
3. Dado um alerta aberto, quando uma leitura abaixo de 32 °C é registrada, então o alerta é encerrado.
4. Dado um alerta já encerrado, quando tento encerrá-lo de novo, então recebo "Alerta já encerrado.".

### F06-TC01 [Positivo] Abrir e atualizar alerta conforme o calor piora

- **Objetivo:** Verificar a abertura do alerta e sua atualização sem duplicação.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 33, "umidadePct": 50}. | Resposta HTTP 201 com nivel "Alto". |
| 2 | Executar GET /api/alertas/ativos. | Um alerta, com origem "Sensor", nivel "Alto" e mensagem iniciada por "Calor alto em Praça da Sombra (simulado)". |
| 3 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 38, "umidadePct": 50}. | Resposta HTTP 201 com nivel "Extremo". |
| 4 | Executar GET /api/alertas/ativos. | Continua um único alerta, agora com nivel "Extremo" e mensagem "Calor extremo em Praça da Sombra (simulado): sensação de 48,6 °C.". |

### F06-TC02 [Positivo] Encerrar alerta quando o calor diminui

- **Objetivo:** Verificar o encerramento automático do alerta.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Caso "Abrir e atualizar alerta conforme o calor piora" executado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 22, "umidadePct": 50}. | Resposta HTTP 201 com nivel "Baixo". |
| 2 | Executar GET /api/alertas/ativos. | O alerta da Praça da Sombra não aparece mais. |

### F06-TC03 [Negativo] Recusar encerramento de alerta já encerrado

- **Objetivo:** Verificar que um alerta não pode ser encerrado duas vezes.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/alertas/previsao, informar {"nivel": "Alto", "mensagem": "Teste"} e anotar o id retornado. | Resposta HTTP 201. |
| 2 | Executar POST /api/alertas/{id}/encerrar. | Resposta HTTP 204. |
| 3 | Executar POST /api/alertas/{id}/encerrar novamente. | Resposta HTTP 400 com title "Alerta já encerrado.". |

## F07 - Previsão de calor da véspera

**Como idoso, quero ser avisado na noite anterior quando o dia seguinte for muito quente, para me preparar antes de o calor chegar.**

Um modelo de Machine Learning treinado com dados reais do INMET (estação A701) prevê se a máxima do dia seguinte chegará a 32 °C ou mais. Quando a probabilidade é de 50% ou mais, o script ml/publicar_previsao.py publica um alerta de origem "Previsao" na API.

**Critérios de aceite**

1. Dado que o modelo prevê calor para amanhã, quando o script roda, então um alerta de previsão é publicado na API.
2. Dado que o modelo não prevê calor, quando o script roda, então nenhum alerta é publicado.
3. Dado o modo --simular, quando o script roda, então ele mostra a probabilidade sem publicar nada.
4. Dado um alerta de previsão sem mensagem, quando ele é enviado, então é recusado.

### F07-TC01 [Positivo] Publicar alerta de previsão manualmente

- **Objetivo:** Verificar que a API aceita alertas vindos da previsão.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/alertas/previsao, informar {"nivel": "Alto", "mensagem": "Amanhã deve passar de 32 °C."}. | Resposta HTTP 201 com origem "Previsao" e ativo true. |
| 2 | Executar GET /api/alertas/ativos. | O alerta aparece na lista. |

### F07-TC02 [Negativo] Recusar alerta de previsão sem mensagem

- **Objetivo:** Verificar que o alerta precisa ter uma mensagem para o cidadão.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/alertas/previsao, informar {"nivel": "Alto", "mensagem": ""}. | Resposta HTTP 400. |

### F07-TC03 [Positivo] Script publica previsão para véspera de dia quente

- **Objetivo:** Verificar a integração entre o modelo e a API em um dia real seguido de calor.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Python com as dependências de ml/requirements.txt. Em 15/03/2024, a máxima foi 34,2 °C, e em 16/03/2024, 34,1 °C.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Na pasta ml, executar python publicar_previsao.py --data 2024-03-15. | O script mostra probabilidade de 50% ou mais e informa que o alerta foi publicado. |
| 2 | Executar GET /api/alertas/ativos. | Aparece um alerta com origem "Previsao" citando 16/03. |

### F07-TC04 [Negativo] Script não publica previsão para dia frio

- **Objetivo:** Verificar que o script não gera alerta quando não há previsão de calor.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Em 01/07/2025, a máxima foi 15,8 °C, e em 02/07/2025, 13,0 °C.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/alertas/ativos e anotar a quantidade de alertas. | Lista retornada. |
| 2 | Na pasta ml, executar python publicar_previsao.py --data 2025-07-01. | O script mostra probabilidade abaixo de 50% e "sem alerta". |
| 3 | Executar GET /api/alertas/ativos. | A quantidade de alertas é a mesma do passo 1. |

## F08 - Indicador de impacto

**Como equipe gestora do Sombra Amiga, quero acompanhar quantos cidadãos confirmam que estão bem nos dias de alerta, para medir se a solução protege as pessoas.**

Indicador da Ficha: percentual de check-ins "estou bem" confirmados em dias com alerta, em relação ao esperado (cidadãos cadastrados × dias com alerta). Cada cidadão conta uma vez por dia.

**Critérios de aceite**

1. Dado um período com alertas e check-ins, quando consulto o indicador, então vejo dias com alerta, check-ins esperados, confirmados e o percentual.
2. Dado um período sem alertas, quando consulto o indicador, então o percentual é 0.
3. Dado uma data final anterior à inicial, quando consulto, então recebo "A data final deve ser maior ou igual à inicial.".

### F08-TC01 [Positivo] Calcular indicador em dia com alerta

- **Objetivo:** Verificar o cálculo do indicador com um cidadão que confirmou estar bem.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Cadastrar um idoso válido em POST /api/cidadaos e anotar o id. | Resposta HTTP 201. |
| 2 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 38, "umidadePct": 50}. | Resposta HTTP 201 e alerta aberto. |
| 3 | Em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "EstouBem"}. | Resposta HTTP 201. |
| 4 | Executar GET /api/indicadores/impacto com inicio e fim iguais à data de hoje (AAAA-MM-DD). | diasComAlerta 1, checkInsEsperados 1, checkInsConfirmados 1 e percentualConfirmado 100. |

### F08-TC02 [Negativo] Recusar período invertido

- **Objetivo:** Verificar a validação do período consultado.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/indicadores/impacto com inicio 2026-11-30 e fim 2026-11-01. | Resposta HTTP 400 com title "A data final deve ser maior ou igual à inicial.". |

## F09 - Gestão dos pontos de hidratação

**Como responsável pelos pontos, quero cadastrar, atualizar e desativar pontos de sombra e água, para manter o mapa do bairro correto.**

Cada ponto tem nome, tipo (sombra, água ou os dois) e coordenadas. A desativação preserva o histórico de leituras.

**Critérios de aceite**

1. Dado nome, tipo e coordenadas válidas, quando cadastro um ponto, então ele passa a aparecer na lista.
2. Dado coordenadas fora do intervalo válido, quando cadastro, então o ponto é recusado.
3. Dado um ponto ativo, quando o desativo, então ele deixa de aparecer nas listas e buscas.

### F09-TC01 [Positivo] Cadastrar ponto válido

- **Objetivo:** Verificar o cadastro de um novo ponto.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/pontos, informar {"nome": "Bebedouro Teste", "tipo": "Agua", "latitude": -23.47, "longitude": -46.68}. | Resposta HTTP 201 com o id do ponto. |
| 2 | Executar GET /api/pontos. | "Bebedouro Teste" aparece na lista. |

### F09-TC02 [Negativo] Recusar ponto com latitude inválida

- **Objetivo:** Verificar a validação das coordenadas.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/pontos, informar {"nome": "Ponto Errado", "tipo": "Agua", "latitude": 95, "longitude": -46.68}. | Resposta HTTP 400. |
| 2 | Executar GET /api/pontos. | "Ponto Errado" não aparece na lista. |

### F09-TC03 [Positivo] Desativar ponto

- **Objetivo:** Verificar que um ponto desativado sai das listas.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar DELETE /api/pontos/33333333-3333-3333-3333-333333333333. | Resposta HTTP 204. |
| 2 | Executar GET /api/pontos. | "Abrigo do Terminal (simulado)" não aparece mais. |

## F10 - Rede de Apoio: acesso dos agentes

**Como agente comunitário de saúde ou voluntário, quero entrar na Rede de Apoio com meu login, para atender pedidos de ajuda sem expor dados de pessoas vulneráveis a quem não deve vê-los.**

Serviço Java (Spring Boot). O agente se cadastra com nome, e-mail, bairro e senha. O login devolve um token JWT, exigido nas rotas de atendimento.

**Critérios de aceite**

1. Dado e-mail e senha corretos, quando faço login, então recebo um token de acesso.
2. Dado uma senha errada, quando faço login, então o acesso é negado sem informar qual dado estava errado.
3. Dado uma requisição sem token, quando acesso os pedidos de ajuda, então o acesso é negado.

### F10-TC01 [Positivo] Fazer login com credenciais válidas

- **Objetivo:** Verificar a emissão do token para um agente cadastrado.
- **Preparação:** Serviço Rede de Apoio em execução, com Swagger aberto. Agente de teste cadastrado com e-mail agente@teste.com.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/auth/login, informar o e-mail e a senha do agente de teste. | Resposta HTTP 200 com um token. |
| 2 | Autorizar o Swagger com o token e executar GET /api/pedidos. | Resposta HTTP 200. |

### F10-TC02 [Negativo] Negar login com senha errada

- **Objetivo:** Verificar que uma senha errada não dá acesso.
- **Preparação:** Serviço Rede de Apoio em execução. Agente de teste cadastrado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/auth/login, informar o e-mail do agente de teste e uma senha errada. | Resposta HTTP 401, sem token e sem indicar se o erro foi no e-mail ou na senha. |

### F10-TC03 [Negativo] Negar acesso aos pedidos sem token

- **Objetivo:** Verificar que os dados dos pedidos exigem autenticação.
- **Preparação:** Serviço Rede de Apoio em execução.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/pedidos sem autorização. | Resposta HTTP 401. |

## F11 - Rede de Apoio: atendimento de pedidos de ajuda

**Como idoso, quero que alguém da minha região venha me ajudar quando eu disser que não estou bem, para não ficar sozinho em um dia de calor perigoso.**

Um check-in "preciso de ajuda" abre um pedido na Rede de Apoio. Um agente aceita o pedido e, depois de atender, o conclui. O pedido passa por aberto, em atendimento e concluído.

**Critérios de aceite**

1. Dado um check-in "preciso de ajuda", quando ele é registrado, então um pedido aberto aparece para os agentes.
2. Dado um pedido aberto, quando um agente o aceita, então o pedido fica em atendimento com esse agente.
3. Dado um pedido já aceito por outro agente, quando tento aceitá-lo, então a ação é recusada.
4. Dado um pedido em atendimento, quando o agente responsável o conclui, então o pedido fica concluído.

### F11-TC01 [Positivo] Pedido de ajuda chega à Rede de Apoio

- **Objetivo:** Verificar a integração entre o check-in da API principal e a Rede de Apoio.
- **Preparação:** API principal e Rede de Apoio em execução. Um cidadão cadastrado na API principal e um agente logado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Na API principal, em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "PrecisoDeAjuda"}. | Resposta HTTP 201. |
| 2 | Na Rede de Apoio, executar GET /api/pedidos com o token do agente. | Aparece um pedido com status "ABERTO" para o cidadão. |

### F11-TC02 [Positivo] Aceitar e concluir um pedido

- **Objetivo:** Verificar o fluxo completo de atendimento.
- **Preparação:** Rede de Apoio em execução. Um pedido aberto e um agente logado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar POST /api/pedidos/{id}/aceitar com o token do agente. | Resposta HTTP 200 com status "EM_ATENDIMENTO". |
| 2 | Executar POST /api/pedidos/{id}/concluir com o mesmo token. | Resposta HTTP 200 com status "CONCLUIDO". |

### F11-TC03 [Negativo] Recusar pedido já aceito por outro agente

- **Objetivo:** Verificar que dois agentes não atendem o mesmo pedido.
- **Preparação:** Rede de Apoio em execução. Um pedido já aceito pelo agente A. O agente B está logado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar POST /api/pedidos/{id}/aceitar com o token do agente B. | Resposta HTTP 409. |

## F12 - App do cidadão

**Como idoso ou trabalhador de rua, quero um app simples no celular, para ver o risco de calor, achar pontos de água e avisar que estou bem.**

App em React Native (Expo) com telas de cadastro, início (risco e orientação), pontos próximos e alertas. O cadastro e os últimos dados ficam salvos no celular, e o app usa letras grandes, bom contraste e linguagem simples.

**Critérios de aceite**

1. Dado o primeiro acesso, quando concluo o cadastro, então o app passa a abrir direto na tela inicial.
2. Dado que há leituras recentes, quando abro o app, então vejo o nível de risco e a orientação do meu perfil.
3. Dado que toco em "Estou bem", quando o envio termina, então vejo a confirmação do check-in.
4. Dado que estou sem internet, quando abro o app, então vejo os últimos dados salvos e o horário da última atualização.

### F12-TC01 [Positivo] Concluir cadastro no primeiro acesso

- **Objetivo:** Verificar a jornada de cadastro pelo app.
- **Preparação:** API em execução. App instalado sem dados salvos.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Abrir o app. | A tela de cadastro é exibida. |
| 2 | Escolher o perfil Idoso, preencher nome, CPF 529.982.247-25 e contato do familiar, e tocar em Cadastrar. | A tela inicial é exibida com o nome do cidadão. |
| 3 | Fechar e abrir o app de novo. | O app abre direto na tela inicial. |

### F12-TC02 [Positivo] Fazer check-in pela tela inicial

- **Objetivo:** Verificar o check-in de um toque.
- **Preparação:** API em execução. App com cadastro concluído.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Na tela inicial, tocar em "Estou bem". | O app mostra a confirmação com o horário do check-in. |

### F12-TC03 [Negativo] Recusar cadastro com CPF inválido no app

- **Objetivo:** Verificar que o app mostra o erro de forma compreensível.
- **Preparação:** API em execução. App sem dados salvos.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Preencher o cadastro com o CPF 123.456.789-00 e tocar em Cadastrar. | O app mostra "CPF inválido." e continua na tela de cadastro. |

### F12-TC04 [Negativo] Mostrar últimos dados sem internet

- **Objetivo:** Verificar o funcionamento sem conexão.
- **Preparação:** App com cadastro concluído e aberto ao menos uma vez com internet.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Ativar o modo avião e abrir o app. | A tela inicial mostra os últimos dados salvos e o horário da última atualização, sem travar. |

## F13 - Estação de monitoramento no ponto (ESP32)

**Como pessoa que passa pelo ponto de hidratação, quero ver ali mesmo o nível de calor, para decidir se paro para me hidratar mesmo sem celular.**

Circuito ESP32 simulado no Wokwi, com sensor DHT22, display LCD e LEDs. Mede temperatura e umidade, calcula a sensação térmica, mostra o nível no display e nos LEDs (verde para baixo, amarelo para atenção, vermelho para alto e extremo, com aviso sonoro no extremo) e envia a leitura para a API.

**Critérios de aceite**

1. Dado uma leitura do sensor, quando ela é processada, então o display mostra a sensação térmica e o nível, e o LED correspondente acende.
2. Dado um nível extremo, quando ele é detectado, então o aviso sonoro é acionado.
3. Dado uma falha de leitura do sensor, quando ela ocorre, então o display mostra "ERRO SENSOR" e nada é enviado à API.
4. Dado que a rede está indisponível, quando há uma leitura, então o aviso local continua funcionando e o display indica "SEM REDE".

### F13-TC01 [Positivo] Exibir nível extremo no ponto

- **Objetivo:** Verificar o aviso local e o envio da leitura para a API.
- **Preparação:** Projeto aberto no Wokwi e simulação iniciada. API acessível pelo simulador.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | No DHT22, ajustar a temperatura para 38 °C e a umidade para 50%. | O display mostra a sensação de cerca de 48,6 °C e o nível EXTREMO. |
| 2 | Observar os LEDs e o buzzer. | O LED vermelho acende e o buzzer toca. |
| 3 | Na API, executar GET /api/leituras com o pontoId do circuito. | A leitura de 38 °C aparece em primeiro lugar. |

### F13-TC02 [Positivo] Exibir nível baixo no ponto

- **Objetivo:** Verificar o estado normal do circuito.
- **Preparação:** Projeto aberto no Wokwi e simulação iniciada.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | No DHT22, ajustar a temperatura para 22 °C e a umidade para 50%. | O display mostra o nível BAIXO, o LED verde acende e o buzzer fica em silêncio. |

### F13-TC03 [Negativo] Manter aviso local sem rede

- **Objetivo:** Verificar que o ponto continua útil sem conexão.
- **Preparação:** Projeto aberto no Wokwi com o endereço da API apontando para um servidor desligado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Iniciar a simulação e ajustar o DHT22 para 38 °C e 50%. | O display mostra EXTREMO e "SEM REDE", e o LED vermelho e o buzzer continuam funcionando. |

## F14 - Painel web de acompanhamento

**Como equipe da UBS ou da ONG parceira, quero um painel com os alertas ativos e o indicador de impacto, para saber onde agir primeiro.**

Página web hospedada na VM Linux. Mostra os alertas ativos, os pontos com a última leitura e o indicador de impacto, com atualização periódica.

**Critérios de aceite**

1. Dado que há alertas ativos, quando abro o painel, então vejo cada alerta com nível, ponto e horário.
2. Dado que um novo alerta é aberto, quando o painel se atualiza, então o alerta aparece sem recarregar a página manualmente.
3. Dado que a API está fora do ar, quando abro o painel, então vejo um aviso de indisponibilidade em vez de uma tela em branco.

### F14-TC01 [Positivo] Exibir alerta novo no painel

- **Objetivo:** Verificar a atualização automática do painel.
- **Preparação:** API e painel em execução. Painel aberto no navegador.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Em POST /api/leituras, informar {"pontoId": "11111111-1111-1111-1111-111111111111", "temperaturaC": 38, "umidadePct": 50}. | Resposta HTTP 201. |
| 2 | Aguardar a próxima atualização do painel, sem recarregar a página. | O alerta extremo da Praça da Sombra aparece com o horário. |

### F14-TC02 [Negativo] Avisar indisponibilidade da API

- **Objetivo:** Verificar o comportamento do painel quando a API cai.
- **Preparação:** Painel em execução e API parada.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Abrir o painel no navegador. | O painel mostra um aviso de que os dados estão indisponíveis. |

## F15 - Proteção de dados pessoais

**Como cidadão, quero que meu CPF, meu contato e minha condição de saúde não fiquem expostos, para confiar no serviço.**

As respostas da API mostram o CPF mascarado e nunca exibem contato do familiar ou condição de saúde. Mensagens de erro não repetem dados enviados. Todos os dados de pessoas usados no projeto são fictícios.

**Critérios de aceite**

1. Dado um cidadão cadastrado, quando consulto a lista ou o detalhe, então o CPF aparece mascarado.
2. Dado um cidadão com condição de saúde, quando consulto seus dados, então só aparece se ele tem condição de saúde, sem o texto.
3. O contato do familiar não aparece em nenhuma resposta.

### F15-TC01 [Positivo] Mascarar dados sensíveis na listagem

- **Objetivo:** Verificar que a listagem não expõe dados sensíveis.
- **Preparação:** API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger. Caso "Cadastrar idoso com dados válidos" executado.

| # | Ação e entradas | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/cidadaos. | O cidadão aparece com cpfMascarado "***.***.***-25". |
| 2 | Procurar no corpo da resposta os textos 52998224725, Hipertensão e Filha Teste. | Nenhum dos três aparece. |
