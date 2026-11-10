package br.com.fiap3espg.rededeapoio.domain;

// A operacao conflita com o estado atual do recurso (ex.: pedido ja aceito por
// outro agente). O TratadorGlobalErros responde 409.
public class ConflitoException extends RuntimeException {
    public ConflitoException(String mensagem) {
        super(mensagem);
    }
}
