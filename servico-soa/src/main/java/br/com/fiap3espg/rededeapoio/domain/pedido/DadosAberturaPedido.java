package br.com.fiap3espg.rededeapoio.domain.pedido;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;

import java.util.UUID;

// Enviado pela API principal (C#) quando o cidadao faz o check-in "preciso de ajuda".
// A localizacao e opcional: o app so a envia se o cidadao permitir.
public record DadosAberturaPedido(
        @NotNull
        UUID cidadaoId,

        @DecimalMin("-90") @DecimalMax("90")
        Double latitude,

        @DecimalMin("-180") @DecimalMax("180")
        Double longitude) {
}
