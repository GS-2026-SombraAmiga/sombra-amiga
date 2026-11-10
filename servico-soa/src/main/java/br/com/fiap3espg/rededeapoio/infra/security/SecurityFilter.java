package br.com.fiap3espg.rededeapoio.infra.security;

import br.com.fiap3espg.rededeapoio.domain.agente.AgenteRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;

// Autentica a requisicao de duas formas:
// 1. Agentes: token JWT no cabecalho "Authorization: Bearer <token>".
// 2. API principal (C#): chave de servico no cabecalho "X-Chave-Servico". E um
//    sistema, nao uma pessoa, por isso recebe o perfil SISTEMA em vez de fazer login.
@Component
public class SecurityFilter extends OncePerRequestFilter {
    public static final String CABECALHO_CHAVE = "X-Chave-Servico";

    private final TokenService tokenService;
    private final AgenteRepository repository;
    private final byte[] chaveServico;

    public SecurityFilter(TokenService tokenService, AgenteRepository repository,
                          @Value("${app.servico.chave}") String chaveServico) {
        this.tokenService = tokenService;
        this.repository = repository;
        this.chaveServico = chaveServico.getBytes(StandardCharsets.UTF_8);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String token = recuperarToken(request);
        if (token != null) {
            autenticarAgente(token);
        } else if (chaveValida(request.getHeader(CABECALHO_CHAVE))) {
            var sistema = new UsernamePasswordAuthenticationToken(
                    "api-principal", null, List.of(new SimpleGrantedAuthority("ROLE_SISTEMA")));
            SecurityContextHolder.getContext().setAuthentication(sistema);
        }
        filterChain.doFilter(request, response);
    }

    private void autenticarAgente(String token) {
        String email = tokenService.getSubject(token);
        if (email == null) {
            return;
        }
        // O agente pode ter sido desativado depois que o token foi emitido.
        repository.findByEmail(email)
                .filter(agente -> agente.isAtivo())
                .ifPresent(agente -> SecurityContextHolder.getContext().setAuthentication(
                        new UsernamePasswordAuthenticationToken(agente, null, agente.getAuthorities())));
    }

    // Comparacao em tempo constante, para nao vazar a chave por diferenca de tempo de resposta.
    private boolean chaveValida(String chaveRecebida) {
        return chaveRecebida != null
                && MessageDigest.isEqual(chaveRecebida.getBytes(StandardCharsets.UTF_8), chaveServico);
    }

    private String recuperarToken(HttpServletRequest request) {
        String authorization = request.getHeader("Authorization");
        if (authorization != null && authorization.startsWith("Bearer ")) {
            return authorization.substring("Bearer ".length()).trim();
        }
        return null;
    }
}
