package br.com.fiap3espg.rededeapoio.controller;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.agente.DadosLogin;
import br.com.fiap3espg.rededeapoio.infra.security.DadosTokenJWT;
import br.com.fiap3espg.rededeapoio.infra.security.TokenService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Tag(name = "Autenticação", description = "Login dos agentes")
public class AutenticacaoController {
    private final AuthenticationManager manager;
    private final TokenService tokenService;

    @PostMapping("/login")
    @Operation(summary = "Faz login e devolve o token JWT", description = "O token vale por 2 horas.")
    @ApiResponse(responseCode = "200", description = "Login realizado")
    @ApiResponse(responseCode = "401", description = "E-mail ou senha inválidos, ou agente desativado")
    public ResponseEntity<DadosTokenJWT> login(@RequestBody @Valid DadosLogin dados) {
        var credenciais = new UsernamePasswordAuthenticationToken(dados.email(), dados.senha());
        Agente agente = (Agente) manager.authenticate(credenciais).getPrincipal();
        return ResponseEntity.ok(new DadosTokenJWT(tokenService.gerarToken(agente)));
    }
}
