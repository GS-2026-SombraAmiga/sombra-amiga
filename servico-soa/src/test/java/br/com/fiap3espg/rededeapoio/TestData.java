package br.com.fiap3espg.rededeapoio;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.agente.DadosCadastroAgente;
import br.com.fiap3espg.rededeapoio.domain.agente.Perfil;
import br.com.fiap3espg.rededeapoio.domain.agente.TipoAgente;
import br.com.fiap3espg.rededeapoio.domain.cidadao.DadosCidadao;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoAjuda;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDateTime;

// Dados ficticios reutilizados pelos testes unitarios.
public final class TestData {
    public static final String CIDADAO_ID = "8bc2c4a5-a9c0-402f-b118-a23df5c17e6b";
    public static final LocalDateTime AGORA = LocalDateTime.of(2026, 11, 10, 14, 0);

    private TestData() {
    }

    public static Agente agente(long id) {
        var dados = new DadosCadastroAgente("Agente " + id, "agente" + id + "@teste.com", "senha12345",
                "Brasilândia", TipoAgente.VOLUNTARIO, Perfil.AGENTE);
        Agente agente = new Agente(dados, "hash");
        ReflectionTestUtils.setField(agente, "id", id);
        return agente;
    }

    public static DadosCidadao cidadao() {
        return new DadosCidadao(CIDADAO_ID, "Lurdes Teste", "Idoso");
    }

    public static PedidoAjuda pedidoAberto() {
        return new PedidoAjuda(cidadao(), -23.462, -46.681, AGORA);
    }
}
