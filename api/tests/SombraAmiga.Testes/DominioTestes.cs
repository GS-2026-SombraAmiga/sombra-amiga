using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;

namespace SombraAmiga.Testes;

public class CpfTestes
{
    [Theory]
    [InlineData("52998224725")]
    [InlineData("529.982.247-25")]
    public void Aceita_cpf_valido_com_ou_sem_pontuacao(string valor) =>
        Assert.Equal("52998224725", Cpf.Criar(valor).Numero);

    [Theory]
    [InlineData("")]
    [InlineData("123")]
    [InlineData("11111111111")]
    [InlineData("52998224724")]
    public void Rejeita_cpf_invalido(string valor) =>
        Assert.Throws<DominioException>(() => Cpf.Criar(valor));

    [Fact]
    public void ToString_nao_expoe_o_numero_completo()
    {
        var cpf = Cpf.Criar("52998224725");

        Assert.Equal("***.***.***-25", cpf.ToString());
        Assert.DoesNotContain("529982247", $"{cpf}");
    }
}

public class IndiceCalorTestes
{
    [Fact]
    public void Dia_quente_usa_a_formula_completa() =>
        Assert.InRange(CalculadoraIndiceCalor.Calcular(35, 50), 40, 41.5);

    [Fact]
    public void Temperatura_amena_usa_a_formula_simples() =>
        Assert.InRange(CalculadoraIndiceCalor.Calcular(20, 50), 19, 21);
}

public class ClassificadorRiscoTestes
{
    [Theory]
    [InlineData(26.9, NivelRisco.Baixo)]
    [InlineData(27, NivelRisco.Atencao)]
    [InlineData(32, NivelRisco.Alto)]
    [InlineData(41, NivelRisco.Extremo)]
    public void Classifica_nos_limites_das_faixas(double indice, NivelRisco esperado) =>
        Assert.Equal(esperado, ClassificadorRisco.Classificar(indice));
}

public class CidadaoTestes
{
    private static readonly Cpf CpfValido = Cpf.Criar("52998224725");

    [Fact]
    public void Idoso_entra_em_risco_antes_do_trabalhador()
    {
        Cidadao idoso = new Idoso("Lurdes", CpfValido, "Filha", null);
        Cidadao trabalhador = new TrabalhadorDeRua("Rafael", CpfValido, "Irmão", null, "Entregador");

        Assert.Equal(NivelRisco.Alto, idoso.AvaliarRisco(29));
        Assert.Equal(NivelRisco.Atencao, trabalhador.AvaliarRisco(29));
    }

    [Fact]
    public void Condicao_de_saude_aumenta_a_sensibilidade()
    {
        var semCondicao = new Idoso("Lurdes", CpfValido, "Filha", null);
        var comCondicao = new Idoso("Lurdes", CpfValido, "Filha", "Hipertensão");

        Assert.Equal(NivelRisco.Atencao, semCondicao.AvaliarRisco(28));
        Assert.Equal(NivelRisco.Alto, comCondicao.AvaliarRisco(28));
    }

    [Fact]
    public void Cada_perfil_recebe_a_propria_orientacao()
    {
        Cidadao idoso = new Idoso("Lurdes", CpfValido, "Filha", null);
        Cidadao trabalhador = new TrabalhadorDeRua("Rafael", CpfValido, "Irmão", null, "Entregador");

        Assert.NotEqual(idoso.Orientar(NivelRisco.Alto), trabalhador.Orientar(NivelRisco.Alto));
    }

    [Fact]
    public void Trabalhador_exige_ocupacao() =>
        Assert.Throws<DominioException>(() => new TrabalhadorDeRua("Rafael", CpfValido, "Irmão", null, " "));

    [Fact]
    public void Nome_em_branco_e_rejeitado() =>
        Assert.Throws<DominioException>(() => new Idoso(" ", CpfValido, "Filha", null));
}

public class PontoHidratacaoTestes
{
    [Fact]
    public void Calcula_distancia_conhecida()
    {
        var ponto = new PontoHidratacao("Teste", TipoPonto.Agua, -23.5, -46.6);

        Assert.InRange(ponto.DistanciaKm(-23.6, -46.6), 11, 11.3);
    }

    [Fact]
    public void Rejeita_coordenada_invalida() =>
        Assert.Throws<DominioException>(() => new PontoHidratacao("Teste", TipoPonto.Agua, -91, 0));
}

public class LeituraSensorTestes
{
    [Theory]
    [InlineData(61, 50)]
    [InlineData(30, 101)]
    public void Rejeita_valores_fora_da_faixa(double temperatura, double umidade) =>
        Assert.Throws<DominioException>(() => new LeituraSensor(Guid.NewGuid(), temperatura, umidade, DateTime.UtcNow));
}

public class FusoTestes
{
    [Fact]
    public void Madrugada_em_utc_ainda_e_o_dia_anterior_em_sao_paulo() =>
        Assert.Equal(new DateOnly(2026, 11, 6), Fuso.DiaLocal(new DateTime(2026, 11, 7, 1, 0, 0, DateTimeKind.Utc)));
}

public class AlertaTestes
{
    [Fact]
    public void Nao_encerra_duas_vezes()
    {
        var alerta = Alerta.DePrevisao(NivelRisco.Alto, "Calor amanhã", DateTime.UtcNow);
        alerta.Encerrar(DateTime.UtcNow);

        Assert.False(alerta.Ativo);
        Assert.Throws<DominioException>(() => alerta.Encerrar(DateTime.UtcNow));
    }
}
