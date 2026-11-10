package br.com.fiap3espg.rededeapoio.domain.agente;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AgenteRepository extends JpaRepository<Agente, Long> {
    Optional<Agente> findByEmail(String email);

    boolean existsByEmail(String email);

    Page<Agente> findAllByAtivoTrue(Pageable paginacao);
}
