package br.com.fiap3espg.rededeapoio.service;

import br.com.fiap3espg.rededeapoio.TestData;
import br.com.fiap3espg.rededeapoio.domain.ConflitoException;
import br.com.fiap3espg.rededeapoio.domain.ValidacaoException;
import br.com.fiap3espg.rededeapoio.domain.cidadao.CidadaoNotFoundException;
import br.com.fiap3espg.rededeapoio.domain.pedido.*;
import br.com.fiap3espg.rededeapoio.domain.pedido.validacao.ValidadorAceite;
import br.com.fiap3espg.rededeapoio.infra.apiprincipal.ApiPrincipalClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.ZoneId;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyCollection;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

class PedidoServiceTest {
    private static final ZoneId SAO_PAULO = ZoneId.of("America/Sao_Paulo");
    private static final UUID CIDADAO = UUID.fromString(TestData.CIDADAO_ID);

    private PedidoRepository repository;
    private ApiPrincipalClient apiPrincipal;
    private ValidadorAceite validador;
    private PedidoService service;

    @BeforeEach
    void preparar() {
        repository = mock(PedidoRepository.class);
        apiPrincipal = mock(ApiPrincipalClient.class);
        validador = mock(ValidadorAceite.class);
        Clock clock = Clock.fixed(TestData.AGORA.atZone(SAO_PAULO).toInstant(), SAO_PAULO);
        service = new PedidoService(repository, apiPrincipal, List.of(validador), clock);
        when(repository.save(any())).thenAnswer(chamada -> chamada.getArgument(0));
    }

    @Test
    @DisplayName("Abre pedido com os dados do cidadao vindos da API principal")
    void abrePedido() {
        when(apiPrincipal.buscarCidadao(CIDADAO)).thenReturn(Optional.of(TestData.cidadao()));

        var pedido = service.abrirPedido(new DadosAberturaPedido(CIDADAO, -23.46, -46.68));

        assertThat(pedido.status()).isEqualTo(StatusPedido.ABERTO);
        assertThat(pedido.nomeCidadao()).isEqualTo("Lurdes Teste");
        assertThat(pedido.abertoEm()).isEqualTo(TestData.AGORA);
    }

    @Test
    @DisplayName("Cidadao inexistente na API principal nao abre pedido")
    void cidadaoInexistente() {
        when(apiPrincipal.buscarCidadao(CIDADAO)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.abrirPedido(new DadosAberturaPedido(CIDADAO, null, null)))
                .isInstanceOf(CidadaoNotFoundException.class);
        verify(repository, never()).save(any());
    }

    @Test
    @DisplayName("Segundo pedido do mesmo cidadao em andamento gera conflito")
    void pedidoDuplicado() {
        when(apiPrincipal.buscarCidadao(CIDADAO)).thenReturn(Optional.of(TestData.cidadao()));
        when(repository.existsByCidadaoIdAndStatusIn(anyString(), anyCollection())).thenReturn(true);

        assertThatThrownBy(() -> service.abrirPedido(new DadosAberturaPedido(CIDADAO, null, null)))
                .isInstanceOf(ConflitoException.class);
    }

    @Test
    @DisplayName("Aceitar executa todos os validadores antes de mudar o pedido")
    void aceitarExecutaValidadores() {
        PedidoAjuda pedido = TestData.pedidoAberto();
        var agente = TestData.agente(1);
        when(repository.findById(10L)).thenReturn(Optional.of(pedido));

        service.aceitarPedido(10L, agente);

        verify(validador).validar(pedido, agente);
        assertThat(pedido.getStatus()).isEqualTo(StatusPedido.EM_ATENDIMENTO);
    }

    @Test
    @DisplayName("Somente o agente responsavel conclui o pedido")
    void concluirPorOutroAgente() {
        PedidoAjuda pedido = TestData.pedidoAberto();
        pedido.aceitar(TestData.agente(1), TestData.AGORA);
        when(repository.findById(10L)).thenReturn(Optional.of(pedido));

        assertThatThrownBy(() -> service.concluirPedido(10L, new DadosConclusaoPedido("ok"), TestData.agente(2)))
                .isInstanceOf(AcessoPedidoNegadoException.class);
        assertThat(pedido.getStatus()).isEqualTo(StatusPedido.EM_ATENDIMENTO);
    }

    @Test
    @DisplayName("Pedido ainda aberto nao pode ser concluido")
    void concluirPedidoAberto() {
        when(repository.findById(10L)).thenReturn(Optional.of(TestData.pedidoAberto()));

        assertThatThrownBy(() -> service.concluirPedido(10L, new DadosConclusaoPedido("ok"), TestData.agente(1)))
                .isInstanceOf(ValidacaoException.class);
    }

    @Test
    @DisplayName("Pedido inexistente gera erro de nao encontrado")
    void pedidoInexistente() {
        when(repository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.detalharPedido(99L)).isInstanceOf(PedidoNotFoundException.class);
    }
}
