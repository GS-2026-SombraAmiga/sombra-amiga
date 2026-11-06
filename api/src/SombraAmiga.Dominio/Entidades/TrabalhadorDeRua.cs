using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Dominio.Entidades;

public sealed class TrabalhadorDeRua : Cidadao
{
    public string Ocupacao { get; private set; } = null!;

    public override PerfilCidadao Perfil => PerfilCidadao.TrabalhadorDeRua;

    protected override double AjusteSensibilidadeC => 2;

    private TrabalhadorDeRua() { }

    public TrabalhadorDeRua(string nome, Cpf cpf, string contatoFamiliar, string? condicaoSaude, string ocupacao)
        : base(nome, cpf, contatoFamiliar, condicaoSaude)
    {
        if (string.IsNullOrWhiteSpace(ocupacao))
            throw new DominioException("Ocupação é obrigatória.");
        Ocupacao = ocupacao.Trim();
    }

    public override string Orientar(NivelRisco nivel) => nivel switch
    {
        NivelRisco.Extremo => "Calor perigoso. Pare em um ponto de sombra e água antes de continuar.",
        NivelRisco.Alto => "Faça pausas na sombra e beba água a cada 20 minutos.",
        NivelRisco.Atencao => "Dia quente. Leve água e use proteção contra o sol.",
        _ => "Sem risco de calor agora.",
    };
}
