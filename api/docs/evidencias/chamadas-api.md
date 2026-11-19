# Evidência: chamadas reais à API

Executado em 19/11/2026 12:26, com a API rodando localmente (`dotnet run`) num banco SQLite novo. Todos os dados de pessoas são fictícios.

## 1. Pontos de sombra e água mais próximos da Brasilândia

`GET /api/pontos/proximos?latitude=-23.4620&longitude=-46.6810&raioKm=3` → **HTTP 200**

Resposta:
```json
[
  {
    "id": "11111111-1111-1111-1111-111111111111",
    "nome": "Praça da Sombra (simulado)",
    "tipo": "SombraEAgua",
    "latitude": -23.462,
    "longitude": -46.681,
    "distanciaKm": 0
  },
  {
    "id": "22222222-2222-2222-2222-222222222222",
    "nome": "Bebedouro da UBS (simulado)",
    "tipo": "Agua",
    "latitude": -23.4685,
    "longitude": -46.6755,
    "distanciaKm": 0.91
  },
  {
    "id": "33333333-3333-3333-3333-333333333333",
    "nome": "Abrigo do Terminal (simulado)",
    "tipo": "Sombra",
    "latitude": -23.455,
    "longitude": -46.689,
    "distanciaKm": 1.13
  }
]
```

## 2. Cadastro de uma idosa fictícia

`POST /api/cidadaos` → **HTTP 201**

Corpo enviado:
```json
{
  "perfil": "Idoso",
  "nome": "Lurdes (fictícia)",
  "cpf": "52998224725",
  "contatoFamiliar": "(11) 90000-0000",
  "condicaoSaude": "Hipertensão"
}
```

Resposta:
```json
{
  "id": "2d78f7cd-4ded-490a-a1a6-d05227473245",
  "nome": "Lurdes (fictícia)",
  "cpfMascarado": "***.***.***-25",
  "perfil": "Idoso",
  "temCondicaoSaude": true
}
```

## 3. Cadastro com CPF inválido (caso negativo)

`POST /api/cidadaos` → **HTTP 400**

Corpo enviado:
```json
{
  "perfil": "Idoso",
  "nome": "Teste",
  "cpf": "12345678900",
  "contatoFamiliar": "(11) 90000-0000"
}
```

Resposta:
```json
{
  "title": "CPF inválido.",
  "status": 400
}
```

## 4. Leitura de calor enviada pela estação ESP32

`POST /api/leituras` → **HTTP 201**

Corpo enviado:
```json
{
  "pontoId": "11111111-1111-1111-1111-111111111111",
  "temperaturaC": 36.5,
  "umidadePct": 55
}
```

Resposta:
```json
{
  "id": "0ad9c482-f4fd-4871-b5b3-00fb1583b781",
  "pontoId": "11111111-1111-1111-1111-111111111111",
  "temperaturaC": 36.5,
  "umidadePct": 55,
  "indiceCalorC": 47,
  "nivel": "Extremo",
  "dataHoraUtc": "2026-11-19T15:26:27.3211572Z"
}
```

## 5. Alertas ativos depois da leitura

`GET /api/alertas/ativos` → **HTTP 200**

Resposta:
```json
[
  {
    "id": "62bd7e1e-d39a-419f-9c85-54928925292b",
    "nivel": "Extremo",
    "origem": "Sensor",
    "mensagem": "Calor extremo em Praça da Sombra (simulado): sensação de 47,0 °C.",
    "pontoId": "11111111-1111-1111-1111-111111111111",
    "criadoEmUtc": "2026-11-19T15:26:27.3211572Z",
    "ativo": true
  }
]
```

## 6. Risco atual personalizado para o perfil idoso

`GET /api/risco/atual?cidadaoId=2d78f7cd-4ded-490a-a1a6-d05227473245` → **HTTP 200**

Resposta:
```json
{
  "indiceCalorC": 47,
  "nivel": "Extremo",
  "orientacao": "Calor perigoso. Fique em local fresco, beba água e avise sua família."
}
```

## 7. Check-in "estou bem"

`POST /api/checkins` → **HTTP 201**

Corpo enviado:
```json
{
  "cidadaoId": "2d78f7cd-4ded-490a-a1a6-d05227473245",
  "status": "EstouBem"
}
```

Resposta:
```json
{
  "id": "a2e6f45c-e9db-4705-8c6a-e8a5a2fe04bf",
  "cidadaoId": "2d78f7cd-4ded-490a-a1a6-d05227473245",
  "status": "EstouBem",
  "dataHoraUtc": "2026-11-19T15:26:27.4696605Z"
}
```

## 8. Indicador de impacto

`GET /api/indicadores/impacto` → **HTTP 200**

Resposta:
```json
{
  "diasComAlerta": 0,
  "checkInsEsperados": 0,
  "checkInsConfirmados": 0,
  "percentualConfirmado": 0
}
```

## 9. Health check

`GET /api/saude` → **HTTP 200**

Resposta:
```json
"Healthy"
```
