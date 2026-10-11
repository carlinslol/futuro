# Financas do casal - agenda o sincronizar no Agendador de Tarefas do Windows.
# ASCII puro de proposito: o Windows PowerShell 5.1 le .ps1 sem BOM como CP1252,
# e um caractere acentuado quebra o parser.
#
#   agendar.bat                 todo dia as 08:00 e as 20:00, e ao entrar no Windows
#   agendar.bat 07:30           so nesse horario (e ao entrar no Windows)
#   agendar.bat 07:30 13:00     varios horarios
#   agendar.bat remover         tira a tarefa
param(
    [string]$Horarios = "08:00 20:00",
    [switch]$Remover
)

$ErrorActionPreference = "Stop"
$Nome = "Financas do Casal - sincronizar"
$Pasta = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bat = Join-Path $Pasta "sincronizar.bat"
$Vbs = Join-Path $Pasta "sincronizar_oculto.vbs"
$Log = Join-Path $Pasta "sincronizar.log"

function Fim($codigo) {
    Write-Host ""
    Write-Host "Pressione Enter para fechar..." -ForegroundColor DarkGray
    [void][Console]::ReadLine()
    exit $codigo
}

Write-Host ""
Write-Host "Financas do Casal - sincronizar sozinho" -ForegroundColor Cyan
Write-Host "pasta: $Pasta"
Write-Host ""

if ($Remover) {
    try {
        Unregister-ScheduledTask -TaskName $Nome -Confirm:$false
        Write-Host "[ok] tarefa removida. O sincronizar.bat continua funcionando na mao." -ForegroundColor Green
    } catch {
        Write-Host "[!] nao havia tarefa com esse nome." -ForegroundColor Yellow
    }
    Fim 0
}

foreach ($arq in @($Bat, $Vbs, (Join-Path $Pasta "financas_config.txt"))) {
    if (-not (Test-Path $arq)) {
        Write-Host "[ERRO] nao achei $(Split-Path -Leaf $arq) nesta pasta." -ForegroundColor Red
        if ($arq -like "*financas_config.txt") {
            Write-Host "       Rode o sincronizar.bat na mao uma vez antes, para conferir que funciona."
        }
        Fim 1
    }
}

# horarios: "08:00 20:00" ou "08:00,20:00"
$lista = @($Horarios -split "[ ,;]+" | Where-Object { $_ })
$horas = @()
foreach ($h in $lista) {
    if ($h -notmatch '^([01]?\d|2[0-3]):([0-5]\d)$') {
        Write-Host "[ERRO] horario invalido: '$h'. Use HH:MM, por exemplo 07:30." -ForegroundColor Red
        Fim 1
    }
    $horas += [datetime]::Today.AddHours([int]$Matches[1]).AddMinutes([int]$Matches[2])
}
if (-not $horas.Count) {
    Write-Host "[ERRO] nenhum horario." -ForegroundColor Red
    Fim 1
}

# Um gatilho diario por horario, mais um ao entrar no Windows (com 2 minutos
# de folga para a internet subir). StartWhenAvailable: se o PC estava
# desligado na hora marcada, roda assim que ligar.
$gatilhos = @()
foreach ($t in $horas) { $gatilhos += New-ScheduledTaskTrigger -Daily -At $t }
$logon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$logon.Delay = "PT2M"
$gatilhos += $logon

# A tarefa chama o .vbs (sem janela), que chama o .bat e grava o log.
$wscript = Join-Path $env:SystemRoot "System32\wscript.exe"
$acao = New-ScheduledTaskAction -Execute $wscript -Argument ('//nologo "' + $Vbs + '"') -WorkingDirectory $Pasta
$cfg = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
        -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
        -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries
# Roda como voce, so com voce logado: nao pede senha, e o Python e o Node
# do seu usuario estao no caminho.
$quem = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

$textoHoras = ($horas | ForEach-Object { $_.ToString("HH:mm") }) -join ", "
try {
    Register-ScheduledTask -TaskName $Nome -Action $acao -Trigger $gatilhos -Settings $cfg -Principal $quem `
        -Description "Baixa as transacoes do Meu Pluggy e sobe para o cofre do casal" -Force | Out-Null
    Write-Host "[ok] tarefa registrada: todo dia as $textoHoras, e ao entrar no Windows." -ForegroundColor Green
} catch {
    Write-Host "[!] Register-ScheduledTask falhou: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "    tentando pelo schtasks.exe (so o primeiro horario)..."
    $alvo = '"' + $wscript + '" //nologo "' + $Vbs + '"'
    $r = schtasks.exe /Create /TN $Nome /TR $alvo /SC DAILY /ST $horas[0].ToString("HH:mm") /F 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] o schtasks tambem falhou:" -ForegroundColor Red
        Write-Host "       $r"
        Fim 1
    }
    Write-Host "[ok] registrada pelo schtasks: todo dia as $($horas[0].ToString('HH:mm'))." -ForegroundColor Green
}

Write-Host ""
Write-Host "Rodando uma vez agora para conferir (leva ate um minuto)..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $Nome
$fim = (Get-Date).AddSeconds(90)
do {
    Start-Sleep -Seconds 3
    $estado = (Get-ScheduledTask -TaskName $Nome).State
} while ($estado -eq "Running" -and (Get-Date) -lt $fim)

$info = Get-ScheduledTaskInfo -TaskName $Nome
if ($estado -eq "Running") {
    Write-Host "[..] ainda rodando; confira o sincronizar.log daqui a pouco." -ForegroundColor Yellow
} elseif ($info.LastTaskResult -eq 0) {
    Write-Host "[ok] rodou certo." -ForegroundColor Green
} else {
    Write-Host "[!] terminou com codigo $($info.LastTaskResult). Veja o sincronizar.log:" -ForegroundColor Yellow
}
if (Test-Path $Log) {
    $novo = Get-Content $Log -Encoding UTF8 -Tail 12
    Write-Host ""
    Write-Host "--- fim do sincronizar.log ---" -ForegroundColor DarkGray
    $novo | ForEach-Object { Write-Host "  $_" }
}
Write-Host ""
Write-Host "Proxima execucao: $($info.NextRunTime)"
Write-Host "Para tirar: agendar.bat remover" -ForegroundColor DarkGray
Fim 0
