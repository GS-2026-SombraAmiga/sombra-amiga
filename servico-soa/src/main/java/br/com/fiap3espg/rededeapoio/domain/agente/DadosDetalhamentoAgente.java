package br.com.fiap3espg.rededeapoio.domain.agente;

// A senha nunca sai da API, nem criptografada.
public record DadosDetalhamentoAgente(
        Long id,
        String nome,
        String email,
        String bairro,
        TipoAgente tipo,
        Perfil perfil,
        boolean ativo) {

    public DadosDetalhamentoAgente(Agente agente) {
        this(agente.getId(), agente.getNome(), agente.getEmail(), agente.getBairro(),
                agente.getTipo(), agente.getPerfil(), agente.isAtivo());
    }
}
