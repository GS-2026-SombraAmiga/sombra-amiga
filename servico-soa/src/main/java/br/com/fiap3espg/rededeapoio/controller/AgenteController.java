package br.com.fiap3espg.rededeapoio.controller;

import br.com.fiap3espg.rededeapoio.domain.agente.*;
import br.com.fiap3espg.rededeapoio.infra.springdoc.SpringDocConfig;
import br.com.fiap3espg.rededeapoio.service.AgenteService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;

@RestController
@RequestMapping("/api/agentes")
@RequiredArgsConstructor
@Tag(name = "Agentes", description = "Cadastro de agentes comunitários de saúde e voluntários (exclusão lógica)")
@SecurityRequirement(name = SpringDocConfig.SECURITY_SCHEME)
public class AgenteController {
    private final AgenteService service;

    @PostMapping
    @PreAuthorize("hasRole('COORDENADOR')")
    @Operation(summary = "Cadastra um agente", description = "Somente COORDENADOR. O e-mail é único e a senha é gravada com BCrypt.")
    @ApiResponse(responseCode = "201", description = "Agente cadastrado")
    @ApiResponse(responseCode = "400", description = "Dados inválidos ou e-mail já cadastrado")
    @ApiResponse(responseCode = "403", description = "Perfil sem permissão")
    public ResponseEntity<DadosDetalhamentoAgente> cadastrarAgente(
            @RequestBody @Valid DadosCadastroAgente dados, UriComponentsBuilder uriBuilder) {
        DadosDetalhamentoAgente dto = service.cadastrarAgente(dados);
        var uri = uriBuilder.path("/api/agentes/{id}").buildAndExpand(dto.id()).toUri();
        return ResponseEntity.created(uri).body(dto);
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('COORDENADOR', 'AGENTE')")
    @Operation(summary = "Lista os agentes ativos", description = "Paginada, 10 por página, ordenada por nome.")
    public ResponseEntity<Page<DadosListagemAgente>> listarAgentes(
            @ParameterObject @PageableDefault(size = 10, sort = "nome", direction = Sort.Direction.ASC) Pageable paginacao) {
        return ResponseEntity.ok(service.listarAgentes(paginacao));
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('COORDENADOR', 'AGENTE')")
    @Operation(summary = "Detalha um agente")
    @ApiResponse(responseCode = "404", description = "Id inexistente")
    public ResponseEntity<DadosDetalhamentoAgente> detalharAgente(@PathVariable Long id) {
        return ResponseEntity.ok(service.detalharAgente(id));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('COORDENADOR')")
    @Operation(summary = "Atualiza nome e bairro do agente")
    @ApiResponse(responseCode = "404", description = "Id inexistente")
    public ResponseEntity<DadosDetalhamentoAgente> atualizarAgente(
            @PathVariable Long id, @RequestBody @Valid DadosAtualizacaoAgente dados) {
        return ResponseEntity.ok(service.atualizarAgente(id, dados));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('COORDENADOR')")
    @Operation(summary = "Desativa um agente", description = "Exclusão lógica: o agente deixa de fazer login, e o histórico é mantido.")
    @ApiResponse(responseCode = "204", description = "Agente desativado")
    @ApiResponse(responseCode = "404", description = "Id inexistente")
    public ResponseEntity<Void> desativarAgente(@PathVariable Long id) {
        service.desativarAgente(id);
        return ResponseEntity.noContent().build();
    }
}
