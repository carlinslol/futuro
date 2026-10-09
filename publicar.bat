@echo off
REM Financas do casal - publica o app e o cofre no Cloudflare (Worker + D1).
REM Na primeira vez cria o banco sozinho. Depois, rode de novo sempre que o
REM financas.html mudar: o app vai embutido no Worker.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0publicar.ps1"
echo.
pause
