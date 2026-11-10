package br.com.fiap3espg.rededeapoio.controller;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.pedido.DadosAberturaPedido;
import br.com.fiap3espg.rededeapoio.domain.pedido.DadosConclusaoPedido;
import br.com.fiap3espg.rededeapoio.domain.pedido.DadosDetalhamentoPedido;
import br.com.fiap3espg.rededeapoio.domain.pedido.StatusPedido;
import br.com.fiap3espg.rededeapoio.infra.springdoc.SpringDocConfig;
import br.com.fiap3espg.rededeapoio.service.PedidoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
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
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.UriComponentsBuilder;

@RestController
@RequestMapping("/api/pedidos")
@RequiredArgsConstructor
@Tag(name = "Pedidos de ajuda", description = "Abertura, aceite e conclusão dos pedidos de ajuda")
public class PedidoController {
    private final PedidoService service;

    @PostMapping
    @PreAuthorize("hasAnyRole('SISTEMA', 'COORDENADOR')")
    @SecurityRequirement(name = SpringDocConfig.CHAVE_SERVICO)
    @SecurityRequirement(name = SpringDocConfig.SECURITY_SCHEME)
    @Operation(summary = "Abre um pedido de ajuda",
            description = "Chamado pela API principal quando o cidadão faz o check-in \"preciso de ajuda\". "
                    + "O cidadão é confirmado na API principal antes de o pedido ser aberto.")
    @ApiResponse(responseCode = "201", description = "Pedido aberto")
    @ApiResponse(responseCode = "404", description = "Cidadão inexistente na API principal")
    @ApiResponse(responseCode = "409", description = "Já existe um pedido em andamento para o cidadão")
    @ApiResponse(responseCode = "503", description = "API principal indisponível")
    public ResponseEntity<DadosDetalhamentoPedido> abrirPedido(
            @RequestBody @Valid DadosAberturaPedido dados, UriComponentsBuilder uriBuilder) {
        DadosDetalhamentoPedido dto = service.abrirPedido(dados);
        var uri = uriBuilder.path("/api/pedidos/{id}").buildAndExpand(dto.id()).toUri();
        return ResponseEntity.created(uri).body(dto);
    }

    @GetMapping
    @PreAuthorize("hasAnyRole('AGENTE', 'COORDENADOR')")
    @SecurityRequirement(name = SpringDocConfig.SECURITY_SCHEME)
    @Operation(summary = "Lista os pedidos",
            description = "Sem filtro, traz os pedidos abertos e em atendimento, do mais antigo ao mais novo.")
    public ResponseEntity<Page<DadosDetalhamentoPedido>> listarPedidos(
            @Parameter(description = "Filtra por status") @RequestParam(required = false) StatusPedido status,
            @ParameterObject @PageableDefault(size = 10, sort = "abertoEm", direction = Sort.Direction.ASC) Pageable paginacao) {
        return ResponseEntity.ok(service.listarPedidos(status, paginacao));
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('AGENTE', 'COORDENADOR')")
    @SecurityRequirement(name = SpringDocConfig.SECURITY_SCHEME)
    @Operation(summary = "Detalha um pedido")
    @ApiResponse(responseCode = "404", description = "Id inexistente")
    public ResponseEntity<DadosDetalhamentoPedido> detalharPedido(@PathVariable Long id) {
        return ResponseEntity.ok(service.detalharPedido(id));
    }

    @PostMapping("/{id}/aceitar")
    @PreAuthorize("hasAnyRole('AGENTE', 'COORDENADOR')")
    @SecurityRequirement(name = SpringDocConfig.SECURITY_SCHEME)
    @Operation(summary = "Aceita um pedido aberto",
            description = "O pedido passa para EM_ATENDIMENTO com o agente logado. Cada agente atende no máximo 3 pedidos ao mesmo tempo.")
    @ApiResponse(responseCode = "200", description = "Pedido aceito")
    @ApiResponse(responseCode = "400", description = "Limite de atendimentos atingido")
    @ApiResponse(responseCode = "409", description = "Pedido já aceito por outro agente ou já concluído")
    public ResponseEntity<DadosDetalhamentoPedido> aceitarPedido(
            @PathVariable Long id, @AuthenticationPrincipal Agente agente) {
        return ResponseEntity.ok(service.aceitarPedido(id, agente));
    }

    @PostMapping("/{id}/concluir")
    @PreAuthorize("hasAnyRole('AGENTE', 'COORDENADOR')")
    @SecurityRequirement(name = SpringDocConfig.SECURITY_SCHEME)
    @Operation(summary = "Conclui um pedido em atendimento", description = "Somente o agente responsável pode concluir.")
    @ApiResponse(responseCode = "200", description = "Pedido concluído")
    @ApiResponse(responseCode = "400", description = "Pedido não está em atendimento")
    @ApiResponse(responseCode = "403", description = "Pedido está com outro agente")
    public ResponseEntity<DadosDetalhamentoPedido> concluirPedido(
            @PathVariable Long id, @RequestBody @Valid DadosConclusaoPedido dados, @AuthenticationPrincipal Agente agente) {
        return ResponseEntity.ok(service.concluirPedido(id, dados, agente));
    }
}
