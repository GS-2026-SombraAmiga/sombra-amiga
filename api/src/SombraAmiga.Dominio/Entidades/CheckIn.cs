using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Dominio.Entidades;

public sealed class CheckIn : Entidade
{
    public Guid CidadaoId { get; private set; }
    public StatusCheckIn Status { get; private set; }
    public DateTime DataHoraUtc { get; private set; }
    public DateOnly DiaLocal { get; private set; }

    private CheckIn() { }

    public CheckIn(Guid cidadaoId, StatusCheckIn status, DateTime agoraUtc)
    {
        CidadaoId = cidadaoId;
        Status = status;
        DataHoraUtc = agoraUtc;
        DiaLocal = Fuso.DiaLocal(agoraUtc);
    }
}
