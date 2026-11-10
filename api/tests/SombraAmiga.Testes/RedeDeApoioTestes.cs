using System.Net;
using Microsoft.Extensions.Logging.Abstractions;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Servicos;
using SombraAmiga.Infra.RedeDeApoio;
using SombraAmiga.Infra.Repositorios;

namespace SombraAmiga.Testes;

internal sealed class RedeDeApoioFalsa : IRedeDeApoio
{
    public List<Guid> Pedidos { get; } = [];

    public Task SolicitarAjudaAsync(Guid cidadaoId, CancellationToken ct = default)
    {
        Pedidos.Add(cidadaoId);
        return Task.CompletedTask;
    }
}

public class ServicoCheckInsTestes : TesteComBanco
{
    private readonly RedeDeApoioFalsa _rede = new();

    private async Task<(ServicoCheckIns Servico, Guid CidadaoId)> PrepararAsync()
    {
        var idoso = new Idoso("Lurdes", Cpf.Criar("52998224725"), "Filha", null);
        Contexto.Add(idoso);
        await Contexto.SaveChangesAsync();
        var servico = new ServicoCheckIns(new RepositorioCidadaos(Contexto), new RepositorioCheckIns(Contexto),
            Contexto, _rede, new RelogioFixo(new DateTime(2026, 11, 10, 15, 0, 0, DateTimeKind.Utc)));
        return (servico, idoso.Id);
    }

    [Fact]
    public async Task Preciso_de_ajuda_abre_pedido_na_rede_de_apoio()
    {
        var (servico, cidadaoId) = await PrepararAsync();

        await servico.RegistrarAsync(cidadaoId, StatusCheckIn.PrecisoDeAjuda);

        Assert.Equal([cidadaoId], _rede.Pedidos);
    }

    [Fact]
    public async Task Estou_bem_nao_aciona_a_rede_de_apoio()
    {
        var (servico, cidadaoId) = await PrepararAsync();

        await servico.RegistrarAsync(cidadaoId, StatusCheckIn.EstouBem);

        Assert.Empty(_rede.Pedidos);
    }
}

public class ClienteRedeDeApoioTestes
{
    private sealed class ServidorFalso(Func<HttpRequestMessage, HttpResponseMessage> responder) : HttpMessageHandler
    {
        public HttpRequestMessage? Recebida { get; private set; }
        public string? Corpo { get; private set; }

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage requisicao, CancellationToken ct)
        {
            Recebida = requisicao;
            Corpo = requisicao.Content is null ? null : await requisicao.Content.ReadAsStringAsync(ct);
            return responder(requisicao);
        }
    }

    private static ClienteRedeDeApoio Criar(HttpMessageHandler servidor)
    {
        var http = new HttpClient(servidor) { BaseAddress = new Uri("http://rede.teste/") };
        http.DefaultRequestHeaders.Add(ClienteRedeDeApoio.CabecalhoChave, "chave-teste");
        return new ClienteRedeDeApoio(http, NullLogger<ClienteRedeDeApoio>.Instance);
    }

    [Fact]
    public async Task Envia_o_cidadao_com_a_chave_de_servico()
    {
        var servidor = new ServidorFalso(_ => new HttpResponseMessage(HttpStatusCode.Created));
        var cidadaoId = Guid.NewGuid();

        await Criar(servidor).SolicitarAjudaAsync(cidadaoId);

        Assert.Equal(HttpMethod.Post, servidor.Recebida!.Method);
        Assert.Equal("http://rede.teste/api/pedidos", servidor.Recebida.RequestUri!.ToString());
        Assert.Equal("chave-teste", servidor.Recebida.Headers.GetValues(ClienteRedeDeApoio.CabecalhoChave).Single());
        Assert.Contains(cidadaoId.ToString(), servidor.Corpo);
    }

    [Theory]
    [InlineData(HttpStatusCode.Conflict)]
    [InlineData(HttpStatusCode.ServiceUnavailable)]
    public async Task Resposta_de_erro_nao_lanca_excecao(HttpStatusCode status)
    {
        var servidor = new ServidorFalso(_ => new HttpResponseMessage(status));

        var erro = await Record.ExceptionAsync(() => Criar(servidor).SolicitarAjudaAsync(Guid.NewGuid()));

        Assert.Null(erro);
    }

    [Fact]
    public async Task Servico_fora_do_ar_nao_lanca_excecao()
    {
        var servidor = new ServidorFalso(_ => throw new HttpRequestException("conexão recusada"));

        var erro = await Record.ExceptionAsync(() => Criar(servidor).SolicitarAjudaAsync(Guid.NewGuid()));

        Assert.Null(erro);
    }
}
