package br.com.fiap3espg.rededeapoio.domain.pedido;

import br.com.fiap3espg.rededeapoio.TestData;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class PedidoAjudaTest {

    @Test
    @DisplayName("Pedido novo nasce ABERTO, sem agente, com os dados do cidadao")
    void pedidoNovo() {
        PedidoAjuda pedido = TestData.pedidoAberto();

        assertThat(pedido.getStatus()).isEqualTo(StatusPedido.ABERTO);
        assertThat(pedido.getAgente()).isNull();
        assertThat(pedido.getNomeCidadao()).isEqualTo("Lurdes Teste");
        assertThat(pedido.getAbertoEm()).isEqualTo(TestData.AGORA);
    }

    @Test
    @DisplayName("Aceitar e concluir percorrem o ciclo ABERTO -> EM_ATENDIMENTO -> CONCLUIDO")
    void cicloCompleto() {
        PedidoAjuda pedido = TestData.pedidoAberto();
        var agente = TestData.agente(1);

        pedido.aceitar(agente, TestData.AGORA.plusMinutes(5));
        assertThat(pedido.getStatus()).isEqualTo(StatusPedido.EM_ATENDIMENTO);
        assertThat(pedido.pertenceA(agente)).isTrue();

        pedido.concluir("Levei água e acompanhei até a UBS.", TestData.AGORA.plusMinutes(40));
        assertThat(pedido.getStatus()).isEqualTo(StatusPedido.CONCLUIDO);
        assertThat(pedido.getObservacao()).isEqualTo("Levei água e acompanhei até a UBS.");
        assertThat(pedido.getConcluidoEm()).isEqualTo(TestData.AGORA.plusMinutes(40));
    }

    @Test
    @DisplayName("Pedido so pertence ao agente que o aceitou")
    void pertenceSomenteAoResponsavel() {
        PedidoAjuda pedido = TestData.pedidoAberto();
        pedido.aceitar(TestData.agente(1), TestData.AGORA);

        assertThat(pedido.pertenceA(TestData.agente(1))).isTrue();
        assertThat(pedido.pertenceA(TestData.agente(2))).isFalse();
    }
}
