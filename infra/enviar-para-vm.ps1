# Gera o pacote da Sombra Amiga no Windows e envia para a VM pelo SSH.
#   pacote/api     API publicada para Linux (precisa do runtime ASP.NET Core 10, instalado pelo 02)
#   pacote/painel  painel web estático
#   infra/         scripts de provisionamento
# Uso (na raiz do repositório): powershell -ExecutionPolicy Bypass -File infra\enviar-para-vm.ps1
param(
    [string]$Endereco = "127.0.0.1",
    [int]$Porta = 2222,
    [string]$Usuario = "sombra",
    [string]$Chave = "$env:USERPROFILE\.ssh\sombra_amiga_vm"
)
$ErrorActionPreference = "Stop"

$raiz = Split-Path -Parent $PSScriptRoot
$trabalho = Join-Path $env:TEMP "sombra-amiga-pacote"
$destino = Join-Path $trabalho "sombra-amiga"
$arquivo = Join-Path $trabalho "sombra-amiga.tar.gz"

Write-Host "==> Limpando $trabalho"
if (Test-Path $trabalho) { Remove-Item -Recurse -Force $trabalho }
New-Item -ItemType Directory -Force "$destino\pacote\painel", "$destino\infra" | Out-Null

Write-Host "==> Publicando a API para Linux (linux-x64)"
dotnet publish "$raiz\api\src\SombraAmiga.Api" -c Release -r linux-x64 --self-contained false -o "$destino\pacote\api" --nologo -v q
if ($LASTEXITCODE -ne 0) { throw "dotnet publish falhou" }

Write-Host "==> Copiando o painel e os scripts"
Copy-Item -Recurse "$raiz\web\*" "$destino\pacote\painel"
Copy-Item -Recurse "$raiz\infra\*.sh", "$raiz\infra\lib" "$destino\infra"

Write-Host "==> Compactando"
tar -czf $arquivo -C $trabalho sombra-amiga
if ($LASTEXITCODE -ne 0) { throw "tar falhou" }
"{0:N1} MB" -f ((Get-Item $arquivo).Length / 1MB) | Write-Host

Write-Host "==> Enviando para $Usuario@${Endereco}:$Porta"
scp -i $Chave -P $Porta $arquivo "${Usuario}@${Endereco}:~/sombra-amiga.tar.gz"
if ($LASTEXITCODE -ne 0) { throw "scp falhou" }

# Na VM: extrai em ~/sombra-amiga e garante fim de linha Unix nos scripts.
$comando = "rm -rf ~/sombra-amiga && tar -xzf ~/sombra-amiga.tar.gz -C ~ && rm ~/sombra-amiga.tar.gz && " +
           "find ~/sombra-amiga/infra -name '*.sh' -exec sed -i 's/\r$//' {} + && ls ~/sombra-amiga ~/sombra-amiga/infra"
ssh -i $Chave -p $Porta "${Usuario}@${Endereco}" $comando
if ($LASTEXITCODE -ne 0) { throw "extração na VM falhou" }

Write-Host ""
Write-Host "Pronto. Na VM, rode:  cd ~/sombra-amiga/infra && sudo bash provisionar.sh"
