package br.com.fiap3espg.rededeapoio.infra.security;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import java.nio.charset.StandardCharsets;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity // As autorizacoes por perfil ficam nos controllers, via @PreAuthorize
@RequiredArgsConstructor
public class SecurityConfig {
    // Endpoints publicos: login, health check e a documentacao do Swagger.
    private static final String[] ROTAS_PUBLICAS = {
            "/api/auth/login",
            "/health-check",
            "/v3/api-docs/**",
            "/swagger-ui.html",
            "/swagger-ui/**"
    };

    private final SecurityFilter securityFilter;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) {
        return http
                .csrf(csrf -> csrf.disable())
                .cors(Customizer.withDefaults())
                .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(ROTAS_PUBLICAS).permitAll()
                        // Gestao de agentes barrada ja no filtro: sem perfil, a resposta e 403
                        // antes de o corpo da requisicao ser lido ou validado.
                        .requestMatchers(HttpMethod.POST, "/api/agentes").hasRole("COORDENADOR")
                        .requestMatchers(HttpMethod.PUT, "/api/agentes/**").hasRole("COORDENADOR")
                        .requestMatchers(HttpMethod.DELETE, "/api/agentes/**").hasRole("COORDENADOR")
                        .anyRequest().authenticated())
                // Sem token (ou com token invalido): 401, e nao o 403 padrao do Spring.
                .exceptionHandling(e -> e.authenticationEntryPoint((request, response, ex) -> {
                    response.setStatus(HttpStatus.UNAUTHORIZED.value());
                    response.setContentType(MediaType.APPLICATION_JSON_VALUE);
                    response.setCharacterEncoding(StandardCharsets.UTF_8.name());
                    response.getWriter().write("{\"mensagem\":\"Autenticação necessária.\"}");
                }))
                .addFilterBefore(securityFilter, UsernamePasswordAuthenticationFilter.class)
                .build();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration configuration) {
        return configuration.getAuthenticationManager();
    }

    // BCrypt: as senhas sao gravadas apenas como hash, nunca em texto puro.
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
