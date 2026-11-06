using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Dominio.Entidades;

/// <summary>
/// Pessoa acompanhada pelo sistema. Cada perfil define a própria sensibilidade
/// ao calor e a própria orientação, por isso a classe é abstrata.
/// </summary>
public abstract class Cidadao : Entidade
{
    private const double AjusteCondicaoSaudeC = 1;

    public string Nome { get; private set; } = null!;
    public Cpf Cpf { get; private set; } = null!;
    public string ContatoFamiliar { get; private set; } = null!;
    public string? CondicaoSaude { get; private set; }

    public bool TemCondicaoSaude => !string.IsNullOrWhiteSpace(CondicaoSaude);

    public abstract PerfilCidadao Perfil { get; }

    /// <summary>Graus somados ao índice de calor para refletir a vulnerabilidade do perfil.</summary>
    protected abstract double AjusteSensibilidadeC { get; }

    protected Cidadao() { }

    protected Cidadao(string nome, Cpf cpf, string contatoFamiliar, string? condicaoSaude)
    {
        Cpf = cpf;
        AtualizarDados(nome, contatoFamiliar, condicaoSaude);
    }

    public void AtualizarDados(string nome, string contatoFamiliar, string? condicaoSaude)
    {
        if (string.IsNullOrWhiteSpace(nome))
            throw new DominioException("Nome é obrigatório.");
        if (string.IsNullOrWhiteSpace(contatoFamiliar))
            throw new DominioException("Contato do familiar é obrigatório.");

        Nome = nome.Trim();
        ContatoFamiliar = contatoFamiliar.Trim();
        CondicaoSaude = string.IsNullOrWhiteSpace(condicaoSaude) ? null : condicaoSaude.Trim();
    }

    public NivelRisco AvaliarRisco(double indiceCalorC)
    {
        var ajuste = AjusteSensibilidadeC + (TemCondicaoSaude ? AjusteCondicaoSaudeC : 0);
        return ClassificadorRisco.Classificar(indiceCalorC + ajuste);
    }

    public abstract string Orientar(NivelRisco nivel);
}
