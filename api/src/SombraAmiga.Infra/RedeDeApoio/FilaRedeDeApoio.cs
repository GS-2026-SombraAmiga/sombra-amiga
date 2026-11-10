using System.Threading.Channels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using SombraAmiga.Dominio.Servicos;

namespace SombraAmiga.Infra.RedeDeApoio;

/// <summary>
/// Fila em memória dos pedidos de ajuda. O check-in só coloca o pedido na fila e responde
/// na hora: o cidadão não espera a Rede de Apoio, nem quando ela está lenta ou fora do ar.
/// </summary>
public sealed class FilaRedeDeApoio : IRedeDeApoio
{
    private readonly Channel<Guid> _canal = Channel.CreateBounded<Guid>(
        new BoundedChannelOptions(1000) { FullMode = BoundedChannelFullMode.DropOldest });

    public ChannelReader<Guid> Leitor => _canal.Reader;

    public Task SolicitarAjudaAsync(Guid cidadaoId, CancellationToken ct = default)
    {
        _canal.Writer.TryWrite(cidadaoId);
        return Task.CompletedTask;
    }
}

/// <summary>Serviço em segundo plano que esvazia a fila e envia cada pedido à Rede de Apoio.</summary>
public sealed class EnvioRedeDeApoio(FilaRedeDeApoio fila, IServiceScopeFactory escopos) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken parar)
    {
        await foreach (var cidadaoId in fila.Leitor.ReadAllAsync(parar))
        {
            using var escopo = escopos.CreateScope();
            var cliente = escopo.ServiceProvider.GetRequiredService<ClienteRedeDeApoio>();
            await cliente.SolicitarAjudaAsync(cidadaoId, parar);
        }
    }
}
