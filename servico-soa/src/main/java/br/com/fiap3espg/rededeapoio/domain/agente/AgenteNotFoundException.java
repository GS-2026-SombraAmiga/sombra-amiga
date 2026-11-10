package br.com.fiap3espg.rededeapoio.domain.agente;

public class AgenteNotFoundException extends RuntimeException {
    public AgenteNotFoundException(Long id) {
        super("Agente com id " + id + " não encontrado.");
    }
}
