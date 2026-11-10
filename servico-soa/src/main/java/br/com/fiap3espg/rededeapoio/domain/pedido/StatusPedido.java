package br.com.fiap3espg.rededeapoio.domain.pedido;

// Ciclo de vida do pedido: ABERTO -> EM_ATENDIMENTO -> CONCLUIDO.
public enum StatusPedido {
    ABERTO,
    EM_ATENDIMENTO,
    CONCLUIDO
}
