package br.com.fiap3espg.rededeapoio.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

// Rota publica usada pelo monitoramento da infraestrutura para saber se o servico esta no ar.
@RestController
@Tag(name = "Health check")
public class HealthCheckController {
    @GetMapping("/health-check")
    @Operation(summary = "Indica se o serviço está no ar")
    public ResponseEntity<Map<String, String>> healthCheck() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
