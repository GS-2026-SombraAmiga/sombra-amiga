using System.Reflection;
using System.Text.Json.Serialization;
using Microsoft.EntityFrameworkCore;
using SombraAmiga.Api;
using SombraAmiga.Infra;
using SombraAmiga.Infra.Dados;
using SombraAmiga.Infra.RedeDeApoio;

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddControllers()
    .AddJsonOptions(o => o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));

builder.Services.AdicionarInfra(p => p.GetRequiredService<IConfiguration>().GetConnectionString("Padrao")!);
builder.Services.AdicionarRedeDeApoio(p =>
{
    var configuracao = p.GetRequiredService<IConfiguration>();
    return new ConfiguracaoRedeDeApoio(configuracao["RedeDeApoio:Url"], configuracao["RedeDeApoio:Chave"]);
});

builder.Services.AddHealthChecks().AddCheck<VerificacaoBanco>("banco");
builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<TratadorDeErros>();
builder.Services.AddCors(o => o.AddDefaultPolicy(p => p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod()));

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(o =>
{
    var xml = Path.Combine(AppContext.BaseDirectory, $"{Assembly.GetExecutingAssembly().GetName().Name}.xml");
    o.IncludeXmlComments(xml);
});

var app = builder.Build();

await using (var escopo = app.Services.CreateAsyncScope())
{
    var contexto = escopo.ServiceProvider.GetRequiredService<SombraAmigaContexto>();
    await contexto.Database.MigrateAsync();
}

app.UseExceptionHandler();
app.UseCors();
app.UseSwagger();
app.UseSwaggerUI();
app.MapControllers();
app.MapHealthChecks("/api/saude");

await app.RunAsync();

public partial class Program;
