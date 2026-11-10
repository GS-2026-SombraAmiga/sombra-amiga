package br.com.fiap3espg.rededeapoio.domain.cidadao;

import java.util.UUID;

public class CidadaoNotFoundException extends RuntimeException {
    public CidadaoNotFoundException(UUID id) {
        super("Cidadão " + id + " não encontrado na API principal.");
    }
}
