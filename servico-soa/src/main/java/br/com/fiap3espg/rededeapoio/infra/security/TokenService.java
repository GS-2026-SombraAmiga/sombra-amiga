package br.com.fiap3espg.rededeapoio.infra.security;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTCreationException;
import com.auth0.jwt.exceptions.JWTVerificationException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;

@Service
public class TokenService {
    private static final String ISSUER = "RedeDeApoio-SombraAmiga";
    private static final Duration VALIDADE = Duration.ofHours(2);

    private final String secret;
    private final Clock clock;

    public TokenService(@Value("${api.security.token.secret}") String secret, Clock clock) {
        this.secret = secret;
        this.clock = clock;
    }

    public String gerarToken(Agente agente) {
        try {
            return JWT.create()
                    .withIssuer(ISSUER)
                    .withSubject(agente.getEmail())
                    .withClaim("perfil", agente.getPerfil().name())
                    .withExpiresAt(Instant.now(clock).plus(VALIDADE))
                    .sign(Algorithm.HMAC256(secret));
        } catch (JWTCreationException ex) {
            throw new IllegalStateException("Erro ao gerar o token JWT.", ex);
        }
    }

    /**
     * Devolve o e-mail contido no token, ou null quando o token e invalido ou expirou.
     * Com null, o SecurityFilter apenas nao autentica, e a requisicao recebe 401.
     */
    public String getSubject(String tokenJWT) {
        try {
            return JWT.require(Algorithm.HMAC256(secret))
                    .withIssuer(ISSUER)
                    .build()
                    .verify(tokenJWT)
                    .getSubject();
        } catch (JWTVerificationException ex) {
            return null;
        }
    }
}
