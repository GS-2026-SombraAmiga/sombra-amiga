using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using SombraAmiga.Dominio.Repositorios;
using SombraAmiga.Dominio.Servicos;
using SombraAmiga.Infra.Dados;
using SombraAmiga.Infra.RedeDeApoio;
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

    /// <summary>
    /// Integração com o serviço Java Rede de Apoio. Sem URL configurada, a integração
    /// fica desativada. A configuração é lida ao resolver o serviço, e não no startup,
    /// para os testes poderem trocá-la.
    /// </summary>
    public static IServiceCollection AdicionarRedeDeApoio(
        this IServiceCollection servicos, Func<IServiceProvider, ConfiguracaoRedeDeApoio> configuracao)
    {
        servicos.AddHttpClient<ClienteRedeDeApoio>((provedor, cliente) =>
        {
            var config = configuracao(provedor);
            cliente.BaseAddress = new Uri(config.Url!.TrimEnd('/') + "/");
            cliente.Timeout = TimeSpan.FromSeconds(5);
            cliente.DefaultRequestHeaders.Add(ClienteRedeDeApoio.CabecalhoChave, config.Chave ?? string.Empty);
        });

        // O check-in só enfileira; o envio acontece em segundo plano.
        servicos.AddSingleton<FilaRedeDeApoio>();
        servicos.AddHostedService<EnvioRedeDeApoio>();

        servicos.AddScoped<IRedeDeApoio>(provedor =>
            string.IsNullOrWhiteSpace(configuracao(provedor).Url)
                ? new RedeDeApoioDesativada()
                : provedor.GetRequiredService<FilaRedeDeApoio>());

        return servicos;
    }
}
