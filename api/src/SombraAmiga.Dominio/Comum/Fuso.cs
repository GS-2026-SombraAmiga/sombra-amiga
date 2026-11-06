namespace SombraAmiga.Dominio.Comum;

/// <summary>Converte UTC para o dia local de São Paulo (UTC-3, sem horário de verão).</summary>
public static class Fuso
{
    private static readonly TimeSpan DeslocamentoSaoPaulo = TimeSpan.FromHours(-3);

    public static DateOnly DiaLocal(DateTime utc) => DateOnly.FromDateTime(utc + DeslocamentoSaoPaulo);
}
