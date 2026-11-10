package br.com.fiap3espg.rededeapoio.domain.pedido;

public class PedidoNotFoundException extends RuntimeException {
    public PedidoNotFoundException(Long id) {
        super("Pedido de ajuda com id " + id + " não encontrado.");
    }
}
