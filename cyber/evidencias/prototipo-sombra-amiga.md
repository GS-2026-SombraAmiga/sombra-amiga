# Sentinela Cidadã: Protótipo Sombra Amiga

- **Risco Cidadão:** 30/100 (Moderado)
- **Arquivos analisados:** 101 · **métodos seguidos pelo Taint Analysis:** 163
- **Achados por gravidade:** Crítica 0, Alta 0, Média 4, Baixa 14
- **Vazamentos que bloqueiam a entrega:** 0
- **Alertas gerados por:** texto padrão das regras
- **Gerado em:** 2026-11-16T04:40:38-03:00

## 1. Média: Senha ou segredo em configuracao (Segredo na configuração)

> **Para o cidadão:** Uma senha ou chave de acesso do sistema pode ser lida por quem consegue ver o código e a configuração guardados no repositório (valor de desenvolvimento, trocável por variável de ambiente). Com ela, alguém poderia entrar no sistema e ver os dados dos cidadãos.

- **Onde:** `api/src/SombraAmiga.Api/appsettings.json`, linha 7
- **Peso:** sensibilidade 5 × exposição 2 = 10
- **Trecho:** `"Chave": "chave-de-desenvolvimento-sombra-amiga"`

## 2. Média: Senha ou segredo em configuracao (Segredo na configuração)

> **Para o cidadão:** Uma senha ou chave de acesso do sistema pode ser lida por quem consegue ver o código e a configuração guardados no repositório (valor de desenvolvimento, trocável por variável de ambiente). Com ela, alguém poderia entrar no sistema e ver os dados dos cidadãos.

- **Onde:** `servico-soa/src/main/resources/application.properties`, linha 8
- **Peso:** sensibilidade 5 × exposição 2 = 10
- **Trecho:** `spring.datasource.password=${DATASOURCE_PASSWORD:rededeapoio}`

## 3. Média: Senha ou segredo em configuracao (Segredo na configuração)

> **Para o cidadão:** Uma senha ou chave de acesso do sistema pode ser lida por quem consegue ver o código e a configuração guardados no repositório (valor de desenvolvimento, trocável por variável de ambiente). Com ela, alguém poderia entrar no sistema e ver os dados dos cidadãos.

- **Onde:** `servico-soa/src/main/resources/application.properties`, linha 12
- **Peso:** sensibilidade 5 × exposição 2 = 10
- **Trecho:** `api.security.token.secret=${JWT_SECRET:segredo-de-desenvolvimento-rede-de-apoio}`

## 4. Média: Senha ou segredo em configuracao (Segredo na configuração)

> **Para o cidadão:** Uma senha ou chave de acesso do sistema pode ser lida por quem consegue ver o código e a configuração guardados no repositório (valor de desenvolvimento, trocável por variável de ambiente). Com ela, alguém poderia entrar no sistema e ver os dados dos cidadãos.

- **Onde:** `servico-soa/src/main/resources/application.properties`, linha 13
- **Peso:** sensibilidade 5 × exposição 2 = 10
- **Trecho:** `app.servico.chave=${CHAVE_SERVICO:chave-de-desenvolvimento-sombra-amiga}`

## 5. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/ApiTestes.cs`, linha 55
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `var resposta = await _cliente.PostAsJsonAsync("/api/cidadaos", Idoso("52998224725"));`

## 6. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/ApiTestes.cs`, linha 72
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `await _cliente.PostAsJsonAsync("/api/cidadaos", Idoso("11144477735"));`

## 7. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/ApiTestes.cs`, linha 74
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `var resposta = await _cliente.PostAsJsonAsync("/api/cidadaos", Idoso("111.444.777-35"));`

## 8. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/ApiTestes.cs`, linha 104
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `cpf = "86288366757",`

## 9. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/DominioTestes.cs`, linha 9
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `[InlineData("52998224725")]`

## 10. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/DominioTestes.cs`, linha 10
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `[InlineData("529.982.247-25")]`

## 11. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/RedeDeApoioTestes.cs`, linha 28
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `var idoso = new Idoso("Lurdes", Cpf.Criar("52998224725"), "Filha", null);`

## 12. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/ServicosTestes.cs`, linha 128
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `var idoso = new Idoso("Lurdes", Cpf.Criar("52998224725"), "Filha", "Hipertensão");`

## 13. Baixa: CPF em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `api/tests/SombraAmiga.Testes/ServicosTestes.cs`, linha 179
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `var b = new Idoso("B", Cpf.Criar("11144477735"), "Filho", null);`

