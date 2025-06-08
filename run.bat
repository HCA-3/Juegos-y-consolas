@echo off
echo ========================================
echo    Iniciando GameHub...
echo ========================================
echo.

if not exist "venv" (
    echo ERROR: Entorno virtual no encontrado.
    echo Por favor ejecuta install.bat primero.
    pause
    exit /b 1
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando servidor...
echo.
echo ========================================
echo   GameHub ejecutándose en:
echo   http://localhost:5002
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python server_test.py

