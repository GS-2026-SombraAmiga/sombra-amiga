using Microsoft.AspNetCore.Mvc;
using SombraAmiga.Api.Contratos;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Api.Controllers;

/// <summary>Alertas de calor gerados pelos sensores ou pela previsão.</summary>
[ApiController]
[Route("api/alertas")]
public sealed class AlertasController(
    IRepositorioAlertas alertas,
    IUnidadeDeTrabalho unidade,
    TimeProvider relogio) : ControllerBase
{
    /// <summary>Lista os alertas ativos.</summary>
    [HttpGet("ativos")]
    public async Task<IEnumerable<AlertaResposta>> ListarAtivos(CancellationToken ct) =>
        (await alertas.ListarAtivosAsync(ct)).Select(AlertaResposta.De);

    /// <summary>Publica um alerta vindo do modelo de previsão.</summary>
    [HttpPost("previsao")]
    [ProducesResponseType<AlertaResposta>(StatusCodes.Status201Created)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> PublicarPrevisao(PrevisaoRequisicao requisicao, CancellationToken ct)
    {
        var alerta = Alerta.DePrevisao(requisicao.Nivel!.Value, requisicao.Mensagem, relogio.GetUtcNow().UtcDateTime);
        await alertas.AdicionarAsync(alerta, ct);
        await unidade.SalvarAsync(ct);
        return Created($"/api/alertas/{alerta.Id}", AlertaResposta.De(alerta));
    }

    /// <summary>Encerra um alerta ativo.</summary>
    [HttpPost("{id:guid}/encerrar")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Encerrar(Guid id, CancellationToken ct)
    {
        var alerta = await alertas.ObterAsync(id, ct) ?? throw new NaoEncontradoException("Alerta");
        alerta.Encerrar(relogio.GetUtcNow().UtcDateTime);
        await unidade.SalvarAsync(ct);
        return NoContent();
    }
}
