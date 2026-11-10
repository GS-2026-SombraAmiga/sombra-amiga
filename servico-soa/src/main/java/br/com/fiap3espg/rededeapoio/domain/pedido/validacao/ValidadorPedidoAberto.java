package br.com.fiap3espg.rededeapoio.domain.pedido.validacao;

import br.com.fiap3espg.rededeapoio.domain.ConflitoException;
import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoAjuda;
import org.springframework.stereotype.Component;

// So pedidos abertos podem ser aceitos: evita que dois agentes atendam a mesma pessoa.
@Component
public class ValidadorPedidoAberto implements ValidadorAceite {
    @Override
    public void validar(PedidoAjuda pedido, Agente agente) {
        switch (pedido.getStatus()) {
            case ABERTO -> { }
            case EM_ATENDIMENTO -> throw new ConflitoException(pedido.pertenceA(agente)
                    ? "Você já está atendendo este pedido."
                    : "Este pedido já está em atendimento por outro agente.");
            case CONCLUIDO -> throw new ConflitoException("Este pedido já foi concluído.");
        }
    }
}
