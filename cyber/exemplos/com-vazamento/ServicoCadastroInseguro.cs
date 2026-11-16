// EXEMPLO PROPOSITAL DE CÓDIGO INSEGURO, para demonstrar a Sentinela Cidadã.
// Não faz parte da API da Sombra Amiga e não é compilado. A versão corrigida está em ../corrigido/.
using Microsoft.Extensions.Logging;

namespace SombraAmiga.Exemplos;

public sealed class ServicoCadastroInseguro(ILogger<ServicoCadastroInseguro> log, HttpClient http)
{
    public async Task<IResult> CadastrarAsync(NovoCidadao dados)
    {
        // Falha 1: o CPF completo vai para o log.
        log.LogInformation("Cadastrando cidadão com CPF {Cpf}", dados.Cpf);

        // Falha 2: a condição de saúde passa por uma variável e acaba no console.
        var resumo = $"{dados.Nome} tem {dados.CondicaoSaude}";
        Console.WriteLine(resumo);

        if (await ExisteAsync(dados.Cpf))
            // Falha 3: a mensagem de erro, que chega ao app, carrega o CPF.
            throw new ConflitoException($"O CPF {dados.Cpf} já está cadastrado.");

        // Falha 4: o telefone da família é enviado a outro sistema.
        await http.PostAsJsonAsync("https://parceiro.example/contatos", new { dados.ContatoFamiliar });

        // Falha 5: a resposta da API devolve o CPF completo.
        return Results.Ok(new { dados.Nome, dados.Cpf });
    }

    public void TrocarSenha(string usuario, string senha)
    {
        // Falha 6: a senha nova vai para o log.
        log.LogWarning("Senha do usuário {Usuario} trocada para {Senha}", usuario, senha);
    }

    private Task<bool> ExisteAsync(string cpf) => Task.FromResult(false);
}
