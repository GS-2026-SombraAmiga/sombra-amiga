using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using SombraAmiga.Infra.Dados;

namespace SombraAmiga.Testes;

/// <summary>Sobe a API real com um banco SQLite temporário.</summary>
public sealed class ApiFabrica : WebApplicationFactory<Program>
{
    private readonly string _arquivo = Path.Combine(Path.GetTempPath(), $"sombra-testes-{Guid.NewGuid()}.db");

    protected override void ConfigureWebHost(IWebHostBuilder builder) =>
        builder.UseSetting("ConnectionStrings:Padrao", $"Data Source={_arquivo}");

    protected override void Dispose(bool disposing)
    {
        base.Dispose(disposing);
        SqliteConnection.ClearAllPools();
        File.Delete(_arquivo);
    }
}

public class ApiTestes(ApiFabrica fabrica) : IClassFixture<ApiFabrica>
{
    private readonly HttpClient _cliente = fabrica.CreateClient();

    private static object Idoso(string cpf) => new
    {
        perfil = "Idoso",
        nome = "Lurdes Teste",
        cpf,
        contatoFamiliar = "Contato Teste",
        condicaoSaude = "Hipertensão",
    };

    [Fact]
    public async Task Cadastro_nao_devolve_cpf_completo_contato_nem_condicao_de_saude()
    {
        var resposta = await _cliente.PostAsJsonAsync("/api/cidadaos", Idoso("52998224725"));
        var corpo = await resposta.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.Created, resposta.StatusCode);
        Assert.Contains("***.***.***-25", corpo);
        Assert.DoesNotContain("52998224725", corpo);
        Assert.DoesNotContain("Hipertensão", corpo);
        Assert.DoesNotContain("Contato Teste", corpo);

