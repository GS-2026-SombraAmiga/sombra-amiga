@echo off
chcp 65001 >nul
rem ============================================================
rem  Sombra Amiga: sobe a API principal e o app para abrir no
rem  celular com o Expo Go. Basta dar dois cliques neste arquivo.
rem ============================================================

rem IP do computador na rede de casa (a conexao que tem acesso a internet).
rem Sem isso, o Expo pode escolher a rede do VirtualBox ou da VPN, e o celular nao conecta.
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null -and $_.NetAdapter.Status -eq 'Up' } | Select-Object -First 1).IPv4Address.IPAddress"`) do set IP_PC=%%i

if "%IP_PC%"=="" (
  echo Nao foi possivel descobrir o IP do computador na rede.
  pause
  exit /b 1
)

echo.
echo  IP do computador na rede: %IP_PC%
echo  API principal: http://%IP_PC%:5080/swagger
echo.
echo  Abrindo duas janelas: a API e o app.
echo  No iPhone, abra a Camera e aponte para o QR code da janela do app.
echo.

start "API Sombra Amiga" /d "%~dp0api" cmd /k dotnet run --project src\SombraAmiga.Api --urls http://0.0.0.0:5080

set REACT_NATIVE_PACKAGER_HOSTNAME=%IP_PC%
start "App Sombra Amiga" /d "%~dp0mobile" cmd /k npx expo start

rem Opcional, para o pedido de ajuda chegar a Rede de Apoio (precisa do MySQL ligado):
rem start "Rede de Apoio" /d "%~dp0servico-soa" cmd /k mvnw.cmd spring-boot:run
