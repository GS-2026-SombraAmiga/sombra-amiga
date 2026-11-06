using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace SombraAmiga.Infra.Dados.Migracoes
{
    /// <inheritdoc />
    public partial class Inicial : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Cidadaos",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    Nome = table.Column<string>(type: "TEXT", maxLength: 120, nullable: false),
                    Cpf = table.Column<string>(type: "TEXT", maxLength: 11, nullable: false),
                    ContatoFamiliar = table.Column<string>(type: "TEXT", maxLength: 120, nullable: false),
                    CondicaoSaude = table.Column<string>(type: "TEXT", maxLength: 250, nullable: true),
                    Tipo = table.Column<string>(type: "TEXT", maxLength: 21, nullable: false),
                    Ocupacao = table.Column<string>(type: "TEXT", maxLength: 80, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Cidadaos", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Pontos",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    Nome = table.Column<string>(type: "TEXT", maxLength: 120, nullable: false),
                    Tipo = table.Column<string>(type: "TEXT", nullable: false),
                    Latitude = table.Column<double>(type: "REAL", nullable: false),
                    Longitude = table.Column<double>(type: "REAL", nullable: false),
                    Ativo = table.Column<bool>(type: "INTEGER", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Pontos", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "CheckIns",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    CidadaoId = table.Column<Guid>(type: "TEXT", nullable: false),
                    Status = table.Column<string>(type: "TEXT", nullable: false),
                    DataHoraUtc = table.Column<DateTime>(type: "TEXT", nullable: false),
                    DiaLocal = table.Column<DateOnly>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CheckIns", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CheckIns_Cidadaos_CidadaoId",
                        column: x => x.CidadaoId,
                        principalTable: "Cidadaos",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Alertas",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    Nivel = table.Column<string>(type: "TEXT", nullable: false),
                    Origem = table.Column<string>(type: "TEXT", nullable: false),
                    Mensagem = table.Column<string>(type: "TEXT", maxLength: 300, nullable: false),
                    PontoId = table.Column<Guid>(type: "TEXT", nullable: true),
                    CriadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: false),
                    DiaLocal = table.Column<DateOnly>(type: "TEXT", nullable: false),
                    EncerradoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Alertas", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Alertas_Pontos_PontoId",
                        column: x => x.PontoId,
                        principalTable: "Pontos",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "Leituras",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    PontoId = table.Column<Guid>(type: "TEXT", nullable: false),
                    TemperaturaC = table.Column<double>(type: "REAL", nullable: false),
                    UmidadePct = table.Column<double>(type: "REAL", nullable: false),
                    IndiceCalorC = table.Column<double>(type: "REAL", nullable: false),
                    Nivel = table.Column<string>(type: "TEXT", nullable: false),
                    DataHoraUtc = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Leituras", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Leituras_Pontos_PontoId",
                        column: x => x.PontoId,
                        principalTable: "Pontos",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.InsertData(
                table: "Pontos",
                columns: new[] { "Id", "Ativo", "Latitude", "Longitude", "Nome", "Tipo" },
                values: new object[,]
                {
                    { new Guid("11111111-1111-1111-1111-111111111111"), true, -23.462, -46.680999999999997, "Praça da Sombra (simulado)", "SombraEAgua" },
                    { new Guid("22222222-2222-2222-2222-222222222222"), true, -23.468499999999999, -46.6755, "Bebedouro da UBS (simulado)", "Agua" },
                    { new Guid("33333333-3333-3333-3333-333333333333"), true, -23.454999999999998, -46.689, "Abrigo do Terminal (simulado)", "Sombra" }
                });

            migrationBuilder.CreateIndex(
                name: "IX_Alertas_DiaLocal",
                table: "Alertas",
                column: "DiaLocal");

            migrationBuilder.CreateIndex(
                name: "IX_Alertas_PontoId",
                table: "Alertas",
                column: "PontoId");

            migrationBuilder.CreateIndex(
                name: "IX_CheckIns_CidadaoId_DiaLocal",
                table: "CheckIns",
                columns: new[] { "CidadaoId", "DiaLocal" });

            migrationBuilder.CreateIndex(
                name: "IX_Cidadaos_Cpf",
                table: "Cidadaos",
                column: "Cpf",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Leituras_PontoId_DataHoraUtc",
                table: "Leituras",
                columns: new[] { "PontoId", "DataHoraUtc" });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Alertas");

            migrationBuilder.DropTable(
                name: "CheckIns");

            migrationBuilder.DropTable(
                name: "Leituras");

            migrationBuilder.DropTable(
                name: "Cidadaos");

            migrationBuilder.DropTable(
                name: "Pontos");
        }
    }
}
