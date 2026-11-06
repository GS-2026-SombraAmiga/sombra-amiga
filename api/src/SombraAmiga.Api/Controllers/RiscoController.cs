using Microsoft.AspNetCore.Mvc;
using SombraAmiga.Dominio.Servicos;

namespace SombraAmiga.Api.Controllers;

/// <summary>Risco de calor atual e indicador de impacto.</summary>
[ApiController]
[Route("api")]
public sealed class RiscoController(ServicoRisco risco, ServicoIndicadores indicadores) : ControllerBase
{
    /// <summary>Risco atual, com orientação personalizada quando o cidadão é informado.</summary>
    [HttpGet("risco/atual")]
    public Task<RiscoAtual> Atual([FromQuery] Guid? cidadaoId, CancellationToken ct) =>
        risco.ObterAtualAsync(cidadaoId, ct);

    /// <summary>Percentual de check-ins confirmados em dias de alerta no período.</summary>
    [HttpGet("indicadores/impacto")]
    public Task<IndicadorImpacto> Impacto([FromQuery] DateOnly inicio, [FromQuery] DateOnly fim, CancellationToken ct) =>
        indicadores.CalcularAsync(inicio, fim, ct);
}
