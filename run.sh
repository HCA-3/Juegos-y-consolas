#!/bin/bash

echo "========================================"
echo "   Iniciando GameHub..."
echo "========================================"
echo

if [ ! -d "venv" ]; then
    echo "ERROR: Entorno virtual no encontrado."
    echo "Por favor ejecuta ./install.sh primero."
    exit 1
fi

echo "Activando entorno virtual..."
source venv/bin/activate

echo
echo "Iniciando servidor..."
echo
echo "========================================"
echo "  GameHub ejecutándose en:"
echo "  http://localhost:5002"
echo "========================================"
echo
echo "Presiona Ctrl+C para detener el servidor"
echo

python server_test.py

