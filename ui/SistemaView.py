# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QHBoxLayout, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

class SistemaView(QWidget):
    
    # 🔥 SEÑALES que espera MainWindow
    signal_backup = Signal()
    signal_restore = Signal()
    signal_update = Signal()
    signal_open_data = Signal()
    signal_open_folder = Signal()

    # --- AQUÍ ESTÁ LA SOLUCIÓN AL ERROR ---
    def __init__(self, data=None): 
        super().__init__()
        self.data = data
        self._build_ui()
    # --------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Título
        titulo = QLabel("⚙️ Configuración y Sistema")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b;")
        layout.addWidget(titulo)

        # Grid para tarjetas de opciones
        grid = QGridLayout()
        grid.setSpacing(20)

        # --- GRUPO 1: DATOS ---
        self._agregar_tarjeta(
            grid, 0, 0, 
            "📦 Copias de Seguridad", 
            "Crea respaldos de tus datos o restaura versiones anteriores.",
            [
                ("Crear Backup", self.signal_backup, "#2563eb"),
                ("Restaurar", self.signal_restore, "#64748b")
            ]
        )

        # --- GRUPO 2: ARCHIVOS ---
        ruta_archivo = "No cargado"
        if self.data and hasattr(self.data, 'archivo_json'):
            ruta_archivo = str(self.data.archivo_json)

        self._agregar_tarjeta(
            grid, 0, 1, 
            "📂 Gestión de Archivos", 
            f"Archivo actual: {ruta_archivo}",
            [
                ("Abrir JSON Actual", self.signal_open_data, "#059669"),
                ("Abrir Carpeta App", self.signal_open_folder, "#d97706")
            ]
        )

        # --- GRUPO 3: ACTUALIZACIONES ---
        self._agregar_tarjeta(
            grid, 1, 0, 
            "🚀 Actualizaciones", 
            "Verificar si existe una nueva versión de Shillong Contabilidad.",
            [
                ("Buscar Actualización", self.signal_update, "#7c3aed")
            ]
        )

        layout.addLayout(grid)
        layout.addStretch() # Empujar todo arriba

        # Footer versión
        lbl_ver = QLabel("Shillong System Core v3.6.1 PRO")
        lbl_ver.setAlignment(Qt.AlignCenter)
        lbl_ver.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_ver)

    def _agregar_tarjeta(self, grid, row, col, titulo, desc, botones):
        """Helper para crear tarjetas bonitas"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet("font-size: 18px; font-weight: bold; color: #334155; border: none;")
        
        lbl_d = QLabel(desc)
        lbl_d.setWordWrap(True)
        lbl_d.setStyleSheet("font-size: 14px; color: #64748b; margin-bottom: 10px; border: none;")
        
        card_layout.addWidget(lbl_t)
        card_layout.addWidget(lbl_d)
        
        # Botones
        for texto, senal, color in botones:
            btn = QPushButton(texto)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 6px;
                    border: none;
                }}
                QPushButton:hover {{ opacity: 0.9; }}
            """)
            # Conectamos el clic del botón a la emisión de la señal correspondiente
            btn.clicked.connect(senal.emit)
            card_layout.addWidget(btn)
            
        card_layout.addStretch()
        grid.addWidget(card, row, col)