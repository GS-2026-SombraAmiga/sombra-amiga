using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Infra.Dados;

/// <summary>Pontos simulados para demonstração. Não representam locais reais.</summary>
public static class PontosIniciais
{
    public static readonly Guid PontoPraca = Guid.Parse("11111111-1111-1111-1111-111111111111");
    public static readonly Guid PontoUbs = Guid.Parse("22222222-2222-2222-2222-222222222222");
    public static readonly Guid PontoTerminal = Guid.Parse("33333333-3333-3333-3333-333333333333");

    public static readonly object[] Todos =
    [
        new { Id = PontoPraca, Nome = "Praça da Sombra (simulado)", Tipo = TipoPonto.SombraEAgua, Latitude = -23.4620, Longitude = -46.6810, Ativo = true },
        new { Id = PontoUbs, Nome = "Bebedouro da UBS (simulado)", Tipo = TipoPonto.Agua, Latitude = -23.4685, Longitude = -46.6755, Ativo = true },
        new { Id = PontoTerminal, Nome = "Abrigo do Terminal (simulado)", Tipo = TipoPonto.Sombra, Latitude = -23.4550, Longitude = -46.6890, Ativo = true },
    ];
}
