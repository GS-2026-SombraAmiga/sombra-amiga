package br.com.fiap3espg.rededeapoio.service;

import br.com.fiap3espg.rededeapoio.domain.ConflitoException;
import br.com.fiap3espg.rededeapoio.domain.ValidacaoException;
import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.cidadao.CidadaoNotFoundException;
import br.com.fiap3espg.rededeapoio.domain.cidadao.DadosCidadao;
import br.com.fiap3espg.rededeapoio.domain.pedido.*;
import br.com.fiap3espg.rededeapoio.domain.pedido.validacao.ValidadorAceite;
import br.com.fiap3espg.rededeapoio.infra.apiprincipal.ApiPrincipalClient;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Clock;
import java.time.LocalDateTime;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class PedidoService {
    private static final Set<StatusPedido> EM_ANDAMENTO = EnumSet.of(StatusPedido.ABERTO, StatusPedido.EM_ATENDIMENTO);

    private final PedidoRepository repository;
    private final ApiPrincipalClient apiPrincipal;
    private final List<ValidadorAceite> validadoresAceite;
    private final Clock clock;

    @Transactional
    public DadosDetalhamentoPedido abrirPedido(DadosAberturaPedido dados) {
        // Confirma na API principal que o cidadao existe e traz nome e perfil.
        DadosCidadao cidadao = apiPrincipal.buscarCidadao(dados.cidadaoId())
                .orElseThrow(() -> new CidadaoNotFoundException(dados.cidadaoId()));

        // Varios toques em "preciso de ajuda" nao podem gerar varios atendimentos.
        if (repository.existsByCidadaoIdAndStatusIn(cidadao.id(), EM_ANDAMENTO)) {
            throw new ConflitoException("Já existe um pedido de ajuda em andamento para este cidadão.");
        }

        PedidoAjuda pedido = new PedidoAjuda(cidadao, dados.latitude(), dados.longitude(), agora());
        return new DadosDetalhamentoPedido(repository.save(pedido));
    }

    // Sem filtro, mostra o que ainda precisa de acao: pedidos abertos e em atendimento.
    @Transactional(readOnly = true)
    public Page<DadosDetalhamentoPedido> listarPedidos(StatusPedido status, Pageable paginacao) {
        Set<StatusPedido> filtro = status == null ? EM_ANDAMENTO : EnumSet.of(status);
        return repository.findAllByStatusIn(filtro, paginacao).map(DadosDetalhamentoPedido::new);
    }

    @Transactional(readOnly = true)
    public DadosDetalhamentoPedido detalharPedido(Long id) {
        return new DadosDetalhamentoPedido(buscarPedido(id));
    }

    @Transactional
    public DadosDetalhamentoPedido aceitarPedido(Long id, Agente agente) {
        PedidoAjuda pedido = buscarPedido(id);
        validadoresAceite.forEach(v -> v.validar(pedido, agente));
        pedido.aceitar(agente, agora());
        return new DadosDetalhamentoPedido(pedido);
    }

    @Transactional
    public DadosDetalhamentoPedido concluirPedido(Long id, DadosConclusaoPedido dados, Agente agente) {
        PedidoAjuda pedido = buscarPedido(id);
        if (pedido.getStatus() != StatusPedido.EM_ATENDIMENTO) {
            throw new ValidacaoException("Só é possível concluir um pedido que está em atendimento.");
        }
        if (!pedido.pertenceA(agente)) {
            throw new AcessoPedidoNegadoException("Somente o agente responsável pode concluir este pedido.");
        }
        pedido.concluir(dados.observacao(), agora());
        return new DadosDetalhamentoPedido(pedido);
    }

    private PedidoAjuda buscarPedido(Long id) {
        return repository.findById(id).orElseThrow(() -> new PedidoNotFoundException(id));
    }

    private LocalDateTime agora() {
        return LocalDateTime.now(clock);
    }
}
