# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
import os


class HeaderBar(QWidget):
    def __init__(self, main=None):
        super().__init__()

        # Layout vertical (título + subtítulo)
        contenedor = QVBoxLayout(self)
        contenedor.setContentsMargins(20, 10, 20, 10)
        contenedor.setSpacing(0)

        # Layout horizontal para título institucional
        layout_superior = QHBoxLayout()
        layout_superior.setContentsMargins(0, 0, 0, 0)
        layout_superior.setSpacing(12)

        # Ruta al logo transparente
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base, "assets", "logo", "shillong_logov3.png")

        # LOGO
        logo = QLabel()
        logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo.setAttribute(Qt.WA_TranslucentBackground, True)
        logo.setStyleSheet("background: transparent;")

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                40, 40,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            logo.setPixmap(pix)
        else:
            logo.setText("[Logo]")
            logo.setStyleSheet("color: red; font-size: 12px;")

        layout_superior.addWidget(logo)

        # TÍTULO INSTITUCIONAL
        titulo = QLabel("Shillong Contabilidad — Sisters Hospitallers")
        titulo.setStyleSheet("color: #334155;")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout_superior.addWidget(titulo)
        layout_superior.addStretch()

        # Añadir al contenedor
        contenedor.addLayout(layout_superior)

        # SUBTÍTULO DINÁMICO (el que cambia según la vista)
        self.subtitulo = QLabel("")
        self.subtitulo.setStyleSheet("color: #64748b; font-size: 13px; margin-top: 2px;")
        self.subtitulo.setAlignment(Qt.AlignLeft)
        contenedor.addWidget(self.subtitulo)

        # Fondo del header
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
            }
        """)

    # -------------------------------------------------------
    #   ACTUALIZAR SUBTÍTULO SEGÚN LA VISTA
    # -------------------------------------------------------
    def actualizar_titulo(self, id_vista):
        titulos = {
            "dashboard": "Dashboard",
            "registrar": "Registrar Movimientos",
            "diario": "Libro Diario",
            "pendientes": "Pendientes",
            "libro_mensual": "Libro Mensual",
            "cierre_mensual": "Cierre Mensual",
            "cierre_anual": "Cierre Anual",
            "informes": "Informes BI",
            "ayuda": "Ayuda y Soporte",
            "tools": "Herramientas"
        }

        texto = titulos.get(id_vista, "")
        self.subtitulo.setText(texto)
