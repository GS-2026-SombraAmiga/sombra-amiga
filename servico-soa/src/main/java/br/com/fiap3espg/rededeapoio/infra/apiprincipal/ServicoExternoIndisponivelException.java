package br.com.fiap3espg.rededeapoio.infra.apiprincipal;

// A API principal esta fora do ar ou nao respondeu a tempo. Responde 503.
public class ServicoExternoIndisponivelException extends RuntimeException {
    public ServicoExternoIndisponivelException(String mensagem, Throwable causa) {
        super(mensagem, causa);
    }
}
