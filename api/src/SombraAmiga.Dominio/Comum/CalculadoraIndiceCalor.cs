namespace SombraAmiga.Dominio.Comum;

/// <summary>Índice de calor pela fórmula de Rothfusz (NWS). Mesma fórmula usada em ml/preparar_dados.py.</summary>
public static class CalculadoraIndiceCalor
{
    public static double Calcular(double temperaturaC, double umidadePct)
    {
        var t = temperaturaC * 9 / 5 + 32;
        var r = umidadePct;

        var indiceF = t >= 80
            ? -42.379 + 2.04901523 * t + 10.14333127 * r - 0.22475541 * t * r
              - 6.83783e-3 * t * t - 5.481717e-2 * r * r + 1.22874e-3 * t * t * r
              + 8.5282e-4 * t * r * r - 1.99e-6 * t * t * r * r
            : 0.5 * (t + 61 + (t - 68) * 1.2 + r * 0.094);

        return Math.Round((indiceF - 32) * 5 / 9, 1);
    }
}
