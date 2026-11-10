package br.com.fiap3espg.rededeapoio.infra.springdoc;

import br.com.fiap3espg.rededeapoio.infra.security.SecurityFilter;
import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

// Documentacao automatica da API (Swagger UI em /swagger-ui.html). O botao
// "Authorize" aceita o token de POST /api/auth/login ou a chave de servico.
@Configuration
public class SpringDocConfig {
    public static final String SECURITY_SCHEME = "bearer-key";
    public static final String CHAVE_SERVICO = "chave-servico";

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .components(new Components()
                        .addSecuritySchemes(SECURITY_SCHEME, new SecurityScheme()
                                .type(SecurityScheme.Type.HTTP)
                                .scheme("bearer")
                                .bearerFormat("JWT")
                                .description("Token JWT obtido em POST /api/auth/login"))
                        .addSecuritySchemes(CHAVE_SERVICO, new SecurityScheme()
                                .type(SecurityScheme.Type.APIKEY)
                                .in(SecurityScheme.In.HEADER)
                                .name(SecurityFilter.CABECALHO_CHAVE)
                                .description("Chave usada pela API principal (C#) para abrir pedidos")))
                .info(new Info()
                        .title("Rede de Apoio - Sombra Amiga")
                        .version("v1")
                        .description("""
                                Servico da CitizenTech Sombra Amiga que conecta idosos e trabalhadores \
                                de rua que pedem ajuda em dias de calor extremo a agentes comunitarios \
                                de saude e voluntarios do bairro.

                                Para testar: faca POST /api/auth/login com o coordenador de \
                                desenvolvimento (veja o README), copie o tokenJWT e cole no botao Authorize.""")
                        .contact(new Contact().name("Glauco Heitor Goncalves (RM 555978) e Pedro Henrique Junqueira (RM 556278)"))
                        .license(new License().name("Uso academico - FIAP Global Solution 2026")));
    }
}
