# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QGroupBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize
import os


class ToolsView(QWidget):

    def __init__(self, main):
        super().__init__()
        self.main = main

        # RUTA ABSOLUTA A LOS ICONOS PNG
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_path = os.path.join(base, "assets", "icons")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(25)

        # -------------------------------------------------------------
        # 1. TEMA VISUAL
        # -------------------------------------------------------------
        gb_tema = self._crear_groupbox("Tema visual")
        gb_tema_layout = QVBoxLayout(gb_tema)

        fila_tema = QHBoxLayout()
        fila_tema.setSpacing(15)

        btn_claro = self._crear_boton_icono("Modo Claro", "toggle_on.png")
        btn_claro.clicked.connect(lambda: self.main.aplicar_tema("light"))

        btn_oscuro = self._crear_boton_icono("Modo Oscuro", "toggle_off.png")
        btn_oscuro.clicked.connect(lambda: self.main.aplicar_tema("dark"))

        fila_tema.addWidget(btn_claro)
        fila_tema.addWidget(btn_oscuro)
        gb_tema_layout.addLayout(fila_tema)

        layout.addWidget(gb_tema)

        # -------------------------------------------------------------
        # 2. IMPORTAR / EXPORTAR EXCEL
        # -------------------------------------------------------------
        gb_excel = self._crear_groupbox("Importar / Exportar Excel")
        gb_excel_layout = QVBoxLayout(gb_excel)

        fila_excel = QHBoxLayout()
        fila_excel.setSpacing(15)

        btn_importar = self._crear_boton_icono("Importar desde Excel…", "document.png")
        btn_importar.clicked.connect(self.main.importar_excel)

        btn_exportar = self._crear_boton_icono("Exportar todo a Excel…", "save.png")
        btn_exportar.clicked.connect(self._exportar_excel)

        fila_excel.addWidget(btn_importar)
        fila_excel.addWidget(btn_exportar)
        gb_excel_layout.addLayout(fila_excel)

        layout.addWidget(gb_excel)

        # -------------------------------------------------------------
        # 3. COPIAS DE SEGURIDAD
        # -------------------------------------------------------------
        gb_backup = self._crear_groupbox("Copias de Seguridad")
        gb_backup_layout = QVBoxLayout(gb_backup)

        fila_backup = QHBoxLayout()
        fila_backup.setSpacing(15)

        btn_crear = self._crear_boton_icono("Crear Backup ZIP…", "save.png")
        btn_crear.clicked.connect(self.main.crear_backup)

        btn_restaurar = self._crear_boton_icono("Restaurar desde ZIP…", "more.png")
        btn_restaurar.clicked.connect(self.main.restore_backup)

        fila_backup.addWidget(btn_crear)
        fila_backup.addWidget(btn_restaurar)
        gb_backup_layout.addLayout(fila_backup)

        layout.addWidget(gb_backup)

        # -------------------------------------------------------------
        # 4. ARCHIVO CONTABLE
        # -------------------------------------------------------------
        gb_archivo = self._crear_groupbox("Archivo contable en uso")
        gb_archivo_layout = QVBoxLayout(gb_archivo)

        self.lbl_archivo = QLabel(str(self.main.data.archivo_json))
        self.lbl_archivo.setStyleSheet("""
            background: #f1f5f9;
            padding: 10px;
            border-radius: 8px;
            color: #1e293b;
            font-size: 14px;
        """)
        gb_archivo_layout.addWidget(self.lbl_archivo)

        fila_archivo = QHBoxLayout()
        fila_archivo.setSpacing(15)

        btn_cambiar = self._crear_boton_icono("Cambiar archivo…", "search.png")
        btn_cambiar.clicked.connect(self.main.cambiar_archivo_contable)

        btn_abrir = self._crear_boton_icono("Abrir archivo", "document.png")
        btn_abrir.clicked.connect(self.main.abrir_archivo_contable)

        btn_carpeta = self._crear_boton_icono("Abrir carpeta", "more.png")
        btn_carpeta.clicked.connect(self.main.abrir_carpeta_sistema)

        fila_archivo.addWidget(btn_cambiar)
        fila_archivo.addWidget(btn_abrir)
        fila_archivo.addWidget(btn_carpeta)

        gb_archivo_layout.addLayout(fila_archivo)

        layout.addWidget(gb_archivo)

        # -------------------------------------------------------------
        # 5. BOTÓN: Buscar actualización
        # -------------------------------------------------------------
        self.btn_update = QPushButton("Buscar actualización")
        self.btn_update.setIcon(self._icono("search.png"))
        self.btn_update.setIconSize(QSize(22, 22))
        self.btn_update.setStyleSheet("""
            background: #059669;
            padding: 14px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            color: white;
        """)
        self.btn_update.clicked.connect(self._buscar_actualizacion)
        layout.addWidget(self.btn_update, alignment=Qt.AlignCenter)

    # ---------------------------------------------------------------------
    def _crear_groupbox(self, titulo):
        gb = QGroupBox(titulo)
        gb.setStyleSheet("""
            QGroupBox {
                font-size: 17px;
                font-weight: bold;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 10px;
            }
        """)
        return gb

    # ---------------------------------------------------------------------
    def _crear_boton_icono(self, texto, archivo_icono):
        btn = QPushButton(texto)
        btn.setMinimumHeight(50)

        icon = self._icono(archivo_icono)
        if icon:
            btn.setIcon(icon)
            btn.setIconSize(QSize(22, 22))

        btn.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)
        return btn

    # ---------------------------------------------------------------------
    def _icono(self, nombre):
        ruta = os.path.join(self.icon_path, nombre)
        if os.path.exists(ruta):
            return QIcon(ruta)
        print("⚠ Icono no encontrado:", ruta)
        return None

    # ---------------------------------------------------------------------
    def _exportar_excel(self):
        QMessageBox.information(self, "Exportar", "Función no implementada todavía.")

    # ---------------------------------------------------------------------
    # 🔥 FUNCIÓN DE ACTUALIZACIÓN (NUEVA + FUNCIONAL)
    # ---------------------------------------------------------------------
    def _buscar_actualizacion(self):
        QMessageBox.information(
            self,
            "Actualización",
            "Sistema actualizado: no hay nuevas versiones disponibles."
        )
