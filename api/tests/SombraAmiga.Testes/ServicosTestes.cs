using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Servicos;
using SombraAmiga.Infra.Dados;
using SombraAmiga.Infra.Repositorios;

namespace SombraAmiga.Testes;

internal sealed class RelogioFixo(DateTime utc) : TimeProvider
{
    public DateTime Agora { get; set; } = utc;

    public override DateTimeOffset GetUtcNow() => new(Agora, TimeSpan.Zero);
}

/// <summary>Banco SQLite em memória, recriado a cada teste.</summary>
public abstract class TesteComBanco : IDisposable
{
    private readonly SqliteConnection _conexao = new("Data Source=:memory:");

    protected SombraAmigaContexto Contexto { get; }

    protected TesteComBanco()
    {
        _conexao.Open();
        var opcoes = new DbContextOptionsBuilder<SombraAmigaContexto>().UseSqlite(_conexao).Options;
        Contexto = new SombraAmigaContexto(opcoes);
        Contexto.Database.Migrate();
    }

    public void Dispose()
    {
        Contexto.Dispose();
        _conexao.Dispose();
        GC.SuppressFinalize(this);
    }
}

public class ServicoLeiturasTestes : TesteComBanco
{
    private readonly RelogioFixo _relogio = new(new DateTime(2026, 11, 6, 15, 0, 0, DateTimeKind.Utc));

    private ServicoLeituras CriarServico() => new(
        new RepositorioPontos(Contexto), new RepositorioLeituras(Contexto),
        new RepositorioAlertas(Contexto), Contexto, _relogio);

    [Fact]
    public async Task Leitura_de_risco_abre_um_unico_alerta()
    {
        var servico = CriarServico();

        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 38, 50);
        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 39, 50);

        var ativos = await new RepositorioAlertas(Contexto).ListarAtivosAsync();
        Assert.Single(ativos);
        Assert.Equal(OrigemAlerta.Sensor, ativos[0].Origem);
    }

    [Fact]
    public async Task Alerta_aberto_acompanha_o_agravamento_do_calor()
    {
        var servico = CriarServico();

        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 33, 50);
        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 38, 50);

        var alerta = Assert.Single(await new RepositorioAlertas(Contexto).ListarAtivosAsync());
        Assert.Equal(NivelRisco.Extremo, alerta.Nivel);
        Assert.Contains("extremo", alerta.Mensagem);
        Assert.Contains("48,6", alerta.Mensagem);
    }

    [Fact]
    public async Task Datas_voltam_do_banco_marcadas_como_utc()
    {
        var servico = CriarServico();
        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 38, 50);
        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 22, 50);
        Contexto.ChangeTracker.Clear();

        var alerta = await Contexto.Alertas.SingleAsync();

        Assert.Equal(DateTimeKind.Utc, alerta.CriadoEmUtc.Kind);
        Assert.Equal(DateTimeKind.Utc, alerta.EncerradoEmUtc!.Value.Kind);
    }

    [Fact]
    public async Task Leitura_amena_encerra_o_alerta_do_ponto()
    {
        var servico = CriarServico();

        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 38, 50);
        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 22, 50);

        Assert.Empty(await new RepositorioAlertas(Contexto).ListarAtivosAsync());
    }

    [Fact]
    public async Task Alertas_de_pontos_diferentes_sao_independentes()
    {
        var servico = CriarServico();

        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 38, 50);
        await servico.RegistrarAsync(PontosIniciais.PontoUbs, 38, 50);
        await servico.RegistrarAsync(PontosIniciais.PontoPraca, 22, 50);

        var ativos = await new RepositorioAlertas(Contexto).ListarAtivosAsync();
        Assert.Equal(PontosIniciais.PontoUbs, Assert.Single(ativos).PontoId);
    }

    [Fact]
    public async Task Ponto_inexistente_e_rejeitado() =>
        await Assert.ThrowsAsync<NaoEncontradoException>(() => CriarServico().RegistrarAsync(Guid.NewGuid(), 30, 50));
}

public class ServicoRiscoTestes : TesteComBanco
{
    private static readonly DateTime Agora = new(2026, 11, 6, 15, 0, 0, DateTimeKind.Utc);

    private ServicoRisco CriarServico() =>
        new(new RepositorioLeituras(Contexto), new RepositorioCidadaos(Contexto), new RelogioFixo(Agora));

