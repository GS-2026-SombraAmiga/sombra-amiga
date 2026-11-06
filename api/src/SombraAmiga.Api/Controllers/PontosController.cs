using Microsoft.AspNetCore.Mvc;
using SombraAmiga.Api.Contratos;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Api.Controllers;

/// <summary>Pontos de sombra e hidratação.</summary>
[ApiController]
[Route("api/pontos")]
public sealed class PontosController(IRepositorioPontos pontos, IUnidadeDeTrabalho unidade) : ControllerBase
{
    /// <summary>Lista os pontos ativos.</summary>
    [HttpGet]
    public async Task<IEnumerable<PontoResposta>> Listar(CancellationToken ct) =>
        (await pontos.ListarAtivosAsync(ct)).Select(p => PontoResposta.De(p));

    /// <summary>Lista os pontos ativos dentro do raio, do mais próximo ao mais distante.</summary>
    [HttpGet("proximos")]
    public async Task<IEnumerable<PontoResposta>> Proximos(
        [FromQuery] double latitude, [FromQuery] double longitude, [FromQuery] double raioKm = 2, CancellationToken ct = default) =>
        (await pontos.ListarAtivosAsync(ct))
            .Select(p => new { Ponto = p, Distancia = p.DistanciaKm(latitude, longitude) })
            .Where(x => x.Distancia <= raioKm)
            .OrderBy(x => x.Distancia)
            .Select(x => PontoResposta.De(x.Ponto, Math.Round(x.Distancia, 2)));

    /// <summary>Cadastra um ponto.</summary>
    [HttpPost]
    [ProducesResponseType<PontoResposta>(StatusCodes.Status201Created)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Cadastrar(PontoRequisicao requisicao, CancellationToken ct)
    {
        var ponto = new PontoHidratacao(requisicao.Nome, requisicao.Tipo!.Value, requisicao.Latitude!.Value, requisicao.Longitude!.Value);
        await pontos.AdicionarAsync(ponto, ct);
        await unidade.SalvarAsync(ct);
        return Created($"/api/pontos/{ponto.Id}", PontoResposta.De(ponto));
    }

    /// <summary>Atualiza um ponto.</summary>
    [HttpPut("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Atualizar(Guid id, PontoRequisicao requisicao, CancellationToken ct)
    {
        var ponto = await pontos.ObterAsync(id, ct) ?? throw new NaoEncontradoException("Ponto");
        ponto.Atualizar(requisicao.Nome, requisicao.Tipo!.Value, requisicao.Latitude!.Value, requisicao.Longitude!.Value);
        await unidade.SalvarAsync(ct);
        return NoContent();
    }

    /// <summary>Desativa um ponto e mantém o histórico de leituras.</summary>
    [HttpDelete("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Desativar(Guid id, CancellationToken ct)
    {
        var ponto = await pontos.ObterAsync(id, ct) ?? throw new NaoEncontradoException("Ponto");
        ponto.Desativar();
        await unidade.SalvarAsync(ct);
        return NoContent();
    }
}
