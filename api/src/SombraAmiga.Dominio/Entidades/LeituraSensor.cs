using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Dominio.Entidades;

public sealed class LeituraSensor : Entidade
{
    public Guid PontoId { get; private set; }
    public double TemperaturaC { get; private set; }
    public double UmidadePct { get; private set; }
    public double IndiceCalorC { get; private set; }
    public NivelRisco Nivel { get; private set; }
    public DateTime DataHoraUtc { get; private set; }

    private LeituraSensor() { }

    public LeituraSensor(Guid pontoId, double temperaturaC, double umidadePct, DateTime dataHoraUtc)
    {
        if (temperaturaC is < -10 or > 60)
            throw new DominioException("Temperatura fora da faixa do sensor.");
        if (umidadePct is < 0 or > 100)
            throw new DominioException("Umidade deve estar entre 0 e 100.");

        PontoId = pontoId;
        TemperaturaC = temperaturaC;
        UmidadePct = umidadePct;
        IndiceCalorC = CalculadoraIndiceCalor.Calcular(temperaturaC, umidadePct);
        Nivel = ClassificadorRisco.Classificar(IndiceCalorC);
        DataHoraUtc = dataHoraUtc;
    }
}