## 14. Baixa: Senha ou segredo em configuracao (Segredo na configuração)

> **Para o cidadão:** Uma senha ou chave de acesso do sistema pode ser lida por quem consegue ver o código e a configuração guardados no repositório (segredo fictício de teste). Com ela, alguém poderia entrar no sistema e ver os dados dos cidadãos.

- **Onde:** `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/infra/security/TokenServiceTest.java`, linha 15
- **Peso:** sensibilidade 5 × exposição 1 = 5
- **Trecho:** `private static final String SEGREDO = "segredo-de-teste";`

## 15. Baixa: Contato pessoal em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O telefone ou contato da família de um cidadão pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). A família pode receber golpes que usam o nome da pessoa atendida.

- **Onde:** `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/infra/security/TokenServiceTest.java`, linha 24
- **Peso:** sensibilidade 3 × exposição 1 = 3
- **Trecho:** `assertThat(service.getSubject(token)).isEqualTo("agente1@teste.com");`

## 16. Baixa: Contato pessoal em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O telefone ou contato da família de um cidadão pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). A família pode receber golpes que usam o nome da pessoa atendida.

- **Onde:** `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/integracao/FluxoRedeDeApoioIntegrationTest.java`, linha 38
- **Peso:** sensibilidade 3 × exposição 1 = 3
- **Trecho:** `private static final String COORDENADOR = "coordenador@sombraamiga.dev";`

## 17. Baixa: Contato pessoal em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O telefone ou contato da família de um cidadão pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). A família pode receber golpes que usam o nome da pessoa atendida.

- **Onde:** `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/integracao/FluxoRedeDeApoioIntegrationTest.java`, linha 108
- **Peso:** sensibilidade 3 × exposição 1 = 3
- **Trecho:** `cadastrarAgente(coordenador, "ana@teste.com");`

## 18. Baixa: Contato pessoal em codigo_fonte (Dado pessoal no código)

> **Para o cidadão:** O telefone ou contato da família de um cidadão pode ser lido por quem consegue ver o código-fonte, que fica no repositório (dado de teste). A família pode receber golpes que usam o nome da pessoa atendida.

- **Onde:** `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/integracao/FluxoRedeDeApoioIntegrationTest.java`, linha 172
- **Peso:** sensibilidade 3 × exposição 1 = 3
- **Trecho:** `cadastrarAgente(coordenador, "bruno@teste.com");`

## Inventário de dados pessoais declarados no código

