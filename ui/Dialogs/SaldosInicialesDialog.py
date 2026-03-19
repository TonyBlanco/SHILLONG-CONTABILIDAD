# -*- coding: utf-8 -*-
"""
SaldosInicialesDialog — SHILLONG CONTABILIDAD v3.8
----------------------------------------------------
Diálogo para introducir / editar los saldos iniciales de TODOS los bancos
de un mes/año determinado en una sola pantalla.

Uso típico:
    dlg = SaldosInicialesDialog(parent)
    dlg.exec()
"""

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QDoubleSpinBox, QComboBox, QSpinBox,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt

try:
    from models.SaldosMensuales import SaldosMensuales
except ImportError:
    SaldosMensuales = None


# Orden fijo de bancos (mismo que bancos.json)
ORDEN_BANCOS = [
    "Caja",
    "SBI- Sr sindhu",
    "Federal Bank sr Sindhu",
    "Federal Bank- sr Juliana",
    "Federal Bank sr Shairilin",
    "Union Bank, sr Elisa",
    "Post- office sr Sindhu",
    "Post-office sr Shairilin",
]


class SaldosInicialesDialog(QDialog):
    """Permite introducir los saldos iniciales de todos los bancos de un mes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💰 Saldos Iniciales del Año")
        self.setMinimumWidth(480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._saldos_model = SaldosMensuales() if SaldosMensuales else None
        self._bancos = self._cargar_bancos()
        self._spinboxes = {}  # banco -> QDoubleSpinBox

        self._build_ui()

    # ------------------------------------------------------------------
    # Carga de bancos
    # ------------------------------------------------------------------
    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                nombres = [b["nombre"] for b in json.load(f).get("banks", [])]
                if nombres:
                    return nombres
        except (IOError, json.JSONDecodeError, KeyError):
            pass
        return ORDEN_BANCOS

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # --- Título ---
        lbl = QLabel("Saldos Iniciales por Banco")
        lbl.setStyleSheet("font-size:18px; font-weight:800; color:#1e293b;")
        layout.addWidget(lbl)

        lbl_sub = QLabel(
            "Introduce el saldo inicial de cada banco para el mes y año seleccionados.\n"
            "Normalmente se usa Enero del año contable (ej. Enero 2026)."
        )
        lbl_sub.setStyleSheet("color:#64748b; font-size:12px;")
        lbl_sub.setWordWrap(True)
        layout.addWidget(lbl_sub)

        # --- Separador ---
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#e2e8f0;")
        layout.addWidget(sep)

        # --- Mes / Año ---
        fecha_layout = QHBoxLayout()
        fecha_layout.addWidget(QLabel("Mes:"))

        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems([
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ])
        self.cbo_mes.setCurrentIndex(0)  # Enero por defecto
        fecha_layout.addWidget(self.cbo_mes)

        fecha_layout.addSpacing(20)
        fecha_layout.addWidget(QLabel("Año:"))

        self.sp_anio = QSpinBox()
        self.sp_anio.setRange(2020, 2035)
        self.sp_anio.setValue(2026)
        fecha_layout.addWidget(self.sp_anio)

        btn_cargar = QPushButton("🔄 Cargar existentes")
        btn_cargar.setStyleSheet(
            "background:#3b82f6; color:white; font-weight:bold; "
            "padding:5px 12px; border-radius:5px;"
        )
        btn_cargar.clicked.connect(self._cargar_valores)
        fecha_layout.addWidget(btn_cargar)
        fecha_layout.addStretch()

        layout.addLayout(fecha_layout)

        # --- Formulario de bancos ---
        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color:#e2e8f0;")
        layout.addWidget(sep2)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(8)

        for banco in self._bancos:
            sb = QDoubleSpinBox()
            sb.setRange(-999_999_999, 999_999_999)
            sb.setDecimals(2)
            sb.setGroupSeparatorShown(True)
            sb.setMinimumWidth(180)
            sb.setSuffix("  INR")
            self._spinboxes[banco] = sb
            form.addRow(banco + ":", sb)

        layout.addLayout(form)

        # --- Botones ---
        sep3 = QFrame(); sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("color:#e2e8f0;")
        layout.addWidget(sep3)

        btns = QHBoxLayout()
        btn_guardar = QPushButton("💾 Guardar todos")
        btn_guardar.setStyleSheet(
            "background:#059669; color:white; font-weight:bold; "
            "padding:8px 20px; border-radius:6px; font-size:13px;"
        )
        btn_guardar.clicked.connect(self._guardar)

        btn_ceros = QPushButton("Poner todo a 0")
        btn_ceros.setStyleSheet("padding:6px 12px; border-radius:6px;")
        btn_ceros.clicked.connect(self._limpiar)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("padding:6px 12px; border-radius:6px;")
        btn_cerrar.clicked.connect(self.reject)

        btns.addWidget(btn_ceros)
        btns.addStretch()
        btns.addWidget(btn_cerrar)
        btns.addWidget(btn_guardar)
        layout.addLayout(btns)

        # Cargar valores al arrancar
        self._cargar_valores()

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------
    def _mes_anio(self):
        return self.cbo_mes.currentIndex() + 1, self.sp_anio.value()

    def _cargar_valores(self):
        """Precarga los spinboxes con los valores existentes en saldos_mensuales.json."""
        if not self._saldos_model:
            return
        mes, anio = self._mes_anio()
        resumen = self._saldos_model.obtener_resumen_mes(mes, anio) or {}
        for banco, sb in self._spinboxes.items():
            dato = resumen.get(banco)
            if isinstance(dato, dict):
                sb.setValue(float(dato.get("inicial", 0.0)))
            else:
                sb.setValue(0.0)

    def _limpiar(self):
        for sb in self._spinboxes.values():
            sb.setValue(0.0)

    def _guardar(self):
        if not self._saldos_model:
            QMessageBox.critical(
                self, "Error",
                "El módulo SaldosMensuales no está disponible."
            )
            return

        mes, anio = self._mes_anio()
        guardados = 0

        for banco, sb in self._spinboxes.items():
            self._saldos_model.editar_saldo_inicial(mes, anio, banco, sb.value())
            guardados += 1

        nombre_mes = self.cbo_mes.currentText()
        QMessageBox.information(
            self,
            "Saldos guardados",
            f"✅ Se guardaron los saldos iniciales de {guardados} bancos\n"
            f"   Período: {nombre_mes} {anio}"
        )