        var lista = await _cliente.GetStringAsync("/api/cidadaos");
        Assert.DoesNotContain("52998224725", lista);
        Assert.DoesNotContain("Hipertensão", lista);
    }

    [Fact]
    public async Task Cpf_duplicado_retorna_409()
    {
        await _cliente.PostAsJsonAsync("/api/cidadaos", Idoso("11144477735"));

        var resposta = await _cliente.PostAsJsonAsync("/api/cidadaos", Idoso("111.444.777-35"));

        Assert.Equal(HttpStatusCode.Conflict, resposta.StatusCode);
    }

    [Fact]
    public async Task Erro_de_cpf_invalido_nao_repete_o_valor_enviado()
    {
        var resposta = await _cliente.PostAsJsonAsync("/api/cidadaos", Idoso("12345678900"));
        var corpo = await resposta.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.BadRequest, resposta.StatusCode);
        Assert.DoesNotContain("12345678900", corpo);
    }

    [Fact]
    public async Task Campo_obrigatorio_ausente_retorna_400()
    {
        var resposta = await _cliente.PostAsJsonAsync("/api/cidadaos", new { perfil = "Idoso", cpf = "52998224725" });

        Assert.Equal(HttpStatusCode.BadRequest, resposta.StatusCode);
    }

    [Fact]
    public async Task Ciclo_de_atualizar_e_remover_cidadao()
    {
        var criado = await _cliente.PostAsJsonAsync("/api/cidadaos", new
        {
            perfil = "TrabalhadorDeRua",
            nome = "Rafael Teste",
            cpf = "86288366757",
            contatoFamiliar = "Contato",
            ocupacao = "Entregador",
        });
        var id = (await criado.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetGuid();

        var atualizado = await _cliente.PutAsJsonAsync($"/api/cidadaos/{id}", new { nome = "Rafael Novo", contatoFamiliar = "Contato" });
        var checkIn = await _cliente.PostAsJsonAsync("/api/checkins", new { cidadaoId = id, status = "EstouBem" });
        var checkIns = await _cliente.GetFromJsonAsync<JsonElement>($"/api/cidadaos/{id}/checkins");
        var removido = await _cliente.DeleteAsync($"/api/cidadaos/{id}");
        var busca = await _cliente.GetAsync($"/api/cidadaos/{id}");

        Assert.Equal(HttpStatusCode.NoContent, atualizado.StatusCode);
        Assert.Equal(HttpStatusCode.Created, checkIn.StatusCode);
        Assert.Equal(1, checkIns.GetArrayLength());
        Assert.Equal(HttpStatusCode.NoContent, removido.StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, busca.StatusCode);
    }

    [Fact]
    public async Task Check_in_de_cidadao_inexistente_retorna_404()
    {
        var resposta = await _cliente.PostAsJsonAsync("/api/checkins", new { cidadaoId = Guid.NewGuid(), status = "EstouBem" });

        Assert.Equal(HttpStatusCode.NotFound, resposta.StatusCode);
    }

    [Fact]
    public async Task Leitura_extrema_aparece_nos_alertas_ativos()
    {
        var resposta = await _cliente.PostAsJsonAsync("/api/leituras", new
        {
            pontoId = PontosIniciais.PontoTerminal,
            temperaturaC = 38.0,
            umidadePct = 50.0,
        });
        var ativos = await _cliente.GetStringAsync("/api/alertas/ativos");

        Assert.Equal(HttpStatusCode.Created, resposta.StatusCode);
        Assert.Contains("Abrigo do Terminal", ativos);

        var alerta = JsonDocument.Parse(ativos).RootElement.EnumerateArray()
            .First(a => a.GetProperty("mensagem").GetString()!.Contains("Abrigo do Terminal"));
        Assert.EndsWith("Z", alerta.GetProperty("criadoEmUtc").GetString());
    }

    [Theory]
    [InlineData(38, 150, HttpStatusCode.BadRequest)]
    [InlineData(99, 50, HttpStatusCode.BadRequest)]
    public async Task Leitura_invalida_e_rejeitada(double temperatura, double umidade, HttpStatusCode esperado)
    {
        var resposta = await _cliente.PostAsJsonAsync("/api/leituras", new
        {
            pontoId = PontosIniciais.PontoUbs,
            temperaturaC = temperatura,
            umidadePct = umidade,
        });

        Assert.Equal(esperado, resposta.StatusCode);
    }

    [Fact]
    public async Task Leitura_de_ponto_inexistente_retorna_404()
    {
        var resposta = await _cliente.PostAsJsonAsync("/api/leituras", new { pontoId = Guid.NewGuid(), temperaturaC = 30.0, umidadePct = 50.0 });

        Assert.Equal(HttpStatusCode.NotFound, resposta.StatusCode);
    }

    [Fact]
    public async Task Pontos_proximos_vem_ordenados_pela_distancia()
    {
        var pontos = await _cliente.GetFromJsonAsync<JsonElement>("/api/pontos/proximos?latitude=-23.4620&longitude=-46.6810&raioKm=5");

        var distancias = pontos.EnumerateArray().Select(p => p.GetProperty("distanciaKm").GetDouble()).ToList();
        Assert.Equal(3, distancias.Count);
        Assert.Equal(distancias.Order(), distancias);
        Assert.Equal(0, distancias[0]);
    }

    [Fact]
    public async Task Previsao_publicada_pode_ser_encerrada()
    {
        var criado = await _cliente.PostAsJsonAsync("/api/alertas/previsao", new { nivel = "Alto", mensagem = "Amanhã deve passar de 32 °C." });
        var id = (await criado.Content.ReadFromJsonAsync<JsonElement>()).GetProperty("id").GetGuid();

        var primeiro = await _cliente.PostAsync($"/api/alertas/{id}/encerrar", null);
        var segundo = await _cliente.PostAsync($"/api/alertas/{id}/encerrar", null);

        Assert.Equal(HttpStatusCode.NoContent, primeiro.StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, segundo.StatusCode);
    }

    [Fact]
    public async Task Indicador_com_periodo_invertido_retorna_400()
    {
        var resposta = await _cliente.GetAsync("/api/indicadores/impacto?inicio=2026-11-30&fim=2026-11-01");

        Assert.Equal(HttpStatusCode.BadRequest, resposta.StatusCode);
    }

    [Fact]
    public async Task Swagger_documenta_os_endpoints()
    {
        var documento = await _cliente.GetStringAsync("/swagger/v1/swagger.json");

        Assert.Contains("/api/leituras", documento);
        Assert.Contains("Registra uma leitura", documento);
    }
}
