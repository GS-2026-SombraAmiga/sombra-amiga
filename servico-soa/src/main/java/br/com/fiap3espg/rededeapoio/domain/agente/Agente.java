package br.com.fiap3espg.rededeapoio.domain.agente;

import jakarta.persistence.*;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;

// Agente comunitario de saude ou voluntario. Tambem e o usuario que faz login
// (o e-mail e o login), por isso implementa UserDetails.
@Entity(name = "Agente")
@Table(name = "agentes")
@NoArgsConstructor
@Getter
@EqualsAndHashCode(of = "id")
public class Agente implements UserDetails {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nome;
    private String email;
    private String senha;
    private String bairro;

    @Enumerated(EnumType.STRING)
    private TipoAgente tipo;

    @Enumerated(EnumType.STRING)
    private Perfil perfil;

    private boolean ativo;

    // A senha chega ja criptografada pelo service: a entidade nunca ve a senha pura.
    public Agente(DadosCadastroAgente dados, String senhaCriptografada) {
        this.ativo = true;
        this.nome = dados.nome();
        this.email = dados.email();
        this.senha = senhaCriptografada;
        this.bairro = dados.bairro();
        this.tipo = dados.tipo();
        this.perfil = dados.perfil();
    }

    // Somente nome e bairro sao alteraveis; e-mail, tipo e perfil sao fixos.
    public void atualizarInformacoes(DadosAtualizacaoAgente dados) {
        if (dados.nome() != null && !dados.nome().isBlank()) {
            this.nome = dados.nome();
        }
        if (dados.bairro() != null && !dados.bairro().isBlank()) {
            this.bairro = dados.bairro();
        }
    }

    public void desativar() {
        this.ativo = false;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_" + perfil.name()));
    }

    @Override
    public String getPassword() {
        return senha;
    }

    @Override
    public String getUsername() {
        return email;
    }

    // Agente desativado nao consegue fazer login.
    @Override
    public boolean isEnabled() {
        return ativo;
    }
}