| Arquivo | Linha | Identificador | Categoria |
|---|---|---|---|
| `api/src/SombraAmiga.Api/Contratos/Contratos.cs` | 10 | `Cpf` | CPF |
| `api/src/SombraAmiga.Api/Contratos/Contratos.cs` | 11 | `ContatoFamiliar` | Contato pessoal |
| `api/src/SombraAmiga.Api/Contratos/Contratos.cs` | 12 | `CondicaoSaude` | Dado de saúde |
| `api/src/SombraAmiga.Api/Contratos/Contratos.cs` | 29 | `Latitude` | Localização ou endereço |
| `api/src/SombraAmiga.Api/Contratos/Contratos.cs` | 30 | `Longitude` | Localização ou endereço |
| `api/src/SombraAmiga.Api/Controllers/PontosController.cs` | 22 | `latitude` | Localização ou endereço |
| `api/src/SombraAmiga.Api/Controllers/PontosController.cs` | 22 | `longitude` | Localização ou endereço |
| `api/src/SombraAmiga.Dominio/Comum/Cpf.cs` | 25 | `cpf` | CPF |
| `api/src/SombraAmiga.Dominio/Entidades/Cidadao.cs` | 11 | `AjusteCondicaoSaudeC` | Dado de saúde |
| `api/src/SombraAmiga.Dominio/Entidades/Cidadao.cs` | 14 | `Cpf` | CPF |
| `api/src/SombraAmiga.Dominio/Entidades/Cidadao.cs` | 15 | `ContatoFamiliar` | Contato pessoal |
| `api/src/SombraAmiga.Dominio/Entidades/Cidadao.cs` | 16 | `CondicaoSaude` | Dado de saúde |
| `api/src/SombraAmiga.Dominio/Entidades/Idoso.cs` | 13 | `cpf` | CPF |
| `api/src/SombraAmiga.Dominio/Entidades/Idoso.cs` | 13 | `contatoFamiliar` | Contato pessoal |
| `api/src/SombraAmiga.Dominio/Entidades/Idoso.cs` | 13 | `condicaoSaude` | Dado de saúde |
| `api/src/SombraAmiga.Dominio/Entidades/PontoHidratacao.cs` | 11 | `Latitude` | Localização ou endereço |
| `api/src/SombraAmiga.Dominio/Entidades/PontoHidratacao.cs` | 12 | `Longitude` | Localização ou endereço |
| `api/src/SombraAmiga.Dominio/Entidades/TrabalhadorDeRua.cs` | 15 | `cpf` | CPF |
| `api/src/SombraAmiga.Dominio/Entidades/TrabalhadorDeRua.cs` | 15 | `contatoFamiliar` | Contato pessoal |
| `api/src/SombraAmiga.Dominio/Entidades/TrabalhadorDeRua.cs` | 15 | `condicaoSaude` | Dado de saúde |
| `api/src/SombraAmiga.Dominio/Repositorios/IRepositorios.cs` | 16 | `cpf` | CPF |
| `api/src/SombraAmiga.Dominio/Servicos/ServicoCidadaos.cs` | 10 | `Cpf` | CPF |
| `api/src/SombraAmiga.Dominio/Servicos/ServicoCidadaos.cs` | 11 | `ContatoFamiliar` | Contato pessoal |
| `api/src/SombraAmiga.Dominio/Servicos/ServicoCidadaos.cs` | 12 | `CondicaoSaude` | Dado de saúde |
| `api/src/SombraAmiga.Infra/RedeDeApoio/ClienteRedeDeApoio.cs` | 39 | `Chave` | Senha ou segredo |
| `api/src/SombraAmiga.Infra/Repositorios/Repositorios.cs` | 28 | `cpf` | CPF |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/Agente.java` | 26 | `email` | Contato pessoal |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/Agente.java` | 27 | `senha` | Senha ou segredo |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/AgenteRepository.java` | 10 | `email` | Contato pessoal |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/DadosCadastroAgente.java` | 16 | `email` | Contato pessoal |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/DadosCadastroAgente.java` | 20 | `senha` | Senha ou segredo |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/DadosDetalhamentoAgente.java` | 7 | `email` | Contato pessoal |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/DadosLogin.java` | 7 | `email` | Contato pessoal |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/agente/DadosLogin.java` | 10 | `senha` | Senha ou segredo |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/pedido/DadosAberturaPedido.java` | 16 | `latitude` | Localização ou endereço |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/pedido/DadosAberturaPedido.java` | 19 | `longitude` | Localização ou endereço |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/pedido/DadosDetalhamentoPedido.java` | 12 | `latitude` | Localização ou endereço |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/pedido/DadosDetalhamentoPedido.java` | 13 | `longitude` | Localização ou endereço |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/pedido/PedidoAjuda.java` | 28 | `latitude` | Localização ou endereço |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/domain/pedido/PedidoAjuda.java` | 29 | `longitude` | Localização ou endereço |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/infra/security/SecurityFilter.java` | 33 | `chaveServico` | Senha ou segredo |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/infra/security/SecurityFilter.java` | 42 | `token` | Senha ou segredo |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/infra/security/SecurityFilter.java` | 54 | `email` | Contato pessoal |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/infra/security/TokenService.java` | 20 | `secret` | Senha ou segredo |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/infra/springdoc/SpringDocConfig.java` | 18 | `CHAVE_SERVICO` | Senha ou segredo |
| `servico-soa/src/main/java/br/com/fiap3espg/rededeapoio/service/AutenticacaoService.java` | 17 | `email` | Contato pessoal |
| `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/infra/security/TokenServiceTest.java` | 15 | `SEGREDO` | Senha ou segredo |
| `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/infra/security/TokenServiceTest.java` | 22 | `token` | Senha ou segredo |
| `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/integracao/FluxoRedeDeApoioIntegrationTest.java` | 49 | `chaveServico` | Senha ou segredo |
| `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/integracao/FluxoRedeDeApoioIntegrationTest.java` | 56 | `email` | Contato pessoal |
| `servico-soa/src/test/java/br/com/fiap3espg/rededeapoio/integracao/FluxoRedeDeApoioIntegrationTest.java` | 56 | `senha` | Senha ou segredo |
| `api/tests/SombraAmiga.Testes/ApiTestes.cs` | 34 | `cpf` | CPF |
| `api/tests/SombraAmiga.Testes/ApiTestes.cs` | 208 | `documento` | CPF |
| `api/tests/SombraAmiga.Testes/DominioTestes.cs` | 25 | `cpf` | CPF |
