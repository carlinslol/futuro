@echo off
REM Financas do casal - baixa as transacoes novas (Pluggy / Open Finance) e
REM sobe direto para o cofre do casal. Na primeira vez o financas_pluggy.py
REM cria o financas_config.txt; a senha do cofre vai em cofre_senha.
REM
REM   sincronizar.bat          mostra tudo e espera uma tecla no fim
REM   sincronizar.bat /auto    o da tarefa agendada (agendar.bat): sem pausa;
REM                            o sincronizar_oculto.vbs grava em sincronizar.log
setlocal
cd /d "%~dp0"
set AUTO=
set ARGS=%*
if /I "%~1"=="/auto" (
  set AUTO=1
  set ARGS=
  set PYTHONIOENCODING=utf-8
  echo.
  echo ===== %date% %time% =====
)
set CODIGO=1
python financas_pluggy.py %ARGS%
if errorlevel 1 goto fim
where node >/dev/null 2>&1
if errorlevel 1 (
  echo.
  echo [ERRO] nao achei o Node. Instale em https://nodejs.org e rode de novo.
  goto fim
)
node subir_cofre.mjs
if errorlevel 1 goto fim
set CODIGO=0
:fim
if not defined AUTO (
  echo.
  pause
)
exit /b %CODIGO%
