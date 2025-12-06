# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QLabel, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Signal, Qt
import os


class Sidebar(QWidget):

    menu_signal = Signal(str)

    def __init__(self, main):
        super().__init__()
        self.main = main

        # Base path del proyecto
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_path = os.path.join(base, "assets", "icons")

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)

        # ----------------------------------------------------------
        #   ESTILO GLOBAL SIDEBAR
        # ----------------------------------------------------------
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 15px;
                font-weight: 600;
                color: #64748b;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #334155;
            }
            QPushButton[selected="true"] {
                background-color: #2563eb;
                color: #ffffff;
            }
        """)

        # ----------------------------------------------------------
        #   BOTONES DEL MENÚ
        # ----------------------------------------------------------
        self.btn_dashboard = self._crear_boton("Dashboard", "dashboard")
        self.btn_registrar = self._crear_boton("Registrar", "registrar")
        self.btn_diario = self._crear_boton("Diario", "diario")
        self.btn_pendientes = self._crear_boton("Pendientes", "pendientes")
        self.btn_libro = self._crear_boton("Libro Mensual", "libro_mensual")
        self.btn_cierres = self._crear_boton("Cierres & BI", "cierres")
        self.btn_ayuda = self._crear_boton("Ayuda / Soporte", "ayuda")

        # Separador para empujar “Herramientas” al fondo
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.btn_tools = self._crear_boton("Herramientas", "tools")

        # Logo al fondo
        logo_path = os.path.join(base, "assets", "logo", "shillong_logov3.png")
        if os.path.exists(logo_path):
            logo = QLabel()
            pix = QPixmap(logo_path)
            if not pix.isNull():
                pix = pix.scaledToWidth(140, Qt.SmoothTransformation)
                logo.setPixmap(pix)
                logo.setAlignment(Qt.AlignCenter)
                logo.setStyleSheet("padding-top: 12px; padding-bottom: 6px;")
                layout.addWidget(logo)

    # ----------------------------------------------------------
    #   Crear botón del menú
    # ----------------------------------------------------------
    def _crear_boton(self, texto, id_vista):
        btn = QPushButton(texto)
        btn.setProperty("id_vista", id_vista)
        btn.setProperty("selected", "false")

        btn.clicked.connect(lambda: self._emitir_cambio(btn, id_vista))

        self.layout().addWidget(btn)
        return btn

    # ----------------------------------------------------------
    #   Emitir señal de cambio de vista
    # ----------------------------------------------------------
    def _emitir_cambio(self, btn_sender, id_vista):
        self.marcar_boton(id_vista)
        self.menu_signal.emit(id_vista)

    # ----------------------------------------------------------
    #   Marcar botón seleccionado con estilo
    # ----------------------------------------------------------
    def marcar_boton(self, id_vista_objetivo):
        for btn in self.findChildren(QPushButton):
            es_el = btn.property("id_vista") == id_vista_objetivo
            btn.setProperty("selected", "true" if es_el else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
