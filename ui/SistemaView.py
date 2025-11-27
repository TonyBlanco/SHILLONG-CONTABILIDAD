# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt
from pathlib import Path
import json


class SistemaView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self._build_ui()

    # ============================================================
    # UI PRINCIPAL
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)

        titulo = QLabel("⚙️ Herramientas del Sistema")
        titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b;")
        layout.addWidget(titulo)

        subt = QLabel("Opciones avanzadas de mantenimiento del sistema")
        subt.setStyleSheet("font-size: 16px; color: #475569;")
        layout.addWidget(subt)

        # CARD
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(25, 25, 25, 25)
        card_l.setSpacing(20)

        # ============================================================
        # ARCHIVO JSON ACTUAL
        # ============================================================
        lbl_json = QLabel("Archivo JSON en uso:")
        lbl_json.setStyleSheet("font-size: 18px; font-weight: bold; color:#1e293b;")
        card_l.addWidget(lbl_json)

        self.lbl_archivo = QLabel(str(self.data.archivo_json))
        self.lbl_archivo.setStyleSheet("font-size: 15px; color:#334155; background:#f1f5f9; padding:8px; border-radius:6px;")
        card_l.addWidget(self.lbl_archivo)

        # ============================================================
        # BOTONES
        # ============================================================

        # CAMBIAR JSON
        btn_cambiar = QPushButton("📂 Cambiar archivo JSON…")
        btn_cambiar.setStyleSheet(self._btn())
        btn_cambiar.clicked.connect(self.cambiar_json)
        card_l.addWidget(btn_cambiar)

        # CREAR NUEVO JSON
        btn_nuevo = QPushButton("🆕 Crear archivo JSON nuevo…")
        btn_nuevo.setStyleSheet(self._btn())
        btn_nuevo.clicked.connect(self.crear_json)
        card_l.addWidget(btn_nuevo)

        # IMPORTAR EXCEL
        btn_importar = QPushButton("📥 Importar movimientos desde Excel…")
        btn_importar.setStyleSheet(self._btn())
        btn_importar.clicked.connect(self.importar_excel)
        card_l.addWidget(btn_importar)

        layout.addWidget(card)
        layout.addStretch()

    # ============================================================
    def _btn(self):
        return """
            QPushButton {
                background: #2563eb;
                color: white;
                padding: 12px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover { background: #1e40af; }
        """

    # ============================================================
    # CAMBIAR ARCHIVO JSON
    # ============================================================
    def cambiar_json(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo JSON",
            "",
            "Archivos JSON (*.json)"
        )
        if not ruta:
            return

        self.data.asignar_archivo(Path(ruta))
        self.data.cargar()

        self.lbl_archivo.setText(str(ruta))

        QMessageBox.information(self, "OK", "Archivo JSON cambiado correctamente.")

    # ============================================================
    # CREAR JSON NUEVO
    # ============================================================
    def crear_json(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Crear nuevo archivo JSON",
            "",
            "Archivos JSON (*.json)",
        )
        if not ruta:
            return

        # Preguntar si existe
        p = Path(ruta)
        if p.exists():
            resp = QMessageBox.question(
                self,
                "Confirmar",
                "El archivo ya existe. ¿Deseas sobrescribirlo?",
            )
            if resp != QMessageBox.Yes:
                return

        # Crear archivo vacío
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

        self.data.asignar_archivo(Path(ruta))
        self.data.cargar()

        self.lbl_archivo.setText(str(ruta))

        QMessageBox.information(self, "OK", "Nuevo archivo JSON creado correctamente.")

    # ============================================================
    # IMPORTAR EXCEL (AÚN NO IMPLEMENTADO)
    # ============================================================
    def importar_excel(self):
        QMessageBox.information(
            self,
            "Importar Excel",
            "La función Importar Excel aún no está implementada en esta versión.\n"
            "Usa la opción del menú Herramientas próximamente."
        )
