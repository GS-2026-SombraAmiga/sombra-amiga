namespace SombraAmiga.Dominio.Servicos;

/// <summary>
/// Serviço Rede de Apoio (Java), que encaminha pedidos de ajuda a agentes comunitários
/// de saúde e voluntários. As implementações nunca lançam exceção: uma falha na Rede de
/// Apoio não pode impedir o cidadão de registrar o check-in.
/// </summary>
public interface IRedeDeApoio
{
    Task SolicitarAjudaAsync(Guid cidadaoId, CancellationToken ct = default);
}
