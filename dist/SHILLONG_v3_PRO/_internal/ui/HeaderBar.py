# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import (
    QToolBar, QLabel, QWidget, QHBoxLayout, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

# --- CONEXIÓN CON EL NUEVO SERVICIO (models/ExcelImporterService.py) ---
try:
    # Intentamos importar el servicio desde la carpeta models
    from models import ExcelImporterService
    print("✅ Servicio de importación cargado correctamente en HeaderBar.")
except ImportError as e:
    print(f"❌ Error crítico: No se pudo cargar 'models.ExcelImporterService': {e}")
    ExcelImporterService = None
# -----------------------------------------------------------------------

class HeaderBar(QToolBar):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main = main_window 
        
        self.setMovable(False)
        self.setFloatable(False)
        
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
        
        # 1. TÍTULO
        self.lbl_titulo = QLabel("Dashboard")
        self.lbl_titulo.setStyleSheet("""
            font-size: 20px; font-weight: 800; color: #1e293b; font-family: 'Segoe UI';
        """)
        layout.addWidget(self.lbl_titulo)
        
        layout.addStretch() 
        
        # 2. BOTÓN IMPORTAR EXCEL
        self.btn_importar = QPushButton("📥 Importar Excel")
        self.btn_importar.setCursor(Qt.PointingHandCursor)
        self.btn_importar.setStyleSheet("""
            QPushButton {
                background-color: #10b981; color: white; font-weight: bold;
                padding: 8px 16px; border-radius: 8px; border: none; font-size: 13px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_importar.clicked.connect(self._abrir_importador)
        layout.addWidget(self.btn_importar)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(line)
        
        # 3. USUARIO
        self.lbl_user = QLabel("Admin")
        self.lbl_user.setStyleSheet("""
            font-weight: 600; color: #64748b; font-size: 14px;
            padding: 5px; border-radius: 5px; background-color: #f1f5f9;
        """)
        layout.addWidget(self.lbl_user)

        self.addWidget(container)

    # =========================================================
    # ACCIONES
    # =========================================================
    def _abrir_importador(self):
        """Llama al NUEVO servicio profesional de importación."""
        
        if ExcelImporterService is None:
            QMessageBox.critical(self, "Error", "El servicio 'models.ExcelImporterService' no está disponible.")
            return

        if not self.main or not hasattr(self.main, 'data') or self.main.data is None:
             QMessageBox.warning(self, "Error", "Los datos contables no están cargados.")
             return

        # 🔥 AQUÍ LLAMAMOS AL NUEVO SERVICIO, NO AL ARCHIVO VIEJO
        print("🚀 Iniciando servicio de importación...")
        ExcelImporterService.ejecutar_proceso_importacion(self.main, self.main.data)

    def actualizar_titulo(self, nombre_vista_raw):
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
        titulo = mapeo.get(nombre_vista_raw, nombre_vista_raw.replace("_", " ").title())
        self.lbl_titulo.setText(titulo)

    def set_user_name(self, name):
        self.lbl_user.setText(f"👤 {name}")