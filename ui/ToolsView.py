# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt


class ToolsView(QWidget):
    """
    Vista de Herramientas del Sistema – SHILLONG v3 Pro
    """

    def __init__(self, mainwindow):
        super().__init__()
        self.main = mainwindow
        self._build_ui()

    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(25)

        # TÍTULO PRINCIPAL
        titulo = QLabel("⚙ Herramientas del Sistema")
        titulo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1e293b;
        """)
        layout.addWidget(titulo)

        # SUBTÍTULO
        sub = QLabel("Opciones avanzadas para administración y mantenimiento.")
        sub.setStyleSheet("font-size: 15px; color: #475569; margin-top:-10px;")
        layout.addWidget(sub)

        # ==================================================================
        # TARJETA DE TEMA VISUAL
        # ==================================================================
        layout.addWidget(self._card_tema())

        # ==================================================================
        # TARJETA DE IMPORTAR/EXPORTAR EXCEL
        # ==================================================================
        layout.addWidget(self._card_excel())

        # ==================================================================
        # TARJETA DE BACKUP Y RESTAURACIÓN
        # ==================================================================
        layout.addWidget(self._card_backup())

        # ==================================================================
        # TARJETA DE ARCHIVO ACTUAL
        # ==================================================================
        layout.addWidget(self._card_archivo_actual())

        layout.addStretch()

    # --------------------------------------------------------------------
    # TARJETA: Tema Claro / Oscuro
    # --------------------------------------------------------------------
    def _card_tema(self):
        card = self._card()
        v = QVBoxLayout(card)

        titulo = QLabel("🎨 Tema visual")
        titulo.setStyleSheet("font-size:18px; font-weight:700; color:#334155;")
        v.addWidget(titulo)

        fila = QHBoxLayout()
        v.addLayout(fila)

        btn_claro = QPushButton("☀️ Modo Claro")
        btn_oscuro = QPushButton("🌙 Modo Oscuro")

        for b in (btn_claro, btn_oscuro):
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._btn_blue())

        btn_claro.clicked.connect(lambda: self.main.aplicar_tema("claro"))
        btn_oscuro.clicked.connect(lambda: self.main.aplicar_tema("oscuro"))

        fila.addWidget(btn_claro)
        fila.addWidget(btn_oscuro)

        return card

    # --------------------------------------------------------------------
    # TARJETA: Importar / Exportar Excel
    # --------------------------------------------------------------------
    def _card_excel(self):
        card = self._card()
        v = QVBoxLayout(card)

        titulo = QLabel("📄 Movimientos – Excel")
        titulo.setStyleSheet("font-size:18px; font-weight:700; color:#334155;")
        v.addWidget(titulo)

        fila = QHBoxLayout()
        v.addLayout(fila)

        btn_imp = QPushButton("📥 Importar desde Excel…")
        btn_exp = QPushButton("📤 Exportar a Excel…")

        for b in (btn_imp, btn_exp):
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._btn_blue())

        btn_imp.clicked.connect(self.main.importar_excel)
        btn_exp.clicked.connect(self.main.exportar_excel)

        fila.addWidget(btn_imp)
        fila.addWidget(btn_exp)

        return card

    # --------------------------------------------------------------------
    # TARJETA: Backup / Restore
    # --------------------------------------------------------------------
    def _card_backup(self):
        card = self._card()
        v = QVBoxLayout(card)

        titulo = QLabel("💾 Copias de Seguridad")
        titulo.setStyleSheet("font-size:18px; font-weight:700; color:#334155;")
        v.addWidget(titulo)

        fila = QHBoxLayout()
        v.addLayout(fila)

        btn_backup = QPushButton("📦 Crear Backup ZIP…")
        btn_restore = QPushButton("🔄 Restaurar desde ZIP…")

        for b in (btn_backup, btn_restore):
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._btn_blue())

        btn_backup.clicked.connect(self.main.crear_backup)
        btn_restore.clicked.connect(self.main.restore_backup)

        fila.addWidget(btn_backup)
        fila.addWidget(btn_restore)

        return card

    # --------------------------------------------------------------------
    # TARJETA: Archivo Contable Actual
    # --------------------------------------------------------------------
    def _card_archivo_actual(self):
        card = self._card()
        v = QVBoxLayout(card)

        titulo = QLabel("📂 Archivo contable en uso")
        titulo.setStyleSheet("font-size:18px; font-weight:700; color:#334155;")
        v.addWidget(titulo)

        archivo = str(self.main.data.archivo_json)
        lbl = QLabel(f"Archivo actual:\n<b>{archivo}</b>")
        lbl.setStyleSheet("font-size:15px; color:#334155; margin:8px 0;")
        v.addWidget(lbl)

        fila = QHBoxLayout()
        v.addLayout(fila)

        btn_cambiar = QPushButton("📁 Cambiar archivo JSON…")
        btn_abrir = QPushButton("🔍 Abrir archivo…")
        btn_carpeta = QPushButton("📂 Abrir carpeta del sistema…")

        for b in (btn_cambiar, btn_abrir, btn_carpeta):
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(self._btn_blue())

        btn_cambiar.clicked.connect(self.main.cambiar_archivo_contable)
        btn_abrir.clicked.connect(self.main.abrir_archivo_contable)
        btn_carpeta.clicked.connect(self.main.abrir_carpeta_sistema)

        fila.addWidget(btn_cambiar)
        fila.addWidget(btn_abrir)
        fila.addWidget(btn_carpeta)

        return card

    # ============================================================
    # ESTÉTICA
    # ============================================================
    def _card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
        """)
        return card

    def _btn_blue(self):
        return """
            QPushButton {
                background: #2563eb;
                color: white;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """
