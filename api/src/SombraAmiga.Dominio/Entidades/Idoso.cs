using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Dominio.Entidades;

public sealed class Idoso : Cidadao
{
    public override PerfilCidadao Perfil => PerfilCidadao.Idoso;

    protected override double AjusteSensibilidadeC => 3;

    private Idoso() { }

    public Idoso(string nome, Cpf cpf, string contatoFamiliar, string? condicaoSaude)
        : base(nome, cpf, contatoFamiliar, condicaoSaude) { }

    public override string Orientar(NivelRisco nivel) => nivel switch
    {
        NivelRisco.Extremo => "Calor perigoso. Fique em local fresco, beba água e avise sua família.",
        NivelRisco.Alto => "Evite sair entre 11h e 16h. Beba água mesmo sem sede.",
        NivelRisco.Atencao => "Dia quente. Mantenha a casa ventilada e beba água.",
        _ => "Sem risco de calor agora.",
    };
}
