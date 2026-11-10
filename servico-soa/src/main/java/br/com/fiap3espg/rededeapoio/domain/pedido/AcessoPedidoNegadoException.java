package br.com.fiap3espg.rededeapoio.domain.pedido;

// O agente tentou agir sobre um pedido que esta com outro agente. Responde 403.
public class AcessoPedidoNegadoException extends RuntimeException {
    public AcessoPedidoNegadoException(String mensagem) {
        super(mensagem);
    }
}
