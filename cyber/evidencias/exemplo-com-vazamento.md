# Sentinela Cidadã: Exemplo com vazamento

- **Risco Cidadão:** 100/100 (Crítico)
- **Arquivos analisados:** 1 · **métodos seguidos pelo Taint Analysis:** 3
- **Achados por gravidade:** Crítica 2, Alta 4, Média 0, Baixa 0
- **Vazamentos que bloqueiam a entrega:** 6
- **Alertas gerados por:** texto padrão das regras
- **Gerado em:** 2026-11-16T04:40:38-03:00

## 1. Crítica: CPF em resposta (Vazamento (Taint Analysis))

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver as respostas da API, que qualquer pessoa com acesso ao app recebe. Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs`, linha 26, método `CadastrarAsync`
- **Peso:** sensibilidade 5 × exposição 5 = 25
- **Trecho:** `return Results.Ok(new { dados.Nome, dados.Cpf })`
- **Caminho do dado:**
  - linha 26: return Results.Ok(new { dados.Nome, dados.Cpf })

## 2. Crítica: CPF em excecao (Vazamento (Taint Analysis))

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver as mensagens de erro, que podem chegar a quem usa o app. Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs`, linha 20, método `CadastrarAsync`
- **Peso:** sensibilidade 5 × exposição 4 = 20
- **Trecho:** `if (await ExisteAsync(dados.Cpf)) throw new ConflitoException($"O CPF {dados.Cpf} já está cadastrado.")`
- **Caminho do dado:**
  - linha 20: if (await ExisteAsync(dados.Cpf)) throw new ConflitoException($"O CPF {dados.Cpf} já está cadastrado.")

## 3. Alta: CPF em log (Vazamento (Taint Analysis))

> **Para o cidadão:** O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver os registros (logs) do sistema. Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes.

- **Onde:** `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs`, linha 12, método `CadastrarAsync`
- **Peso:** sensibilidade 5 × exposição 3 = 15
- **Trecho:** `log.LogInformation("Cadastrando cidadão com CPF {Cpf}", dados.Cpf)`
- **Caminho do dado:**
  - linha 12: log.LogInformation("Cadastrando cidadão com CPF {Cpf}", dados.Cpf)

## 4. Alta: Dado de saúde em console (Vazamento (Taint Analysis))

> **Para o cidadão:** A condição de saúde de um idoso ou trabalhador de rua pode ser vista por quem consegue ver a tela e os registros do servidor. Isso expõe a pessoa a discriminação e é dado sensível pela LGPD.

- **Onde:** `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs`, linha 16, método `CadastrarAsync`
- **Peso:** sensibilidade 5 × exposição 3 = 15
- **Trecho:** `Console.WriteLine(resumo)`
- **Caminho do dado:**
  - linha 15: resumo recebe Dado de saúde: var resumo = $"{dados.Nome} tem {dados.CondicaoSaude}"
  - linha 16: Console.WriteLine(resumo)

## 5. Alta: Senha ou segredo em log (Vazamento (Taint Analysis))

> **Para o cidadão:** Uma senha ou chave de acesso do sistema pode ser lida por quem consegue ver os registros (logs) do sistema. Com ela, alguém poderia entrar no sistema e ver os dados dos cidadãos.

- **Onde:** `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs`, linha 32, método `TrocarSenha`
- **Peso:** sensibilidade 5 × exposição 3 = 15
- **Trecho:** `log.LogWarning("Senha do usuário {Usuario} trocada para {Senha}", usuario, senha)`
- **Caminho do dado:**
  - linha 29: parâmetro senha (Senha ou segredo)
  - linha 32: log.LogWarning("Senha do usuário {Usuario} trocada para {Senha}", usuario, senha)

## 6. Alta: Contato pessoal em http_externo (Vazamento (Taint Analysis))

> **Para o cidadão:** O telefone ou contato da família de um cidadão pode ser lido por quem consegue ver os dados enviados a outro sistema pela internet. A família pode receber golpes que usam o nome da pessoa atendida.

- **Onde:** `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs`, linha 23, método `CadastrarAsync`
- **Peso:** sensibilidade 3 × exposição 4 = 12
- **Trecho:** `await http.PostAsJsonAsync("https://parceiro.example/contatos", new { dados.ContatoFamiliar })`
- **Caminho do dado:**
  - linha 23: await http.PostAsJsonAsync("https://parceiro.example/contatos", new { dados.ContatoFamiliar })

## Inventário de dados pessoais declarados no código

| Arquivo | Linha | Identificador | Categoria |
|---|---|---|---|
| `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs` | 12 | `CPF` | CPF |
| `cyber/exemplos/com-vazamento/ServicoCadastroInseguro.cs` | 29 | `senha` | Senha ou segredo |
