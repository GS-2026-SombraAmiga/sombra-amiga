using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using SombraAmiga.Dominio.Repositorios;
using SombraAmiga.Dominio.Servicos;
using SombraAmiga.Infra.Dados;
using SombraAmiga.Infra.Repositorios;

namespace SombraAmiga.Infra;

public static class InjecaoDeDependencia
{
    public static IServiceCollection AdicionarInfra(this IServiceCollection servicos, Func<IServiceProvider, string> conexao)
    {
        servicos.AddDbContext<SombraAmigaContexto>((provedor, opcoes) => opcoes.UseSqlite(conexao(provedor)));
        servicos.AddScoped<IUnidadeDeTrabalho>(p => p.GetRequiredService<SombraAmigaContexto>());

        servicos.AddScoped<IRepositorioCidadaos, RepositorioCidadaos>();
        servicos.AddScoped<IRepositorioPontos, RepositorioPontos>();
        servicos.AddScoped<IRepositorioLeituras, RepositorioLeituras>();
        servicos.AddScoped<IRepositorioAlertas, RepositorioAlertas>();
        servicos.AddScoped<IRepositorioCheckIns, RepositorioCheckIns>();

        servicos.AddScoped<ServicoCidadaos>();
        servicos.AddScoped<ServicoCheckIns>();
        servicos.AddScoped<ServicoLeituras>();
        servicos.AddScoped<ServicoRisco>();
        servicos.AddScoped<ServicoIndicadores>();

        servicos.AddSingleton(TimeProvider.System);
        return servicos;
    }
}
