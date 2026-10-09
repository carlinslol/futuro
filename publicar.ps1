# Financas do casal - publica o Worker que serve o app e guarda o cofre.
#
# Primeira vez: faz o login na Cloudflare (abre o navegador), cria o banco D1,
# poe o id dele no wrangler.toml, cria a tabela e publica. Das outras vezes:
# so confere a tabela e publica.
# Precisa do Node e do wrangler (npm install -g wrangler).
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "worker")

if (Get-Command wrangler -ErrorAction SilentlyContinue) { $usarNpx = $false }
elseif (Get-Command npx -ErrorAction SilentlyContinue) { $usarNpx = $true }
else {
  Write-Host "[ERRO] nao achei o wrangler nem o npx. Instale o Node e depois:  npm install -g wrangler"
  exit 1
}

# O wrangler escreve avisos no stderr. No Windows PowerShell 5.1, com
# ErrorActionPreference = Stop, uma linha no stderr de programa externo pode
# virar erro fatal - por isso, dentro destas funcoes, vale "Continue", e quem
# decide se deu certo e o codigo de saida do wrangler.
function W {
  $ErrorActionPreference = "Continue"
  if ($usarNpx) { & npx wrangler @args } else { & wrangler @args }
  if ($LASTEXITCODE) { throw "wrangler $args falhou (codigo $LASTEXITCODE)" }
}
function Capturar {
  $ErrorActionPreference = "Continue"
  if ($usarNpx) { $s = & npx wrangler @args 2>$null } else { $s = & wrangler @args 2>$null }
  return [pscustomobject]@{ Codigo = $LASTEXITCODE; Texto = ($s | Out-String) }
}

# Com a saida capturada o wrangler se acha "nao interativo" e nao pede login
# sozinho: o login tem de vir antes, aqui, com a janela do navegador.
$quem = Capturar whoami
if ($quem.Codigo -or $quem.Texto -match "not authenticated") {
  Write-Host "Entrando na Cloudflare (vai abrir o navegador)..."
  W login
}

# O id do banco vem da lista em JSON, e nao do texto do 'd1 create', que
# muda de formato entre versoes do wrangler. Serve tambem quando o banco ja
# existe (por exemplo, se uma tentativa anterior parou no meio).
function IdDoBanco {
  $r = Capturar d1 list --json
  if ($r.Codigo) { throw "wrangler d1 list falhou (codigo $($r.Codigo))" }
  $json = [regex]::Match($r.Texto, "(?s)\[.*\]").Value
  if (-not $json) { return $null }
  $banco = @($json | ConvertFrom-Json) | Where-Object { $_.name -eq "financas-casal" } | Select-Object -First 1
  if (-not $banco) { return $null }
  if ($banco.uuid) { return $banco.uuid }
  return $banco.database_id
}

$toml = Join-Path (Get-Location) "wrangler.toml"
$texto = [IO.File]::ReadAllText($toml)
if ($texto -match "COLE-AQUI") {
  $id = IdDoBanco
  if (-not $id) {
    Write-Host "Primeira vez: criando o banco financas-casal..."
    W d1 create financas-casal
    $id = IdDoBanco
  } else {
    Write-Host "O banco financas-casal ja existe; usando ele."
  }
  if (-not $id) {
    Write-Host "[ERRO] nao achei o id do banco financas-casal."
    Write-Host "       Rode 'wrangler d1 list', copie o id dele e cole no worker\wrangler.toml."
    exit 1
  }
  # Sem BOM: o wrangler nao gosta de TOML com BOM.
  [IO.File]::WriteAllText($toml, ($texto -replace "COLE-AQUI-O-ID-DO-wrangler-d1-create", $id))
  Write-Host "database_id $id gravado no worker\wrangler.toml (pode commitar: nao e segredo)."
}

Write-Host "Conferindo a tabela..."
W d1 execute financas-casal --remote --file schema.sql
Write-Host "Publicando..."
W deploy
Write-Host ""
Write-Host "Pronto. Abra no celular o endereco https://... que o wrangler mostrou acima,"
Write-Host "va em Configurar > Cada um no seu celular, gere a senha e conecte."
