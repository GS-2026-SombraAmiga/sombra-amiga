using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Dominio.Servicos;

public sealed record RiscoAtual(double? IndiceCalorC, NivelRisco? Nivel, string Orientacao);

/// <summary>Calcula o risco atual a partir das leituras recentes, ajustado ao perfil quando informado.</summary>
public sealed class ServicoRisco(IRepositorioLeituras leituras, IRepositorioCidadaos cidadaos, TimeProvider relogio)
{
    private static readonly TimeSpan JanelaRecente = TimeSpan.FromHours(3);

    public async Task<RiscoAtual> ObterAtualAsync(Guid? cidadaoId, CancellationToken ct = default)
    {
        var desde = relogio.GetUtcNow().UtcDateTime - JanelaRecente;
        var indice = await leituras.MaiorIndiceDesdeAsync(desde, ct);

        var cidadao = cidadaoId is null
            ? null
            : await cidadaos.ObterAsync(cidadaoId.Value, ct) ?? throw new NaoEncontradoException("Cidadão");

        if (indice is null)
            return new RiscoAtual(null, null, "Sem leituras recentes dos sensores.");

        if (cidadao is null)
        {
            var nivelGeral = ClassificadorRisco.Classificar(indice.Value);
            return new RiscoAtual(indice, nivelGeral, $"Risco geral: {ClassificadorRisco.Descrever(nivelGeral)}.");
        }

        var nivel = cidadao.AvaliarRisco(indice.Value);
        return new RiscoAtual(indice, nivel, cidadao.Orientar(nivel));
    }
}
