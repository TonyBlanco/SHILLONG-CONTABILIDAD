# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QApplication
from ui.MainWindow import MainWindow
from core.theme_detector import windows_is_dark
import os

def load_theme(app):
    # Ruta raíz de temas
    base = "themes"

    # Detección automática de Windows
    if windows_is_dark():
        theme_file = os.path.join(base, "dark.qss")
        print("🌙 Windows detectado en modo oscuro → usando DARK")
    else:
        theme_file = os.path.join(base, "light.qss")
        print("☀️ Windows detectado en modo claro → usando LIGHT")

    # Cargar archivo QSS
    try:
        with open(theme_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("⚠️ Error cargando tema:", e)


def main():
    app = QApplication(sys.argv)

    # Carga de tema automático
    load_theme(app)

    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
