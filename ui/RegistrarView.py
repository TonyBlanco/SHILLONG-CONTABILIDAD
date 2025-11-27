# -*- coding: utf-8 -*-
"""
RegistrarView — SHILLONG CONTABILIDAD v3 PRO (versión original reparada)
"""

# === IMPORT FIJO OBLIGATORIO PARA SHILLONG V3 ===
from models.CuentasMotor import MotorCuentas
# ===============================================

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QCompleter, QHeaderView, QAbstractItemView, QApplication,
    QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
import random
from datetime import datetime


class RegistrarView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.motor = MotorCuentas()
        self.tema_oscuro = False

        QApplication.setStyle("windows")
        self.setStyleSheet(self._estilo_claro())

        self._build_ui()
        self._cargar_ultimos()


    # ============================================================
    # ESTILOS
    # ============================================================
    def _estilo_claro(self):
        return """
            QWidget { background: #f8fafc; font-family: 'Segoe UI'; }
            QLabel { color: #1e293b; font-size: 14px; }
            QLineEdit, QDateEdit, QComboBox {
                padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 8px;
                font-size: 15px; background: white;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #3b82f6; }
            QPushButton {
                padding: 12px 24px; border-radius: 10px; font-weight: bold; font-size: 14px;
                color: white;
            }
            QPushButton#guardar { background: #2563eb; }
            QPushButton#refresh { background: #64748b; }
            QPushButton#duplicar { background: #7c3aed; }
            QPushButton#tema { background: #475569; }
            QPushButton#limpiar { background: #0ea5e9; }
            QPushButton#limpiar_dh { background: #6b7280; }
            QPushButton#nuevo { background: #059669; }
            QHeaderView::section { background: #e0e7ff; padding: 10px; font-weight: bold; }
            QGroupBox {
                font-weight: bold; border: 2px solid #cbd5e1; border-radius: 12px;
                margin-top: 10px; padding-top: 10px;
            }
        """

    def _estilo_oscuro(self):
        return """
            QWidget { background: #0f172a; color: #e2e8f0; }
            QLabel { color: #e2e8f0; }
            QLineEdit, QDateEdit, QComboBox {
                background: #1e293b; color: #e2e8f0; border: 2px solid #334155;
                padding: 12px 16px; border-radius: 8px;
            }
            QPushButton#guardar { background: #3b82f6; }
            QPushButton#refresh { background: #64748b; }
            QPushButton#duplicar { background: #8b5cf6; }
            QPushButton#tema { background: #475569; }
            QPushButton#limpiar { background: #0ea5e9; }
            QPushButton#limpiar_dh { background: #6b7280; }
            QPushButton#nuevo { background: #059669; }
            QHeaderView::section { background: #334155; color: white; }
        """

    def _cambiar_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        self.setStyleSheet(self._estilo_oscuro() if self.tema_oscuro else self._estilo_claro())
        self.btn_tema.setText("Modo claro" if self.tema_oscuro else "Modo oscuro")

    # ============================================================
    # UI PRINCIPAL (ORIGINAL)
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # Título + Tema
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
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Fecha:", self.fecha)

        # DOCUMENTO
        self.documento = QLineEdit()
        self.documento.setPlaceholderText("Opcional — si está vacío se genera automático")
        form.addRow("Documento:", self.documento)

        # CUENTA CONTABLE
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.setEditable(True)
        opciones = self.motor.todas_las_opciones()
        self.cuenta_combo.addItems(opciones)

        completer = QCompleter(opciones, self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.cuenta_combo.setCompleter(completer)
        self.cuenta_combo.currentTextChanged.connect(self._on_cuenta_changed)

        form.addRow("Cuenta contable:", self.cuenta_combo)

        # NOMBRE
        self.lbl_nombre = QLabel("Seleccione una cuenta")
        self.lbl_nombre.setStyleSheet("font-style:italic;color:#64748b;")
        form.addRow("", self.lbl_nombre)

        # SUGERENCIAS
        self.lbl_sugerencias = QLabel("")
        self.lbl_sugerencias.setStyleSheet("color:#6366f1;font-size:13px;")
        self.lbl_sugerencias.setWordWrap(True)
        form.addRow("", self.lbl_sugerencias)

        # CONCEPTO
        self.concepto = QLineEdit()
        self.concepto.setPlaceholderText("Descripción del movimiento…")
        self.concepto.textChanged.connect(self._validar_concepto_live)
        form.addRow("Concepto:", self.concepto)

        # DEBE / HABER
        row_dh = QHBoxLayout()
        self.debe = QLineEdit("0,00")
        self.haber = QLineEdit("0,00")
        self.debe.textChanged.connect(self._calcular_importe)
        self.haber.textChanged.connect(self._calcular_importe)
        row_dh.addWidget(QLabel("Debe:"))
        row_dh.addWidget(self.debe)
        row_dh.addWidget(QLabel("Haber:"))
        row_dh.addWidget(self.haber)
        form.addRow("Importe:", row_dh)

        # BANCO
        banco_group = QGroupBox("Banco")
        banco_layout = QHBoxLayout()
        self.banco_buttons = QButtonGroup()
        bancos = ["Caja", "Federal Bank", "SBI", "Union Bank", "Otro"]
        for i, b in enumerate(bancos):
            rb = QRadioButton(b)
            if i == 0:
                rb.setChecked(True)
            self.banco_buttons.addButton(rb, i)
            banco_layout.addWidget(rb)
        banco_group.setLayout(banco_layout)
        form.addRow("", banco_group)

        # ESTADO
        estado_group = QGroupBox("Estado")
        estado_layout = QHBoxLayout()
        self.estado_buttons = QButtonGroup()
        rb1 = QRadioButton("Pagado")
        rb2 = QRadioButton("Pendiente")
        rb1.setChecked(True)
        self.estado_buttons.addButton(rb1, 0)
        self.estado_buttons.addButton(rb2, 1)
        estado_layout.addWidget(rb1)
        estado_layout.addWidget(rb2)
        estado_group.setLayout(estado_layout)
        form.addRow("", estado_group)

        layout.addLayout(form)

        # BOTONES
        btns = QHBoxLayout()
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
            self.btn_refresh,
            self.btn_duplicar,
            self.btn_guardar,
            self.btn_limpiar,
            self.btn_limpiar_dh,
            self.btn_nuevo,
        ]:
            btns.addWidget(b)

        layout.addLayout(btns)

        # BUSCADOR
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar en movimientos…")
        self.buscador.textChanged.connect(self._filtrar_tabla)
        layout.addWidget(self.buscador)

        # TABLA ORIGINAL
        self.tabla = QTableWidget(0, 10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Documento", "Concepto", "Cuenta",
            "Nombre Cuenta", "Debe", "Haber",
            "Banco", "Estado", "Saldo"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tabla)

        # TOTALES
        self.lbl_totales = QLabel()
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        self.lbl_totales.setStyleSheet(
            "font-weight:bold;font-size:15px;padding:10px;background:#e0e7ff;border-radius:8px;"
        )
        layout.addWidget(self.lbl_totales)

    # ============================================================
    # LOGICA ORIGINAL + FIXES
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

    def _calcular_importe(self):
        debe = self._normalizar_numero(self.debe.text())
        haber = self._normalizar_numero(self.haber.text())
        if debe > 0:
            self.haber.setText("0,00")
        elif haber > 0:
            self.debe.setText("0,00")

    def _normalizar_numero(self, txt):
        if not txt:
            return 0.0
        txt = txt.replace(".", "").replace(",", ".")
        try:
            return float(txt)
        except:
            return 0.0

    def _formatear_numero(self, v):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ============================================================
    # GUARDAR (VERSIÓN ORIGINAL + FIX FINAL)
    # ============================================================
    def _guardar(self):

        documento = self.documento.text().strip() or f"SIN-DOC-{random.randint(10000,99999)}"

        # Documento duplicado
        if any(m.get("documento","") == documento for m in self.data.movimientos):
            QMessageBox.critical(self, "Error", "Documento duplicado.")
            return

        # Validación básica
        if not self.concepto.text().strip() or " – " not in self.cuenta_combo.currentText():
            QMessageBox.warning(self, "Faltan datos", "Complete concepto y cuenta.")
            return

        debe = self._normalizar_numero(self.debe.text())
        haber = self._normalizar_numero(self.haber.text())

        if debe == 0 and haber == 0:
            QMessageBox.warning(self, "Error", "Debe ingresar Debe o Haber.")
            return
        if debe > 0 and haber > 0:
            QMessageBox.warning(self, "Error", "Debe y Haber no pueden coexistir.")
            return

        codigo = self.cuenta_combo.currentText().split(" – ")[0]
        concepto = self.concepto.text().strip()

        # Validación blanda
        if not self.motor.es_concepto_valido(codigo, concepto):
            r = QMessageBox.question(
                self, "Validación", 
                "El concepto no coincide con las reglas típicas.\n¿Desea guardarlo igual?",
                QMessageBox.Yes | QMessageBox.No
            )
            if r != QMessageBox.Yes:
                return

        # Banco
        banco = next((b.text() for b in self.banco_buttons.buttons() if b.isChecked()), "Caja")

        # Estado
        estado = "pagado" if self.estado_buttons.checkedId() == 0 else "pendiente"

        # *** FIX FINAL: Banco enviado correctamente ***
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

        cuenta = m["cuenta"]
        self.cuenta_combo.setCurrentText(f"{cuenta} – {self.data.obtener_nombre_cuenta(cuenta)}")

        self.debe.setText(self._formatear_numero(float(m["debe"])))
        self.haber.setText(self._formatear_numero(float(m["haber"])))

        # Banco
        banco_val = m.get("banco","Caja")
        for rb in self.banco_buttons.buttons():
            if rb.text() == banco_val:
                rb.setChecked(True)

        # Estado
        estado = m.get("estado","pagado")
        self.estado_buttons.button(0 if estado=="pagado" else 1).setChecked(True)

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
    # LISTA / TABLA ORIGINAL
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
            debe = float(m["debe"])
            haber = float(m["haber"])
            saldo += haber - debe

            total_debe += debe
            total_haber += haber

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            datos = [
                m["fecha"],
                m["documento"],
                m["concepto"],
                m["cuenta"],
                self.data.obtener_nombre_cuenta(m["cuenta"]),
                self._formatear_numero(debe),
                self._formatear_numero(haber),
                m["banco"],
                m["estado"],
                self._formatear_numero(saldo),
            ]

            for col, val in enumerate(datos):
                it = QTableWidgetItem(str(val))
                if col in (5,6,9):
                    it.setTextAlignment(Qt.AlignRight)
                self.tabla.setItem(row, col, it)

        self.lbl_totales.setText(
            f"TOTAL DEBE: {self._formatear_numero(total_debe)}  |  "
            f"TOTAL HABER: {self._formatear_numero(total_haber)}  |  "
            f"SALDO: {self._formatear_numero(total_haber-total_debe)}"
        )

    # ============================================================
    # FILTRAR ORIGINAL
    # ============================================================
    def _filtrar_tabla(self):
        texto = self.buscador.text().lower()
        for row in range(self.tabla.rowCount()):
            mostrar = any(
                texto in (self.tabla.item(row,col).text().lower() 
                          if self.tabla.item(row,col) else "")
                for col in range(10)
            )
            self.tabla.setRowHidden(row, not mostrar)
