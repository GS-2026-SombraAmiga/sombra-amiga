"""Fonte única das Features e dos Test Cases do Azure DevOps.

Edite aqui e rode gerar_azure.py para atualizar os CSVs e o documento.
"""

API = "API em execução (dotnet run) e Swagger aberto em http://localhost:5080/swagger"
BANCO_NOVO = "Banco recém-criado: apague api/src/SombraAmiga.Api/sombra-amiga.db antes de iniciar a API"
PRACA = "11111111-1111-1111-1111-111111111111"

FEATURES = [
    {
        "id": "F01",
        "titulo": "Cadastro e manutenção do cidadão",
        "historia": "Como idoso ou trabalhador de rua, quero me cadastrar informando meu perfil, para receber alertas de calor adequados à minha vulnerabilidade.",
        "descricao": "O cadastro guarda nome, CPF, contato de um familiar, condição de saúde (opcional) e, para trabalhadores de rua, a ocupação. O cidadão pode atualizar os dados ou remover o cadastro.",
        "testes": [
            {
                "titulo": "Cadastrar idoso com dados válidos",
                "tipo": "Positivo",
                "objetivo": "Verificar que um idoso consegue se cadastrar com dados válidos.",
                "preparacao": f"{API}. CPF 529.982.247-25 ainda não cadastrado.",
                "passos": [
                    ("Abrir POST /api/cidadaos e clicar em Try it out.", "O campo de requisição fica editável."),
                    ('Informar {"perfil": "Idoso", "nome": "Lurdes Teste", "cpf": "52998224725", "contatoFamiliar": "Filha Teste", "condicaoSaude": "Hipertensão"} e clicar em Execute.', "Resposta HTTP 201."),
                    ("Conferir o corpo da resposta.", 'Contém id, nome "Lurdes Teste", cpfMascarado "***.***.***-25", perfil "Idoso" e temCondicaoSaude true.'),
                ],
            },
            {
                "titulo": "Recusar trabalhador de rua sem ocupação",
                "tipo": "Negativo",
                "objetivo": "Verificar que o cadastro de trabalhador de rua exige a ocupação.",
                "preparacao": f"{API}. CPF 111.444.777-35 ainda não cadastrado.",
                "passos": [
                    ("Abrir POST /api/cidadaos e clicar em Try it out.", "O campo de requisição fica editável."),
                    ('Informar {"perfil": "TrabalhadorDeRua", "nome": "Rafael Teste", "cpf": "11144477735", "contatoFamiliar": "Irmão Teste"} e clicar em Execute.', 'Resposta HTTP 400 com title "Ocupação é obrigatória.".'),
                    ("Consultar GET /api/cidadaos.", 'O nome "Rafael Teste" não aparece na lista.'),
                ],
            },
            {
                "titulo": "Recusar CPF inválido sem repetir o valor enviado",
                "tipo": "Negativo",
                "objetivo": "Verificar que um CPF inválido é recusado e que a mensagem de erro não expõe o número.",
                "preparacao": API + ".",
                "passos": [
                    ("Abrir POST /api/cidadaos e clicar em Try it out.", "O campo de requisição fica editável."),
                    ('Informar {"perfil": "Idoso", "nome": "Teste", "cpf": "12345678900", "contatoFamiliar": "Contato"} e clicar em Execute.', 'Resposta HTTP 400 com title "CPF inválido.".'),
                    ("Conferir o corpo da resposta.", "O número 12345678900 não aparece no corpo."),
                ],
            },
            {
                "titulo": "Recusar CPF já cadastrado",
                "tipo": "Negativo",
                "objetivo": "Verificar que não é possível cadastrar duas pessoas com o mesmo CPF.",
                "preparacao": f"{API}. Caso de teste \"Cadastrar idoso com dados válidos\" executado.",
                "passos": [
                    ("Abrir POST /api/cidadaos e clicar em Try it out.", "O campo de requisição fica editável."),
                    ('Informar {"perfil": "Idoso", "nome": "Outra Pessoa", "cpf": "529.982.247-25", "contatoFamiliar": "Contato"} e clicar em Execute.', 'Resposta HTTP 409 com title "Já existe um cadastro com este CPF.".'),
                ],
            },
            {
                "titulo": "Atualizar e remover o cadastro",
                "tipo": "Positivo",
                "objetivo": "Verificar que o cidadão consegue atualizar os dados e remover o cadastro.",
                "preparacao": f"{API}. Um cidadão cadastrado, com o id anotado.",
                "passos": [
                    ('Em PUT /api/cidadaos/{id}, informar {"nome": "Nome Atualizado", "contatoFamiliar": "Contato"} e clicar em Execute.', "Resposta HTTP 204."),
                    ("Consultar GET /api/cidadaos/{id}.", 'Resposta HTTP 200 com nome "Nome Atualizado".'),
                    ("Executar DELETE /api/cidadaos/{id}.", "Resposta HTTP 204."),
                    ("Consultar GET /api/cidadaos/{id} novamente.", 'Resposta HTTP 404 com title "Cidadão não encontrado.".'),
                ],
            },
        ],
    },
    {
        "id": "F02",
        "titulo": "Risco de calor personalizado",
        "historia": "Como cidadão, quero ver o risco de calor de agora ajustado ao meu perfil, com uma orientação simples, para saber como me proteger.",
        "descricao": "O risco usa a maior sensação térmica medida pelos sensores nas últimas 3 horas. As faixas são: baixo (abaixo de 27 °C), atenção (27 °C), alto (32 °C) e extremo (41 °C). Para refletir a vulnerabilidade, somam-se 3 °C para idosos, 2 °C para trabalhadores de rua e 1 °C para quem informou condição de saúde.",
        "testes": [
            {
                "titulo": "Consultar risco geral sem leituras recentes",
                "tipo": "Negativo",
                "objetivo": "Verificar a resposta quando os sensores não enviaram dados nas últimas 3 horas.",
                "preparacao": f"{API}. {BANCO_NOVO}.",
                "passos": [
                    ("Executar GET /api/risco/atual sem parâmetros.", 'Resposta HTTP 200 com nivel null e orientacao "Sem leituras recentes dos sensores.".'),
                ],
            },
            {
                "titulo": "Consultar risco geral com calor de atenção",
                "tipo": "Positivo",
                "objetivo": "Verificar o cálculo do risco geral a partir de uma leitura recente.",
                "preparacao": f"{API}. {BANCO_NOVO}.",
                "passos": [
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 29, "umidadePct": 50}} e clicar em Execute.', 'Resposta HTTP 201 com indiceCalorC 29.7 e nivel "Atencao".'),
                    ("Executar GET /api/risco/atual sem parâmetros.", 'Resposta HTTP 200 com nivel "Atencao" e orientacao "Risco geral: atenção.".'),
                ],
            },
            {
                "titulo": "Consultar risco personalizado de idoso com hipertensão",
                "tipo": "Positivo",
                "objetivo": "Verificar que o mesmo calor tem risco maior para um idoso com condição de saúde.",
                "preparacao": f"{API}. Executados, nesta ordem, os casos \"Consultar risco geral com calor de atenção\" e \"Cadastrar idoso com dados válidos\", com o id do idoso anotado.",
                "passos": [
                    ("Executar GET /api/risco/atual com cidadaoId igual ao id do idoso.", 'Resposta HTTP 200 com nivel "Alto".'),
                    ("Conferir a orientação.", 'orientacao "Evite sair entre 11h e 16h. Beba água mesmo sem sede.".'),
                ],
            },
            {
                "titulo": "Consultar risco de cidadão inexistente",
                "tipo": "Negativo",
                "objetivo": "Verificar que um identificador desconhecido é recusado.",
                "preparacao": API + ".",
                "passos": [
                    ("Executar GET /api/risco/atual com cidadaoId 00000000-0000-0000-0000-000000000001.", 'Resposta HTTP 404 com title "Cidadão não encontrado.".'),
                ],
            },
        ],
    },
    {
        "id": "F03",
        "titulo": "Pontos de sombra e água próximos",
        "historia": "Como trabalhador de rua, quero ver os pontos de sombra e água mais próximos de onde estou, para parar e me hidratar sem perder tempo.",
        "descricao": "A busca considera apenas pontos ativos dentro de um raio, de 2 km por padrão, e mostra tipo e distância, do mais próximo ao mais distante.",
        "testes": [
            {
                "titulo": "Buscar pontos próximos ordenados pela distância",
                "tipo": "Positivo",
                "objetivo": "Verificar a ordenação e a distância dos pontos retornados.",
                "preparacao": f"{API}. {BANCO_NOVO}. Os 3 pontos simulados de demonstração estão ativos.",
                "passos": [
                    ("Executar GET /api/pontos/proximos com latitude -23.4620, longitude -46.6810 e raioKm 5.", "Resposta HTTP 200 com 3 pontos."),
                    ("Conferir o primeiro ponto e a ordem.", 'O primeiro é "Praça da Sombra (simulado)" com distanciaKm 0, e as distâncias seguintes são crescentes.'),
                ],
            },
            {
                "titulo": "Buscar pontos longe de qualquer ponto cadastrado",
                "tipo": "Negativo",
                "objetivo": "Verificar a resposta quando não há pontos dentro do raio.",
                "preparacao": f"{API}. {BANCO_NOVO}.",
                "passos": [
                    ("Executar GET /api/pontos/proximos com latitude -23.5505, longitude -46.6333 e raioKm 2.", "Resposta HTTP 200 com lista vazia []."),
                ],
            },
        ],
    },
    {
        "id": "F04",
        "titulo": "Check-in \"estou bem\"",
        "historia": "Como idoso, quero avisar com um toque que estou bem ou que preciso de ajuda, para minha família ficar tranquila sem precisar me ligar.",
        "descricao": "O check-in registra o status e o horário. O histórico fica disponível para a família, do mais recente ao mais antigo. Um check-in \"preciso de ajuda\" abre um pedido na Rede de Apoio (F11).",
        "testes": [
            {
                "titulo": "Registrar check-in e consultar o histórico",
                "tipo": "Positivo",
                "objetivo": "Verificar o registro do check-in e sua exibição no histórico.",
                "preparacao": f"{API}. Um cidadão cadastrado, com o id anotado.",
                "passos": [
                    ('Em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "EstouBem"} e clicar em Execute.', 'Resposta HTTP 201 com status "EstouBem" e dataHoraUtc preenchida.'),
                    ("Executar GET /api/cidadaos/{id}/checkins.", "O check-in registrado aparece em primeiro lugar."),
                ],
            },
            {
                "titulo": "Recusar check-in de cidadão inexistente",
                "tipo": "Negativo",
                "objetivo": "Verificar que não é possível registrar check-in para quem não está cadastrado.",
                "preparacao": API + ".",
                "passos": [
                    ('Em POST /api/checkins, informar {"cidadaoId": "00000000-0000-0000-0000-000000000001", "status": "EstouBem"} e clicar em Execute.', 'Resposta HTTP 404 com title "Cidadão não encontrado.".'),
                ],
            },
            {
                "titulo": "Recusar check-in com status inválido",
                "tipo": "Negativo",
                "objetivo": "Verificar que só os status previstos são aceitos.",
                "preparacao": f"{API}. Um cidadão cadastrado, com o id anotado.",
                "passos": [
                    ('Em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "Talvez"} e clicar em Execute.', "Resposta HTTP 400."),
                    ("Executar GET /api/cidadaos/{id}/checkins.", "Nenhum check-in novo aparece."),
                ],
            },
        ],
    },
    {
        "id": "F05",
        "titulo": "Recebimento das leituras dos sensores",
        "historia": "Como responsável pelos pontos de hidratação, quero que cada ponto envie temperatura e umidade, para o sistema saber a sensação térmica real em cada lugar.",
        "descricao": "A API recebe a leitura do ESP32, calcula o índice de calor pela fórmula de Rothfusz (NWS) e classifica o nível de risco. Leituras fora da faixa do sensor são recusadas.",
        "testes": [
            {
                "titulo": "Registrar leitura de calor extremo",
                "tipo": "Positivo",
                "objetivo": "Verificar o cálculo da sensação térmica e do nível de uma leitura válida.",
                "preparacao": API + ".",
                "passos": [
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 38, "umidadePct": 50}} e clicar em Execute.', 'Resposta HTTP 201 com indiceCalorC 48.6 e nivel "Extremo".'),
                ],
            },
            {
                "titulo": "Recusar umidade acima de 100%",
                "tipo": "Negativo",
                "objetivo": "Verificar que leituras impossíveis de umidade são recusadas.",
                "preparacao": API + ".",
                "passos": [
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 30, "umidadePct": 150}} e clicar em Execute.', 'Resposta HTTP 400 com title "Umidade deve estar entre 0 e 100.".'),
                ],
            },
            {
                "titulo": "Recusar temperatura fora da faixa do sensor",
                "tipo": "Negativo",
                "objetivo": "Verificar que leituras impossíveis de temperatura são recusadas.",
                "preparacao": API + ".",
                "passos": [
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 99, "umidadePct": 50}} e clicar em Execute.', 'Resposta HTTP 400 com title "Temperatura fora da faixa do sensor.".'),
                ],
            },
            {
                "titulo": "Recusar leitura de ponto inexistente",
                "tipo": "Negativo",
                "objetivo": "Verificar que só pontos cadastrados podem enviar leituras.",
                "preparacao": API + ".",
                "passos": [
                    ('Em POST /api/leituras, informar {"pontoId": "00000000-0000-0000-0000-000000000001", "temperaturaC": 30, "umidadePct": 50} e clicar em Execute.', 'Resposta HTTP 404 com title "Ponto não encontrado.".'),
                ],
            },
        ],
    },
    {
        "id": "F06",
        "titulo": "Alertas automáticos de calor",
        "historia": "Como cidadão, quero ser avisado quando um ponto do meu bairro estiver com calor perigoso, para evitar me expor naquele momento.",
        "descricao": "Uma leitura com sensação térmica de 32 °C ou mais abre um alerta para o ponto. Se o calor piorar, o mesmo alerta é atualizado, sem duplicar. Quando a sensação cai abaixo de 32 °C, o alerta é encerrado.",
        "testes": [
            {
                "titulo": "Abrir e atualizar alerta conforme o calor piora",
                "tipo": "Positivo",
                "objetivo": "Verificar a abertura do alerta e sua atualização sem duplicação.",
                "preparacao": f"{API}. {BANCO_NOVO}.",
                "passos": [
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 33, "umidadePct": 50}}.', 'Resposta HTTP 201 com nivel "Alto".'),
                    ("Executar GET /api/alertas/ativos.", 'Um alerta, com origem "Sensor", nivel "Alto" e mensagem iniciada por "Calor alto em Praça da Sombra (simulado)".'),
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 38, "umidadePct": 50}}.', 'Resposta HTTP 201 com nivel "Extremo".'),
                    ("Executar GET /api/alertas/ativos.", 'Continua um único alerta, agora com nivel "Extremo" e mensagem "Calor extremo em Praça da Sombra (simulado): sensação de 48,6 °C.".'),
                ],
            },
            {
                "titulo": "Encerrar alerta quando o calor diminui",
                "tipo": "Positivo",
                "objetivo": "Verificar o encerramento automático do alerta.",
                "preparacao": f"{API}. Caso \"Abrir e atualizar alerta conforme o calor piora\" executado.",
                "passos": [
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 22, "umidadePct": 50}}.', 'Resposta HTTP 201 com nivel "Baixo".'),
                    ("Executar GET /api/alertas/ativos.", "O alerta da Praça da Sombra não aparece mais."),
                ],
            },
            {
                "titulo": "Recusar encerramento de alerta já encerrado",
                "tipo": "Negativo",
                "objetivo": "Verificar que um alerta não pode ser encerrado duas vezes.",
                "preparacao": API + ".",
                "passos": [
                    ('Em POST /api/alertas/previsao, informar {"nivel": "Alto", "mensagem": "Teste"} e anotar o id retornado.', "Resposta HTTP 201."),
                    ("Executar POST /api/alertas/{id}/encerrar.", "Resposta HTTP 204."),
                    ("Executar POST /api/alertas/{id}/encerrar novamente.", 'Resposta HTTP 400 com title "Alerta já encerrado.".'),
                ],
            },
        ],
    },
    {
        "id": "F07",
        "titulo": "Previsão de calor da véspera",
        "historia": "Como idoso, quero ser avisado na noite anterior quando o dia seguinte for muito quente, para me preparar antes de o calor chegar.",
        "descricao": "Um modelo de Machine Learning treinado com dados reais do INMET (estação A701) prevê se a máxima do dia seguinte chegará a 32 °C ou mais. Quando a probabilidade é de 50% ou mais, o script ml/publicar_previsao.py publica um alerta de origem \"Previsao\" na API.",
        "testes": [
            {
                "titulo": "Publicar alerta de previsão manualmente",
                "tipo": "Positivo",
                "objetivo": "Verificar que a API aceita alertas vindos da previsão.",
                "preparacao": API + ".",
                "passos": [
                    ('Em POST /api/alertas/previsao, informar {"nivel": "Alto", "mensagem": "Amanhã deve passar de 32 °C."}.', 'Resposta HTTP 201 com origem "Previsao" e ativo true.'),
                    ("Executar GET /api/alertas/ativos.", "O alerta aparece na lista."),
                ],
            },
            {
                "titulo": "Recusar alerta de previsão sem mensagem",
                "tipo": "Negativo",
                "objetivo": "Verificar que o alerta precisa ter uma mensagem para o cidadão.",
                "preparacao": API + ".",
                "passos": [
                    ('Em POST /api/alertas/previsao, informar {"nivel": "Alto", "mensagem": ""}.', "Resposta HTTP 400."),
                ],
            },
            {
                "titulo": "Script publica previsão para véspera de dia quente",
                "tipo": "Positivo",
                "objetivo": "Verificar a integração entre o modelo e a API em um dia real seguido de calor.",
                "preparacao": f"{API}. Python com as dependências de ml/requirements.txt. Em 15/03/2024, a máxima foi 34,2 °C, e em 16/03/2024, 34,1 °C.",
                "passos": [
                    ("Na pasta ml, executar python publicar_previsao.py --data 2024-03-15.", "O script mostra probabilidade de 50% ou mais e informa que o alerta foi publicado."),
                    ("Executar GET /api/alertas/ativos.", 'Aparece um alerta com origem "Previsao" citando 16/03.'),
                ],
            },
            {
                "titulo": "Script não publica previsão para dia frio",
                "tipo": "Negativo",
                "objetivo": "Verificar que o script não gera alerta quando não há previsão de calor.",
                "preparacao": f"{API}. Em 01/07/2025, a máxima foi 15,8 °C, e em 02/07/2025, 13,0 °C.",
                "passos": [
                    ("Executar GET /api/alertas/ativos e anotar a quantidade de alertas.", "Lista retornada."),
                    ("Na pasta ml, executar python publicar_previsao.py --data 2025-07-01.", 'O script mostra probabilidade abaixo de 50% e "sem alerta".'),
                    ("Executar GET /api/alertas/ativos.", "A quantidade de alertas é a mesma do passo 1."),
                ],
            },
        ],
    },
    {
        "id": "F08",
        "titulo": "Indicador de impacto",
        "historia": "Como equipe gestora do Sombra Amiga, quero acompanhar quantos cidadãos confirmam que estão bem nos dias de alerta, para medir se a solução protege as pessoas.",
        "descricao": "Indicador da Ficha: percentual de check-ins \"estou bem\" confirmados em dias com alerta, em relação ao esperado (cidadãos cadastrados × dias com alerta). Cada cidadão conta uma vez por dia.",
        "testes": [
            {
                "titulo": "Calcular indicador em dia com alerta",
                "tipo": "Positivo",
                "objetivo": "Verificar o cálculo do indicador com um cidadão que confirmou estar bem.",
                "preparacao": f"{API}. {BANCO_NOVO}.",
                "passos": [
                    ("Cadastrar um idoso válido em POST /api/cidadaos e anotar o id.", "Resposta HTTP 201."),
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 38, "umidadePct": 50}}.', "Resposta HTTP 201 e alerta aberto."),
                    ('Em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "EstouBem"}.', "Resposta HTTP 201."),
                    ("Executar GET /api/indicadores/impacto com inicio e fim iguais à data de hoje (AAAA-MM-DD).", "diasComAlerta 1, checkInsEsperados 1, checkInsConfirmados 1 e percentualConfirmado 100."),
                ],
            },
            {
                "titulo": "Recusar período invertido",
                "tipo": "Negativo",
                "objetivo": "Verificar a validação do período consultado.",
                "preparacao": API + ".",
                "passos": [
                    ("Executar GET /api/indicadores/impacto com inicio 2026-11-30 e fim 2026-11-01.", 'Resposta HTTP 400 com title "A data final deve ser maior ou igual à inicial.".'),
                ],
            },
        ],
    },
    {
        "id": "F09",
        "titulo": "Gestão dos pontos de hidratação",
        "historia": "Como responsável pelos pontos, quero cadastrar, atualizar e desativar pontos de sombra e água, para manter o mapa do bairro correto.",
        "descricao": "Cada ponto tem nome, tipo (sombra, água ou os dois) e coordenadas. A desativação preserva o histórico de leituras.",
        "testes": [
            {
                "titulo": "Cadastrar ponto válido",
                "tipo": "Positivo",
                "objetivo": "Verificar o cadastro de um novo ponto.",
                "preparacao": API + ".",
                "passos": [
                    ('Em POST /api/pontos, informar {"nome": "Bebedouro Teste", "tipo": "Agua", "latitude": -23.47, "longitude": -46.68}.', "Resposta HTTP 201 com o id do ponto."),
                    ("Executar GET /api/pontos.", '"Bebedouro Teste" aparece na lista.'),
                ],
            },
            {
                "titulo": "Recusar ponto com latitude inválida",
                "tipo": "Negativo",
                "objetivo": "Verificar a validação das coordenadas.",
                "preparacao": API + ".",
                "passos": [
                    ('Em POST /api/pontos, informar {"nome": "Ponto Errado", "tipo": "Agua", "latitude": 95, "longitude": -46.68}.', "Resposta HTTP 400."),
                    ("Executar GET /api/pontos.", '"Ponto Errado" não aparece na lista.'),
                ],
            },
            {
                "titulo": "Desativar ponto",
                "tipo": "Positivo",
                "objetivo": "Verificar que um ponto desativado sai das listas.",
                "preparacao": f"{API}. {BANCO_NOVO}.",
                "passos": [
                    ("Executar DELETE /api/pontos/33333333-3333-3333-3333-333333333333.", "Resposta HTTP 204."),
                    ("Executar GET /api/pontos.", '"Abrigo do Terminal (simulado)" não aparece mais.'),
                ],
            },
        ],
    },
    {
        "id": "F10",
        "titulo": "Rede de Apoio: acesso dos agentes",
        "historia": "Como agente comunitário de saúde ou voluntário, quero entrar na Rede de Apoio com meu login, para atender pedidos de ajuda sem expor dados de pessoas vulneráveis a quem não deve vê-los.",
        "descricao": "Serviço Java (Spring Boot). O agente se cadastra com nome, e-mail, bairro e senha. O login devolve um token JWT, exigido nas rotas de atendimento.",
        "testes": [
            {
                "titulo": "Fazer login com credenciais válidas",
                "tipo": "Positivo",
                "objetivo": "Verificar a emissão do token para um agente cadastrado.",
                "preparacao": "Serviço Rede de Apoio em execução, com Swagger aberto. Agente de teste cadastrado com e-mail agente@teste.com.",
                "passos": [
                    ("Em POST /api/auth/login, informar o e-mail e a senha do agente de teste.", "Resposta HTTP 200 com um token."),
                    ("Autorizar o Swagger com o token e executar GET /api/pedidos.", "Resposta HTTP 200."),
                ],
            },
            {
                "titulo": "Negar login com senha errada",
                "tipo": "Negativo",
                "objetivo": "Verificar que uma senha errada não dá acesso.",
                "preparacao": "Serviço Rede de Apoio em execução. Agente de teste cadastrado.",
                "passos": [
                    ("Em POST /api/auth/login, informar o e-mail do agente de teste e uma senha errada.", "Resposta HTTP 401, sem token e sem indicar se o erro foi no e-mail ou na senha."),
                ],
            },
            {
                "titulo": "Negar acesso aos pedidos sem token",
                "tipo": "Negativo",
                "objetivo": "Verificar que os dados dos pedidos exigem autenticação.",
                "preparacao": "Serviço Rede de Apoio em execução.",
                "passos": [
                    ("Executar GET /api/pedidos sem autorização.", "Resposta HTTP 401."),
                ],
            },
        ],
    },
    {
        "id": "F11",
        "titulo": "Rede de Apoio: atendimento de pedidos de ajuda",
        "historia": "Como idoso, quero que alguém da minha região venha me ajudar quando eu disser que não estou bem, para não ficar sozinho em um dia de calor perigoso.",
        "descricao": "Um check-in \"preciso de ajuda\" abre um pedido na Rede de Apoio. Um agente aceita o pedido e, depois de atender, o conclui. O pedido passa por aberto, em atendimento e concluído.",
        "testes": [
            {
                "titulo": "Pedido de ajuda chega à Rede de Apoio",
                "tipo": "Positivo",
                "objetivo": "Verificar a integração entre o check-in da API principal e a Rede de Apoio.",
                "preparacao": "API principal e Rede de Apoio em execução. Um cidadão cadastrado na API principal e um agente logado.",
                "passos": [
                    ('Na API principal, em POST /api/checkins, informar {"cidadaoId": "<id>", "status": "PrecisoDeAjuda"}.', "Resposta HTTP 201."),
                    ("Na Rede de Apoio, executar GET /api/pedidos com o token do agente.", 'Aparece um pedido com status "ABERTO" para o cidadão.'),
                ],
            },
            {
                "titulo": "Aceitar e concluir um pedido",
                "tipo": "Positivo",
                "objetivo": "Verificar o fluxo completo de atendimento.",
                "preparacao": "Rede de Apoio em execução. Um pedido aberto e um agente logado.",
                "passos": [
                    ("Executar POST /api/pedidos/{id}/aceitar com o token do agente.", 'Resposta HTTP 200 com status "EM_ATENDIMENTO".'),
                    ("Executar POST /api/pedidos/{id}/concluir com o mesmo token.", 'Resposta HTTP 200 com status "CONCLUIDO".'),
                ],
            },
            {
                "titulo": "Recusar pedido já aceito por outro agente",
                "tipo": "Negativo",
                "objetivo": "Verificar que dois agentes não atendem o mesmo pedido.",
                "preparacao": "Rede de Apoio em execução. Um pedido já aceito pelo agente A. O agente B está logado.",
                "passos": [
                    ("Executar POST /api/pedidos/{id}/aceitar com o token do agente B.", "Resposta HTTP 409."),
                ],
            },
        ],
    },
    {
        "id": "F12",
        "titulo": "App do cidadão",
        "historia": "Como idoso ou trabalhador de rua, quero um app simples no celular, para ver o risco de calor, achar pontos de água e avisar que estou bem.",
        "descricao": "App em React Native (Expo) com telas de cadastro, início (risco e orientação), pontos próximos e alertas. O cadastro e os últimos dados ficam salvos no celular, e o app usa letras grandes, bom contraste e linguagem simples.",
        "testes": [
            {
                "titulo": "Concluir cadastro no primeiro acesso",
                "tipo": "Positivo",
                "objetivo": "Verificar a jornada de cadastro pelo app.",
                "preparacao": "API em execução. App instalado sem dados salvos.",
                "passos": [
                    ("Abrir o app.", "A tela de cadastro é exibida."),
                    ("Escolher o perfil Idoso, preencher nome, CPF 529.982.247-25 e contato do familiar, e tocar em Cadastrar.", "A tela inicial é exibida com o nome do cidadão."),
                    ("Fechar e abrir o app de novo.", "O app abre direto na tela inicial."),
                ],
            },
            {
                "titulo": "Fazer check-in pela tela inicial",
                "tipo": "Positivo",
                "objetivo": "Verificar o check-in de um toque.",
                "preparacao": "API em execução. App com cadastro concluído.",
                "passos": [
                    ("Na tela inicial, tocar em \"Estou bem\".", "O app mostra a confirmação com o horário do check-in."),
                ],
            },
            {
                "titulo": "Recusar cadastro com CPF inválido no app",
                "tipo": "Negativo",
                "objetivo": "Verificar que o app mostra o erro de forma compreensível.",
                "preparacao": "API em execução. App sem dados salvos.",
                "passos": [
                    ("Preencher o cadastro com o CPF 123.456.789-00 e tocar em Cadastrar.", "O app mostra \"CPF inválido.\" e continua na tela de cadastro."),
                ],
            },
            {
                "titulo": "Mostrar últimos dados sem internet",
                "tipo": "Negativo",
                "objetivo": "Verificar o funcionamento sem conexão.",
                "preparacao": "App com cadastro concluído e aberto ao menos uma vez com internet.",
                "passos": [
                    ("Ativar o modo avião e abrir o app.", "A tela inicial mostra os últimos dados salvos e o horário da última atualização, sem travar."),
                ],
            },
        ],
    },
    {
        "id": "F13",
        "titulo": "Estação de monitoramento no ponto (ESP32)",
        "historia": "Como pessoa que passa pelo ponto de hidratação, quero ver ali mesmo o nível de calor, para decidir se paro para me hidratar mesmo sem celular.",
        "descricao": "Circuito ESP32 simulado no Wokwi, com sensor DHT22, display LCD e LEDs. Mede temperatura e umidade, calcula a sensação térmica, mostra o nível no display e nos LEDs (verde para baixo, amarelo para atenção, vermelho para alto e extremo, com aviso sonoro no extremo) e envia a leitura para a API.",
        "testes": [
            {
                "titulo": "Exibir nível extremo no ponto",
                "tipo": "Positivo",
                "objetivo": "Verificar o aviso local e o envio da leitura para a API.",
                "preparacao": "Projeto aberto no Wokwi e simulação iniciada. API acessível pelo simulador.",
                "passos": [
                    ("No DHT22, ajustar a temperatura para 38 °C e a umidade para 50%.", "O display mostra a sensação de cerca de 48,6 °C e o nível EXTREMO."),
                    ("Observar os LEDs e o buzzer.", "O LED vermelho acende e o buzzer toca."),
                    ("Na API, executar GET /api/leituras com o pontoId do circuito.", "A leitura de 38 °C aparece em primeiro lugar."),
                ],
            },
            {
                "titulo": "Exibir nível baixo no ponto",
                "tipo": "Positivo",
                "objetivo": "Verificar o estado normal do circuito.",
                "preparacao": "Projeto aberto no Wokwi e simulação iniciada.",
                "passos": [
                    ("No DHT22, ajustar a temperatura para 22 °C e a umidade para 50%.", "O display mostra o nível BAIXO, o LED verde acende e o buzzer fica em silêncio."),
                ],
            },
            {
                "titulo": "Manter aviso local sem rede",
                "tipo": "Negativo",
                "objetivo": "Verificar que o ponto continua útil sem conexão.",
                "preparacao": "Projeto aberto no Wokwi com o endereço da API apontando para um servidor desligado.",
                "passos": [
                    ("Iniciar a simulação e ajustar o DHT22 para 38 °C e 50%.", "O display mostra EXTREMO e \"SEM REDE\", e o LED vermelho e o buzzer continuam funcionando."),
                ],
            },
        ],
    },
    {
        "id": "F14",
        "titulo": "Painel web de acompanhamento",
        "historia": "Como equipe da UBS ou da ONG parceira, quero um painel com os alertas ativos e o indicador de impacto, para saber onde agir primeiro.",
        "descricao": "Página web hospedada na VM Linux. Mostra os alertas ativos, os pontos com a última leitura e o indicador de impacto, com atualização periódica.",
        "testes": [
            {
                "titulo": "Exibir alerta novo no painel",
                "tipo": "Positivo",
                "objetivo": "Verificar a atualização automática do painel.",
                "preparacao": "API e painel em execução. Painel aberto no navegador.",
                "passos": [
                    (f'Em POST /api/leituras, informar {{"pontoId": "{PRACA}", "temperaturaC": 38, "umidadePct": 50}}.', "Resposta HTTP 201."),
                    ("Aguardar a próxima atualização do painel, sem recarregar a página.", "O alerta extremo da Praça da Sombra aparece com o horário."),
                ],
            },
            {
                "titulo": "Avisar indisponibilidade da API",
                "tipo": "Negativo",
                "objetivo": "Verificar o comportamento do painel quando a API cai.",
                "preparacao": "Painel em execução e API parada.",
                "passos": [
                    ("Abrir o painel no navegador.", "O painel mostra um aviso de que os dados estão indisponíveis."),
                ],
            },
        ],
    },
    {
        "id": "F15",
        "titulo": "Proteção de dados pessoais",
        "historia": "Como cidadão, quero que meu CPF, meu contato e minha condição de saúde não fiquem expostos, para confiar no serviço.",
        "descricao": "As respostas da API mostram o CPF mascarado e nunca exibem contato do familiar ou condição de saúde. Mensagens de erro não repetem dados enviados. Todos os dados de pessoas usados no projeto são fictícios.",
        "testes": [
            {
                "titulo": "Mascarar dados sensíveis na listagem",
                "tipo": "Positivo",
                "objetivo": "Verificar que a listagem não expõe dados sensíveis.",
                "preparacao": f"{API}. Caso \"Cadastrar idoso com dados válidos\" executado.",
                "passos": [
                    ("Executar GET /api/cidadaos.", 'O cidadão aparece com cpfMascarado "***.***.***-25".'),
                    ("Procurar no corpo da resposta os textos 52998224725, Hipertensão e Filha Teste.", "Nenhum dos três aparece."),
                ],
            },
        ],
    },
]

