package br.com.fiap3espg.rededeapoio.domain.pedido;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;

public interface PedidoRepository extends JpaRepository<PedidoAjuda, Long> {
    Page<PedidoAjuda> findAllByStatusIn(Collection<StatusPedido> status, Pageable paginacao);

    long countByAgenteAndStatus(Agente agente, StatusPedido status);

    boolean existsByCidadaoIdAndStatusIn(String cidadaoId, Collection<StatusPedido> status);
}
