#!/bin/bash

echo "========================================"
echo "   GameHub - Sistema de Videojuegos"
echo "========================================"
echo

echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Por favor instala Python 3.8 o superior"
    exit 1
fi

python3 --version

echo
echo "Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Entorno virtual creado."
else
    echo "Entorno virtual ya existe."
fi

echo
echo "Activando entorno virtual..."
source venv/bin/activate

echo
echo "Instalando dependencias..."
pip install -r requirements.txt

echo
echo "========================================"
echo "  Instalación completada exitosamente!"
echo "========================================"
echo
echo "Para ejecutar el sistema:"
echo "1. Ejecuta: ./run.sh"
echo "2. Abre tu navegador en: http://localhost:5002"
echo
echo "Para desarrollo en VS Code:"
echo "1. Abre: gamehub.code-workspace"
echo "2. Selecciona el intérprete de Python del venv"
echo

