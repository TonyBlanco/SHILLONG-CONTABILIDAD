# -*- coding: utf-8 -*-
"""
SHILLONG v3.8.0 PRO - UPDATER COMPLETO
Actualiza módulos de SHILLONG con:
✔ Detección automática de instalación
✔ Cierre automático del programa
✔ Backup seguro
✔ Copia del módulo actualizado
"""

import os
import shutil
import subprocess
import time
import sys

# VERSION INFO
UPDATE_VERSION = "3.8.0"

# NOMBRE DEL EJECUTABLE DE SHILLONG
APP_EXE = "SHILLONG_v3_PRO.exe"

# ARCHIVOS A ACTUALIZAR
MODULES_TO_UPDATE = [
    "ui/RegistrarView.py",
    "ui/DashboardView.py",
    "core/updater.py",
    "core/version.py"
]

# NOMBRE DEL ARCHIVO A ACTUALIZAR (legacy)
MODULE_NAME = "RegistrarView.py"

# RUTAS POSIBLES DE INSTALACIÓN
POSSIBLE_PATHS = [
    r"C:\Program Files\SHILLONGv3PRO",
    r"C:\SHILLONGV3"
]

# RUTA LOCAL donde está el archivo nuevo (al ejecutar EXE empaquetado)
if getattr(sys, 'frozen', False):
    LOCAL_PATH = sys._MEIPASS  
else:
    LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

LOCAL_FILE = os.path.join(LOCAL_PATH, MODULE_NAME)


def find_install_path():
    """Detecta dónde está instalado SHILLONG."""
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            return path
    return None


def kill_shillong():
    """Cierra automáticamente SHILLONG."""
    try:
        subprocess.run(["taskkill", "/IM", APP_EXE, "/F"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
    except Exception as e:
        print(f"[ERROR] No se pudo cerrar SHILLONG: {e}")


def backup_file(target_path):
    """Crea backup seguro antes de actualizar."""
    backup_dir = os.path.join(os.path.dirname(target_path), f"_backup_{UPDATE_VERSION}")
    os.makedirs(backup_dir, exist_ok=True)

    backup_dest = os.path.join(backup_dir, MODULE_NAME)

    try:
        shutil.copy2(target_path, backup_dest)
        print(f"[OK] Backup creado en: {backup_dest}")
    except Exception as e:
        print(f"[ERROR] No se pudo crear backup: {e}")


def update_file(install_path):
    """Copia el nuevo RegistrarView.py al SHILLONG instalado."""
    target = os.path.join(install_path, "ui", MODULE_NAME)

    if not os.path.exists(LOCAL_FILE):
        print(f"[ERROR] No se encuentra el archivo local a actualizar: {LOCAL_FILE}")
        return False

    try:
        backup_file(target)
        shutil.copy2(LOCAL_FILE, target)
        print(f"[OK] Archivo actualizado: {target}")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar el archivo: {e}")
        return False


def main():
    print(f"=== SHILLONG UPDATER {UPDATE_VERSION} ===")

    install_path = find_install_path()

    if not install_path:
        print("[ERROR] No se encontró una instalación válida.")
        input("Presione ENTER para salir.")
        return

    print(f"[INFO] Instalación encontrada en: {install_path}")

    print("[INFO] Cerrando SHILLONG si está abierto...")
    kill_shillong()

    print("[INFO] Actualizando archivo...")
    if update_file(install_path):
        print("[OK] ¡Actualización completada con éxito!")

        # Reabrir SHILLONG
        exe_path = os.path.join(install_path, APP_EXE)
        if os.path.exists(exe_path):
            print("[INFO] Iniciando SHILLONG...")
            subprocess.Popen([exe_path], shell=True)

    input("\nPresione ENTER para finalizar.")


if __name__ == "__main__":
    main()
