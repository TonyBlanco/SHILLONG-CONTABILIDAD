import os
import sys
import requests
import subprocess
import threading
from PySide6.QtWidgets import QMessageBox
from core.version import APP_VERSION

# URLS DEL REPOSITORIO GITHUB
VERSION_URL = "https://raw.githubusercontent.com/TonyBlanco/SHILLONG-CONTABILIDAD/main/update/version.json"
INSTALLER_URL = "https://raw.githubusercontent.com/TonyBlanco/SHILLONG-CONTABILIDAD/main/update/SHILLONG_v3_PRO_Setup_Final.exe"
INSTALLER_LOCAL = "SHILLONG_v3_PRO_Setup_Final.exe"


def check_update(parent=None, silent=False):
    """
    Comprueba si existe una nueva versión en GitHub.
    Si silent=True, no muestra mensajes a menos que haya nueva versión.
    """

    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code != 200:
            if not silent:
                QMessageBox.warning(parent, "Actualización", "No se pudo comprobar la versión online.")
            return

        data = response.json()
        latest_version = data.get("version", APP_VERSION)

        if latest_version.strip() != APP_VERSION.strip():
            _ask_to_update(parent, latest_version)
        else:
            if not silent:
                QMessageBox.information(parent, "Actualización",
                                        f"Ya tienes la última versión ({APP_VERSION}).")

    except Exception as e:
        if not silent:
            QMessageBox.warning(parent, "Actualización", f"Error comprobando actualización:\n{e}")


def _ask_to_update(parent, latest_version):
    """Pregunta si desea actualizar."""
    r = QMessageBox.question(
        parent,
        "Nueva versión disponible",
        f"Hay una versión nueva disponible:\n\n"
        f"Versión instalada: {APP_VERSION}\n"
        f"Versión nueva: {latest_version}\n\n"
        f"¿Desea actualizar ahora?",
        QMessageBox.Yes | QMessageBox.No
    )

    if r == QMessageBox.Yes:
        _download_and_install(parent)


def _download_and_install(parent):
    """Descarga y ejecuta el instalador."""
    try:
        QMessageBox.information(parent, "Actualización", "Comenzando descarga del instalador...")

        response = requests.get(INSTALLER_URL, stream=True)
        total = int(response.headers.get("content-length", 0))

        downloaded = 0
        chunk_size = 4096

        with open(INSTALLER_LOCAL, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

        QMessageBox.information(parent, "Actualización",
                                "Descarga completada.\n"
                                "El instalador se ejecutará ahora.")

        # Ejecutar instalador
        subprocess.Popen([INSTALLER_LOCAL], shell=True)

        # Cerrar la app actual
        os._exit(0)

    except Exception as e:
        QMessageBox.warning(parent, "Actualización",
                            f"No se pudo completar la actualización:\n{e}")
