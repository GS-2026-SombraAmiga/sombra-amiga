package br.com.fiap3espg.rededeapoio.infra.apiprincipal;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.time.Duration;

@Configuration
public class ApiPrincipalConfig {
    // RestClient dedicado a API principal (C#), com URL base e timeout
    // configuraveis em application.properties (api-principal.url / api-principal.timeout).
    @Bean
    public RestClient apiPrincipalRestClient(
            @Value("${api-principal.url}") String baseUrl,
            @Value("${api-principal.timeout:5s}") Duration timeout) {
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(timeout);
        requestFactory.setReadTimeout(timeout);

        return RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(requestFactory)
                .build();
    }
}
