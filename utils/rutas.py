# -*- coding: utf-8 -*-
"""
utils/rutas.py — Sistema profesional de rutas para SHILLONG v3 PRO
Funciona en desarrollo y en EXE empaquetado con PyInstaller
"""

import sys
from pathlib import Path


def ruta_recurso(rel_path: str) -> Path:
    """
    Devuelve la ruta correcta tanto en desarrollo como en EXE.
    Uso: ruta_recurso("data/plan_contable_v3.json")
    """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # En modo desarrollo: usa la ruta del proyecto
        base_path = Path(__file__).resolve().parent.parent

    return base_path / rel_path


def crear_carpeta_si_no_existe(rel_path: str):
    """Crea carpeta si no existe (útil en primera ejecución)"""
    path = ruta_recurso(rel_path)
    path.mkdir(parents=True, exist_ok=True)