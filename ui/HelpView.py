# -*- coding: utf-8 -*-
"""
HelpView.py — SHILLONG CONTABILIDAD v3.7.7 PRO
---------------------------------------------------------
ESTADO: MASTER FINAL • DISEÑO REFINADO • MANUAL PDF • 100% ESTABLE
---------------------------------------------------------
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QScrollArea, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

import os
from datetime import datetime


class HelpView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self._build_ui()


    # -------------------------------------------------------------------
    # UI PRINCIPAL
    # -------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(25)

        # Título principal
        titulo = QLabel("❓ Centro de Ayuda")
        titulo.setStyleSheet("font-size:26px; font-weight:900; color:#1e293b;")
        self.layout.addWidget(titulo)

        # -------------------------------------------------------------------
        # Paneles
        # -------------------------------------------------------------------
        self.layout.addWidget(self._panel_info())
        self.layout.addWidget(self._panel_manual_pdf())
        self.layout.addWidget(self._panel_tecnico())
        self.layout.addWidget(self._panel_archivos())
        self.layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)


    # -------------------------------------------------------------------
    # PANEL INFO GENERAL
    # -------------------------------------------------------------------
    def _panel_info(self):
        f = QFrame()
        f.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #e2e8f0;
                border-radius:8px;
            }
        """)
        l = QVBoxLayout(f)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(10)

        titulo = QLabel("Información del Sistema")
        titulo.setStyleSheet("font-size:18px; font-weight:bold; color:#1e293b;")
        l.addWidget(titulo)

        texto = QLabel(
            f"""
SHILLONG CONTABILIDAD v3.7.7 PRO  
Engine Interno v4.3.2  
Base de datos actual: {self.data.archivo_json}

Total movimientos cargados: {len(self.data.movimientos)}
Fecha de última modificación: {self._fecha_mod_json()}
            """
        )
        texto.setStyleSheet("font-size:14px; color:#334155;")
        texto.setWordWrap(True)
        l.addWidget(texto)

        return f


    # -------------------------------------------------------------------
    # PANEL MANUAL PDF
    # -------------------------------------------------------------------
    def _panel_manual_pdf(self):
        f = QFrame()
        f.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #e2e8f0;
                border-radius:8px;
            }
        """)
        l = QVBoxLayout(f)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(10)

        titulo = QLabel("📘 Manual de Usuario SHILLONG")
        titulo.setStyleSheet("font-size:18px; font-weight:bold; color:#1e293b;")
        l.addWidget(titulo)

        texto = QLabel(
            "Incluye instrucciones completas, capturas, flujos de trabajo y "
            "todas las funciones explicadas paso a paso."
        )
        texto.setWordWrap(True)
        texto.setStyleSheet("font-size:13px; color:#475569;")
        l.addWidget(texto)

        btn = QPushButton("Abrir Manual en PDF")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(45)
        btn.setStyleSheet("""
            background-color:#0f172a;
            color:white;
            font-weight:bold;
            border-radius:6px;
        """)
        btn.clicked.connect(self._abrir_manual)

        l.addWidget(btn)
        return f


    def _abrir_manual(self):
        pdf = "data/manual_shillong.pdf"

        if not os.path.exists(pdf):
            QMessageBox.warning(
                self,
                "Manual no encontrado",
                "No se encontró manual_shillong.pdf en la carpeta /data.\n"
                "Colócalo allí para que el botón funcione."
            )
            return

        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(pdf)))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    # -------------------------------------------------------------------
    # PANEL TÉCNICO
    # -------------------------------------------------------------------
    def _panel_tecnico(self):
        f = QFrame()
        f.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #e2e8f0;
                border-radius:8px;
            }
        """)
        l = QVBoxLayout(f)
        l.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("⚙️ Información Técnica")
        titulo.setStyleSheet("font-size:18px; font-weight:bold; color:#1e293b;")
        l.addWidget(titulo)

        texto = QLabel(
            """
Lenguaje: Python 3.10+  
Framework gráfico: PySide6 (Qt6)  
Exportación Excel: openpyxl  
Compatibilidad 100% Windows  
Actualizaciones por módulos  
Sistema de logs integrado  
            """
        )
        texto.setStyleSheet("font-size:14px; color:#334155;")
        texto.setWordWrap(True)

        l.addWidget(texto)
        return f


    # -------------------------------------------------------------------
    # PANEL ARCHIVOS
    # -------------------------------------------------------------------
    def _panel_archivos(self):
        f = QFrame()
        f.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #e2e8f0;
                border-radius:8px;
            }
        """)
        l = QVBoxLayout(f)
        l.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("📂 Archivos Importantes")
        titulo.setStyleSheet("font-size:18px; font-weight:bold; color:#1e293b;")
        l.addWidget(titulo)

        texto = QLabel(
            f"""
📁 Archivo principal de datos:  
{self.data.archivo_json}

📁 Carpeta "data"  
Movimientos, backups, plan contable, manual PDF.

📄 JSON de configuración del calendario kabbalístico  
data/kabbalah_72.json
            """
        )
        texto.setStyleSheet("font-size:14px; color:#334155;")
        texto.setWordWrap(True)
        l.addWidget(texto)

        return f


    # -------------------------------------------------------------------
    # UTIL
    # -------------------------------------------------------------------
    def _fecha_mod_json(self):
        try:
            ts = os.path.getmtime(self.data.archivo_json)
            return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
        except:
            return "Desconocido"
