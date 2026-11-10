package br.com.fiap3espg.rededeapoio.domain.pedido;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;

import java.time.LocalDateTime;

public record DadosDetalhamentoPedido(
        Long id,
        String cidadaoId,
        String nomeCidadao,
        String perfilCidadao,
        Double latitude,
        Double longitude,
        StatusPedido status,
        Long agenteId,
        String nomeAgente,
        LocalDateTime abertoEm,
        LocalDateTime aceitoEm,
        LocalDateTime concluidoEm,
        String observacao) {

    public DadosDetalhamentoPedido(PedidoAjuda pedido) {
        this(pedido.getId(), pedido.getCidadaoId(), pedido.getNomeCidadao(), pedido.getPerfilCidadao(),
                pedido.getLatitude(), pedido.getLongitude(), pedido.getStatus(),
                idDoAgente(pedido.getAgente()), nomeDoAgente(pedido.getAgente()),
                pedido.getAbertoEm(), pedido.getAceitoEm(), pedido.getConcluidoEm(), pedido.getObservacao());
    }

    private static Long idDoAgente(Agente agente) {
        return agente == null ? null : agente.getId();
    }

    private static String nomeDoAgente(Agente agente) {
        return agente == null ? null : agente.getNome();
    }
}
