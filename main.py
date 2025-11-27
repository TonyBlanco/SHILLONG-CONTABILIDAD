# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.MainWindow import MainWindow

def main():
    # Crear aplicación
    app = QApplication(sys.argv)

    # Cargar estilos QSS
    try:
        with open("core/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("⚠️ No se encontró core/styles.qss, se usará estilo por defecto.")

    # Crear ventana principal
    ventana = MainWindow()
    ventana.show()

    # Ejecutar loop principal
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
