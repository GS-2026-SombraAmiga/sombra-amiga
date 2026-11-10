using System.Net;
using System.Net.Http.Json;
using Microsoft.Extensions.Logging;
using SombraAmiga.Dominio.Servicos;

namespace SombraAmiga.Infra.RedeDeApoio;

/// <summary>Abre o pedido de ajuda no serviço Java (POST /api/pedidos), autenticado pela chave de serviço.</summary>
public sealed class ClienteRedeDeApoio(HttpClient http, ILogger<ClienteRedeDeApoio> log) : IRedeDeApoio
{
    public const string CabecalhoChave = "X-Chave-Servico";

    public async Task SolicitarAjudaAsync(Guid cidadaoId, CancellationToken ct = default)
    {
        try
        {
            using var resposta = await http.PostAsJsonAsync("api/pedidos", new { cidadaoId }, ct);

            if (resposta.IsSuccessStatusCode)
                log.LogInformation("Pedido de ajuda aberto na Rede de Apoio.");
            else if (resposta.StatusCode == HttpStatusCode.Conflict)
                log.LogInformation("A Rede de Apoio já tinha um pedido em andamento para este cidadão.");
            else
                log.LogWarning("A Rede de Apoio recusou o pedido de ajuda: HTTP {Status}.", (int)resposta.StatusCode);
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException)
        {
            log.LogWarning("Rede de Apoio indisponível; o check-in foi salvo, mas o pedido não foi aberto: {Erro}", ex.Message);
        }
    }
}

/// <summary>Usada quando a URL da Rede de Apoio não está configurada, como nos testes.</summary>
public sealed class RedeDeApoioDesativada : IRedeDeApoio
{
    public Task SolicitarAjudaAsync(Guid cidadaoId, CancellationToken ct = default) => Task.CompletedTask;
}

public sealed record ConfiguracaoRedeDeApoio(string? Url, string? Chave);
