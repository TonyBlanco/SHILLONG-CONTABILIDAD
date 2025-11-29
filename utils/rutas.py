# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

def ruta_recurso(ruta_relativa):
    """
    Obtiene la ruta absoluta al recurso (archivos estáticos dentro del exe).
    Funciona para desarrollo y para PyInstaller (_MEIPASS).
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return Path(base_path) / ruta_relativa

def ruta_datos_usuario(archivo):
    """
    Devuelve la ruta a un archivo en la carpeta 'data' junto al ejecutable.
    Esto es crucial para que los datos persistan y no se borren al cerrar el exe.
    """
    if getattr(sys, 'frozen', False):
        # Si es exe, usar la carpeta donde está el exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Si es script, usar la carpeta actual
        base_path = os.path.abspath(".")
        
    # Construir ruta: base_path/data/archivo
    return Path(base_path) / "data" / archivo