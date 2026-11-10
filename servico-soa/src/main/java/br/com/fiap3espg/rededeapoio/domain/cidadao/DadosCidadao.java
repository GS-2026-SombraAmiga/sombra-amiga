package br.com.fiap3espg.rededeapoio.domain.cidadao;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

// Resposta de GET /api/cidadaos/{id} da API principal (C#). A API principal ja
// devolve o CPF mascarado e nao expoe contato nem condicao de saude; aqui
// guardamos apenas id, nome e perfil.
@JsonIgnoreProperties(ignoreUnknown = true)
public record DadosCidadao(String id, String nome, String perfil) {
}
