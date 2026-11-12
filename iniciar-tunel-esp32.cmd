@echo off
rem ============================================================
rem  Sombra Amiga: tunel temporario para o ESP32 do Wokwi.
rem
rem  O Wokwi roda na nuvem e nao enxerga o seu computador. Este atalho
rem  cria um endereco publico (https://....trycloudflare.com) que leva
rem  para a API principal, que precisa estar rodando (iniciar-demo.cmd).
rem
rem  ATENCAO: enquanto esta janela estiver aberta, QUALQUER pessoa com o
rem  endereco consegue usar a API. Use so durante a demonstracao, com dados
rem  ficticios, e feche a janela ao terminar. O endereco muda a cada uso.
rem ============================================================
echo.
echo  Procure abaixo a linha com "https://....trycloudflare.com"
echo  e cole esse endereco na constante API_URL do sketch no Wokwi.
echo  Para encerrar o tunel, feche esta janela ou aperte Ctrl+C.
echo.
"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --no-autoupdate --url http://127.0.0.1:5080
