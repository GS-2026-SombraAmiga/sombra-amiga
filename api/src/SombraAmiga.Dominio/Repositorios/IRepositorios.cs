using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;

namespace SombraAmiga.Dominio.Repositorios;

public interface IRepositorio<T> where T : Entidade
{
    Task<T?> ObterAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<T>> ListarAsync(CancellationToken ct = default);
    Task AdicionarAsync(T entidade, CancellationToken ct = default);
    void Remover(T entidade);
}

public interface IRepositorioCidadaos : IRepositorio<Cidadao>
{
    Task<bool> ExisteCpfAsync(Cpf cpf, CancellationToken ct = default);
    Task<int> ContarAsync(CancellationToken ct = default);
}

public interface IRepositorioPontos : IRepositorio<PontoHidratacao>
{
    Task<IReadOnlyList<PontoHidratacao>> ListarAtivosAsync(CancellationToken ct = default);
}

public interface IRepositorioLeituras : IRepositorio<LeituraSensor>
{
    Task<IReadOnlyList<LeituraSensor>> ListarDoPontoAsync(Guid pontoId, int limite, CancellationToken ct = default);
    Task<double?> MaiorIndiceDesdeAsync(DateTime desdeUtc, CancellationToken ct = default);
}

public interface IRepositorioAlertas : IRepositorio<Alerta>
{
    Task<IReadOnlyList<Alerta>> ListarAtivosAsync(CancellationToken ct = default);
    Task<Alerta?> ObterAtivoDoPontoAsync(Guid pontoId, CancellationToken ct = default);
    Task<IReadOnlyList<DateOnly>> ListarDiasComAlertaAsync(DateOnly inicio, DateOnly fim, CancellationToken ct = default);
}

public interface IRepositorioCheckIns : IRepositorio<CheckIn>
{
    Task<IReadOnlyList<CheckIn>> ListarDoCidadaoAsync(Guid cidadaoId, CancellationToken ct = default);
    Task<int> ContarConfirmadosAsync(IReadOnlyCollection<DateOnly> dias, CancellationToken ct = default);
}

public interface IUnidadeDeTrabalho
{
    Task SalvarAsync(CancellationToken ct = default);
}
