package br.com.fiap3espg.rededeapoio.service;

import br.com.fiap3espg.rededeapoio.domain.agente.AgenteRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

// Usado pelo AuthenticationManager no login: o "username" e o e-mail do agente.
@Service
@RequiredArgsConstructor
public class AutenticacaoService implements UserDetailsService {
    private final AgenteRepository repository;

    @Override
    public UserDetails loadUserByUsername(String email) {
        return repository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Agente não encontrado."));
    }
}
