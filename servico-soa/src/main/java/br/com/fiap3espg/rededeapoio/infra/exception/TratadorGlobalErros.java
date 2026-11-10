package br.com.fiap3espg.rededeapoio.infra.exception;

import br.com.fiap3espg.rededeapoio.domain.ConflitoException;
import br.com.fiap3espg.rededeapoio.domain.ValidacaoException;
import br.com.fiap3espg.rededeapoio.domain.agente.AgenteNotFoundException;
import br.com.fiap3espg.rededeapoio.domain.cidadao.CidadaoNotFoundException;
import br.com.fiap3espg.rededeapoio.domain.pedido.AcessoPedidoNegadoException;
import br.com.fiap3espg.rededeapoio.domain.pedido.PedidoNotFoundException;
import br.com.fiap3espg.rededeapoio.infra.apiprincipal.ServicoExternoIndisponivelException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.orm.ObjectOptimisticLockingFailureException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.util.List;

@RestControllerAdvice
public class TratadorGlobalErros {

    @ExceptionHandler({
            AgenteNotFoundException.class,
            PedidoNotFoundException.class,
            CidadaoNotFoundException.class
    })
    public ResponseEntity<DadosMessage> tratarNaoEncontrado(RuntimeException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new DadosMessage(ex.getMessage()));
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<DadosMessage> tratarRotaInexistente() {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new DadosMessage("Recurso não encontrado."));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<List<DadosBadRequest>> tratarBadRequest(MethodArgumentNotValidException ex) {
        return ResponseEntity.badRequest().body(ex.getFieldErrors().stream().map(DadosBadRequest::new).toList());
    }

    @ExceptionHandler(ValidacaoException.class)
    public ResponseEntity<DadosMessage> tratarRegraDeNegocio(ValidacaoException ex) {
        return ResponseEntity.badRequest().body(new DadosMessage(ex.getMessage()));
    }

    // JSON malformado ou valor fora das opcoes de um enum.
    @ExceptionHandler({HttpMessageNotReadableException.class, MethodArgumentTypeMismatchException.class})
    public ResponseEntity<DadosMessage> tratarRequisicaoInvalida() {
        return ResponseEntity.badRequest().body(new DadosMessage("Requisição inválida: confira o formato dos dados."));
    }

    @ExceptionHandler(ConflitoException.class)
    public ResponseEntity<DadosMessage> tratarConflito(ConflitoException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(new DadosMessage(ex.getMessage()));
    }

    // Dois agentes aceitaram o mesmo pedido ao mesmo tempo (bloqueio otimista).
    @ExceptionHandler(ObjectOptimisticLockingFailureException.class)
    public ResponseEntity<DadosMessage> tratarConcorrencia() {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(new DadosMessage("O pedido foi alterado por outro agente. Atualize a lista e tente novamente."));
    }

    // Login invalido: a mensagem nao diz se o erro foi no e-mail ou na senha.
    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<DadosMessage> tratarFalhaAutenticacao() {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new DadosMessage("E-mail ou senha inválidos."));
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<DadosMessage> tratarAcessoNegado() {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(new DadosMessage("Seu perfil não tem permissão para esta ação."));
    }

    @ExceptionHandler(AcessoPedidoNegadoException.class)
    public ResponseEntity<DadosMessage> tratarAcessoPedidoNegado(AcessoPedidoNegadoException ex) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(new DadosMessage(ex.getMessage()));
    }

    @ExceptionHandler(ServicoExternoIndisponivelException.class)
    public ResponseEntity<DadosMessage> tratarServicoExterno(ServicoExternoIndisponivelException ex) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(new DadosMessage(ex.getMessage()));
    }
}
