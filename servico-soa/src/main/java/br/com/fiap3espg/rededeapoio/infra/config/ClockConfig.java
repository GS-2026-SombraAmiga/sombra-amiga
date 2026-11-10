package br.com.fiap3espg.rededeapoio.infra.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Clock;
import java.time.ZoneId;

// Relogio unico da aplicacao, no fuso de Sao Paulo. Nos testes, um Clock fixo
// pode substituir este bean para tornar as datas previsiveis.
@Configuration
public class ClockConfig {
    @Bean
    public Clock clock(@Value("${app.timezone:America/Sao_Paulo}") String timezone) {
        return Clock.system(ZoneId.of(timezone));
    }
}
