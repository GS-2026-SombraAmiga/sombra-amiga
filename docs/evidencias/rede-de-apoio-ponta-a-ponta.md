# Evidência: API principal e Rede de Apoio funcionando juntas

**Data:** 09/11/2026. **Ambiente:** Windows 11, MySQL 8.0 local, API principal (C#/.NET 10) e Rede de Apoio (Java 21, Spring Boot 4.1.2). Todos os dados de pessoas são fictícios.

## 1. Migrações no MySQL

Na primeira execução, o Flyway criou as tabelas e o coordenador inicial no schema `rede_de_apoio`:

```
Successfully validated 3 migrations
Current version of schema `rede_de_apoio`: << Empty Schema >>
Migrating schema `rede_de_apoio` to version "1 - create-table-agentes"
Migrating schema `rede_de_apoio` to version "2 - create-table-pedidos-ajuda"
Migrating schema `rede_de_apoio` to version "3 - insert-coordenador-inicial"
Successfully applied 3 migrations to schema `rede_de_apoio`, now at version v3
```

## 2. Fluxo completo

Roteiro executado contra os dois serviços no ar:

| # | Passo | Resultado |
|---|---|---|
| 1 | API C#: cadastro de idosa fictícia | HTTP 201 |
| 2 | API C#: check-in "preciso de ajuda" | HTTP 201 em 89 ms |
| 3 | Rede: login do coordenador | HTTP 200, token JWT |
| 4 | Rede: coordenador cadastra a agente | HTTP 201, sem senha na resposta |
| 5 | Rede: a agente lista os pedidos | O pedido do passo 2 aparece com status ABERTO e o nome vindo da API C# |
| 6 | API C#: segundo toque em "preciso de ajuda" | Check-in salvo e nenhum pedido duplicado |
| 7 | Rede: a agente aceita | HTTP 200, EM_ATENDIMENTO |
| 8 | Rede: a agente conclui com observação | HTTP 200, CONCLUIDO |
| 9 | API C#: novo "preciso de ajuda" após a conclusão | Um novo pedido é aberto |

Registros da API C# durante o fluxo:

```
Pedido de ajuda aberto na Rede de Apoio.
A Rede de Apoio já tinha um pedido em andamento para este cidadão.
Pedido de ajuda aberto na Rede de Apoio.
```

## 3. Rede de Apoio fora do ar

Com o serviço Java desligado, o cidadão continua conseguindo pedir ajuda:

| Medida | Resultado |
|---|---|
| Check-in "preciso de ajuda" | HTTP 201 em 4 ms |
| API C# depois da falha | Continua respondendo (HTTP 200) |

Registro da falha, em segundo plano:

```
Rede de Apoio indisponível; o check-in foi salvo, mas o pedido não foi aberto:
No connection could be made because the target machine actively refused it. (localhost:8085)
```

Na primeira versão, o check-in esperava a resposta da Rede de Apoio e levava **4,1 segundos** com o serviço fora do ar. Por isso o envio passou a ser feito por uma fila em segundo plano.

## 4. Documentação automática

A especificação OpenAPI gerada por cada serviço foi exportada:

- [servico-soa/docs/openapi.json](../../servico-soa/docs/openapi.json): Rede de Apoio, 8 rotas
- [api/docs/swagger.json](../../api/docs/swagger.json): API principal, 13 rotas
