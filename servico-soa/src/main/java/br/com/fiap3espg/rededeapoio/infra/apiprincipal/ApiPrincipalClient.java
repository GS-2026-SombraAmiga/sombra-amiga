package br.com.fiap3espg.rededeapoio.infra.apiprincipal;

import br.com.fiap3espg.rededeapoio.domain.cidadao.DadosCidadao;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.Optional;
import java.util.UUID;

// Cliente HTTP da API principal do Sombra Amiga (C#/.NET).
@Component
public class ApiPrincipalClient {
    private final RestClient restClient;

    public ApiPrincipalClient(@Qualifier("apiPrincipalRestClient") RestClient restClient) {
        this.restClient = restClient;
    }

    /**
     * Consulta um cidadao pelo id.
     * Devolve vazio quando o cidadao nao existe (404) e lanca
     * ServicoExternoIndisponivelException quando a API principal esta fora do ar.
     */
    public Optional<DadosCidadao> buscarCidadao(UUID id) {
        try {
            DadosCidadao cidadao = restClient.get()
                    .uri("/api/cidadaos/{id}", id)
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .body(DadosCidadao.class);
            return Optional.ofNullable(cidadao);
        } catch (HttpClientErrorException.NotFound ex) {
            return Optional.empty();
        } catch (RestClientException ex) {
            throw new ServicoExternoIndisponivelException(
                    "Não foi possível consultar a API principal no momento. Tente novamente mais tarde.", ex);
        }
    }
}
