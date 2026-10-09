# Financas do casal - publica o Worker que serve o app e guarda o cofre.
#
# Primeira vez: cria o banco D1, poe o id dele no wrangler.toml, cria a
# tabela e publica. Das outras vezes: so confere a tabela e publica.
# Precisa do wrangler (npm install -g wrangler); se nao estiver logado, ele
# abre o navegador para o login da Cloudflare.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "worker")

if (Get-Command wrangler -ErrorAction SilentlyContinue) { $usarNpx = $false }
elseif (Get-Command npx -ErrorAction SilentlyContinue) { $usarNpx = $true }
else {
  Write-Host "[ERRO] nao achei o wrangler nem o npx. Instale com:  npm install -g wrangler"
  exit 1
}
function W {
  if ($usarNpx) { & npx wrangler @args } else { & wrangler @args }
  if ($LASTEXITCODE) { throw "wrangler $args falhou (codigo $LASTEXITCODE)" }
}

$toml = Join-Path (Get-Location) "wrangler.toml"
$texto = [IO.File]::ReadAllText($toml)
if ($texto -match "COLE-AQUI") {
  Write-Host "Primeira vez: criando o banco financas-casal..."
  $saida = (W d1 create financas-casal 2>&1 | Out-String)
  Write-Host $saida
  if ($saida -notmatch '"?database_id"?\s*[=:]\s*"([0-9a-fA-F-]{36})"') {
    Write-Host "[ERRO] nao achei o database_id na resposta acima."
    Write-Host "       Se o banco ja existia, pegue o id com 'wrangler d1 list' e cole no wrangler.toml."
    exit 1
  }
  # Sem BOM: o wrangler nao gosta de TOML com BOM.
  [IO.File]::WriteAllText($toml, ($texto -replace "COLE-AQUI-O-ID-DO-wrangler-d1-create", $Matches[1]))
  Write-Host "database_id gravado no wrangler.toml."
}

Write-Host "Conferindo a tabela..."
W d1 execute financas-casal --remote --file schema.sql
Write-Host "Publicando..."
W deploy
Write-Host ""
Write-Host "Pronto. Abra o endereco https://... que o wrangler mostrou acima no celular,"
Write-Host "va em Configurar > Cada um no seu celular, gere a senha e conecte."
