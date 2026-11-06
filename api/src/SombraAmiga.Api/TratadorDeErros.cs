using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using SombraAmiga.Dominio.Comum;

namespace SombraAmiga.Api;

/// <summary>Converte exceções do domínio em respostas ProblemDetails.</summary>
public sealed class TratadorDeErros : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(HttpContext contexto, Exception excecao, CancellationToken ct)
    {
        var status = excecao switch
        {
            NaoEncontradoException => StatusCodes.Status404NotFound,
            ConflitoException => StatusCodes.Status409Conflict,
            DominioException => StatusCodes.Status400BadRequest,
            _ => (int?)null,
        };

        if (status is null)
            return false;

        contexto.Response.StatusCode = status.Value;
        await contexto.Response.WriteAsJsonAsync(
            new ProblemDetails { Status = status, Title = excecao.Message },
            options: null,
            contentType: "application/problem+json",
            cancellationToken: ct);
        return true;
    }
}
