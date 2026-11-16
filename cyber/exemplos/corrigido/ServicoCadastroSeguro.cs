// Versão corrigida de ../com-vazamento/ServicoCadastroInseguro.cs.
// Cada dado pessoal é protegido antes de chegar a uma saída. Não é compilado.
using Microsoft.Extensions.Logging;

namespace SombraAmiga.Exemplos;

public sealed class ServicoCadastroSeguro(ILogger<ServicoCadastroSeguro> log, HttpClient http)
{
    public async Task<IResult> CadastrarAsync(NovoCidadao dados)
    {
        // Correção 1: só o CPF mascarado vai para o log.
        log.LogInformation("Cadastrando cidadão com CPF {Cpf}", Mascarar(dados.Cpf));

        // Correção 2: o console registra só que existe condição de saúde, não qual é.
        var temCondicao = !string.IsNullOrWhiteSpace(dados.CondicaoSaude);
        Console.WriteLine($"{dados.Nome}: condição de saúde informada = {temCondicao}");

        if (await ExisteAsync(dados.Cpf))
            // Correção 3: a mensagem de erro não repete o dado.
            throw new ConflitoException("Já existe um cadastro com este CPF.");

        // Correção 4: o parceiro recebe um identificador, não o telefone.
        var id = Guid.NewGuid();
        await http.PostAsJsonAsync("https://parceiro.example/contatos", new { id });

        // Correção 5: a resposta devolve o CPF mascarado.
        return Results.Ok(new { dados.Nome, CpfMascarado = Mascarar(dados.Cpf) });
    }

    public void TrocarSenha(string usuario, string senha)
    {
        // Correção 6: o log registra o evento, nunca a senha.
        log.LogWarning("Senha do usuário {Usuario} foi trocada", usuario);
    }

    private static string Mascarar(string cpf) => $"***.***.***-{cpf[^2..]}";

    private Task<bool> ExisteAsync(string cpf) => Task.FromResult(false);
}
