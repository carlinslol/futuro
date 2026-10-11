@echo off
REM Financas do casal - faz o Windows rodar o sincronizar sozinho, sem janela.
REM
REM   agendar.bat                 todo dia as 08:00 e as 20:00, e ao entrar no Windows
REM   agendar.bat 07:30           so nesse horario (e ao entrar no Windows)
REM   agendar.bat 07:30 13:00     varios horarios
REM   agendar.bat remover         tira a tarefa
REM
REM O que cada rodada fez fica no sincronizar.log, nesta pasta.
REM Este .bat so contorna a politica de execucao e a marca de "arquivo
REM baixado da internet", que fazem o .ps1 fechar sem dizer nada.
setlocal
cd /d "%~dp0"
set ARG=
if /I "%~1"=="remover" set ARG=-Remover
if not "%~1"=="" if /I not "%~1"=="remover" set ARG=-Horarios "%*"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -Path '%~dp0agendar.ps1' -ErrorAction SilentlyContinue"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0agendar.ps1" %ARG%
if errorlevel 1 (
  echo.
  echo [ERRO] o PowerShell nao conseguiu executar o agendar.ps1. Codigo: %errorlevel%
  pause
)
