using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;
using SombraAmiga.Dominio.Repositorios;

namespace SombraAmiga.Dominio.Servicos;

public sealed record DadosCadastro(
    PerfilCidadao Perfil,
    string Nome,
    string Cpf,
    string ContatoFamiliar,
    string? CondicaoSaude,
    string? Ocupacao);

public sealed class ServicoCidadaos(IRepositorioCidadaos cidadaos, IUnidadeDeTrabalho unidade)
{
    public async Task<Cidadao> CadastrarAsync(DadosCadastro dados, CancellationToken ct = default)
    {
        var cpf = Cpf.Criar(dados.Cpf);
        if (await cidadaos.ExisteCpfAsync(cpf, ct))
            throw new ConflitoException("Já existe um cadastro com este CPF.");

        Cidadao cidadao = dados.Perfil switch
        {
            PerfilCidadao.Idoso => new Idoso(dados.Nome, cpf, dados.ContatoFamiliar, dados.CondicaoSaude),
            PerfilCidadao.TrabalhadorDeRua => new TrabalhadorDeRua(
                dados.Nome, cpf, dados.ContatoFamiliar, dados.CondicaoSaude, dados.Ocupacao ?? string.Empty),
            _ => throw new DominioException("Perfil inválido."),
        };

        await cidadaos.AdicionarAsync(cidadao, ct);
        await unidade.SalvarAsync(ct);
        return cidadao;
    }
}
