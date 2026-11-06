using Microsoft.AspNetCore.Mvc;
using SombraAmiga.Api.Contratos;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Repositorios;
using SombraAmiga.Dominio.Servicos;

namespace SombraAmiga.Api.Controllers;

/// <summary>Cadastro de idosos e trabalhadores de rua.</summary>
[ApiController]
[Route("api/cidadaos")]
public sealed class CidadaosController(
    ServicoCidadaos servico,
    IRepositorioCidadaos cidadaos,
    IRepositorioCheckIns checkIns,
    IUnidadeDeTrabalho unidade) : ControllerBase
{
    /// <summary>Cadastra um cidadão.</summary>
    [HttpPost]
    [ProducesResponseType<CidadaoResposta>(StatusCodes.Status201Created)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status409Conflict)]
    public async Task<IActionResult> Cadastrar(CadastrarCidadaoRequisicao requisicao, CancellationToken ct)
    {
        var dados = new DadosCadastro(
            requisicao.Perfil!.Value, requisicao.Nome, requisicao.Cpf,
            requisicao.ContatoFamiliar, requisicao.CondicaoSaude, requisicao.Ocupacao);

        var cidadao = await servico.CadastrarAsync(dados, ct);
        return CreatedAtAction(nameof(Obter), new { id = cidadao.Id }, CidadaoResposta.De(cidadao));
    }

    /// <summary>Lista os cidadãos, com CPF mascarado.</summary>
    [HttpGet]
    public async Task<IEnumerable<CidadaoResposta>> Listar(CancellationToken ct) =>
        (await cidadaos.ListarAsync(ct)).Select(CidadaoResposta.De);

    /// <summary>Busca um cidadão pelo identificador.</summary>
    [HttpGet("{id:guid}")]
    [ProducesResponseType<CidadaoResposta>(StatusCodes.Status200OK)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Obter(Guid id, CancellationToken ct)
    {
        var cidadao = await cidadaos.ObterAsync(id, ct) ?? throw new NaoEncontradoException("Cidadão");
        return Ok(CidadaoResposta.De(cidadao));
    }

    /// <summary>Atualiza nome, contato e condição de saúde.</summary>
    [HttpPut("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Atualizar(Guid id, AtualizarCidadaoRequisicao requisicao, CancellationToken ct)
    {
        var cidadao = await cidadaos.ObterAsync(id, ct) ?? throw new NaoEncontradoException("Cidadão");
        cidadao.AtualizarDados(requisicao.Nome, requisicao.ContatoFamiliar, requisicao.CondicaoSaude);
        await unidade.SalvarAsync(ct);
        return NoContent();
    }

    /// <summary>Remove o cidadão e os check-ins dele.</summary>
    [HttpDelete("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ProblemDetails>(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Remover(Guid id, CancellationToken ct)
    {
        var cidadao = await cidadaos.ObterAsync(id, ct) ?? throw new NaoEncontradoException("Cidadão");
        cidadaos.Remover(cidadao);
        await unidade.SalvarAsync(ct);
        return NoContent();
    }

    /// <summary>Lista os check-ins do cidadão, do mais recente ao mais antigo.</summary>
    [HttpGet("{id:guid}/checkins")]
    public async Task<IEnumerable<CheckInResposta>> ListarCheckIns(Guid id, CancellationToken ct) =>
        (await checkIns.ListarDoCidadaoAsync(id, ct)).Select(CheckInResposta.De);
}
