param()

$python = ".\.venv\Scripts\python.exe"
if (!(Test-Path $python)) {
    Write-Error "No se encontro .venv. Crea el entorno primero."
    exit 1
}

& $python -m src.main
