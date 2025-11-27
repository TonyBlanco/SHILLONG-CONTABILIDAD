# -*- coding: utf-8 -*-
"""
RegistrarView — SHILLONG CONTABILIDAD v5 ULTRA-PRO TURBO 2025
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QCompleter, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont

from models.CuentasMotor import MotorCuentas
import json
from datetime import datetime


class RegistrarView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.motor = MotorCuentas()
        self.bancos = self._cargar_bancos()
        self.tema_oscuro = False

        self.setStyleSheet(self._estilo_claro())

        self._build_ui()
        self._cargar_ultimos()

    # ------------------------------------------------------------
    # ESTILOS
    # ------------------------------------------------------------
    def _estilo_claro(self):
        return """
            QWidget { background: #f8fafc; font-family: 'Segoe UI', sans-serif; }
            QLabel { color: #1e293b; font-size: 14px; }
            QLineEdit, QDateEdit, QComboBox, QTableWidget {
                padding: 10px 14px; border: 2px solid #e2e8f0; border-radius: 10px;
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
        """

    def _estilo_oscuro(self):
        return """
            QWidget { background: #0f172a; color: #e2e8f0; font-family: 'Segoe UI'; }
            QLabel { color: #e2e8f0; }
            QLineEdit, QDateEdit, QComboBox, QTableWidget {
                background: #1e293b; color: #e2e8f0; border: 2px solid #334155;
                padding: 10px 14px; border-radius: 10px;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #60a5fa; }
            QPushButton { border-radius: 10px; padding: 12px 24px; font-weight: bold; }
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

    # ------------------------------------------------------------
    # HELPERS DE NÚMEROS
    # ------------------------------------------------------------
    def _normalizar_numero(self, txt):
        if not txt:
            return 0.0
        txt = txt.strip().replace(".", "").replace(",", ".")
        try:
            return float(txt)
        except:
            return 0.0

    def _formatear_numero(self, valor):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ------------------------------------------------------------
    # BANCO
    # ------------------------------------------------------------
    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return [b["nombre"] for b in data.get("banks", [])]
        except:
            return ["Caja", "Federal Bank", "SBI", "Union Bank", "Otro"]

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # Top bar
        top_bar = QHBoxLayout()
        titulo = QLabel("REGISTRAR MOVIMIENTO CONTABLE")
        titulo.setStyleSheet("font-size: 26px; font-weight: 800;")
        titulo.setAlignment(Qt.AlignLeft)
        self.btn_tema = QPushButton("Modo oscuro")
        self.btn_tema.setObjectName("tema")
        self.btn_tema.clicked.connect(self._cambiar_tema)
        top_bar.addWidget(titulo)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_tema)
        layout.addLayout(top_bar)

        # Formulario
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(12)

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(QDate.currentDate())
        form.addRow("Fecha:", self.fecha)

        self.documento = QLineEdit()
        self.documento.setPlaceholderText("Ej: FAC-2025-001")
        form.addRow("Documento:", self.documento)

        self.concepto = QLineEdit()
        self.concepto.setPlaceholderText("Descripción del movimiento")
        self.concepto.textChanged.connect(self._validar_concepto_live)
        form.addRow("Concepto:", self.concepto)

        self.cuenta_combo = QComboBox()
        self.cuenta_combo.setEditable(True)
        self.cuenta_combo.setPlaceholderText("Escriba o seleccione cuenta...")
        completer = QCompleter(self.motor.todas_las_opciones(), self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.cuenta_combo.setCompleter(completer)
        self.cuenta_combo.currentTextChanged.connect(self._mostrar_nombre_cuenta)
        form.addRow("Cuenta contable:", self.cuenta_combo)

        self.lbl_nombre = QLabel("Nombre de la cuenta aparecerá aquí")
        self.lbl_nombre.setStyleSheet("color: #64748b; font-style: italic;")
        form.addRow("", self.lbl_nombre)

        row_dh = QHBoxLayout()
        self.debe = QLineEdit("0,00")
        self.haber = QLineEdit("0,00")
        self.debe.textChanged.connect(self._calcular_importe)
        self.haber.textChanged.connect(self._calcular_importe)
        row_dh.addWidget(QLabel("Debe:"))
        row_dh.addWidget(self.debe)
        row_dh.addSpacing(20)
        row_dh.addWidget(QLabel("Haber:"))
        row_dh.addWidget(self.haber)
        form.addRow("Importe:", row_dh)

        self.banco = QComboBox()
        self.banco.addItems(self.bancos)
        form.addRow("Banco:", self.banco)

        self.estado = QComboBox()
        self.estado.addItems(["pagado", "pendiente"])
        form.addRow("Estado:", self.estado)

        layout.addLayout(form)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

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

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_duplicar)
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_limpiar)
        btn_layout.addWidget(self.btn_limpiar_dh)
        btn_layout.addWidget(self.btn_nuevo)
        layout.addLayout(btn_layout)

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar en movimientos…")
        self.buscador.textChanged.connect(self._filtrar_tabla)
        layout.addWidget(self.buscador)

        # Tabla
        self.tabla = QTableWidget(0, 10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Documento", "Concepto", "Cuenta", "Nombre Cuenta",
            "Debe", "Haber", "Banco", "Estado", "Saldo"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

        # Totales
        self.lbl_totales = QLabel()
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        self.lbl_totales.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 10px; "
            "background: #e0e7ff; border-radius: 10px;"
        )
        layout.addWidget(self.lbl_totales)

    # ------------------------------------------------------------
    # LIMPIEZA Y MODO TURBO
    # ------------------------------------------------------------
    def _limpiar(self):
        self.fecha.setDate(QDate.currentDate())
        self.documento.clear()
        self.concepto.clear()
        self.cuenta_combo.setCurrentIndex(-1)
        self.debe.setText("0,00")
        self.haber.setText("0,00")
        self.banco.setCurrentIndex(0)
        self.estado.setCurrentIndex(0)
        self.lbl_nombre.setText("Nombre de la cuenta aparecerá aquí")
        self.concepto.setStyleSheet("padding:10px 14px; border:2px solid #e2e8f0; border-radius:10px;")
        self.documento.setFocus()

    def _limpiar_dh(self):
        self.debe.setText("0,00")
        self.haber.setText("0,00")
        self.debe.setFocus()

    def _nuevo_registro(self):
        self._limpiar()

    # ------------------------------------------------------------
    # VALIDACIONES
    # ------------------------------------------------------------
    def _mostrar_nombre_cuenta(self, texto):
        if not texto or " – " not in texto:
            self.lbl_nombre.setText("Nombre de la cuenta aparecerá aquí")
            return
        codigo = texto.split(" – ")[0]
        nombre = self.motor.get_nombre(codigo)
        self.lbl_nombre.setText(f"→ {nombre}" if nombre else "Cuenta no encontrada")

    def _validar_concepto_live(self):
        concepto = self.concepto.text().lower()
        cuenta_texto = self.cuenta_combo.currentText()
        if not cuenta_texto or " – " not in cuenta_texto:
            self.concepto.setStyleSheet("padding:10px 14px; border:2px solid #e2e8f0; border-radius:10px;")
            return
        codigo = cuenta_texto.split(" – ")[0]
        if self.motor.es_concepto_valido(codigo, concepto):
            self.concepto.setStyleSheet("padding:10px 14px; border:2px solid #34d399; border-radius:10px; background:#f0fdf4;")
        else:
            self.concepto.setStyleSheet("padding:10px 14px; border:2px solid #fbbf24; border-radius:10px; background:#fffbeb;")

    def _documento_existe(self, doc):
        return any(m.get("documento", "").strip().lower() == doc.strip().lower() for m in self.data.movimientos)

    # ------------------------------------------------------------
    # DUPLICAR MOVIMIENTO
    # ------------------------------------------------------------
    def _duplicar(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self, "Duplicar", "Seleccione un movimiento para duplicar.")
            return
        m = self.movimientos_filtrados[row]
        self.fecha.setDate(QDate.fromString(m.get("fecha", ""), "dd/MM/yyyy"))
        self.documento.clear()
        self.concepto.setText(m.get("concepto", ""))
        cuenta = m.get("cuenta", "")
        nombre = self.data.obtener_nombre_cuenta(cuenta)
        self.cuenta_combo.setCurrentText(f"{cuenta} – {nombre}")
        debe = float(m.get("debe", 0))
        haber = float(m.get("haber", 0))
        self.debe.setText(self._formatear_numero(debe))
        self.haber.setText(self._formatear_numero(haber))
        self.banco.setCurrentText(m.get("banco", "Caja"))
        self.estado.setCurrentText(m.get("estado", "pagado"))
        QMessageBox.information(self, "Duplicado", "Movimiento cargado. Ingrese un nuevo documento para guardarlo.")

    # ------------------------------------------------------------
    # GUARDAR
    # ------------------------------------------------------------
    def _guardar(self):
        if not all([self.documento.text().strip(), self.concepto.text().strip(), self.cuenta_combo.currentText()]):
            QMessageBox.warning(self, "Faltan datos", "Complete todos los campos obligatorios.")
            return

        if self._documento_existe(self.documento.text()):
            QMessageBox.critical(self, "Error", "Este número de documento ya existe.")
            return

        debe = self._normalizar_numero(self.debe.text())
        haber = self._normalizar_numero(self.haber.text())

        if debe == 0 and haber == 0:
            QMessageBox.warning(self, "Importe", "Debe o Haber debe tener un valor.")
            return
        if debe > 0 and haber > 0:
            QMessageBox.warning(self, "Error", "Debe y Haber no pueden tener valor simultáneamente.")
            return

        cuenta_texto = self.cuenta_combo.currentText()
        codigo = cuenta_texto.split(" – ")[0] if " – " in cuenta_texto else cuenta_texto

        if not self.motor.get_nombre(codigo):
            reply = QMessageBox.question(self, "Cuenta nueva",
                                         f"La cuenta {codigo} no existe.\n¿Desea crearla automáticamente?")
            if reply == QMessageBox.Yes:
                import os
                ruta = "data/plan_contable_v3.json"
                plan = {}
                if os.path.exists(ruta):
                    with open(ruta, "r", encoding="utf-8") as f:
                        plan = json.load(f)
                plan[codigo] = {
                    "nombre": "Cuenta sin nombre",
                    "descripcion": "Creada automáticamente"
                }
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2, ensure_ascii=False)
                self.motor = MotorCuentas()
                self.cuenta_combo.clear()
                self.cuenta_combo.addItems(self.motor.todas_las_opciones())

        if not self.motor.es_concepto_valido(codigo, self.concepto.text()):
            reply = QMessageBox.question(self, "Advertencia",
                                         "El concepto no coincide con la naturaleza de la cuenta.\n"
                                         "¿Desea continuar?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

        if QMessageBox.question(self, "Confirmar", "¿Guardar este movimiento?") != QMessageBox.Yes:
            return

        self.data.agregar_movimiento(
            fecha=self.fecha.date().toString("dd/MM/yyyy"),
            documento=self.documento.text().strip(),
            concepto=self.concepto.text(),
            cuenta=codigo,
            debe=debe,
            haber=haber,
            moneda="INR",
            banco=self.banco.currentText(),
            estado=self.estado.currentText()
        )

        self._limpiar()
        self._cargar_ultimos()
        QMessageBox.information(self, "Éxito", "Movimiento registrado correctamente.")

    # ------------------------------------------------------------
    # TABLA + TOTALES
    # ------------------------------------------------------------
    def _filtrar_tabla(self):
        texto = self.buscador.text().lower()
        for row in range(self.tabla.rowCount()):
            mostrar = any(
                texto in (self.tabla.item(row, col).text().lower() if self.tabla.item(row, col) else "")
                for col in range(self.tabla.columnCount())
            )
            self.tabla.setRowHidden(row, not mostrar)

    def _cargar_ultimos(self):
        def fecha_key(m):
            try:
                d, m_, a = m.get("fecha", "01/01/1900").split("/")
                return datetime(int(a), int(m_), int(d))
            except:
                return datetime(1900, 1, 1)

        movimientos = sorted(self.data.movimientos, key=fecha_key, reverse=True)[:20]
        self.movimientos_filtrados = movimientos

        self.tabla.setRowCount(0)
        saldo_acum = total_debe = total_haber = 0

        for idx, m in enumerate(movimientos):
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            total_debe += debe
            total_haber += haber

            self.tabla.insertRow(idx)
            items = [
                m.get("fecha", ""),
                m.get("documento", ""),
                m.get("concepto", ""),
                str(m.get("cuenta", "")),
                self.data.obtener_nombre_cuenta(m.get("cuenta")),
                self._formatear_numero(debe),
                self._formatear_numero(haber),
                m.get("banco", "Caja"),
                m.get("estado", ""),
                self._formatear_numero(saldo_acum)
            ]

            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                if idx == 0:
                    item.setBackground(QColor("#dbeafe"))
                    item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                if col == 5 and debe > 0:
                    item.setForeground(QColor("#dc2626"))
                if col == 6 and haber > 0:
                    item.setForeground(QColor("#16a34a"))
                self.tabla.setItem(idx, col, item)

        self.lbl_totales.setText(
            f"TOTAL DEBE: {self._formatear_numero(total_debe)} | "
            f"TOTAL HABER: {self._formatear_numero(total_haber)} | "
            f"SALDO: {self._formatear_numero(total_haber - total_debe)}"
        )

        self._filtrar_tabla()

    def _calcular_importe(self):
        debe = self._normalizar_numero(self.debe.text())
        haber = self._normalizar_numero(self.haber.text())
        if debe > 0:
            self.haber.setText("0,00")
        elif haber > 0:
            self.debe.setText("0,00")