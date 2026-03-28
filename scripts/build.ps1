param()

$python = ".\.venv\Scripts\python.exe"
if (!(Test-Path $python)) {
    Write-Error "No se encontro .venv. Crea el entorno primero."
    exit 1
}

& $python -m pip show pyinstaller | Out-Null
if ($LASTEXITCODE -ne 0) {
    & $python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Error "No se pudo instalar PyInstaller."
        exit 1
    }
}

& $python -m PyInstaller --noconfirm --clean btrack_prototype.spec

if ($LASTEXITCODE -eq 0) {
    Write-Output "Build completado en dist/BTrackPrototype"
}
