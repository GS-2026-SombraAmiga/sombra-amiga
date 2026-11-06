using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Dominio.Servicos;

public sealed record IndicadorImpacto(int DiasComAlerta, int CheckInsEsperados, int CheckInsConfirmados, double PercentualConfirmado);

/// <summary>Indicador de impacto da Ficha: check-ins confirmados em dias de alerta.</summary>
public sealed class ServicoIndicadores(
    IRepositorioAlertas alertas,
    IRepositorioCheckIns checkIns,
    IRepositorioCidadaos cidadaos)
{
    public async Task<IndicadorImpacto> CalcularAsync(DateOnly inicio, DateOnly fim, CancellationToken ct = default)
    {
        if (fim < inicio)
            throw new DominioException("A data final deve ser maior ou igual à inicial.");

        var dias = await alertas.ListarDiasComAlertaAsync(inicio, fim, ct);
        var totalCidadaos = await cidadaos.ContarAsync(ct);
        var confirmados = await checkIns.ContarConfirmadosAsync(dias, ct);

        var esperados = dias.Count * totalCidadaos;
        var percentual = esperados == 0 ? 0 : Math.Round(100.0 * confirmados / esperados, 1);

        return new IndicadorImpacto(dias.Count, esperados, confirmados, percentual);
    }
}