    private async Task<Idoso> SalvarIdosoAsync()
    {
        var idoso = new Idoso("Lurdes", Cpf.Criar("52998224725"), "Filha", "Hipertensão");
        Contexto.Add(idoso);
        await Contexto.SaveChangesAsync();
        return idoso;
    }

    [Fact]
    public async Task Sem_leituras_recentes_informa_que_nao_ha_dados()
    {
        Contexto.Add(new LeituraSensor(PontosIniciais.PontoPraca, 38, 50, Agora.AddHours(-4)));
        await Contexto.SaveChangesAsync();

        var risco = await CriarServico().ObterAtualAsync(null);

        Assert.Null(risco.Nivel);
    }

    [Fact]
    public async Task Mesmo_calor_tem_risco_maior_para_idoso_com_condicao_de_saude()
    {
        var idoso = await SalvarIdosoAsync();
        Contexto.Add(new LeituraSensor(PontosIniciais.PontoPraca, 29, 50, Agora.AddHours(-1)));
        await Contexto.SaveChangesAsync();

        var geral = await CriarServico().ObterAtualAsync(null);
        var pessoal = await CriarServico().ObterAtualAsync(idoso.Id);

        Assert.Equal(NivelRisco.Atencao, geral.Nivel);
        Assert.Equal("Risco geral: atenção.", geral.Orientacao);
        Assert.Equal(NivelRisco.Alto, pessoal.Nivel);
        Assert.Equal(idoso.Orientar(NivelRisco.Alto), pessoal.Orientacao);
    }

    [Fact]
    public async Task Cidadao_inexistente_e_rejeitado() =>
        await Assert.ThrowsAsync<NaoEncontradoException>(() => CriarServico().ObterAtualAsync(Guid.NewGuid()));
}

public class ServicoIndicadoresTestes : TesteComBanco
{
    private static readonly DateTime Dia1 = new(2026, 11, 2, 15, 0, 0, DateTimeKind.Utc);
    private static readonly DateTime Dia2 = new(2026, 11, 3, 15, 0, 0, DateTimeKind.Utc);
    private static readonly DateTime DiaSemAlerta = new(2026, 11, 4, 15, 0, 0, DateTimeKind.Utc);

    private ServicoIndicadores CriarServico() => new(
        new RepositorioAlertas(Contexto), new RepositorioCheckIns(Contexto), new RepositorioCidadaos(Contexto));

    [Fact]
    public async Task Conta_cada_cidadao_uma_vez_por_dia_e_so_em_dias_de_alerta()
    {
        var a = new Idoso("A", Cpf.Criar("52998224725"), "Filha", null);
        var b = new Idoso("B", Cpf.Criar("11144477735"), "Filho", null);
        Contexto.AddRange(a, b);
        Contexto.AddRange(
            Alerta.DePrevisao(NivelRisco.Alto, "Calor", Dia1),
            Alerta.DePrevisao(NivelRisco.Alto, "Calor de novo", Dia1),
            Alerta.DePrevisao(NivelRisco.Alto, "Calor", Dia2));
        Contexto.AddRange(
            new CheckIn(a.Id, StatusCheckIn.EstouBem, Dia1),
            new CheckIn(a.Id, StatusCheckIn.EstouBem, Dia1.AddHours(2)),
            new CheckIn(b.Id, StatusCheckIn.PrecisoDeAjuda, Dia1),
            new CheckIn(a.Id, StatusCheckIn.EstouBem, DiaSemAlerta));
        await Contexto.SaveChangesAsync();

        var indicador = await CriarServico().CalcularAsync(new DateOnly(2026, 11, 1), new DateOnly(2026, 11, 30));

        Assert.Equal(new IndicadorImpacto(2, 4, 1, 25), indicador);
    }

    [Fact]
    public async Task Sem_alertas_o_percentual_e_zero()
    {
        var indicador = await CriarServico().CalcularAsync(new DateOnly(2026, 11, 1), new DateOnly(2026, 11, 30));

        Assert.Equal(0, indicador.PercentualConfirmado);
    }

    [Fact]
    public async Task Periodo_invertido_e_rejeitado() =>
        await Assert.ThrowsAsync<DominioException>(() =>
            CriarServico().CalcularAsync(new DateOnly(2026, 11, 30), new DateOnly(2026, 11, 1)));
}
