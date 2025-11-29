# -*- coding: utf-8 -*-
"""
RegistrarView — SHILLONG CONTABILIDAD v3 PRO
Versión DEFINITIVA (Diseño original + DPI-SAFE + FIX QMessageBox)
"""

from models.CuentasMotor import MotorCuentas

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QCompleter, QHeaderView, QAbstractItemView,
    QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from datetime import datetime
import random


class RegistrarView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.motor = MotorCuentas()

        self.tema_oscuro = False

        self.setStyleSheet(self._estilo_claro())
        self._build_ui()
        self._cargar_ultimos()

    # ============================================================
    # ESTILOS DPI-SAFE
    # ============================================================
    def _estilo_claro(self):
        return """
            QWidget { background: #f8fafc; font-family: 'Segoe UI'; }
            QLabel { color: #1e293b; font-size: 14px; }
            QLineEdit, QDateEdit, QComboBox {
                padding: 10px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                font-size: 15px;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #3b82f6; }

            QPushButton {
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                color: white;
            }
            QPushButton#refresh { background: #64748b; }
            QPushButton#duplicar { background: #7c3aed; }
            QPushButton#guardar { background: #2563eb; }
            QPushButton#limpiar { background: #0ea5e9; }
            QPushButton#limpiar_dh { background: #6b7280; }
            QPushButton#nuevo { background: #059669; }
            QPushButton#tema { background: #475569; }

            QHeaderView::section {
                background: #e0e7ff;
                padding: 8px;
                font-weight: bold;
            }
            QGroupBox {
                border: 2px solid #cbd5e1;
                border-radius: 10px;
                padding: 10px;
            }
        """

    def _estilo_oscuro(self):
        return """
            QWidget { background: #0f172a; color: #e2e8f0; }
            QLabel { color: #e2e8f0; }
            QLineEdit, QDateEdit, QComboBox {
                background: #1e293b;
                color: #e2e8f0;
                border: 2px solid #334155;
                padding: 10px 14px;
                border-radius: 8px;
            }
            QPushButton#refresh { background: #64748b; }
            QPushButton#duplicar { background: #8b5cf6; }
            QPushButton#guardar { background: #3b82f6; }
            QPushButton#limpiar { background: #0ea5e9; }
            QPushButton#limpiar_dh { background: #6b7280; }
            QPushButton#nuevo { background: #059669; }
            QPushButton#tema { background: #475569; }
            QHeaderView::section { background: #334155; color: white; }
        """

    def _cambiar_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        self.setStyleSheet(
            self._estilo_oscuro() if self.tema_oscuro else self._estilo_claro()
        )
        self.btn_tema.setText("Modo claro" if self.tema_oscuro else "Modo oscuro")

    # ============================================================
    # UI PRINCIPAL (ORIGINAL EXACTA)
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # -----------------------------
        # TÍTULO + BOTÓN TEMA
        # -----------------------------
        top = QHBoxLayout()
        titulo = QLabel("REGISTRAR MOVIMIENTO CONTABLE")
        titulo.setStyleSheet("font-size: 26px; font-weight: 800;")
        self.btn_tema = QPushButton("Modo oscuro")
        self.btn_tema.setObjectName("tema")
        self.btn_tema.clicked.connect(self._cambiar_tema)

        top.addWidget(titulo)
        top.addStretch()
        top.addWidget(self.btn_tema)
        layout.addLayout(top)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # FECHA
        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setDate(QDate.currentDate())
        form.addRow("Fecha:", self.fecha)

        # DOCUMENTO
        self.documento = QLineEdit()
        self.documento.setPlaceholderText("Opcional — si está vacío se genera automático")
        form.addRow("Documento:", self.documento)

        # CUENTA CONTABLE — ORIGINAL COMPLETA
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.setEditable(True)

        opciones = []
        try:
            opciones = self.motor.todas_las_opciones()
        except:
            pass

        self.cuenta_combo.addItems(opciones)

        completer = QCompleter(opciones, self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.cuenta_combo.setCompleter(completer)

        self.cuenta_combo.currentTextChanged.connect(self._on_cuenta_changed)
        form.addRow("Cuenta contable:", self.cuenta_combo)

        # NOMBRE CUENTA
        self.lbl_nombre = QLabel("Seleccione una cuenta")
        self.lbl_nombre.setStyleSheet("font-style: italic; color: #64748b;")
        form.addRow("", self.lbl_nombre)

        # SUGERENCIAS
        self.lbl_sugerencias = QLabel("")
        self.lbl_sugerencias.setWordWrap(True)
        self.lbl_sugerencias.setStyleSheet("color:#6366f1; font-size:13px;")
        form.addRow("", self.lbl_sugerencias)

        # CONCEPTO
        self.concepto = QLineEdit()
        self.concepto.setPlaceholderText("Descripción del movimiento…")
        self.concepto.textChanged.connect(self._validar_concepto_live)
        form.addRow("Concepto:", self.concepto)

        # DEBE / HABER
        box_dh = QHBoxLayout()
        self.debe = QLineEdit("0,00")
        self.haber = QLineEdit("0,00")

        self.debe.textChanged.connect(self._calcular_importe)
        self.haber.textChanged.connect(self._calcular_importe)

        box_dh.addWidget(QLabel("Debe:"))
        box_dh.addWidget(self.debe)
        box_dh.addWidget(QLabel("Haber:"))
        box_dh.addWidget(self.haber)
        form.addRow("Importe:", box_dh)

        # ----------------------------------------------------
        # BANCO / ESTADO (ORIGINAL CHIP STYLE)
        # ----------------------------------------------------
        banco_estado = QHBoxLayout()

        # BANCO
        banco_layout = QHBoxLayout()
        self.banco_buttons = QButtonGroup(self)
        chip_banco = """
            QRadioButton {
                padding: 6px 14px;
                border-radius: 14px;
                background: #f1f5f9;
                border: 1px solid #cbd5e1;
            }
            QRadioButton:checked {
                background: #3b82f6;
                color: white;
                font-weight: bold;
            }
            QRadioButton::indicator { width:0; height:0; }
        """

        for b in ["Caja", "Federal Bank", "SBI", "Union Bank", "Otro"]:
            rb = QRadioButton(b)
            rb.setStyleSheet(chip_banco)
            banco_layout.addWidget(rb)
            self.banco_buttons.addButton(rb)
            if b == "Caja":
                rb.setChecked(True)

        banco_estado.addLayout(banco_layout)

        # ESTADO
        estado_layout = QHBoxLayout()
        self.estado_buttons = QButtonGroup(self)

        chip_estado = """
            QRadioButton {
                padding: 6px 14px;
                border-radius: 14px;
                background: #f1f5f9;
                border: 1px solid #cbd5e1;
            }
            QRadioButton:checked {
                background: #10b981;
                color: white;
                font-weight: bold;
            }
            QRadioButton::indicator { width:0; height:0; }
        """

        for e in ["Pagado", "Pendiente"]:
            rb = QRadioButton(e)
            rb.setStyleSheet(chip_estado)
            estado_layout.addWidget(rb)
            self.estado_buttons.addButton(rb)
            if e == "Pagado":
                rb.setChecked(True)

        banco_estado.addLayout(estado_layout)
        banco_estado.addStretch()

        form.addRow("Banco / Estado:", banco_estado)

        layout.addLayout(form)

        # BOTONES GRANDES — ORIGINAL
        botones = QHBoxLayout()

        self.btn_refresh = QPushButton("Actualizar lista")
        self.btn_refresh.setObjectName("refresh")
        self.btn_refresh.clicked.connect(self._cargar_ultimos)

        self.btn_duplicar = QPushButton("Duplicar movimiento")
        self.btn_duplicar.setObjectName("duplicar")
        self.btn_duplicar.clicked.connect(self._duplicar)

        self.btn_guardar = QPushButton("Guardar Movimiento")
        self.btn_guardar.setObjectName("guardar")
        self.btn_guardar.clicked.connect(self._guardar)

        self.btn_limpiar = QPushButton("Limpiar Formulario")
        self.btn_limpiar.setObjectName("limpiar")
        self.btn_limpiar.clicked.connect(self._limpiar)

        self.btn_limpiar_dh = QPushButton("Limpiar Debe/Haber")
        self.btn_limpiar_dh.setObjectName("limpiar_dh")
        self.btn_limpiar_dh.clicked.connect(self._limpiar_dh)

        self.btn_nuevo = QPushButton("Nuevo Registro")
        self.btn_nuevo.setObjectName("nuevo")
        self.btn_nuevo.clicked.connect(self._nuevo_registro)

        for b in [
            self.btn_refresh, self.btn_duplicar, self.btn_guardar,
            self.btn_limpiar, self.btn_limpiar_dh, self.btn_nuevo
        ]:
            botones.addWidget(b)

        layout.addLayout(botones)

        # BUSCADOR
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar en movimientos…")
        self.buscador.textChanged.connect(self._filtrar_tabla)
        layout.addWidget(self.buscador)

        # TABLA
        self.tabla = QTableWidget(0, 10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Documento", "Concepto", "Cuenta",
            "Nombre Cuenta", "Debe", "Haber",
            "Banco", "Estado", "Saldo"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.tabla)

        # TOTALES
        self.lbl_totales = QLabel()
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        self.lbl_totales.setStyleSheet(
            "font-weight:bold;font-size:15px;padding:10px;background:#e0e7ff;border-radius:8px;"
        )
        layout.addWidget(self.lbl_totales)

    # ============================================================
    # INTERACCIÓN CUENTA
    # ============================================================
    def _on_cuenta_changed(self, texto):
        if " – " not in texto:
            self.lbl_nombre.setText("Seleccione una cuenta")
            self.lbl_sugerencias.setText("")
            return

        codigo = texto.split(" – ")[0]
        self.lbl_nombre.setText("→ " + self.motor.get_nombre(codigo))

        regla = self.motor.reglas.get(codigo, {})
        sugeridos = regla.get("permitidos", [])

        if sugeridos:
            self.lbl_sugerencias.setText("Ejemplos: " + ", ".join(sugeridos[:5]))
        else:
            self.lbl_sugerencias.setText("No hay sugerencias")

    # ============================================================
    # VALIDACIÓN LIVE (verde / amarillo)
    # ============================================================
    def _validar_concepto_live(self):
        concepto = self.concepto.text().lower()
        cuenta_txt = self.cuenta_combo.currentText()
        if " – " not in cuenta_txt:
            return
        codigo = cuenta_txt.split(" – ")[0]

        if self.motor.es_concepto_valido(codigo, concepto):
            self.concepto.setStyleSheet("border:2px solid #22c55e;background:#f0fdf4;")
        else:
            self.concepto.setStyleSheet("border:2px solid #facc15;background:#fffbeb;")

    # ============================================================
    # IMPORTES
    # ============================================================
    def _calcular_importe(self):
        debe = self._normalizar(self.debe.text())
        haber = self._normalizar(self.haber.text())

        if debe > 0:
            self.haber.setText("0,00")
        elif haber > 0:
            self.debe.setText("0,00")

    def _normalizar(self, txt):
        if not txt:
            return 0
        try:
            return float(txt.replace(".", "").replace(",", "."))
        except:
            return 0

    def _fmt(self, v):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ============================================================
    # GUARDAR (Mejorado + FIX QMessageBox)
    # ============================================================
    def _guardar(self):

        documento = self.documento.text().strip() or f"SIN-DOC-{random.randint(10000,99999)}"

        # Documento duplicado
        if any(m.get("documento","") == documento for m in self.data.movimientos):
            QMessageBox.critical(self, "Error", "Documento duplicado.")
            return

        if not self.concepto.text().strip():
            QMessageBox.warning(self, "Faltan datos", "Debe ingresar concepto.")
            return

        if " – " not in self.cuenta_combo.currentText():
            QMessageBox.warning(self, "Error", "Seleccione una cuenta válida.")
            return

        debe = self._normalizar(self.debe.text())
        haber = self._normalizar(self.haber.text())

        if debe == 0 and haber == 0:
            QMessageBox.warning(self, "Error", "Debe ingresar Debe o Haber.")
            return

        if debe > 0 and haber > 0:
            QMessageBox.warning(self, "Error", "Debe y Haber no pueden coexistir.")
            return

        codigo = self.cuenta_combo.currentText().split(" – ")[0]
        concepto = self.concepto.text().strip()

        # 🔥 VALIDACIÓN SUAVE + FIX botones SI/NO
        if not self.motor.es_concepto_valido(codigo, concepto):

            msg = QMessageBox(self)
            msg.setWindowTitle("Validación")
            msg.setText("El concepto no coincide con las reglas típicas.\n¿Guardar de todos modos?")
            msg.setIcon(QMessageBox.Question)

            btn_si = msg.addButton("Sí", QMessageBox.YesRole)
            btn_no = msg.addButton("No", QMessageBox.NoRole)

            btn_si.setStyleSheet("""
                padding: 8px 20px; background:#2563eb; color:white;
                border-radius:8px; font-weight:bold;
            """)
            btn_no.setStyleSheet("""
                padding: 8px 20px; background:#64748b; color:white;
                border-radius:8px; font-weight:bold;
            """)

            msg.exec()

            if msg.clickedButton() != btn_si:
                return

            # Aprendizaje
            self.motor.agregar_concepto_a_reglas(codigo, concepto)

        # Banco
        banco = next((b.text() for b in self.banco_buttons.buttons() if b.isChecked()), "Caja")

        # Estado (SIN usar checkedId porque no siempre devuelve orden)
        estado = "pagado" if any(rb.isChecked() and rb.text()=="Pagado"
                                 for rb in self.estado_buttons.buttons()) else "pendiente"

        self.data.agregar_movimiento(
            fecha=self.fecha.date().toString("dd/MM/yyyy"),
            documento=documento,
            concepto=concepto,
            cuenta=codigo,
            debe=debe,
            haber=haber,
            moneda="INR",
            banco=banco,
            estado=estado
        )

        self._limpiar()
        self._cargar_ultimos()

        QMessageBox.information(self, "Éxito", "Movimiento guardado correctamente.")

    # ============================================================
    # DUPLICAR
    # ============================================================
    def _duplicar(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Duplicar", "Seleccione un movimiento.")
            return

        m = self.movimientos_filtrados[row]

        self.fecha.setDate(QDate.fromString(m["fecha"], "dd/MM/yyyy"))
        self.documento.clear()
        self.concepto.setText(m["concepto"])

        self.cuenta_combo.setCurrentText(
            f"{m['cuenta']} – {self.data.obtener_nombre_cuenta(m['cuenta'])}"
        )

        self.debe.setText(self._fmt(float(m["debe"])))
        self.haber.setText(self._fmt(float(m["haber"])))

        for rb in self.banco_buttons.buttons():
            if rb.text() == m.get("banco","Caja"):
                rb.setChecked(True)

        for rb in self.estado_buttons.buttons():
            if rb.text() == m.get("estado","pagado"):
                rb.setChecked(True)

    # ============================================================
    # LIMPIAR
    # ============================================================
    def _limpiar(self):
        self.fecha.setDate(QDate.currentDate())
        self.documento.clear()
        self.concepto.clear()
        self.debe.setText("0,00")
        self.haber.setText("0,00")
        self.cuenta_combo.setCurrentIndex(-1)
        self.lbl_nombre.setText("Seleccione una cuenta")
        self.lbl_sugerencias.setText("")

    def _limpiar_dh(self):
        self.debe.setText("0,00")
        self.haber.setText("0,00")

    def _nuevo_registro(self):
        self._limpiar()

    # ============================================================
    # TABLA
    # ============================================================
    def _cargar_ultimos(self):
        movs = sorted(
            self.data.movimientos,
            key=lambda m: datetime.strptime(m["fecha"], "%d/%m/%Y"),
            reverse=True
        )[:20]

        self.movimientos_filtrados = movs
        self.tabla.setRowCount(0)

        total_debe = 0
        total_haber = 0
        saldo = 0

        for m in movs:
            d = float(m["debe"])
            h = float(m["haber"])
            saldo += h - d
            total_debe += d
            total_haber += h

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            datos = [
                m["fecha"], m["documento"], m["concepto"], m["cuenta"],
                self.data.obtener_nombre_cuenta(m["cuenta"]),
                self._fmt(d), self._fmt(h),
                m["banco"], m["estado"], self._fmt(saldo)
            ]

            for col, val in enumerate(datos):
                it = QTableWidgetItem(str(val))
                if col in (5, 6, 9):
                    it.setTextAlignment(Qt.AlignRight)
                self.tabla.setItem(row, col, it)

        self.lbl_totales.setText(
            f"TOTAL DEBE: {self._fmt(total_debe)}  |  "
            f"TOTAL HABER: {self._fmt(total_haber)}  |  "
            f"SALDO: {self._fmt(total_haber-total_debe)}"
        )

    # ============================================================
    # FILTRAR TABLA
    # ============================================================
    def _filtrar_tabla(self):
        txt = self.buscador.text().lower()
        for row in range(self.tabla.rowCount()):
            mostrar = any(
                txt in (self.tabla.item(row, col).text().lower()
                        if self.tabla.item(row, col) else "")
                for col in range(10)
            )
            self.tabla.setRowHidden(row, not mostrar)
