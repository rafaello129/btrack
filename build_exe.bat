@echo off
REM ============================================
REM NeuroFace - Script de compilación
REM Genera el ejecutable portable
REM ============================================

echo.
echo ========================================
echo   NEUROFACE - Generador de Ejecutable
echo ========================================
echo.

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Verificar PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

REM Limpiar builds anteriores
echo Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist\NeuroFace.exe" del /f "dist\NeuroFace.exe"

REM Compilar
echo.
echo Compilando NeuroFace...
echo Esto puede tomar varios minutos...
echo.

pyinstaller NeuroFace.spec --clean

REM Verificar resultado
echo.
if exist "dist\NeuroFace.exe" (
    echo ========================================
    echo   COMPILACION EXITOSA!
    echo ========================================
    echo.
    echo El ejecutable está en: dist\NeuroFace.exe
    echo.
    for %%A in ("dist\NeuroFace.exe") do echo Tamaño: %%~zA bytes
) else (
    echo ========================================
    echo   ERROR EN LA COMPILACION
    echo ========================================
    echo Revisa los mensajes de error arriba.
)

echo.
pause
