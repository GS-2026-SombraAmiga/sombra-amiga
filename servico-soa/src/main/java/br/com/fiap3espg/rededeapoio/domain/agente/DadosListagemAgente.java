package br.com.fiap3espg.rededeapoio.domain.agente;

public record DadosListagemAgente(Long id, String nome, String bairro, TipoAgente tipo, Perfil perfil) {
    public DadosListagemAgente(Agente agente) {
        this(agente.getId(), agente.getNome(), agente.getBairro(), agente.getTipo(), agente.getPerfil());
    }
}
