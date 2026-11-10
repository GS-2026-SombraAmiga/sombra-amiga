package br.com.fiap3espg.rededeapoio.service;

import br.com.fiap3espg.rededeapoio.domain.ValidacaoException;
import br.com.fiap3espg.rededeapoio.domain.agente.*;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AgenteService {
    private final AgenteRepository repository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public DadosDetalhamentoAgente cadastrarAgente(DadosCadastroAgente dados) {
        // O e-mail e unico na tabela; validar antes evita um erro 500 do banco.
        if (repository.existsByEmail(dados.email())) {
            throw new ValidacaoException("Já existe um agente cadastrado com o e-mail informado.");
        }
        Agente agente = new Agente(dados, passwordEncoder.encode(dados.senha()));
        return new DadosDetalhamentoAgente(repository.save(agente));
    }

    @Transactional(readOnly = true)
    public Page<DadosListagemAgente> listarAgentes(Pageable paginacao) {
        return repository.findAllByAtivoTrue(paginacao).map(DadosListagemAgente::new);
    }

    @Transactional(readOnly = true)
    public DadosDetalhamentoAgente detalharAgente(Long id) {
        return new DadosDetalhamentoAgente(buscarAgente(id));
    }

    @Transactional
    public DadosDetalhamentoAgente atualizarAgente(Long id, DadosAtualizacaoAgente dados) {
        Agente agente = buscarAgente(id);
        agente.atualizarInformacoes(dados);
        return new DadosDetalhamentoAgente(agente);
    }

    // Exclusao logica: o historico de atendimentos do agente continua valido.
    @Transactional
    public void desativarAgente(Long id) {
        buscarAgente(id).desativar();
    }

    private Agente buscarAgente(Long id) {
        return repository.findById(id).orElseThrow(() -> new AgenteNotFoundException(id));
    }
}
