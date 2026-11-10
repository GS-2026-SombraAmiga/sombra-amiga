package br.com.fiap3espg.rededeapoio.domain.agente;

import jakarta.validation.constraints.Size;

// Campos opcionais: so o que for informado e alterado.
public record DadosAtualizacaoAgente(
        @Size(max = 100)
        String nome,

        @Size(max = 100)
        String bairro) {
}
