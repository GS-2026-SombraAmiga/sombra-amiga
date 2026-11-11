@echo off
rem Renova o cenario da demonstracao: nova leitura de calor extremo e previsao para amanha.
rem Use quando a API ja estiver rodando e o "Calor agora" do app tiver sumido (a leitura vale 3 horas).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0demo\cenario-demo.ps1"
pause
