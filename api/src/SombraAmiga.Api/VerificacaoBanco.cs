using Microsoft.Extensions.Diagnostics.HealthChecks;
using SombraAmiga.Infra.Dados;

namespace SombraAmiga.Api;

/// <summary>Health check usado pelo monitoramento da VM: a API só está saudável se alcança o banco.</summary>
public sealed class VerificacaoBanco(SombraAmigaContexto contexto) : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        return await contexto.Database.CanConnectAsync(cancellationToken)
            ? HealthCheckResult.Healthy("Banco acessível")
            : HealthCheckResult.Unhealthy("Banco inacessível");
    }
}
