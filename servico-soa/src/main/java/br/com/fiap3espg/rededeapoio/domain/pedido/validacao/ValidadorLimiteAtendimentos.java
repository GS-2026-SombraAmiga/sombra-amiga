package br.com.fiap3espg.rededeapoio.domain.pedido.validacao;

import br.com.fiap3espg.rededeapoio.domain.ValidacaoException;
import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoAjuda;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoRepository;
import br.com.fiap3espg.rededeapoio.domain.pedido.StatusPedido;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

// Um agente atende no maximo 3 pessoas ao mesmo tempo: em dia de calor extremo,
// acumular pedidos significa demorar a chegar em quem precisa.
@Component
@RequiredArgsConstructor
public class ValidadorLimiteAtendimentos implements ValidadorAceite {
    static final int LIMITE = 3;

    private final PedidoRepository repository;

    @Override
    public void validar(PedidoAjuda pedido, Agente agente) {
        if (repository.countByAgenteAndStatus(agente, StatusPedido.EM_ATENDIMENTO) >= LIMITE) {
            throw new ValidacaoException(
                    "Você já tem " + LIMITE + " atendimentos em andamento. Conclua um antes de aceitar outro.");
        }
    }
}
