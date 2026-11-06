namespace SombraAmiga.Dominio.Comum;

/// <summary>Base de todas as entidades persistidas.</summary>
public abstract class Entidade
{
    public Guid Id { get; private set; } = Guid.NewGuid();
}
