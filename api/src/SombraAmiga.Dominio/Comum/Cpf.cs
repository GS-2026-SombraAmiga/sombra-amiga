namespace SombraAmiga.Dominio.Comum;

/// <summary>
/// CPF validado. ToString devolve o valor mascarado para que o número
/// completo não vaze por acidente em logs ou mensagens.
/// </summary>
public sealed record Cpf
{
    public string Numero { get; }

    private Cpf(string numero) => Numero = numero;

    public string Mascarado => $"***.***.***-{Numero[^2..]}";

    public override string ToString() => Mascarado;

    public static Cpf Criar(string valor)
    {
        var digitos = new string((valor ?? string.Empty).Where(char.IsDigit).ToArray());
        if (!EhValido(digitos))
            throw new DominioException("CPF inválido.");
        return new Cpf(digitos);
    }

    private static bool EhValido(string cpf)
    {
        if (cpf.Length != 11 || cpf.Distinct().Count() == 1)
            return false;
        return DigitoConfere(cpf, 9) && DigitoConfere(cpf, 10);
    }

    private static bool DigitoConfere(string cpf, int posicao)
    {
        var soma = Enumerable.Range(0, posicao).Sum(i => (cpf[i] - '0') * (posicao + 1 - i));
        var digito = soma * 10 % 11 % 10;
        return cpf[posicao] - '0' == digito;
    }
}
