using Microsoft.AspNetCore.Mvc;
using SombraAmiga.Api.Contratos;
using SombraAmiga.Dominio.Repositorios;
using SombraAmiga.Dominio.Servicos;

namespace SombraAmiga.Api.Controllers;

/// <summary>Leituras enviadas pelos sensores ESP32.</summary>
[ApiController]
[Route("api/leituras")]
public sealed class LeiturasController(ServicoLeituras servico, IRepositorioLeituras leituras) : ControllerBase
{
    /// <summary>Registra uma leitura e abre ou encerra o alerta do ponto.</summary>
    [HttpPost]
    [ProducesResponseType<LeituraResposta>(StatusCodes.Status201Created)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Registrar(LeituraRequisicao requisicao, CancellationToken ct)
    {
        var leitura = await servico.RegistrarAsync(
            requisicao.PontoId!.Value, requisicao.TemperaturaC!.Value, requisicao.UmidadePct!.Value, ct);
        return Created($"/api/leituras/{leitura.Id}", LeituraResposta.De(leitura));
    }

    /// <summary>Lista as leituras mais recentes de um ponto.</summary>
    [HttpGet]
    public async Task<IEnumerable<LeituraResposta>> Listar([FromQuery] Guid pontoId, [FromQuery] int limite = 50, CancellationToken ct = default) =>
        (await leituras.ListarDoPontoAsync(pontoId, Math.Clamp(limite, 1, 500), ct)).Select(LeituraResposta.De);
}
