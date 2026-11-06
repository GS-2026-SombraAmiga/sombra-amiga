namespace SombraAmiga.Dominio.Comum;

/// <summary>Regra de negócio violada. Vira HTTP 400.</summary>
public class DominioException(string mensagem) : Exception(mensagem);

/// <summary>Recurso inexistente. Vira HTTP 404.</summary>
public sealed class NaoEncontradoException(string recurso) : Exception($"{recurso} não encontrado.");

/// <summary>Conflito com dado já existente. Vira HTTP 409.</summary>
public sealed class ConflitoException(string mensagem) : Exception(mensagem);
