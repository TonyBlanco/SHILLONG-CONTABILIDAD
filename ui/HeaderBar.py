# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QToolBar, QToolButton, QMenu, QMessageBox, QLabel, QWidget, QHBoxLayout
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize

# Importar el diálogo (con fallback)
try:
    from ui.Dialogs.ImportarExcelDialog import ImportarExcelDialog
except Exception as e:
    print("ERROR cargando ImportarExcelDialog:", e)


class HeaderBar(QToolBar):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main = parent

        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(22, 22))

        self.setStyleSheet("""
            QToolBar {
                background: #f1f5f9;
                padding: 6px;
                border: none;
            }
            QToolButton {
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 15px;
            }
            QToolButton:hover {
                background: #e2e8f0;
            }
        """)

        # Contenedor principal
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(20)

        # Título dinámico
        self.lbl_titulo = QLabel("Dashboard")
        self.lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e293b;")
        layout.addWidget(self.lbl_titulo)
        layout.addStretch()

        # Botón Herramientas
        self.btn_tools = QToolButton()
        self.btn_tools.setText("Herramientas")
        self.btn_tools.setPopupMode(QToolButton.InstantPopup)

        self.menu = QMenu()
        self.btn_tools.setMenu(self.menu)
        layout.addWidget(self.btn_tools)

        self.addWidget(container)

        # =====================================================
        # Menú Herramientas
        # =====================================================
        self.menu.addSection("Tema Visual")
        self._add_action("Tema Claro", self._safe_call("aplicar_tema", "claro"))
        self._add_action("Tema Oscuro", self._safe_call("aplicar_tema", "oscuro"))

        self.menu.addSection("Importar / Exportar")
        self._add_action("Importar Excel…", self._abrir_importador_excel)
        self._add_action("Exportar Excel…", self._safe_call("exportar_excel"))

        self.menu.addSection("Copia de Seguridad")
        self._add_action("Crear Backup (.zip)", self._safe_call("crear_backup"))
        self._add_action("Restaurar desde archivo…", self._safe_call("restore_backup"))

        self.menu.addSection("Archivo Contable")
        self._add_action("Abrir archivo contable actual", self._safe_call("abrir_archivo_contable"))
        self._add_action("Cambiar archivo contable…", self._safe_call("cambiar_archivo_contable"))

        self.menu.addSection("Sistema")
        self._add_action("Abrir carpeta del sistema", self._safe_call("abrir_carpeta_sistema"))

    # =========================================================
    # Añadir acción al menú
    # =========================================================
    def _add_action(self, nombre, funcion):
        act = QAction(nombre, self)
        act.triggered.connect(funcion)
        self.menu.addAction(act)

    # =========================================================
    # Importar Excel
    # =========================================================
    def _abrir_importador_excel(self):
        if self.main is None:
            QMessageBox.warning(self, "Error", "MainWindow no está inicializado.")
            return

        try:
            dlg = ImportarExcelDialog(self)
            dlg.exec()

            if hasattr(self.main, "data"):
                self.main.data.cargar()

            if hasattr(self.main, "refrescar_dashboard"):
                self.main.refrescar_dashboard()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el importador:\n{e}")

    # =========================================================
    # Llamada segura a métodos del MainWindow
    # =========================================================
    def _safe_call(self, method_name, *args):
        def wrapper():
            if self.main is None:
                QMessageBox.warning(self, "Error", "MainWindow no está inicializado.")
                return

            metodo = getattr(self.main, method_name, None)
            if callable(metodo):
                metodo(*args)
            else:
                QMessageBox.warning(
                    self,
                    "Función no disponible",
                    f"El método '{method_name}()' no existe en MainWindow."
                )
        return wrapper

    # =========================================================
    # MÉTODO REQUERIDO POR MainWindow
    # =========================================================
    def actualizar_titulo(self, nombre_vista: str):
        titulos = {
            "dashboard": "Dashboard",
            "registrar": "Registrar Movimiento",
            "pendientes": "Movimientos Pendientes",
            "libro_mensual": "Libro Mensual",
            "cierre": "Cierre Mensual",
            "informes": "Informes",
            "herramientas": "Herramientas"
        }
        titulo = titulos.get(nombre_vista, nombre_vista.replace("_", " ").title())
        self.lbl_titulo.setText(titulo)