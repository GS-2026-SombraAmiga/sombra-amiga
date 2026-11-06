using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Dominio.Entidades;

public sealed class PontoHidratacao : Entidade
{
    private const double RaioTerraKm = 6371;

    public string Nome { get; private set; } = null!;
    public TipoPonto Tipo { get; private set; }
    public double Latitude { get; private set; }
    public double Longitude { get; private set; }
    public bool Ativo { get; private set; } = true;

    private PontoHidratacao() { }

    public PontoHidratacao(string nome, TipoPonto tipo, double latitude, double longitude)
    {
        Atualizar(nome, tipo, latitude, longitude);
    }

    public void Atualizar(string nome, TipoPonto tipo, double latitude, double longitude)
    {
        if (string.IsNullOrWhiteSpace(nome))
            throw new DominioException("Nome é obrigatório.");
        if (latitude is < -90 or > 90 || longitude is < -180 or > 180)
            throw new DominioException("Coordenadas inválidas.");

        Nome = nome.Trim();
        Tipo = tipo;
        Latitude = latitude;
        Longitude = longitude;
    }

    public void Desativar() => Ativo = false;

    /// <summary>Distância em linha reta pela fórmula de Haversine.</summary>
    public double DistanciaKm(double latitude, double longitude)
    {
        var dLat = EmRadianos(latitude - Latitude);
        var dLon = EmRadianos(longitude - Longitude);
        var a = Math.Pow(Math.Sin(dLat / 2), 2)
                + Math.Cos(EmRadianos(Latitude)) * Math.Cos(EmRadianos(latitude)) * Math.Pow(Math.Sin(dLon / 2), 2);
        return 2 * RaioTerraKm * Math.Asin(Math.Sqrt(a));
    }

    private static double EmRadianos(double graus) => graus * Math.PI / 180;
}
