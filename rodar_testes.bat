@echo off
REM Financas do casal - roda todos os testes.
cd /d "%~dp0"
set FALHOU=0
node testes\financas.js || set FALHOU=1
node testes\financas_worker.mjs || set FALHOU=1
node testes\subir_cofre.mjs || set FALHOU=1
python testes\financas_pluggy.py || set FALHOU=1
echo.
if "%FALHOU%"=="1" (echo  ALGUM TESTE FALHOU) else (echo  Tudo verde.)
echo.
pause
