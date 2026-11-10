package br.com.fiap3espg.rededeapoio.domain.pedido;

import br.com.fiap3espg.rededeapoio.domain.agente.Agente;
import br.com.fiap3espg.rededeapoio.domain.cidadao.DadosCidadao;
import jakarta.persistence.*;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

// Pedido de ajuda aberto quando um cidadao faz o check-in "preciso de ajuda"
// no app. Os dados do cidadao vem da API principal (C#): aqui so guardamos o
// necessario para o agente encontrar e atender a pessoa.
@Entity(name = "PedidoAjuda")
@Table(name = "pedidos_ajuda")
@NoArgsConstructor
@Getter
@EqualsAndHashCode(of = "id")
public class PedidoAjuda {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String cidadaoId;
    private String nomeCidadao;
    private String perfilCidadao;
    private Double latitude;
    private Double longitude;

    @Enumerated(EnumType.STRING)
    private StatusPedido status;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "agente_id")
    private Agente agente;

    private LocalDateTime abertoEm;
    private LocalDateTime aceitoEm;
    private LocalDateTime concluidoEm;
    private String observacao;

    // Bloqueio otimista: se dois agentes aceitarem o mesmo pedido ao mesmo tempo,
    // so o primeiro grava; o segundo recebe 409.
    @Version
    private Long versao;

    public PedidoAjuda(DadosCidadao cidadao, Double latitude, Double longitude, LocalDateTime agora) {
        this.cidadaoId = cidadao.id();
        this.nomeCidadao = cidadao.nome();
        this.perfilCidadao = cidadao.perfil();
        this.latitude = latitude;
        this.longitude = longitude;
        this.status = StatusPedido.ABERTO;
        this.abertoEm = agora;
    }

    public void aceitar(Agente responsavel, LocalDateTime agora) {
        this.agente = responsavel;
        this.status = StatusPedido.EM_ATENDIMENTO;
        this.aceitoEm = agora;
    }

    public void concluir(String observacao, LocalDateTime agora) {
        this.observacao = observacao;
        this.status = StatusPedido.CONCLUIDO;
        this.concluidoEm = agora;
    }

    public boolean pertenceA(Agente outro) {
        return agente != null && agente.getId() != null && agente.getId().equals(outro.getId());
    }
}
