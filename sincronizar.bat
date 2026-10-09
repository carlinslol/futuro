@echo off
REM Financas do casal - baixa as transacoes novas (Pluggy / Open Finance) e
REM sobe direto para o cofre do casal. Na primeira vez o financas_pluggy.py
REM cria o financas_config.txt; a senha do cofre vai em cofre_senha.
cd /d "%~dp0"
python financas_pluggy.py %*
if errorlevel 1 goto erro
where node >nul 2>&1
if errorlevel 1 (
  echo.
  echo [ERRO] nao achei o Node. Instale em https://nodejs.org e rode de novo.
  goto erro
)
node subir_cofre.mjs
if errorlevel 1 goto erro
echo.
pause
exit /b 0
:erro
echo.
pause
exit /b 1
