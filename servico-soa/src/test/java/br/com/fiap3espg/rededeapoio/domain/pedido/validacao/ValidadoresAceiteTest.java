package br.com.fiap3espg.rededeapoio.domain.pedido.validacao;

import br.com.fiap3espg.rededeapoio.TestData;
import br.com.fiap3espg.rededeapoio.domain.ConflitoException;
import br.com.fiap3espg.rededeapoio.domain.ValidacaoException;
import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoAjuda;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoRepository;
import br.com.fiap3espg.rededeapoio.domain.pedido.StatusPedido;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class ValidadoresAceiteTest {
    private final ValidadorPedidoAberto pedidoAberto = new ValidadorPedidoAberto();
    private final ValidadorAgenteAtivo agenteAtivo = new ValidadorAgenteAtivo();

    @Test
    @DisplayName("Pedido aberto pode ser aceito")
    void pedidoAbertoPassa() {
        assertThatCode(() -> pedidoAberto.validar(TestData.pedidoAberto(), TestData.agente(1)))
                .doesNotThrowAnyException();
    }

    @Test
    @DisplayName("Pedido em atendimento por outro agente gera conflito")
    void pedidoDeOutroAgente() {
        PedidoAjuda pedido = TestData.pedidoAberto();
        pedido.aceitar(TestData.agente(1), TestData.AGORA);

        assertThatThrownBy(() -> pedidoAberto.validar(pedido, TestData.agente(2)))
                .isInstanceOf(ConflitoException.class)
                .hasMessageContaining("outro agente");
    }

    @Test
    @DisplayName("Aceitar de novo o proprio pedido gera conflito com mensagem propria")
    void pedidoDoProprioAgente() {
        PedidoAjuda pedido = TestData.pedidoAberto();
        pedido.aceitar(TestData.agente(1), TestData.AGORA);

        assertThatThrownBy(() -> pedidoAberto.validar(pedido, TestData.agente(1)))
                .isInstanceOf(ConflitoException.class)
                .hasMessageContaining("Você já está atendendo");
    }

    @Test
    @DisplayName("Pedido concluido nao pode ser aceito")
    void pedidoConcluido() {
        PedidoAjuda pedido = TestData.pedidoAberto();
        pedido.aceitar(TestData.agente(1), TestData.AGORA);
        pedido.concluir("ok", TestData.AGORA);

        assertThatThrownBy(() -> pedidoAberto.validar(pedido, TestData.agente(2)))
                .isInstanceOf(ConflitoException.class)
                .hasMessageContaining("concluído");
    }

    @Test
    @DisplayName("Agente desativado nao aceita pedidos")
    void agenteDesativado() {
        Agente agente = TestData.agente(1);
        agente.desativar();

        assertThatThrownBy(() -> agenteAtivo.validar(TestData.pedidoAberto(), agente))
                .isInstanceOf(ValidacaoException.class);
    }

    @Test
    @DisplayName("Agente com 3 atendimentos em andamento nao aceita o quarto")
    void limiteDeAtendimentos() {
        PedidoRepository repository = mock(PedidoRepository.class);
        when(repository.countByAgenteAndStatus(any(), eq(StatusPedido.EM_ATENDIMENTO))).thenReturn(3L);
        var validador = new ValidadorLimiteAtendimentos(repository);

        assertThatThrownBy(() -> validador.validar(TestData.pedidoAberto(), TestData.agente(1)))
                .isInstanceOf(ValidacaoException.class)
                .hasMessageContaining("3 atendimentos");
    }

    @Test
    @DisplayName("Agente com 2 atendimentos em andamento ainda pode aceitar")
    void abaixoDoLimite() {
        PedidoRepository repository = mock(PedidoRepository.class);
        when(repository.countByAgenteAndStatus(any(), eq(StatusPedido.EM_ATENDIMENTO))).thenReturn(2L);
        var validador = new ValidadorLimiteAtendimentos(repository);

        assertThatCode(() -> validador.validar(TestData.pedidoAberto(), TestData.agente(1)))
                .doesNotThrowAnyException();
    }
}
