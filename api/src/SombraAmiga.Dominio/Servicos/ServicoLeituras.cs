using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Dominio.Servicos;

/// <summary>Registra leituras e abre ou encerra o alerta do ponto conforme o risco.</summary>
public sealed class ServicoLeituras(
    IRepositorioPontos pontos,
    IRepositorioLeituras leituras,
    IRepositorioAlertas alertas,
    IUnidadeDeTrabalho unidade,
    TimeProvider relogio)
{
    public async Task<LeituraSensor> RegistrarAsync(Guid pontoId, double temperaturaC, double umidadePct, CancellationToken ct = default)
    {
        var ponto = await pontos.ObterAsync(pontoId, ct) ?? throw new NaoEncontradoException("Ponto");
        var agora = relogio.GetUtcNow().UtcDateTime;
        var leitura = new LeituraSensor(ponto.Id, temperaturaC, umidadePct, agora);

        await leituras.AdicionarAsync(leitura, ct);

        var alertaAtivo = await alertas.ObterAtivoDoPontoAsync(ponto.Id, ct);
        var emRisco = leitura.Nivel >= NivelRisco.Alto;

        if (emRisco && alertaAtivo is null)
            await alertas.AdicionarAsync(Alerta.DeSensor(leitura, ponto), ct);
        else if (emRisco)
            alertaAtivo!.AtualizarComLeitura(leitura, ponto);
        else
            alertaAtivo?.Encerrar(agora);

        await unidade.SalvarAsync(ct);
        return leitura;
    }
}