# Critérios de aceite no padrão BDD/Gherkin ensinado em aula:
# (nome do cenário, Dado, Quando, Então, [E...])
CENARIOS = {
    "F01": [
        ("Cadastro com dados válidos", "que informo perfil, nome, CPF válido e contato de um familiar", "envio o cadastro", "o cadastro é criado", ["recebo um identificador", "o CPF aparece mascarado na resposta"]),
        ("Trabalhador de rua sem ocupação", "que escolhi o perfil trabalhador de rua", "envio o cadastro sem a ocupação", "o cadastro é recusado com a mensagem \"Ocupação é obrigatória.\"", []),
        ("CPF inválido", "um CPF com dígitos verificadores errados", "envio o cadastro", "o cadastro é recusado com a mensagem \"CPF inválido.\"", ["o número enviado não aparece na mensagem de erro"]),
        ("CPF já cadastrado", "que já existe um cadastro com o meu CPF", "envio um novo cadastro com o mesmo CPF", "o cadastro é recusado com a mensagem \"Já existe um cadastro com este CPF.\"", []),
        ("Atualização e remoção", "que estou cadastrado", "atualizo meus dados ou removo o cadastro", "a alteração é aplicada", ["após a remoção, a consulta ao cadastro retorna \"Cidadão não encontrado.\""]),
    ],
    "F02": [
        ("Risco geral com leituras recentes", "que os sensores enviaram leituras nas últimas 3 horas", "consulto o risco sem informar o cidadão", "vejo a maior sensação térmica do período e o nível correspondente", ["o nível segue as faixas baixo, atenção (27 °C), alto (32 °C) e extremo (41 °C)"]),
        ("Risco personalizado para idoso com condição de saúde", "que sou idoso e informei uma condição de saúde", "consulto o meu risco", "o nível considera 3 °C a mais pelo perfil e 1 °C a mais pela condição de saúde", ["a orientação exibida é a própria para idosos"]),
        ("Sem leituras recentes", "que nenhum sensor enviou leitura nas últimas 3 horas", "consulto o risco", "vejo a mensagem \"Sem leituras recentes dos sensores.\"", ["nenhum nível é informado"]),
        ("Cidadão inexistente", "um identificador de cidadão que não existe", "consulto o risco desse cidadão", "recebo a mensagem \"Cidadão não encontrado.\"", []),
    ],
    "F03": [
        ("Pontos dentro do raio", "que informo minha localização e um raio de busca", "busco pontos próximos", "vejo os pontos ativos dentro do raio", ["eles aparecem do mais próximo ao mais distante, com tipo e distância"]),
        ("Nenhum ponto no raio", "que não há pontos ativos dentro do raio", "busco pontos próximos", "recebo uma lista vazia, sem erro", []),
        ("Ponto desativado", "que um ponto foi desativado", "busco pontos próximos", "esse ponto não aparece no resultado", []),
    ],
    "F04": [
        ("Check-in \"estou bem\"", "que estou cadastrado", "faço o check-in \"estou bem\"", "ele é registrado com data e hora", []),
        ("Histórico para a família", "que fiz check-ins", "a família consulta meu histórico", "os check-ins aparecem do mais recente ao mais antigo", []),
        ("Cidadão inexistente", "um identificador de cidadão que não existe", "o check-in é enviado", "ele é recusado com a mensagem \"Cidadão não encontrado.\"", []),
        ("Status inválido", "um status diferente de \"EstouBem\" ou \"PrecisoDeAjuda\"", "o check-in é enviado", "ele é recusado", ["nada é gravado no histórico"]),
    ],
    "F05": [
        ("Leitura válida", "uma leitura com temperatura entre -10 °C e 60 °C e umidade entre 0% e 100%", "o ponto envia a leitura", "ela é registrada com a sensação térmica e o nível de risco", []),
        ("Temperatura fora da faixa", "uma temperatura fora da faixa do sensor", "a leitura é enviada", "ela é recusada com a mensagem \"Temperatura fora da faixa do sensor.\"", []),
        ("Umidade fora da faixa", "uma umidade abaixo de 0% ou acima de 100%", "a leitura é enviada", "ela é recusada com a mensagem \"Umidade deve estar entre 0 e 100.\"", []),
        ("Ponto inexistente", "um ponto que não está cadastrado", "a leitura é enviada", "ela é recusada com a mensagem \"Ponto não encontrado.\"", []),
    ],
    "F06": [
        ("Abertura do alerta", "que o ponto não tem alerta ativo", "uma leitura com sensação térmica de 32 °C ou mais é registrada", "um alerta ativo é aberto para o ponto", ["a mensagem informa o nível, o ponto e a sensação térmica"]),
        ("Agravamento do calor", "que o ponto já tem um alerta ativo", "uma leitura de nível mais alto é registrada", "o mesmo alerta passa a mostrar o novo nível", ["nenhum alerta duplicado é criado"]),
        ("Encerramento automático", "que o ponto tem um alerta ativo", "uma leitura abaixo de 32 °C é registrada", "o alerta é encerrado", []),
        ("Alerta já encerrado", "um alerta já encerrado", "tento encerrá-lo de novo", "recebo a mensagem \"Alerta já encerrado.\"", []),
    ],
    "F07": [
        ("Previsão de calor", "que o modelo prevê máxima de 32 °C ou mais para amanhã, com probabilidade de 50% ou mais", "o script de previsão roda", "um alerta de origem \"Previsao\" é publicado na API", []),
        ("Sem previsão de calor", "que a probabilidade de calor para amanhã é menor que 50%", "o script de previsão roda", "nenhum alerta é publicado", ["o script informa \"sem alerta\" e a probabilidade"]),
        ("Modo de simulação", "que o script é executado com --simular", "a previsão é calculada", "a probabilidade é exibida", ["nada é publicado na API"]),
        ("Alerta sem mensagem", "um alerta de previsão com a mensagem vazia", "ele é enviado à API", "ele é recusado", []),
    ],
    "F08": [
        ("Período com alertas", "um período com alertas e check-ins \"estou bem\"", "consulto o indicador", "vejo os dias com alerta, os check-ins esperados, os confirmados e o percentual", ["cada cidadão conta uma vez por dia"]),
        ("Período sem alertas", "um período sem nenhum alerta", "consulto o indicador", "o percentual é 0", []),
        ("Período invertido", "uma data final anterior à inicial", "consulto o indicador", "recebo a mensagem \"A data final deve ser maior ou igual à inicial.\"", []),
    ],
    "F09": [
        ("Cadastro de ponto", "nome, tipo e coordenadas válidas", "cadastro um ponto", "ele passa a aparecer na lista de pontos", []),
        ("Coordenadas inválidas", "uma latitude fora de -90 a 90 ou uma longitude fora de -180 a 180", "cadastro o ponto", "o cadastro é recusado", []),
        ("Desativação", "um ponto ativo", "eu o desativo", "ele deixa de aparecer nas listas e buscas", ["o histórico de leituras do ponto é mantido"]),
    ],
    "F10": [
        ("Login válido", "um agente cadastrado", "ele faz login com e-mail e senha corretos", "recebe um token de acesso", []),
        ("Senha errada", "um agente cadastrado", "ele faz login com a senha errada", "o acesso é negado", ["a mensagem não informa se o erro foi no e-mail ou na senha"]),
        ("Acesso sem token", "uma requisição sem token", "ela tenta consultar os pedidos de ajuda", "o acesso é negado", []),
    ],
    "F11": [
        ("Pedido de ajuda", "que um cidadão fez o check-in \"preciso de ajuda\"", "um agente consulta os pedidos", "o pedido aparece com status aberto", []),
        ("Aceite do pedido", "um pedido aberto", "um agente o aceita", "o pedido fica em atendimento com esse agente", []),
        ("Pedido já aceito", "um pedido já aceito por outro agente", "tento aceitá-lo", "a ação é recusada", []),
        ("Conclusão", "um pedido em atendimento", "o agente responsável o conclui", "o pedido fica concluído", []),
    ],
    "F12": [
        ("Primeiro acesso", "que abro o app pela primeira vez", "concluo o cadastro", "o app passa a abrir direto na tela inicial", []),
        ("Risco na tela inicial", "que há leituras recentes", "abro o app", "vejo o nível de risco e a orientação do meu perfil", []),
        ("Check-in pelo app", "que estou na tela inicial", "toco em \"Estou bem\"", "vejo a confirmação com o horário do check-in", []),
        ("Sem internet", "que estou sem internet", "abro o app", "vejo os últimos dados salvos e o horário da última atualização", ["o app não trava"]),
    ],
    "F13": [
        ("Leitura no ponto", "que o sensor fez uma leitura", "ela é processada", "o display mostra a sensação térmica e o nível", ["o LED da cor do nível acende"]),
        ("Nível extremo", "uma leitura de nível extremo", "ela é processada", "o aviso sonoro é acionado", []),
        ("Falha do sensor", "que o sensor falhou na leitura", "o circuito tenta processá-la", "o display mostra \"ERRO SENSOR\"", ["nada é enviado à API"]),
        ("Sem rede", "que a rede está indisponível", "há uma nova leitura", "o aviso local continua funcionando", ["o display indica \"SEM REDE\""]),
    ],
    "F14": [
        ("Alertas ativos", "que há alertas ativos", "abro o painel", "vejo cada alerta com nível, ponto e horário", []),
        ("Atualização automática", "que o painel está aberto", "um novo alerta é aberto", "ele aparece na próxima atualização, sem recarregar a página", []),
        ("API fora do ar", "que a API está fora do ar", "abro o painel", "vejo um aviso de indisponibilidade", ["a tela não fica em branco"]),
    ],
    "F15": [
        ("CPF mascarado", "um cidadão cadastrado", "consulto a lista ou o detalhe", "o CPF aparece mascarado", []),
        ("Condição de saúde", "um cidadão com condição de saúde", "consulto seus dados", "só aparece se ele tem condição de saúde", ["o texto da condição não é exibido"]),
        ("Contato do familiar", "qualquer cidadão cadastrado", "consulto qualquer rota da API", "o contato do familiar não aparece em nenhuma resposta", []),
    ],
}

for _f in FEATURES:
    _f["criterios"] = CENARIOS[_f["id"]]


# ---------- formato comum aos CSVs, ao documento e ao script do Azure ----------

def codigo_feature(f):
    """F01 vira F-01, no padrão do projeto anterior."""
    return f"F-{f['id'][1:]}"


def titulo_feature(f):
    return f"{codigo_feature(f)} — {f['titulo']}"


def codigo_teste(f, n):
    return f"TC-{f['id'][1:]}.{n:02d}"


def titulo_teste(f, n, t):
    return f"{codigo_teste(f, n)} — [{t['tipo']}] {t['titulo']}"


def tags_feature(f):
    return codigo_feature(f)


def tags_teste(f, t):
    return f"{codigo_feature(f)}; {t['tipo']}"


def cenario_linhas(cenario):
    """Linhas Gherkin de um cenário, sem formatação."""
    nome, dado, quando, entao, extras = cenario
    return [f"Cenário: {nome}", f"Dado {dado}", f"Quando {quando}", f"Então {entao}"] + [f"E {e}" for e in extras]
