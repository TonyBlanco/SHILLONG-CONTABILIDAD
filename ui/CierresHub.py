# -*- coding: utf-8 -*-
"""
CierresHub.py - Contenedor de cierres y BI
Agrupa Libro Mensual (principal), Cierre Mensual, Cierre Anual e Informes BI en tabs.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.LibroMensualView import LibroMensualView
from ui.CierreMensualView import CierreMensualView
from ui.CierreView import CierreView
from ui.InformesView import InformesView


class CierresHub(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setDocumentMode(True)
        tabs.setMovable(False)

        # Tab principal: Libro Mensual (edición/auditoría/export)
        self.tab_libro = LibroMensualView(self.data)
        tabs.addTab(self.tab_libro, "Libro Mensual")

        # Tab Cierre Mensual (herramientas adicionales)
        self.tab_cierre = CierreMensualView(self.data)
        tabs.addTab(self.tab_cierre, "Cierre Mensual")

        # Tab Cierre Anual
        self.tab_anual = CierreView(self.data)
        tabs.addTab(self.tab_anual, "Cierre Anual")

        # Tab Informes BI
        self.tab_informes = InformesView(self.data)
        tabs.addTab(self.tab_informes, "Informes BI")

        layout.addWidget(tabs)

    def actualizar(self):
        # Propaga actualización a la pestaña activa
        for view in [self.tab_libro, self.tab_cierre, self.tab_anual, self.tab_informes]:
            if hasattr(view, "actualizar"):
                view.actualizar()
            elif hasattr(view, "actualizar_datos"):
                view.actualizar_datos()
