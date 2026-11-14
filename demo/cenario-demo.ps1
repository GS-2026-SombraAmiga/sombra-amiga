# Prepara o cenario da demonstracao do app Sombra Amiga:
# 1. espera a API principal responder;
# 2. envia uma leitura de calor extremo do sensor da Praca da Sombra (simulado);
# 3. publica a previsao de calor para amanha, se ainda nao houver uma ativa.
# A leitura aparece no "Calor agora" do app por 3 horas.

# 127.0.0.1 em vez de localhost: o Windows tenta primeiro o IPv6, que a API nao escuta,
# e cada chamada demoraria cerca de 2 segundos a mais.
# Para a VM Linux de Operating Systems: -Api http://192.168.56.10/api
param([string]$api = 'http://127.0.0.1:5080/api')

Write-Host 'Esperando a API principal responder...'
$pronta = $false
for ($i = 0; $i -lt 90; $i++) {
    try {
        Invoke-RestMethod "$api/pontos" -TimeoutSec 5 | Out-Null
        $pronta = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $pronta) {
    Write-Host 'A API nao respondeu em 90 segundos. Confira a janela "API Sombra Amiga".'
    exit 1
}

$corpoLeitura = '{"pontoId":"11111111-1111-1111-1111-111111111111","temperaturaC":38,"umidadePct":50}'
$leitura = Invoke-RestMethod "$api/leituras" -Method Post -ContentType 'application/json' -Body $corpoLeitura
Write-Host ("Sensor da Praca da Sombra: sensacao de {0} C, nivel {1}." -f $leitura.indiceCalorC, $leitura.nivel)

$ativos = @(Invoke-RestMethod "$api/alertas/ativos")
if (-not ($ativos | Where-Object { $_.origem -eq 'Previsao' })) {
    # Acentos como escapes JSON (\u00e3 etc.), para nao depender da codificacao do terminal.
    $corpoPrevisao = '{"nivel":"Alto","mensagem":"Amanh\u00e3 a m\u00e1xima deve passar de 32 \u00b0C. Beba \u00e1gua e evite o sol entre 11h e 16h."}'
    Invoke-RestMethod "$api/alertas/previsao" -Method Post -ContentType 'application/json' -Body $corpoPrevisao | Out-Null
    Write-Host 'Previsao de calor para amanha publicada.'
} else {
    Write-Host 'A previsao de calor para amanha ja estava ativa.'
}

Write-Host ''
Write-Host 'Cenario pronto. O "Calor agora" mostra o risco por 3 horas.'
Write-Host 'Para renovar depois disso, de dois cliques em atualizar-calor-demo.cmd.'
