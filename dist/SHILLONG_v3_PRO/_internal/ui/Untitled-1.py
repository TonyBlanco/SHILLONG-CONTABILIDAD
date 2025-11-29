# -*- coding: utf-8 -*-
"""
RegistrarView — SHILLONG CONTABILIDAD v3 PRO
Versión FINAL 100% funcional (2025) – Diseño original + validación personalizada
"""

from models.CuentasMotor import MotorCuentas

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox,
    QCompleter, QHeaderView, QApplication, QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QDate
import random
from datetime import datetime


class RegistrarView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.motor = MotorCuentas()

        QApplication.setStyle("windows")
        self.setStyleSheet(self._estilo())

        self._build_ui()
        self._cargar_ultimos()

    def _estilo(self):
        return """
            QWidget { background: #f8fafc; font-family: 'Segoe UI'; }
            QLabel { color: #1e293b; font-size: 14px; font-weight: 600; }
            QLineEdit, QDateEdit, QComboBox {
                padding: 10px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 15px;
                background: white;
                min-height: 38px;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #3b82f6; }
            QPushButton {
                padding: 9px 20px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                color: white;
                min-height: 32px;
            }
            QPushButton#guardar { background: #2563eb; }
            QPushButton#refresh { background: #64748b; }
        """

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Título
        titulo = QLabel("Registrar Movimiento")
        titulo.setStyleSheet("font-size: 26px; font-weight: 800; color: #1e293b;")
        layout.addWidget(titulo)

        # Formulario
        form = QGroupBox("Nuevo movimiento")
        form.setStyleSheet("QGroupBox { font-size: 17px; font-weight: bold; }")
        fl = QFormLayout(form)

        # Fecha
        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        fl.addRow("Fecha:", self.fecha)

        # Cuenta + Concepto
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.setEditable(True)
        self.cuenta_combo.addItems(self.motor.todas_las_opciones())
        completer = QCompleter(self.motor.todas_las_opciones())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.cuenta_combo.setCompleter(completer)

        self.concepto = QLineEdit()
        h = QHBoxLayout()
        h.addWidget(self.cuenta_combo, 3)
        h.addWidget(self.concepto, 2)
        fl.addRow("Cuenta / Concepto:", h)

        # Documento
        self.documento = QLineEdit()
        fl.addRow("Documento:", self.documento)

        # Debe / Haber
        self.debe = QLineEdit()
        self.haber = QLineEdit()
        dh = QHBoxLayout()
        dh.addWidget(QLabel("Debe:"))
        dh.addWidget(self.debe)
        dh.addWidget(QLabel("Haber:"))
        dh.addWidget(self.haber)
        fl.addRow(dh)

        # Banco y estado
        banco_layout = QHBoxLayout()
        self.banco_group = QButtonGroup()
        for b in ["Caja", "Federal Bank", "SBI", "Union Bank", "Otro"]:
            rb = QRadioButton(b)
            self.banco_group.addButton(rb)
            banco_layout.addWidget(rb)
        self.banco_group.buttons()[0].setChecked(True)

        self.estado_pagado = QRadioButton("Pagado")
        self.estado_pendiente = QRadioButton("Pendiente")
        self.estado_pagado.setChecked(True)
        banco_layout.addStretch()
        banco_layout.addWidget(self.estado_pagado)
        banco_layout.addWidget(self.estado_pendiente)
        fl.addRow("Banco / Estado:", banco_layout)

        # Botones
        btns = QHBoxLayout()
        guardar = QPushButton("Guardar")
        guardar.setObjectName("guardar")
        guardar.clicked.connect(self._guardar)
        refresh = QPushButton("Refrescar")
        refresh.clicked.connect(self._cargar_ultimos)
        btns.addWidget(guardar)
        btns.addWidget(refresh)
        fl.addRow(btns)

        layout.addWidget(form)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Doc", "Concepto", "Cuenta", "Nombre", "Debe", "Haber", "Banco", "Estado", "Saldo"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        self._cargar_ultimos()

    def _guardar(self):
        fecha = self.fecha.date().toString("dd/MM/yyyy")
        documento = self.documento.text().strip()
        concepto = self.concepto.text().strip()
        cuenta_texto = self.cuenta_combo.currentText().strip()

        if not concepto:
            QMessageBox.warning(self, "Error", "El concepto es obligatorio")
            return

        # Extraer código de cuenta
        if " – " in cuenta_texto:
            cuenta = cuenta_texto.split(" – ")[0]
        elif cuenta_texto.startswith("SUB – "):
            cuenta = "659090"
        else:
            QMessageBox.warning(self, "Error", "Selecciona una cuenta válida")
            return

        # Validación personalizada EXACTAMENTE como pediste
        if not self.motor.es_concepto_valido(cuenta, concepto):
            msg = QMessageBox(self)
            msg.setWindowTitle("Validación")
            msg.setText("El concepto no coincide con las reglas típicas.\n¿Desea guardarlo igual?")
            msg.setIcon(QMessageBox.Question)

            yes_btn = msg.addButton("Sí", QMessageBox.YesRole)
            msg.addButton("No", QMessageBox.NoRole)

            msg.exec()

            if msg.clickedButton() != yes_btn:
                return

            # Aprende la nueva regla
            self.motor.agregar_concepto_a_reglas(cuenta, concepto.lower())

        # Importes
        try:
            debe = float(self.debe.text() or 0)
            haber = float(self.haber.text() or 0)
        except:
            QMessageBox.warning(self, "Error", "Importes deben ser números")
            return

        if debe == haber == 0:
            QMessageBox.warning(self, "Error", "Debe o Haber debe ser mayor a 0")
            return

        # Banco y estado
        banco = next((b.text() for b in self.banco_group.buttons() if b.isChecked()), "Caja")
        estado = "pagado" if self.estado_pagado.isChecked() else "pendiente"

        # Saldo
        saldo_prev = self.data.movimientos[-1]["saldo"] if self.data.movimientos else 0.0
        saldo = round(saldo_prev + haber - debe, 2)

        # Movimiento
        mov = {
            "fecha": fecha,
            "documento": documento or f"SIN-DOC-{random.randint(10000,99999)}",
            "concepto": concepto,
            "cuenta": cuenta,
            "debe": debe,
            "haber": haber,
            "moneda": "INR",
            "banco": banco,
            "estado": estado,
            "saldo": saldo
        }

        self.data.movimientos.append(mov)
        self.data.guardar()

        QMessageBox.information(self, "Éxito", "Movimiento guardado correctamente")
        self.concepto.clear()
        self.debe.clear()
        self.haber.clear()
        self.documento.clear()
        self._cargar_ultimos()

    def _cargar_ultimos(self):
        # Muestra solo los últimos 20 movimientos
        movs = sorted(self.data.movimientos, key=lambda m: datetime.strptime(m["fecha"], "%d/%m/%Y"), reverse=True)[:20]
        self.tabla.setRowCount(0)

        saldo = 0
        for m in movs:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo += haber - debe

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            items = [
                m["fecha"],
                m.get("documento", ""),
                m["concepto"],
                m["cuenta"],
                self.data.obtener_nombre_cuenta(m["cuenta"]),
                f"{debe:,.2f}" if debe else "",
                f"{haber:,.2f}" if haber else "",
                m["banco"],
                m["estado"],
                f"{saldo:,.2f}"
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(str(val))
                if col in (5, 6, 9):
                    item.setTextAlignment(Qt.AlignRight)
                self.tabla.setItem(row, col, item)