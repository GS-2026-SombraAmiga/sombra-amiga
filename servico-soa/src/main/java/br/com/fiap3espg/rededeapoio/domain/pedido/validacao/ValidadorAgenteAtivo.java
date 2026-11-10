package br.com.fiap3espg.rededeapoio.domain.pedido.validacao;

import br.com.fiap3espg.rededeapoio.domain.ValidacaoException;
import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoAjuda;
import org.springframework.stereotype.Component;

@Component
public class ValidadorAgenteAtivo implements ValidadorAceite {
    @Override
    public void validar(PedidoAjuda pedido, Agente agente) {
        if (!agente.isAtivo()) {
            throw new ValidacaoException("Agente desativado não pode aceitar pedidos.");
        }
    }
}
