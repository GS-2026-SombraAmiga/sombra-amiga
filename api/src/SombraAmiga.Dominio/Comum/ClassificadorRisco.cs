namespace SombraAmiga.Dominio.Comum;

/// <summary>Faixas de índice de calor em Celsius, baseadas nas faixas do NWS.</summary>
public static class ClassificadorRisco
{
    public const double LimiteAtencao = 27;
    public const double LimiteAlto = 32;
    public const double LimiteExtremo = 41;

    public static NivelRisco Classificar(double indiceCalorC) => indiceCalorC switch
    {
        >= LimiteExtremo => NivelRisco.Extremo,
        >= LimiteAlto => NivelRisco.Alto,
        >= LimiteAtencao => NivelRisco.Atencao,
        _ => NivelRisco.Baixo,
    };

    /// <summary>Nome do nível para exibição ao cidadão.</summary>
    public static string Descrever(NivelRisco nivel) => nivel switch
    {
        NivelRisco.Extremo => "extremo",
        NivelRisco.Alto => "alto",
        NivelRisco.Atencao => "atenção",
        _ => "baixo",
    };
}
