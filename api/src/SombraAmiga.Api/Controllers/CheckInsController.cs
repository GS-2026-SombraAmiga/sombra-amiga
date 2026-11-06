using Microsoft.AspNetCore.Mvc;
using SombraAmiga.Api.Contratos;
using SombraAmiga.Dominio.Servicos;

namespace SombraAmiga.Api.Controllers;

/// <summary>Check-in "estou bem" do cidadão.</summary>
[ApiController]
[Route("api/checkins")]
public sealed class CheckInsController(ServicoCheckIns servico) : ControllerBase
{
    /// <summary>Registra um check-in.</summary>
    [HttpPost]
    [ProducesResponseType<CheckInResposta>(StatusCodes.Status201Created)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Registrar(CheckInRequisicao requisicao, CancellationToken ct)
    {
        var checkIn = await servico.RegistrarAsync(requisicao.CidadaoId!.Value, requisicao.Status!.Value, ct);
        return Created($"/api/checkins/{checkIn.Id}", CheckInResposta.De(checkIn));
    }
}
