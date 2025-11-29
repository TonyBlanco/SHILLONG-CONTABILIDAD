# -*- coding: utf-8 -*-
import sys
import os

# --- PARCHE DE RUTAS (CRÍTICO) ---
# Esto añade la carpeta principal (donde está main.py) a la lista de búsqueda de Python.
# Sin esto, 'import importador_excel' fallará al ejecutar desde carpetas anidadas.
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# ---------------------------------

from PySide6.QtWidgets import (
    QToolBar, QLabel, QWidget, QHBoxLayout, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction

# Importamos el módulo helper con manejo de errores
try:
    import importador_excel
except ImportError:
    print("⚠️ ADVERTENCIA CRÍTICA: No se encontró 'importador_excel.py' en la raíz.")
    importador_excel = None

class HeaderBar(QToolBar):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main = main_window # Referencia a MainWindow para acceder a sus datos y métodos
        
        self.setMovable(False)
        self.setFloatable(False)
        
        # Estilo visual limpio y moderno
        self.setStyleSheet("""
            QToolBar {
                background: white; 
                border-bottom: 1px solid #e2e8f0; 
                padding: 10px;
                spacing: 10px;
            }
        """)
        
        # --- CONTENEDOR INTERNO ---
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)
        
        # 1. TÍTULO DE LA PANTALLA
        self.lbl_titulo = QLabel("Dashboard")
        self.lbl_titulo.setStyleSheet("""
            font-size: 20px; 
            font-weight: 800; 
            color: #1e293b;
            font-family: 'Segoe UI';
        """)
        layout.addWidget(self.lbl_titulo)
        
        layout.addStretch() # Empuja todo lo demás a la derecha
        
        # 2. BOTÓN IMPORTAR EXCEL (Verde)
        self.btn_importar = QPushButton("📥 Importar Excel")
        self.btn_importar.setCursor(Qt.PointingHandCursor)
        self.btn_importar.setStyleSheet("""
            QPushButton {
                background-color: #10b981; 
                color: white; 
                font-weight: bold;
                padding: 8px 16px; 
                border-radius: 8px; 
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:pressed { background-color: #047857; }
        """)
        self.btn_importar.clicked.connect(self._abrir_importador)
        layout.addWidget(self.btn_importar)
        
        # Separador vertical
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(line)
        
        # 3. USUARIO / INFO
        self.lbl_user = QLabel("Admin")
        self.lbl_user.setStyleSheet("""
            font-weight: 600; 
            color: #64748b; 
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
            background-color: #f1f5f9;
        """)
        layout.addWidget(self.lbl_user)

        # Añadir el widget contenedor a la barra
        self.addWidget(container)

    # =========================================================
    # ACCIONES
    # =========================================================
    def _abrir_importador(self):
        """Lanza el importador usando el módulo helper de forma segura"""
        if importador_excel is None:
            QMessageBox.critical(self, "Error Fatal", "El módulo 'importador_excel.py' no fue cargado correctamente.\nVerifique que el archivo esté en la carpeta principal.")
            return

        # Verifica que 'data' exista en main_window antes de intentar acceder
        if self.main and hasattr(self.main, 'data'):
            try:
                importador_excel.abrir_importador(self.main, self.main.data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Fallo al abrir el importador:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No se puede acceder a los datos de la aplicación (self.main.data no existe).")

    def actualizar_titulo(self, nombre_vista_raw):
        """Actualiza el título del Header según la vista activa"""
        mapeo = {
            "dashboard": "📊 Panel de Control",
            "registrar": "💳 Registrar Movimiento",
            "diario": "📘 Diario General",
            "pendientes": "⏳ Movimientos Pendientes",
            "libro_mensual": "📑 Libro Diario Mensual",
            "cierre_mensual": "🔒 Cierre Mensual",
            "cierre_anual": "📅 Cierre Anual",
            "informes": "📈 Informes & BI",
            "tools": "🛠️ Herramientas",
            "sistema": "⚙️ Sistema"
        }
        
        # Obtener nombre bonito o formatear el raw si no está en el mapa
        titulo = mapeo.get(nombre_vista_raw, nombre_vista_raw.replace("_", " ").title())
        self.lbl_titulo.setText(titulo)

    def set_user_name(self, name):
        self.lbl_user.setText(f"👤 {name}")