# -*- coding: utf-8 -*-
import sys
import os
import ctypes

# ===============================================
# DPI PERFECTO 2025 – PySide6 (sin warnings ni errores)
# ===============================================

# 1. Forzamos DPI Awareness a nivel de proceso (Windows)
try:
    # Solo funciona si la app NO está empaquetada con PyInstaller o si tiene manifiesto
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PER_MONITOR_AWARE_V2
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()   # fallback antiguo
    except:
        pass

# 2. Variables de entorno Qt (las únicas que funcionan hoy)
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_FONT_DPI"] = "96"

# 3. Importamos QApplication DESPUÉS de configurar todo
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# 4. Configuración moderna (sin usar atributos obsoletos)
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

# Estas dos líneas ya están obsoletas y fueron eliminadas intencionalmente:
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)     ← deprecated
# QApplication.setAttribute(Qt.AA_UseHighDpiScaling, True)       ← ya no existe

# ===============================================
# IMPORTS PRINCIPALES
# ===============================================
from ui.MainWindow import MainWindow
from core.theme_detector import windows_is_dark
from core.version import APP_VERSION


# ============================
#   CARGA DE TEMA AUTOMÁTICA
# ============================
def load_theme(app):
    base = "themes"

    if windows_is_dark():
        theme_file = os.path.join(base, "dark.qss")
        print("🌙 Windows detectado en modo oscuro → usando DARK")
    else:
        theme_file = os.path.join(base, "light.qss")
        print("☀ Windows detectado en modo claro → usando LIGHT")

    if os.path.exists(theme_file):
        with open(theme_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


# ============================
#   DESACTIVAR DPI DE WINDOWS
# ============================
def disable_windows_dpi_scaling():
    """Evita que Windows vuelva a reescalar la app."""
    if sys.platform == "win32":
        try:
            # 0 = deshabilitar completamente scaling
            ctypes.windll.shcore.SetProcessDpiAwareness(0)
        except Exception:
            pass


# ============================
#   MAIN
# ============================
def main():

    print(f"🔥 Cargando SHILLONG v3 PRO — Versión {APP_VERSION}")

    disable_windows_dpi_scaling()

    # Qt Application
    app = QApplication(sys.argv)

    # Tema automático
    load_theme(app)

    # Crear ventana principal
    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
