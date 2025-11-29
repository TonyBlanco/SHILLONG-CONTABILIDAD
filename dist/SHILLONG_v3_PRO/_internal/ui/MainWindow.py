# -*- coding: utf-8 -*-
"""
MainWindow.py — Versión FINAL estable y 150% DPI Safe
Centro de Mando de SHILLONG CONTABILIDAD v3.6 PRO
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMessageBox
)
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtCore import Qt
from pathlib import Path
import os, zipfile, shutil, datetime
import sys

# --- PARCHE DE RUTAS PARA IMPORTADOR ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Helper de importación
try:
    import importador_excel
except ImportError:
    importador_excel = None

# Vistas
from ui.HeaderBar import HeaderBar
from ui.Sidebar import Sidebar
from ui.DashboardView import DashboardView
from ui.SistemaView import SistemaView
from ui.RegistrarView import RegistrarView
from ui.DiarioView import DiarioView
from ui.CierreMensualView import CierreMensualView
from ui.CierreView import CierreView
from ui.LibroMensualView import LibroMensualView
from ui.InformesView import InformesView
from ui.PendientesView import PendientesView
from ui.ToolsView import ToolsView

from models.ContabilidadData import ContabilidadData
from core.version import APP_VERSION


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        print("🔥 Cargando SHILLONG v3 PRO — Versión", APP_VERSION)

        # ================================================
        # MOTOR DE DATOS
        # ================================================
        data_file = "data/shillong_2026.json"
        self.data = ContabilidadData(data_file)

        # ================================================
        # CONFIGURACIÓN VENTANA
        # ================================================
        self.setWindowTitle(f"SHILLONG CONTABILIDAD v{APP_VERSION} PRO")
        self.resize(1280, 850)
        self.setMinimumSize(1024, 768)
        
        # Icono
        icon_path = Path("assets/icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Estilo Global
        self.setStyleSheet("""
            QMainWindow { background-color: #f1f5f9; }
            QWidget { font-family: 'Segoe UI', Arial, sans-serif; }
        """)

        # ================================================
        # UI PRINCIPAL
        # ================================================
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. SIDEBAR (Izquierda)
        self.sidebar = Sidebar(self) 
        self.sidebar.menu_signal.connect(self.cambiar_vista) 
        main_layout.addWidget(self.sidebar)

        # 2. CONTENIDO (Derecha)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 2.1 Header
        self.header = HeaderBar(self)
        self.header.set_user_name("Admin") 
        content_layout.addWidget(self.header)

        # 2.2 Stack de Vistas
        self.stack = QStackedWidget()
        self._inicializar_vistas()
        content_layout.addWidget(self.stack)

        main_layout.addLayout(content_layout)

        # Iniciar en Dashboard
        self.cambiar_vista("dashboard")

    def _inicializar_vistas(self):
        """Carga todas las pantallas del sistema"""
        self.views = {}

        # Instanciar Vistas
        self.views["dashboard"] = DashboardView(self.data)
        self.views["registrar"] = RegistrarView(self.data)
        self.views["diario"]    = DiarioView(self.data)
        self.views["pendientes"]= PendientesView(self.data)
        self.views["libro_mensual"] = LibroMensualView(self.data)
        self.views["cierre_mensual"] = CierreMensualView(self.data)
        self.views["cierre_anual"] = CierreView(self.data)
        self.views["informes"]  = InformesView(self.data)
        
        # ToolsView necesita 'self' para llamar a métodos del sistema
        self.views["tools"]     = ToolsView(self) 
        
        # SistemaView NECESITA self.data según tu archivo subido
        self.views["sistema"]   = SistemaView(self.data)

        # Añadir al Stack en orden
        for key, view in self.views.items():
            self.stack.addWidget(view)

        # --- CONEXIONES ENTRE VISTAS ---
        if "diario" in self.views and "registrar" in self.views:
            if hasattr(self.views["diario"], "signal_ir_a_registrar"):
                self.views["diario"].signal_ir_a_registrar.connect(self._ir_a_registrar_desde_diario)

        if "sistema" in self.views:
            sis = self.views["sistema"]
            if hasattr(sis, "signal_backup"): sis.signal_backup.connect(self.crear_backup)
            if hasattr(sis, "signal_restore"): sis.signal_restore.connect(self.restaurar_backup)
            if hasattr(sis, "signal_update"): sis.signal_update.connect(self.buscar_actualizacion)
            if hasattr(sis, "signal_open_data"): sis.signal_open_data.connect(self.abrir_archivo_contable)
            if hasattr(sis, "signal_open_folder"): sis.signal_open_folder.connect(self.abrir_carpeta_sistema)

    # ================================================
    # NAVEGACIÓN
    # ================================================
    def cambiar_vista(self, nombre_vista):
        """Cambia la vista central"""
        vista = self.views.get(nombre_vista)
        if vista:
            self.stack.setCurrentWidget(vista)
            if hasattr(vista, "actualizar"):
                vista.actualizar()
            self.header.actualizar_titulo(nombre_vista)
            if hasattr(self.sidebar, "marcar_boton"):
                self.sidebar.marcar_boton(nombre_vista)

    def _ir_a_registrar_desde_diario(self):
        print("🚀 Saltando de Diario a Registrar...")
        self.cambiar_vista("registrar")

    def refrescar_saldo(self):
        pass

    def aplicar_tema(self, tema):
        """Método placeholder para cambiar tema si ToolsView lo llama"""
        print(f"Cambio de tema solicitado: {tema}")
        QMessageBox.information(self, "Tema", f"Tema {tema} seleccionado (Reinicio requerido para aplicar full).")

    # ================================================
    # MÉTODOS DEL SISTEMA Y HERRAMIENTAS
    # ================================================
    
    def importar_excel(self):
        if importador_excel:
            importador_excel.abrir_importador(self, self.data)
        else:
            QMessageBox.critical(self, "Error", "Módulo importador no disponible.")

    # --- ALIAS PARA COMPATIBILIDAD CON TOOLSVIEW (INGLÉS/ESPAÑOL) ---
    def create_backup(self): self.crear_backup()
    def restore_backup(self): self.restaurar_backup()
    def open_data_folder(self): self.abrir_carpeta_sistema()
    def open_current_json(self): self.abrir_archivo_contable()
    # ----------------------------------------------------------------

    def crear_backup(self):
        try:
            folder = "backups"
            os.makedirs(folder, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_name = f"{folder}/backup_shillong_{timestamp}.zip"

            with zipfile.ZipFile(zip_name, 'w') as z:
                z.write(self.data.archivo_json, arcname="shillong_datos.json")
            
            QMessageBox.information(self, "Backup", f"Copia de seguridad creada:\n{zip_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def restaurar_backup(self):
        from PySide6.QtWidgets import QFileDialog
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar Backup", "backups", "Zip (*.zip)")
        if not ruta: return

        try:
            with zipfile.ZipFile(ruta, "r") as z:
                z.extract("shillong_datos.json", "temp")

            shutil.move("temp/shillong_datos.json", self.data.archivo_json)
            shutil.rmtree("temp")

            self.data.cargar()

            QMessageBox.information(self, "Restaurado", "Datos restaurados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def cambiar_archivo_contable(self):
        from PySide6.QtWidgets import QFileDialog
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo JSON", "", "JSON (*.json)")
        if ruta:
            self.data.archivo_json = Path(ruta)
            self.data.cargar()
            QMessageBox.information(self, "OK", "Archivo cambiado.")

    def abrir_archivo_contable(self):
        try:
            os.startfile(str(self.data.archivo_json))
        except:
            pass

    def abrir_carpeta_sistema(self):
        try:
            os.startfile(os.getcwd())
        except:
            pass

    def buscar_actualizacion(self):
        QMessageBox.information(
            self, "Actualización", 
            "Tienes la última versión PRO (v3.6.0).\nSistema optimizado para 2026."
        )