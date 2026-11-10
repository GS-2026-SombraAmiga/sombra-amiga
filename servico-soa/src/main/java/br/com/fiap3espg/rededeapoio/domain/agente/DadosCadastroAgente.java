package br.com.fiap3espg.rededeapoio.domain.agente;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record DadosCadastroAgente(
        @NotBlank
        @Size(max = 100)
        String nome,

        @NotBlank
        @Email
        @Size(max = 100)
        String email,

        @NotBlank
        @Size(min = 8, max = 72)
        String senha,

        @NotBlank
        @Size(max = 100)
        String bairro,

        @NotNull
        TipoAgente tipo,

        @NotNull
        Perfil perfil) {
}
