# Rede de Apoio (Java / Spring Boot)

Serviço da disciplina **Arquitetura Orientada a Serviços (SOA) e Web Services**, parte da CitizenTech **Sombra Amiga**. A Ficha completa está no [README da raiz](../README.md).

**Integrantes:** Glauco Heitor Gonçalves (RM 555978) e Pedro Henrique Junqueira (RM 556278).

## O que o serviço faz

Quando um idoso faz o check-in **"preciso de ajuda"** no app, alguém precisa agir. A Rede de Apoio:

1. **Recebe o pedido:** a API principal (C#) avisa este serviço, que confirma o cidadão consultando a própria API principal por REST.
2. **Mostra os pedidos aos agentes:** agentes comunitários de saúde e voluntários do bairro veem os pedidos abertos.
3. **Acompanha o atendimento:** um agente aceita o pedido, vai até a pessoa e conclui o atendimento com uma observação. O pedido passa por `ABERTO`, `EM_ATENDIMENTO` e `CONCLUIDO`.

```
App ──check-in "preciso de ajuda"──▶ API principal (C#, :5080)
                                        │ POST /api/pedidos (chave de serviço)
                                        ▼
                                  Rede de Apoio (Java, :8085) ──GET /api/cidadaos/{id}──▶ API principal
                                        │
                                        ▼
                                  Agente (login JWT): lista, aceita e conclui
```

## Tecnologias

| Item | Versão |
|---|---|
| Java | 21 (Temurin) |
| Spring Boot | **4.1.2** (o checkpoint de referência da disciplina usa 4.0.8, da mesma linha) |
| Maven | 3.10.0, pelo Maven Wrapper (`mvnw`) |
| Banco de dados | MySQL 8, com migrações Flyway |
| Segurança | Spring Security, JWT (`com.auth0:java-jwt` 4.6.0) e BCrypt |
| Documentação | SpringDoc OpenAPI 3.0.2 (Swagger UI) |
| Testes | JUnit 5, Mockito, MockMvc e H2 em memória |

## Como rodar

**1. Banco de dados.** Com o MySQL 8 rodando, execute no MySQL Workbench como root:

```sql
CREATE DATABASE IF NOT EXISTS rede_de_apoio;
CREATE USER IF NOT EXISTS 'rededeapoio'@'localhost' IDENTIFIED BY 'rededeapoio';
GRANT ALL PRIVILEGES ON rede_de_apoio.* TO 'rededeapoio'@'localhost';
```

As tabelas são criadas pelo Flyway na primeira execução. Para usar outro banco ou usuário, defina `DATASOURCE_URL`, `DATASOURCE_USERNAME` e `DATASOURCE_PASSWORD`.

**2. Aplicação.**

```bash
cd servico-soa
./mvnw spring-boot:run
```

**3. Documentação dos endpoints:** http://localhost:8085/swagger-ui.html

Para testar no Swagger, faça `POST /api/auth/login` com o coordenador de desenvolvimento, copie o `tokenJWT` e cole no botão **Authorize**.

| Credencial de desenvolvimento | Valor |
|---|---|
| Coordenador | `coordenador@sombraamiga.dev` / `coordenador123` (criado pela migração V3) |
| Chave de serviço da API principal | `chave-de-desenvolvimento-sombra-amiga` (cabeçalho `X-Chave-Servico`) |

Essas credenciais são só de desenvolvimento. Em outro ambiente, troque-as pelas variáveis `JWT_SECRET` e `CHAVE_SERVICO`.

## Como testar

```bash
cd servico-soa
./mvnw test
```

Os testes usam H2 em memória com as mesmas migrações, então **não precisam do MySQL**. São 35 testes:

| Tipo | O que cobre |
|---|---|
| Unitários de domínio | Ciclo de vida do pedido e os três validadores de aceite |
| Unitários de serviço (Mockito) | Abertura, duplicidade, cidadão inexistente, aceite e conclusão |
| Unitários de segurança | Token válido, expirado, com outro segredo e inválido |
| Integração (MockMvc + H2) | Login, 401 sem token, 403 por perfil, fluxo completo do pedido, 409 de pedido já aceito, chave de serviço e Swagger |

## Endpoints

| Método | Rota | Quem acessa | Função |
|---|---|---|---|
| POST | `/api/auth/login` | Público | Login do agente e emissão do token JWT |
| POST | `/api/agentes` | Coordenador | Cadastra agente (senha gravada com BCrypt) |
| GET | `/api/agentes` | Agente, coordenador | Lista agentes ativos (paginado) |
| GET | `/api/agentes/{id}` | Agente, coordenador | Detalha agente |
| PUT | `/api/agentes/{id}` | Coordenador | Atualiza nome e bairro |
| DELETE | `/api/agentes/{id}` | Coordenador | Desativa o agente (exclusão lógica) |
| POST | `/api/pedidos` | API principal (chave), coordenador | Abre pedido de ajuda |
| GET | `/api/pedidos` | Agente, coordenador | Lista pedidos abertos e em atendimento |
| GET | `/api/pedidos/{id}` | Agente, coordenador | Detalha pedido |
| POST | `/api/pedidos/{id}/aceitar` | Agente, coordenador | Aceita pedido |
| POST | `/api/pedidos/{id}/concluir` | Agente responsável | Conclui com observação |
| GET | `/health-check` | Público | Verificação de disponibilidade |

## Estrutura do domínio

```
domain/
  agente/      Agente (também é o usuário do login), DTOs e repositório
  pedido/      PedidoAjuda, StatusPedido, DTOs e repositório
    validacao/ Regras de aceite: pedido aberto, agente ativo, limite de 3 atendimentos
  cidadao/     Dados do cidadão vindos da API principal
infra/
  apiprincipal/  Cliente REST da API principal (RestClient)
  security/      JWT, chave de serviço, BCrypt e CORS
  exception/     Tratamento global de erros
  springdoc/     Configuração do Swagger
service/       Regras de aplicação
controller/    Endpoints REST
```

**Regras de negócio:**
- Cada cidadão tem no máximo um pedido em andamento, o que evita duplicar atendimentos por vários toques no botão.
- Um pedido aceito por um agente não pode ser aceito por outro. Com bloqueio otimista, isso vale até para aceites simultâneos.
- Cada agente atende no máximo 3 pessoas ao mesmo tempo.
- Só o agente responsável conclui o pedido.
- Agente desativado não faz login.

## Privacidade

A Rede de Apoio guarda do cidadão apenas o identificador, o nome e o perfil, obtidos da API principal, que não expõe CPF, contato ou condição de saúde. As senhas dos agentes são gravadas só como hash BCrypt e nunca aparecem nas respostas.
