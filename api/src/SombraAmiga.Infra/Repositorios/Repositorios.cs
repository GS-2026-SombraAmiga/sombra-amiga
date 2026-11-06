using Microsoft.EntityFrameworkCore;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Repositorios;
using SombraAmiga.Infra.Dados;

namespace SombraAmiga.Infra.Repositorios;

public abstract class RepositorioBase<T>(SombraAmigaContexto contexto) : IRepositorio<T> where T : Entidade
{
    protected DbSet<T> Conjunto { get; } = contexto.Set<T>();

    public Task<T?> ObterAsync(Guid id, CancellationToken ct = default) =>
        Conjunto.FirstOrDefaultAsync(e => e.Id == id, ct);

    public async Task<IReadOnlyList<T>> ListarAsync(CancellationToken ct = default) =>
        await Conjunto.AsNoTracking().ToListAsync(ct);

    public async Task AdicionarAsync(T entidade, CancellationToken ct = default) =>
        await Conjunto.AddAsync(entidade, ct);

    public void Remover(T entidade) => Conjunto.Remove(entidade);
}

public sealed class RepositorioCidadaos(SombraAmigaContexto contexto)
    : RepositorioBase<Cidadao>(contexto), IRepositorioCidadaos
{
    public Task<bool> ExisteCpfAsync(Cpf cpf, CancellationToken ct = default) =>
        Conjunto.AnyAsync(c => c.Cpf == cpf, ct);

    public Task<int> ContarAsync(CancellationToken ct = default) => Conjunto.CountAsync(ct);
}

public sealed class RepositorioPontos(SombraAmigaContexto contexto)
    : RepositorioBase<PontoHidratacao>(contexto), IRepositorioPontos
{
    public async Task<IReadOnlyList<PontoHidratacao>> ListarAtivosAsync(CancellationToken ct = default) =>
        await Conjunto.AsNoTracking().Where(p => p.Ativo).OrderBy(p => p.Nome).ToListAsync(ct);
}

public sealed class RepositorioLeituras(SombraAmigaContexto contexto)
    : RepositorioBase<LeituraSensor>(contexto), IRepositorioLeituras
{
    public async Task<IReadOnlyList<LeituraSensor>> ListarDoPontoAsync(Guid pontoId, int limite, CancellationToken ct = default) =>
        await Conjunto.AsNoTracking()
            .Where(l => l.PontoId == pontoId)
            .OrderByDescending(l => l.DataHoraUtc)
            .Take(limite)
            .ToListAsync(ct);

    public Task<double?> MaiorIndiceDesdeAsync(DateTime desdeUtc, CancellationToken ct = default) =>
        Conjunto.Where(l => l.DataHoraUtc >= desdeUtc).MaxAsync(l => (double?)l.IndiceCalorC, ct);
}

public sealed class RepositorioAlertas(SombraAmigaContexto contexto)
    : RepositorioBase<Alerta>(contexto), IRepositorioAlertas
{
    public async Task<IReadOnlyList<Alerta>> ListarAtivosAsync(CancellationToken ct = default) =>
        await Conjunto.AsNoTracking()
            .Where(a => a.EncerradoEmUtc == null)
            .OrderByDescending(a => a.CriadoEmUtc)
            .ToListAsync(ct);

    public Task<Alerta?> ObterAtivoDoPontoAsync(Guid pontoId, CancellationToken ct = default) =>
        Conjunto.FirstOrDefaultAsync(a => a.PontoId == pontoId && a.EncerradoEmUtc == null, ct);

    public async Task<IReadOnlyList<DateOnly>> ListarDiasComAlertaAsync(DateOnly inicio, DateOnly fim, CancellationToken ct = default) =>
        await Conjunto.AsNoTracking()
            .Where(a => a.DiaLocal >= inicio && a.DiaLocal <= fim)
            .Select(a => a.DiaLocal)
            .Distinct()
            .OrderBy(d => d)
            .ToListAsync(ct);
}

public sealed class RepositorioCheckIns(SombraAmigaContexto contexto)
    : RepositorioBase<CheckIn>(contexto), IRepositorioCheckIns
{
    public async Task<IReadOnlyList<CheckIn>> ListarDoCidadaoAsync(Guid cidadaoId, CancellationToken ct = default) =>
        await Conjunto.AsNoTracking()
            .Where(c => c.CidadaoId == cidadaoId)
            .OrderByDescending(c => c.DataHoraUtc)
            .ToListAsync(ct);

    /// <summary>Conta cada cidadão uma vez por dia, mesmo com vários check-ins no mesmo dia.</summary>
    public Task<int> ContarConfirmadosAsync(IReadOnlyCollection<DateOnly> dias, CancellationToken ct = default) =>
        Conjunto
            .Where(c => c.Status == StatusCheckIn.EstouBem && dias.Contains(c.DiaLocal))
            .Select(c => new { c.CidadaoId, c.DiaLocal })
            .Distinct()
            .CountAsync(ct);
}
