# -*- coding: utf-8 -*-
import sys
import os
import logging
import traceback
from datetime import datetime
from pathlib import Path

# --- CONFIGURACIÓN DE RUTAS ---
# Detectar si estamos en ejecutable o en código fuente
if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegurar que Python encuentre los módulos base
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- PRIORIDAD PARA MÓDULOS EXTERNOS (HOT-UPDATE) ---
# Con esto, cuando modifiques ui/*.py o models/*.py,
# Python intentará usar primero los archivos del disco
# antes que los módulos empaquetados en el EXE.
UI_DIR = os.path.join(ROOT_DIR, "ui")
MODELS_DIR = os.path.join(ROOT_DIR, "models")

if UI_DIR not in sys.path:
    sys.path.insert(0, UI_DIR)

if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPalette, QColor, QFont

# Importamos las piezas clave
from models.ContabilidadData import ContabilidadData
from ui.MainWindow import MainWindow

# --- CONSTANTES ---
APP_VERSION = "3.7.8"

# ============================================================
#  SISTEMA DE LOGS (LA CAJA NEGRA) 📦
# ============================================================
def setup_logging():
    """Configura el sistema para guardar errores en la carpeta logs/"""
    log_dir = os.path.join(ROOT_DIR, "logs")
    
    # 1. Crear carpeta si no existe
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. Nombre del archivo: log_2025-12-01.txt
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"log_{fecha_hoy}.txt")

    # 3. Configurar el logger
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # 4. Hook para capturar CRASHES (Errores no controlados)
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Escribir el error completo en el archivo
        logging.error("🔥 ERROR NO CONTROLADO (CRASH):", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Opcional: Mostrar alerta visual al usuario antes de morir
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print("CRITICAL ERROR:", error_msg)  # Para consola si existe
        
        # Intentar mostrar ventana de error (si Qt sigue vivo)
        try:
            app = QApplication.instance()
            if app:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ocurrió un error inesperado.")
                msg.setInformativeText("El error ha sido guardado en la carpeta 'logs'.")
                msg.setDetailedText(error_msg)
                msg.setWindowTitle("Error Crítico")
                msg.exec()
        except:
            pass

    sys.excepthook = handle_exception
    print(f"[OK] Sistema de Logs activado en: {log_file}")

# ============================================================
#  CONFIGURACIÓN VISUAL
# ============================================================
def disable_windows_dpi_scaling():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)
    if hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.Floor
        )

def load_theme(app):
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 250, 252)) 
    palette.setColor(QPalette.WindowText, QColor(15, 23, 42)) 
    app.setPalette(palette)

# ============================================================
#  MAIN
# ============================================================
def main():
    # 1. ACTIVAR LOGS ANTES DE NADA
    setup_logging()

    print("SHILLONG CONTABILIDAD v3.7.8 PRO -- Engine v4.3.2 Iniciado")
    print(f"ROOT_DIR detectado: {ROOT_DIR}")
    print(f"UI_DIR: {UI_DIR}")
    print(f"MODELS_DIR: {MODELS_DIR}")

    disable_windows_dpi_scaling()

    app = QApplication(sys.argv)
    app.setApplicationName("Shillong Contabilidad")
    app.setApplicationVersion(APP_VERSION)
    
    # Icono de ventana (si existe logo.ico)
    icon_path = os.path.join(ROOT_DIR, "logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    load_theme(app)

    try:
        data = ContabilidadData()
    except Exception as e:
        logging.error(f"Error cargando datos iniciales: {e}")
        print(f"❌ Error crítico: {e}")
        data = None 

    if data:
        ventana = MainWindow(data)
        ventana.resize(1280, 800)
        ventana.show()
        sys.exit(app.exec())
    else:
        print("⚠️ No se pudo iniciar la aplicación.")

if __name__ == "__main__":
    main()
