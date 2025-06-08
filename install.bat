@echo off
echo ========================================
echo    GameHub - Sistema de Videojuegos
echo ========================================
echo.

echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8 o superior desde https://python.org
    pause
    exit /b 1
)

echo.
echo Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo Entorno virtual creado.
) else (
    echo Entorno virtual ya existe.
)

echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo ========================================
echo   Instalación completada exitosamente!
echo ========================================
echo.
echo Para ejecutar el sistema:
echo 1. Ejecuta: run.bat
echo 2. Abre tu navegador en: http://localhost:5002
echo.
echo Para desarrollo en VS Code:
echo 1. Abre: gamehub.code-workspace
echo 2. Selecciona el intérprete de Python del venv
echo.
pause

