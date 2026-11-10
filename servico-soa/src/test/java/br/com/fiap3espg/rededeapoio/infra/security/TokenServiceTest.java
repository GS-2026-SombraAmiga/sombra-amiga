package br.com.fiap3espg.rededeapoio.infra.security;

import br.com.fiap3espg.rededeapoio.TestData;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;

import static org.assertj.core.api.Assertions.assertThat;

class TokenServiceTest {
    private static final String SEGREDO = "segredo-de-teste";

    @Test
    @DisplayName("Token gerado devolve o e-mail do agente")
    void tokenValido() {
        var service = new TokenService(SEGREDO, Clock.systemUTC());

        String token = service.gerarToken(TestData.agente(1));

        assertThat(service.getSubject(token)).isEqualTo("agente1@teste.com");
    }

    @Test
    @DisplayName("Token assinado com outro segredo nao e aceito")
    void segredoDiferente() {
        String token = new TokenService("outro-segredo", Clock.systemUTC()).gerarToken(TestData.agente(1));

        assertThat(new TokenService(SEGREDO, Clock.systemUTC()).getSubject(token)).isNull();
    }

    @Test
    @DisplayName("Token expirado nao e aceito")
    void tokenExpirado() {
        Clock tresHorasAtras = Clock.fixed(Instant.now().minus(Duration.ofHours(3)), ZoneOffset.UTC);
        String token = new TokenService(SEGREDO, tresHorasAtras).gerarToken(TestData.agente(1));

        assertThat(new TokenService(SEGREDO, Clock.systemUTC()).getSubject(token)).isNull();
    }

    @Test
    @DisplayName("Texto qualquer no lugar do token nao e aceito")
    void tokenInvalido() {
        assertThat(new TokenService(SEGREDO, Clock.systemUTC()).getSubject("token.invalido")).isNull();
    }
}
