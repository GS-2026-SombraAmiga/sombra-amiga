package br.com.fiap3espg.rededeapoio.domain.pedido;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

// O agente registra o que foi feito no atendimento.
public record DadosConclusaoPedido(
        @NotBlank
        @Size(max = 500)
        String observacao) {
}
