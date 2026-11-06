using Microsoft.EntityFrameworkCore;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Infra.Dados;

public sealed class SombraAmigaContexto(DbContextOptions<SombraAmigaContexto> opcoes)
    : DbContext(opcoes), IUnidadeDeTrabalho
{
    public DbSet<Cidadao> Cidadaos => Set<Cidadao>();
    public DbSet<PontoHidratacao> Pontos => Set<PontoHidratacao>();
    public DbSet<LeituraSensor> Leituras => Set<LeituraSensor>();
    public DbSet<Alerta> Alertas => Set<Alerta>();
    public DbSet<CheckIn> CheckIns => Set<CheckIn>();

    public Task SalvarAsync(CancellationToken ct = default) => SaveChangesAsync(ct);

    protected override void ConfigureConventions(ModelConfigurationBuilder configuracao)
    {
        configuracao.Properties<DateTime>().HaveConversion<DataUtcConverter>();
        configuracao.Properties<NivelRisco>().HaveConversion<string>();
        configuracao.Properties<TipoPonto>().HaveConversion<string>();
        configuracao.Properties<StatusCheckIn>().HaveConversion<string>();
        configuracao.Properties<OrigemAlerta>().HaveConversion<string>();
    }

    protected override void OnModelCreating(ModelBuilder modelo)
    {
        modelo.Entity<Cidadao>(e =>
        {
            e.ToTable("Cidadaos");
            e.HasDiscriminator<string>("Tipo")
                .HasValue<Idoso>(nameof(Idoso))
                .HasValue<TrabalhadorDeRua>(nameof(TrabalhadorDeRua));
            e.Property(c => c.Nome).HasMaxLength(120).IsRequired();
            e.Property(c => c.ContatoFamiliar).HasMaxLength(120).IsRequired();
            e.Property(c => c.CondicaoSaude).HasMaxLength(250);
            e.Property(c => c.Cpf)
                .HasConversion(cpf => cpf.Numero, numero => Cpf.Criar(numero))
                .HasMaxLength(11)
                .IsRequired();
            e.HasIndex(c => c.Cpf).IsUnique();
        });

        modelo.Entity<TrabalhadorDeRua>().Property(t => t.Ocupacao).HasMaxLength(80);

        modelo.Entity<PontoHidratacao>(e =>
        {
            e.ToTable("Pontos");
            e.Property(p => p.Nome).HasMaxLength(120).IsRequired();
            e.HasData(PontosIniciais.Todos);
        });

        modelo.Entity<LeituraSensor>(e =>
        {
            e.ToTable("Leituras");
            e.HasOne<PontoHidratacao>().WithMany().HasForeignKey(l => l.PontoId).OnDelete(DeleteBehavior.Restrict);
            e.HasIndex(l => new { l.PontoId, l.DataHoraUtc });
        });

        modelo.Entity<Alerta>(e =>
        {
            e.ToTable("Alertas");
            e.Property(a => a.Mensagem).HasMaxLength(300).IsRequired();
            e.HasOne<PontoHidratacao>().WithMany().HasForeignKey(a => a.PontoId).OnDelete(DeleteBehavior.Restrict);
            e.HasIndex(a => a.DiaLocal);
        });

        modelo.Entity<CheckIn>(e =>
        {
            e.ToTable("CheckIns");
            e.HasOne<Cidadao>().WithMany().HasForeignKey(c => c.CidadaoId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(c => new { c.CidadaoId, c.DiaLocal });
        });
    }
}
