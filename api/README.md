# API principal (C# / .NET)

Backend da CitizenTech Sombra Amiga. A Ficha completa está no [README da raiz](../README.md).

**Integrantes:** Glauco Heitor Gonçalves (RM 555978) e Pedro Henrique Junqueira (RM 556278).

## Como rodar

Requisito: [.NET 10 SDK](https://dotnet.microsoft.com/download). O banco SQLite é criado e migrado ao iniciar.

```bash
cd api
dotnet run --project src/SombraAmiga.Api --urls http://localhost:5080
```

Documentação dos endpoints (Swagger): http://localhost:5080/swagger

## Como testar

```bash
cd api
dotnet test
```

## Estrutura

| Projeto | Responsabilidade |
|---|---|
| `SombraAmiga.Dominio` | Entidades, regras de risco, interfaces e serviços. Não depende de banco nem de web. |
| `SombraAmiga.Infra` | EF Core, SQLite, migrações, repositórios e injeção de dependência. |
| `SombraAmiga.Api` | Controllers, contratos JSON, tratamento de erros e Swagger. |
| `SombraAmiga.Testes` | Testes unitários e de ponta a ponta com xUnit. |

## Conceitos aplicados

| Critério | Onde ver |
|---|---|
| POO | `Cidadao` é abstrata. `Idoso` e `TrabalhadorDeRua` definem sensibilidade e orientação próprias. `Cpf` é um objeto de valor. |
| Interfaces e injeção de dependência | `IRepositorios.cs` e `InjecaoDeDependencia.cs` |
| Web API | Pasta `Controllers`, com códigos 201, 204, 400, 404 e 409 |
| EF Core e LINQ | `SombraAmigaContexto.cs`, `Repositorios.cs` e migrações em `Dados/Migracoes` |
| Programação assíncrona | Repositórios, serviços e controllers usam `async/await` com `CancellationToken` |
| Testes | `tests/SombraAmiga.Testes` |

## Principais endpoints

| Método | Rota | Função |
|---|---|---|
| POST | `/api/leituras` | Recebe a leitura do ESP32 e abre, atualiza ou encerra o alerta |
| GET | `/api/risco/atual?cidadaoId=` | Risco atual, personalizado por perfil |
| GET | `/api/pontos/proximos` | Pontos de sombra e água mais próximos |
| POST | `/api/checkins` | Check-in "estou bem" |
| GET | `/api/alertas/ativos` | Alertas ativos |
| POST | `/api/alertas/previsao` | Publica o alerta vindo do modelo de ML |
| GET | `/api/indicadores/impacto` | Indicador de impacto da Ficha |

## Regras de risco

As faixas de índice de calor usam como base as do NWS: atenção a partir de 27 °C, alto a partir de 32 °C e extremo a partir de 41 °C.

Os ajustes por perfil são **critério da equipe, sem validação clínica**: +3 °C para idoso, +2 °C para trabalhador de rua e +1 °C para quem informa condição de saúde.

## Integração com a Rede de Apoio

Um check-in **"preciso de ajuda"** abre um pedido no serviço Java [Rede de Apoio](../servico-soa/README.md) (`POST /api/pedidos`, autenticado pelo cabeçalho `X-Chave-Servico`). O check-in é salvo antes e nunca é desfeito: se a Rede de Apoio estiver fora do ar, a falha só fica registrada no log.

A configuração fica em `appsettings.json`, na seção `RedeDeApoio` (`Url` e `Chave`). Com `Url` vazia, a integração fica desligada.

## Privacidade

As respostas nunca trazem CPF completo, contato do familiar ou condição de saúde. Os dados de pessoas usados em testes são fictícios, e os pontos cadastrados são simulados.

**Limitações do protótipo:** ainda não há autenticação, e os dados pessoais ficam sem criptografia no SQLite.
