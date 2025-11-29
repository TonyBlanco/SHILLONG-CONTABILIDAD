# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal  # <--- IMPORTANTE: Signal añadido
import os


class Sidebar(QWidget):
    
    # 🔥 Esta es la señal que MainWindow está buscando
    menu_signal = Signal(str)

    def __init__(self, main):
        super().__init__()
        self.main = main

        # Ruta absoluta a icons/
        # Ajusta esto si tu estructura de carpetas es diferente
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_path = os.path.join(base, "assets", "icons")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)

        # Estilo CSS moderno para el Sidebar
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

        # --- DEFINICIÓN DE BOTONES ---
        # El nombre del botón (ej: "dashboard") debe coincidir con las claves en MainWindow.views
        
        self.btn_dashboard = self._crear_boton("Dashboard", "dashboard")
        self.btn_registrar = self._crear_boton("Registrar", "registrar")
        self.btn_diario = self._crear_boton("Diario", "diario")
        self.btn_pendientes = self._crear_boton("Pendientes", "pendientes")
        self.btn_libro = self._crear_boton("Libro Mensual", "libro_mensual")
        self.btn_cierre = self._crear_boton("Cierre Mensual", "cierre_mensual") # Nuevo
        self.btn_anual = self._crear_boton("Cierre Anual", "cierre_anual")
        self.btn_informes = self._crear_boton("Informes BI", "informes")
        
        # Espaciador para empujar herramientas y sistema abajo
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.btn_tools = self._crear_boton("Herramientas", "tools")
        self.btn_sistema = self._crear_boton("Sistema", "sistema")

    # ---------------------------------------------------------
    # Crear botón
    # ---------------------------------------------------------
    def _crear_boton(self, texto, id_vista):
        btn = QPushButton(texto)
        btn.setProperty("id_vista", id_vista) # Guardamos el ID en el botón
        btn.setProperty("selected", "false")
        
        # Intentar cargar icono (opcional)
        # ruta_icono = os.path.join(self.icon_path, f"{id_vista}.png")
        # if os.path.exists(ruta_icono):
        #     btn.setIcon(QIcon(ruta_icono))
        #     btn.setIconSize(QSize(20, 20))

        # Conectar acción usando el ID de vista
        btn.clicked.connect(lambda: self._emitir_cambio(btn, id_vista))
        
        self.layout().addWidget(btn)
        return btn

    # ---------------------------------------------------------
    # Emitir señal al hacer clic
    # ---------------------------------------------------------
    def _emitir_cambio(self, btn_sender, id_vista):
        # 1. Actualizar visualmente (marcar seleccionado)
        self.marcar_boton(id_vista)
        
        # 2. Emitir la señal para que MainWindow cambie la pantalla
        self.menu_signal.emit(id_vista)

    # ---------------------------------------------------------
    # Método público para resaltar un botón desde fuera
    # ---------------------------------------------------------
    def marcar_boton(self, id_vista_objetivo):
        for btn in self.findChildren(QPushButton):
            es_el_elegido = btn.property("id_vista") == id_vista_objetivo
            
            # Actualizar propiedad
            btn.setProperty("selected", "true" if es_el_elegido else "false")
            
            # Forzar refresco de estilo
            btn.style().unpolish(btn)
            btn.style().polish(btn)