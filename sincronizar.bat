@echo off
REM Financas do casal - baixa as transacoes novas das duas contas (Pluggy /
REM Open Finance) e abre o app. Na primeira vez ele cria o financas_config.txt.
cd /d "%~dp0"
python financas_pluggy.py %*
if errorlevel 1 (
  echo.
  pause
  exit /b 1
)
start "" "financas.html"
