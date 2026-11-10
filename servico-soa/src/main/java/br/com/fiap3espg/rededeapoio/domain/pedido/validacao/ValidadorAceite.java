package br.com.fiap3espg.rededeapoio.domain.pedido.validacao;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoAjuda;

// Regra verificada antes de um agente aceitar um pedido. Cada regra e um bean;
// o PedidoService recebe todas e executa uma a uma. Para criar uma regra nova,
// basta implementar esta interface.
public interface ValidadorAceite {
    void validar(PedidoAjuda pedido, Agente agente);
}
