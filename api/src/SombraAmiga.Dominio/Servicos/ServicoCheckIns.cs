using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Dominio.Servicos;

public sealed class ServicoCheckIns(
    IRepositorioCidadaos cidadaos,
    IRepositorioCheckIns checkIns,
    IUnidadeDeTrabalho unidade,
    IRedeDeApoio redeDeApoio,
    TimeProvider relogio)
{
    public async Task<CheckIn> RegistrarAsync(Guid cidadaoId, StatusCheckIn status, CancellationToken ct = default)
    {
        _ = await cidadaos.ObterAsync(cidadaoId, ct) ?? throw new NaoEncontradoException("Cidadão");

        var checkIn = new CheckIn(cidadaoId, status, relogio.GetUtcNow().UtcDateTime);
        await checkIns.AdicionarAsync(checkIn, ct);
        await unidade.SalvarAsync(ct);

        // O check-in já está salvo: a Rede de Apoio é avisada depois e nunca o desfaz.
        if (status == StatusCheckIn.PrecisoDeAjuda)
            await redeDeApoio.SolicitarAjudaAsync(cidadaoId, ct);

        return checkIn;
    }
}
