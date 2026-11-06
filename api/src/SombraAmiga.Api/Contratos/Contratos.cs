using System.ComponentModel.DataAnnotations;
using SombraAmiga.Dominio.Comum;
using SombraAmiga.Dominio.Entidades;

namespace SombraAmiga.Api.Contratos;

public sealed record CadastrarCidadaoRequisicao(
    [Required] PerfilCidadao? Perfil,
    [Required, StringLength(120)] string Nome,
    [Required] string Cpf,
    [Required, StringLength(120)] string ContatoFamiliar,
    [StringLength(250)] string? CondicaoSaude,
    [StringLength(80)] string? Ocupacao);

public sealed record AtualizarCidadaoRequisicao(
    [Required, StringLength(120)] string Nome,
    [Required, StringLength(120)] string ContatoFamiliar,
    [StringLength(250)] string? CondicaoSaude);

/// <summary>Resposta sem CPF completo, contato ou condição de saúde.</summary>
public sealed record CidadaoResposta(Guid Id, string Nome, string CpfMascarado, PerfilCidadao Perfil, bool TemCondicaoSaude)
{
    public static CidadaoResposta De(Cidadao c) => new(c.Id, c.Nome, c.Cpf.Mascarado, c.Perfil, c.TemCondicaoSaude);
}

public sealed record PontoRequisicao(
    [Required, StringLength(120)] string Nome,
    [Required] TipoPonto? Tipo,
    [Required, Range(-90, 90)] double? Latitude,
    [Required, Range(-180, 180)] double? Longitude);

public sealed record PontoResposta(Guid Id, string Nome, TipoPonto Tipo, double Latitude, double Longitude, double? DistanciaKm = null)
{
    public static PontoResposta De(PontoHidratacao p, double? distanciaKm = null) =>
        new(p.Id, p.Nome, p.Tipo, p.Latitude, p.Longitude, distanciaKm);
}

public sealed record LeituraRequisicao(
    [Required] Guid? PontoId,
    [Required] double? TemperaturaC,
    [Required] double? UmidadePct);

public sealed record LeituraResposta(Guid Id, Guid PontoId, double TemperaturaC, double UmidadePct, double IndiceCalorC, NivelRisco Nivel, DateTime DataHoraUtc)
{
    public static LeituraResposta De(LeituraSensor l) =>
        new(l.Id, l.PontoId, l.TemperaturaC, l.UmidadePct, l.IndiceCalorC, l.Nivel, l.DataHoraUtc);
}

public sealed record PrevisaoRequisicao(
    [Required] NivelRisco? Nivel,
    [Required, StringLength(300)] string Mensagem);

public sealed record AlertaResposta(Guid Id, NivelRisco Nivel, OrigemAlerta Origem, string Mensagem, Guid? PontoId, DateTime CriadoEmUtc, bool Ativo)
{
    public static AlertaResposta De(Alerta a) =>
        new(a.Id, a.Nivel, a.Origem, a.Mensagem, a.PontoId, a.CriadoEmUtc, a.Ativo);
}

public sealed record CheckInRequisicao(
    [Required] Guid? CidadaoId,
    [Required] StatusCheckIn? Status);

public sealed record CheckInResposta(Guid Id, Guid CidadaoId, StatusCheckIn Status, DateTime DataHoraUtc)
{
    public static CheckInResposta De(CheckIn c) => new(c.Id, c.CidadaoId, c.Status, c.DataHoraUtc);
}
