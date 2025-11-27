# ui/MainWindow.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QLabel, QStatusBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path
import os

# ===============================================
# IMPORTAR TODAS LAS VISTAS
# ===============================================
from ui.LibroMensualView import LibroMensualView
from ui.Sidebar import Sidebar
from ui.HeaderBar import HeaderBar
from ui.DashboardView import DashboardView
from ui.RegistrarView import RegistrarView
from ui.PendientesView import PendientesView
from ui.InformesView import InformesView
from ui.CierreMensualView import CierreMensualView
from ui.ToolsView import ToolsView


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SHILLONG COMUNIDAD – CONTABILIDAD v3")
        self.resize(1300, 780)

        # ============================================================
        # MODELO DE DATOS
        # ============================================================
        from models.ContabilidadData import ContabilidadData
        self.data = ContabilidadData("shillong_2026.json")

        # ============================================================
        # BARRA DE ESTADO
        # ============================================================
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet("padding:4px; color:#475569;")

        status = QStatusBar()
        status.addWidget(self.status_label)
        self.setStatusBar(status)

        # ============================================================
        # CONTENEDOR PRINCIPAL
        # ============================================================
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(central)

        # SIDEBAR
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        # STACK DINÁMICO DE VISTAS
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # HEADER SUPERIOR
        self.header = HeaderBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.header)

        # ============================================================
        # REGISTRAR TODAS LAS VISTAS
        # ============================================================
        self.views = {
            "dashboard": DashboardView(self.data),
            "registrar": RegistrarView(self.data),
            "pendientes": PendientesView(self.data),
            "informes": InformesView(self.data),
            "libro_mensual": LibroMensualView(self.data),
            "cierre": CierreMensualView(self.data),
            "herramientas": ToolsView(self),
        }

        for vista in self.views.values():
            self.stack.addWidget(vista)

        # Conectar eventos del sidebar
        self.sidebar.change_view.connect(self.cargar_vista)

        # Cargar vista inicial
        self.cargar_vista("dashboard")

    # ============================================================
    # CAMBIAR VISTA
    # ============================================================
    def cargar_vista(self, nombre):
        if nombre in self.views:
            self.stack.setCurrentWidget(self.views[nombre])
            self.header.actualizar_titulo(nombre)

    # ============================================================
    # IMPORTAR EXCEL
    # ============================================================
    def importar_excel(self):
        try:
            from ui.Dialogs.ImportarExcelDialog import ImportarExcelDialog
        except Exception as e:
            QMessageBox.critical(self, "Error importando diálogo", str(e))
            return

        dialogo = ImportarExcelDialog(self, self.data)
        dialogo.exec()

        self.refrescar_saldo()
        self.set_status("Importación completada")

    # ============================================================
    # EXPORTAR EXCEL
    # ============================================================
    def exportar_excel(self):
        from models.exportador_excel import ExportadorExcel

        archivo, _ = QFileDialog.getSaveFileName(
            self, "Exportar Excel", "movimientos.xlsx", "Excel (*.xlsx)"
        )
        if not archivo:
            return

        try:
            ExportadorExcel.exportar(archivo, self.data.movimientos)
            QMessageBox.information(self, "OK", "Exportación completa.")
        except Exception as e:
            QMessageBox.critical(self, "Error exportando Excel", str(e))

    # ============================================================
    # BACKUP
    # ============================================================
    def crear_backup(self):
        import zipfile

        archivo, _ = QFileDialog.getSaveFileName(
            self, "Crear Backup", "backup.zip", "ZIP (*.zip)"
        )
        if not archivo:
            return

        with zipfile.ZipFile(archivo, "w") as z:
            z.write(self.data.archivo_json, arcname="datos.json")

        QMessageBox.information(self, "Backup", "Backup creado correctamente.")

    # ============================================================
    # RESTAURAR
    # ============================================================
    def restore_backup(self):
        import zipfile

        archivo, _ = QFileDialog.getOpenFileName(
            self, "Restaurar Backup", "", "ZIP (*.zip)"
        )
        if not archivo:
            return

        with zipfile.ZipFile(archivo, "r") as z:
            z.extract("datos.json", "data/")

        QMessageBox.information(self, "Restaurado", "Datos restaurados correctamente.")

    # ============================================================
    # ABRIR ARCHIVO CONTABLE ACTUAL
    # ============================================================
    def abrir_archivo_contable(self):
        os.startfile(self.data.archivo_json)

    # ============================================================
    # CAMBIAR JSON CONTABLE
    # ============================================================
    def cambiar_archivo_contable(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Cambiar archivo contable", "", "JSON (*.json)"
        )
        if not archivo:
            return

        self.data.archivo_json = Path(archivo)
        self.data.cargar()

        QMessageBox.information(self, "OK", "Archivo cambiado correctamente.")
        self.views["dashboard"].actualizar_saldo()

    # ============================================================
    # ABRIR CARPETA DEL SISTEMA
    # ============================================================
    def abrir_carpeta_sistema(self):
        os.startfile(os.getcwd())

    def set_status(self, texto):
        self.status_label.setText(texto)

    def refrescar_saldo(self):
        for vista in self.views.values():
            if hasattr(vista, "actualizar"):
                vista.actualizar()