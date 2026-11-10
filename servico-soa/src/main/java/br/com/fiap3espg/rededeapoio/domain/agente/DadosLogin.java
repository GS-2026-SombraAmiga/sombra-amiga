package br.com.fiap3espg.rededeapoio.domain.agente;

import jakarta.validation.constraints.NotBlank;

public record DadosLogin(
        @NotBlank
        String email,

        @NotBlank
        String senha) {
}
