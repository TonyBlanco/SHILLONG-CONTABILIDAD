# -*- coding: utf-8 -*-
"""
MainWindow.py — SHILLONG CONTABILIDAD v3.7.8 PRO
Versión Restaurada: Sidebar Azul Original + SistemaView + Imports correctos.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

# Import update checker
try:
    from core.updater import check_for_updates, get_update_info
    UPDATE_CHECKER_AVAILABLE = True
except ImportError:
    UPDATE_CHECKER_AVAILABLE = False

# =======================================================
# 1. TUS IMPORTACIONES ORIGINALES (EXACTAS)
# =======================================================
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
from ui.HelpView import HelpView
# =======================================================

class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("Shillong Contabilidad v3.7.8 PRO")
        self.resize(1280, 800)
        
        # Mapa para conectar los IDs de tu Sidebar con los Widgets reales
        self.views = {} 

        self._init_ui()
        
        # Check for updates after window is shown (delayed to not slow startup)
        if UPDATE_CHECKER_AVAILABLE:
            QTimer.singleShot(3000, self._check_updates_on_startup)

    def _init_ui(self):
        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout Principal (Horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------------------------
        # A. SIDEBAR (Tu clase original azul)
        # ----------------------------------------------------
        self.sidebar = Sidebar(self)
        # Conectamos tu señal personalizada 'menu_signal'
        self.sidebar.menu_signal.connect(self.cambiar_vista)
        main_layout.addWidget(self.sidebar)

        # ----------------------------------------------------
        # B. CONTENIDO DERECHO
        # ----------------------------------------------------
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 1. Header
        self.header = HeaderBar(self)
        right_layout.addWidget(self.header)

        # 2. Stack de Vistas
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack)
        
        main_layout.addWidget(right_container)

        # Cargar vistas
        self._cargar_vistas()
        
        # Iniciar en Dashboard (Simulamos clic para que el botón se ponga azul)
        self.sidebar.btn_dashboard.click()

    def _cargar_vistas(self):
        """
        Instancia las vistas y las asigna a los IDs exactos que usa tu Sidebar.py
        IDs de Sidebar: dashboard, registrar, diario, pendientes, libro_mensual,
                        cierre_mensual, cierre_anual, informes, ayuda, tools, sistema
        """
        
        # Dashboard
        self.views["dashboard"] = DashboardView(self.data)
        
        # 🔥 ESTA ES LA LÍNEA QUE FALTA (El cable de conexión):
        self.views["dashboard"].navegar_a.connect(self.cambiar_vista)
        
        self.stack.addWidget(self.views["dashboard"])

        # Registrar
        self.views["registrar"] = RegistrarView(self.data)
        self.stack.addWidget(self.views["registrar"])

        # Diario (Con conexión especial para ir a Registrar)
        self.views["diario"] = DiarioView(self.data)
        self.views["diario"].signal_ir_a_registrar.connect(lambda: self.sidebar.btn_registrar.click())
        self.stack.addWidget(self.views["diario"])

        # Pendientes
        self.views["pendientes"] = PendientesView(self.data)
        self.stack.addWidget(self.views["pendientes"])

        # Libro Mensual
        self.views["libro_mensual"] = LibroMensualView(self.data)
        self.stack.addWidget(self.views["libro_mensual"])

        # Cierre Mensual
        self.views["cierre_mensual"] = CierreMensualView(self.data)
        self.stack.addWidget(self.views["cierre_mensual"])

        # Cierre Anual (cierre_anual en sidebar)
        self.views["cierre_anual"] = CierreView(self.data)
        self.stack.addWidget(self.views["cierre_anual"])

        # Informes
        self.views["informes"] = InformesView(self.data)
        self.stack.addWidget(self.views["informes"])

        # Herramientas
        self.views["tools"] = ToolsView(self.data)
        self.stack.addWidget(self.views["tools"])

        # Sistema
        self.views["sistema"] = SistemaView(self.data)
        self.stack.addWidget(self.views["sistema"])

        # Ayuda (ID 'ayuda' en tu sidebar)
        self.views["ayuda"] = HelpView(self.data)
        self.stack.addWidget(self.views["ayuda"])

    def cambiar_vista(self, id_vista):
        """Recibe el string ID desde la Sidebar y cambia la página"""
        if id_vista in self.views:
            widget = self.views[id_vista]
            self.stack.setCurrentWidget(widget)
            
            # Actualizar título header
            if self.header:
                self.header.actualizar_titulo(id_vista)
            
            # Auto-refresco al entrar
            if hasattr(widget, "actualizar"): widget.actualizar()
            elif hasattr(widget, "actualizar_datos"): widget.actualizar_datos()
            elif hasattr(widget, "_cargar_ultimos"): widget._cargar_ultimos() # Registrar
            elif hasattr(widget, "_filtrar"): widget._filtrar() # Diario

    def actualizar_vistas(self):
        """
        Método llamado por el Importador de Excel para refrescar todo.
        """
        print("🔄 Refrescando datos globales...")
        self.data.cargar()
        for view in self.views.values():
            if hasattr(view, "actualizar"): view.actualizar()
            elif hasattr(view, "actualizar_datos"): view.actualizar_datos()
            elif hasattr(view, "_cargar_ultimos"): view._cargar_ultimos()
            elif hasattr(view, "_filtrar"): view._filtrar()

    def _check_updates_on_startup(self):
        """
        Check for updates silently on startup and notify user if available.
        """
        try:
            info = get_update_info()
            
            if info["available"]:
                # Show non-intrusive notification
                msg = QMessageBox(self)
                msg.setWindowTitle("🎉 Actualización Disponible")
                msg.setIcon(QMessageBox.Information)
                msg.setText(
                    f"<h3>Nueva versión v{info['remote_version']} disponible</h3>"
                    f"<p>Tu versión actual: v{info['local_version']}</p>"
                    f"<p>¿Deseas descargar la actualización ahora?</p>"
                )
                
                btn_download = msg.addButton("⬇️ Descargar", QMessageBox.AcceptRole)
                btn_later = msg.addButton("Recordar Más Tarde", QMessageBox.RejectRole)
                
                msg.exec()
                
                if msg.clickedButton() == btn_download:
                    if info.get("download_url"):
                        QDesktopServices.openUrl(QUrl(info["download_url"]))
                        
        except Exception as e:
            # Silent fail - don't bother user if update check fails
            print(f"[MainWindow] Update check failed: {e}")