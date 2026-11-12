@echo off
rem ============================================================
rem  Sombra Amiga: abre o painel web no navegador.
rem  A API precisa estar rodando (iniciar-demo.cmd).
rem  Para fechar o painel, feche a janela "Painel Sombra Amiga".
rem ============================================================
start "Painel Sombra Amiga" /d "%~dp0web" cmd /k python -m http.server 8090 --bind 127.0.0.1
timeout /t 2 /nobreak >nul
start "" "http://localhost:8090/?api=http://127.0.0.1:5080"
