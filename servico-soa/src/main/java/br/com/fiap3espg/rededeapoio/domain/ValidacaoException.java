package br.com.fiap3espg.rededeapoio.domain;

// Regra de negocio violada. O TratadorGlobalErros responde 400.
public class ValidacaoException extends RuntimeException {
    public ValidacaoException(String mensagem) {
        super(mensagem);
    }
}
