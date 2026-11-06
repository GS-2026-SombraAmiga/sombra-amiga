using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

namespace SombraAmiga.Infra.Dados;

/// <summary>
/// O SQLite não guarda o fuso da data. Sem esta marcação, a data volta do banco
/// sem o "Z" no JSON e o cliente a interpreta como horário local.
/// </summary>
public sealed class DataUtcConverter() : ValueConverter<DateTime, DateTime>(
    valor => valor,
    valor => DateTime.SpecifyKind(valor, DateTimeKind.Utc));
