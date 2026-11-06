using System.Globalization;
using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Dominio.Entidades;

public sealed class Alerta : Entidade
{
    public NivelRisco Nivel { get; private set; }
    public OrigemAlerta Origem { get; private set; }
    public string Mensagem { get; private set; } = null!;
    public Guid? PontoId { get; private set; }
    public DateTime CriadoEmUtc { get; private set; }
    public DateOnly DiaLocal { get; private set; }
    public DateTime? EncerradoEmUtc { get; private set; }

    public bool Ativo => EncerradoEmUtc is null;

    private Alerta() { }

    private Alerta(NivelRisco nivel, OrigemAlerta origem, string mensagem, Guid? pontoId, DateTime agoraUtc)
    {
        Nivel = nivel;
        Origem = origem;
        Mensagem = mensagem;
        PontoId = pontoId;
        CriadoEmUtc = agoraUtc;
        DiaLocal = Fuso.DiaLocal(agoraUtc);
    }

    public static Alerta DeSensor(LeituraSensor leitura, PontoHidratacao ponto) => new(
        leitura.Nivel,
        OrigemAlerta.Sensor,
        MensagemDoSensor(leitura, ponto),
        ponto.Id,
        leitura.DataHoraUtc);

    /// <summary>Mantém o alerta aberto com o nível e a sensação da leitura mais recente.</summary>
    public void AtualizarComLeitura(LeituraSensor leitura, PontoHidratacao ponto)
    {
        Nivel = leitura.Nivel;
        Mensagem = MensagemDoSensor(leitura, ponto);
    }

    private static string MensagemDoSensor(LeituraSensor leitura, PontoHidratacao ponto) =>
        $"Calor {ClassificadorRisco.Descrever(leitura.Nivel)} em {ponto.Nome}: sensação de {leitura.IndiceCalorC.ToString("F1", CultureInfo.GetCultureInfo("pt-BR"))} °C.";

    public static Alerta DePrevisao(NivelRisco nivel, string mensagem, DateTime agoraUtc)
    {
        if (string.IsNullOrWhiteSpace(mensagem))
            throw new DominioException("Mensagem é obrigatória.");
        return new Alerta(nivel, OrigemAlerta.Previsao, mensagem.Trim(), null, agoraUtc);
    }

    public void Encerrar(DateTime agoraUtc)
    {
        if (!Ativo)
            throw new DominioException("Alerta já encerrado.");
        EncerradoEmUtc = agoraUtc;
    }
}
