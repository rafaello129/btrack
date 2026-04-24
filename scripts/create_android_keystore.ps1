param(
    [string]$StoreFile = "keystore/btrack-release.jks",
    [string]$Alias = "btrack",
    [string]$StorePass = "CHANGE_ME",
    [string]$KeyPass = "CHANGE_ME"
)

if (!(Get-Command keytool -ErrorAction SilentlyContinue)) {
    Write-Error "No se encontro keytool. Instala JDK 17 y agrega keytool al PATH."
    exit 1
}

$target = Join-Path (Get-Location) $StoreFile
$targetDir = Split-Path -Parent $target
if (!(Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

keytool -genkeypair `
  -v `
  -keystore $target `
  -alias $Alias `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000 `
  -storepass $StorePass `
  -keypass $KeyPass `
  -dname "CN=BTrack, OU=Mobile, O=BTrack, L=Cancun, S=Quintana Roo, C=MX"

if ($LASTEXITCODE -eq 0) {
    Write-Output "Keystore generado: $target"
}
