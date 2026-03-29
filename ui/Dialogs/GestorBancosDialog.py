# -*- coding: utf-8 -*-
"""
GestorBancosDialog — SHILLONG CONTABILIDAD v3.8
------------------------------------------------
Diálogo para gestionar bancos/cajas sin editar JSON manualmente.
Permite Agregar, Editar y Eliminar bancos, guardando en bancos.json.

Uso típico:
    dlg = GestorBancosDialog(parent)
    dlg.exec()
"""

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QComboBox, QDoubleSpinBox, QFormLayout, QFrame,
    QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

try:
    from models.BankManager import BankManager
except ImportError:
    BankManager = None

try:
    from utils.rutas import ruta_datos_usuario
except ImportError:
    ruta_datos_usuario = None


def _cargar_cuentas_57xx():
    """Lee plan_contable_v3.json y retorna lista de (código, nombre) para cuentas 57xx."""
    cuentas = []
    try:
        if ruta_datos_usuario:
            ruta = ruta_datos_usuario("plan_contable_v3.json")
        else:
            ruta = Path("data/plan_contable_v3.json")
        if ruta.exists():
            data = json.loads(ruta.read_text(encoding="utf-8"))
            for codigo, info in data.items():
                if str(codigo).startswith("57"):
                    nombre = info.get("nombre", codigo) if isinstance(info, dict) else str(info)
                    cuentas.append((str(codigo), nombre))
    except Exception:
        pass
    return sorted(cuentas, key=lambda x: x[0])


# ─────────────────────────────────────────────────────────────────────────────
# Formulario Agregar / Editar
# ─────────────────────────────────────────────────────────────────────────────
class _BancoFormDialog(QDialog):
    """Sub-diálogo para capturar los datos de un banco (nuevo o edición)."""

    def __init__(self, cuentas_57xx, banco=None, parent=None):
        """
        cuentas_57xx: lista de (código, nombre) obtenida de plan_contable_v3.json
        banco: dict existente para edición, None para agregar
        """
        super().__init__(parent)
        self._cuentas = cuentas_57xx
        self._banco = banco or {}
        self.setWindowTitle("Editar Banco" if banco else "Agregar Banco")
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        titulo = QLabel("Editar Banco / Caja" if self._banco else "Nuevo Banco / Caja")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b;")
        layout.addWidget(titulo)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        # Nombre
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej: Federal Bank sr Laura")
        self.txt_nombre.setMaxLength(80)
        self.txt_nombre.setText(self._banco.get("nombre", ""))
        self.txt_nombre.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")
        form.addRow("Nombre:", self.txt_nombre)

        # Cuenta contable (combo + texto libre)
        self.cmb_cuenta = QComboBox()
        self.cmb_cuenta.setEditable(True)
        self.cmb_cuenta.addItem("-- Sin asignar --", "")
        for codigo, nombre in self._cuentas:
            self.cmb_cuenta.addItem(f"{codigo} – {nombre}", codigo)
        self.cmb_cuenta.setStyleSheet("padding: 4px; border: 1px solid #cbd5e1; border-radius: 4px;")

        # Preseleccionar valor actual
        cuenta_actual = self._banco.get("cuenta_contable", "")
        if cuenta_actual:
            idx = self.cmb_cuenta.findData(cuenta_actual)
            if idx >= 0:
                self.cmb_cuenta.setCurrentIndex(idx)
            else:
                # Es un código personalizado, escribirlo directamente
                self.cmb_cuenta.setCurrentText(cuenta_actual)
        form.addRow("Cuenta contable:", self.cmb_cuenta)

        # Saldo inicial
        self.spn_saldo = QDoubleSpinBox()
        self.spn_saldo.setRange(-9_999_999.99, 9_999_999.99)
        self.spn_saldo.setDecimals(2)
        self.spn_saldo.setSingleStep(100.0)
        self.spn_saldo.setPrefix("₹ ")
        self.spn_saldo.setValue(float(self._banco.get("saldo", 0.0)))
        self.spn_saldo.setStyleSheet("padding: 4px; border: 1px solid #cbd5e1; border-radius: 4px;")
        form.addRow("Saldo inicial:", self.spn_saldo)

        layout.addLayout(form)

        # Nota informativa
        nota = QLabel("💡 El código de cuenta contable (57xx) vincula este banco al Plan Contable.")
        nota.setStyleSheet("font-size: 11px; color: #64748b;")
        nota.setWordWrap(True)
        layout.addWidget(nota)

        layout.addSpacing(8)

        # Botones
        h = QHBoxLayout()
        h.setSpacing(8)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(
            "border: 1px solid #cbd5e1; border-radius: 5px; color: #475569; background: white;"
            "QPushButton:hover { background: #f8fafc; }"
        )
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Guardar")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(
            "background-color: #2563eb; color: white; border-radius: 5px; font-weight: bold;"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        btn_ok.clicked.connect(self._aceptar)

        h.addStretch()
        h.addWidget(btn_cancel)
        h.addWidget(btn_ok)
        layout.addLayout(h)

    def _aceptar(self):
        nombre = self.txt_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo obligatorio", "El nombre del banco no puede estar vacío.")
            self.txt_nombre.setFocus()
            return

        # Obtener código contable (primero datos del combo, si no el texto)
        cuenta = self.cmb_cuenta.currentData()
        if not cuenta:
            # El usuario escribió libremente
            texto = self.cmb_cuenta.currentText().strip()
            if texto and texto != "-- Sin asignar --":
                cuenta = texto
            else:
                cuenta = ""

        self._resultado = {
            "nombre": nombre,
            "cuenta_contable": cuenta,
            "saldo": round(self.spn_saldo.value(), 2),
        }
        self.accept()

    def get_resultado(self):
        return getattr(self, "_resultado", None)


# ─────────────────────────────────────────────────────────────────────────────
# Diálogo principal de gestión
# ─────────────────────────────────────────────────────────────────────────────
class GestorBancosDialog(QDialog):
    """Ventana de gestión completa de Bancos / Cajas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏦 Gestión de Bancos y Cajas")
        self.setMinimumSize(620, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        if BankManager is None:
            self._sin_modulo()
            return

        self._bm = BankManager()
        self._cuentas_57xx = _cargar_cuentas_57xx()
        self._build_ui()
        self._cargar_tabla()

    def _sin_modulo(self):
        l = QVBoxLayout(self)
        l.addWidget(QLabel("❌ Módulo BankManager no disponible.", styleSheet="color:red; padding:20px;"))
        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.reject)
        l.addWidget(btn)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Encabezado
        lbl = QLabel("Bancos y Cajas")
        lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #1e293b;")
        layout.addWidget(lbl)

        sub = QLabel("Gestione los bancos y cajas sin editar archivos JSON.")
        sub.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(sub)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(sep)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Cuenta Contable", "Saldo Inicial"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: #f1f5f9; color: #374151; "
            "font-weight: bold; border: none; padding: 6px; }"
        )
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet(
            "QTableWidget { border: 1px solid #e2e8f0; border-radius: 6px; }"
            "QTableWidget::item { padding: 5px; }"
            "QTableWidget::item:selected { background-color: #dbeafe; color: #1e293b; }"
        )
        self.tabla.setColumnWidth(0, 45)
        self.tabla.setColumnWidth(2, 150)
        self.tabla.setColumnWidth(3, 110)
        layout.addWidget(self.tabla)

        # Botones de acción
        h_btn = QHBoxLayout()
        h_btn.setSpacing(8)

        self.btn_agregar = self._btn("➕  Agregar", "#16a34a", self._agregar)
        self.btn_editar = self._btn("✏️  Editar", "#2563eb", self._editar)
        self.btn_eliminar = self._btn("🗑️  Eliminar", "#dc2626", self._eliminar)

        h_btn.addWidget(self.btn_agregar)
        h_btn.addWidget(self.btn_editar)
        h_btn.addWidget(self.btn_eliminar)
        h_btn.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedHeight(36)
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.setStyleSheet(
            "border: 1px solid #cbd5e1; border-radius: 5px; color: #475569; "
            "background: white; padding: 0 16px;"
        )
        btn_cerrar.clicked.connect(self.accept)
        h_btn.addWidget(btn_cerrar)

        layout.addLayout(h_btn)

        # Pie informativo
        pie = QLabel("Los cambios se guardan automáticamente en bancos.json.")
        pie.setStyleSheet("font-size: 10px; color: #94a3b8;")
        layout.addWidget(pie)

    def _btn(self, texto, color, callback):
        b = QPushButton(texto)
        b.setFixedHeight(36)
        b.setCursor(Qt.PointingHandCursor)
        b.setStyleSheet(
            f"background-color: {color}; color: white; border-radius: 5px; "
            f"font-weight: bold; padding: 0 14px;"
            f"QPushButton:hover {{ opacity: 0.85; }}"
        )
        b.clicked.connect(callback)
        return b

    def _cargar_tabla(self):
        bancos = self._bm.listar()
        self.tabla.setRowCount(0)
        for banco in bancos:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            item_id = QTableWidgetItem(str(banco.get("id", "")))
            item_id.setTextAlignment(Qt.AlignCenter)
            item_id.setForeground(QColor("#94a3b8"))

            item_nombre = QTableWidgetItem(banco.get("nombre", ""))
            item_nombre.setFont(QFont("Segoe UI", 10))

            cuenta = banco.get("cuenta_contable", "")
            item_cuenta = QTableWidgetItem(cuenta if cuenta else "—")
            item_cuenta.setTextAlignment(Qt.AlignCenter)
            if not cuenta:
                item_cuenta.setForeground(QColor("#cbd5e1"))

            saldo = banco.get("saldo", 0.0)
            item_saldo = QTableWidgetItem(f"₹ {float(saldo):,.2f}")
            item_saldo.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tabla.setItem(row, 0, item_id)
            self.tabla.setItem(row, 1, item_nombre)
            self.tabla.setItem(row, 2, item_cuenta)
            self.tabla.setItem(row, 3, item_saldo)

        self.tabla.resizeRowsToContents()

    def _fila_seleccionada(self):
        """Retorna el dict del banco de la fila seleccionada, o None."""
        filas = self.tabla.selectionModel().selectedRows()
        if not filas:
            return None, -1
        fila = filas[0].row()
        try:
            banco_id = int(self.tabla.item(fila, 0).text())
            bancos = self._bm.listar()
            for b in bancos:
                if b["id"] == banco_id:
                    return b, fila
        except (ValueError, AttributeError):
            pass
        return None, -1

    def _agregar(self):
        dlg = _BancoFormDialog(self._cuentas_57xx, banco=None, parent=self)
        if dlg.exec() == QDialog.Accepted:
            res = dlg.get_resultado()
            if res:
                # Verificar nombre duplicado
                nombres = [b["nombre"].strip().lower() for b in self._bm.listar()]
                if res["nombre"].lower() in nombres:
                    QMessageBox.warning(self, "Nombre duplicado",
                                        f"Ya existe un banco con el nombre:\n«{res['nombre']}»")
                    return
                self._bm.agregar_banco(res["nombre"], res["cuenta_contable"])
                # Actualizar saldo inicial si no es 0
                if res["saldo"] != 0.0:
                    nuevo_id = self._bm.listar()[-1]["id"]
                    self._bm.actualizar_saldo_inicial(nuevo_id, res["saldo"])
                self._cargar_tabla()
                QMessageBox.information(self, "Guardado",
                                        f"Banco «{res['nombre']}» agregado correctamente.")

    def _editar(self):
        banco, _ = self._fila_seleccionada()
        if not banco:
            QMessageBox.information(self, "Selección", "Selecciona un banco de la lista para editarlo.")
            return
        dlg = _BancoFormDialog(self._cuentas_57xx, banco=banco, parent=self)
        if dlg.exec() == QDialog.Accepted:
            res = dlg.get_resultado()
            if res:
                # Verificar nombre duplicado (excluyendo este mismo banco)
                nombres = [b["nombre"].strip().lower() for b in self._bm.listar()
                           if b["id"] != banco["id"]]
                if res["nombre"].lower() in nombres:
                    QMessageBox.warning(self, "Nombre duplicado",
                                        f"Ya existe otro banco con el nombre:\n«{res['nombre']}»")
                    return
                # Aplicar cambios directamente
                for b in self._bm.bancos:
                    if b["id"] == banco["id"]:
                        b["nombre"] = res["nombre"]
                        b["cuenta_contable"] = res["cuenta_contable"]
                        b["saldo"] = res["saldo"]
                        break
                self._bm._guardar()
                self._cargar_tabla()
                QMessageBox.information(self, "Guardado",
                                        f"Banco «{res['nombre']}» actualizado correctamente.")

    def _eliminar(self):
        banco, _ = self._fila_seleccionada()
        if not banco:
            QMessageBox.information(self, "Selección", "Selecciona un banco de la lista para eliminarlo.")
            return

        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar el banco «{banco['nombre']}»?\n\n"
            "Los movimientos existentes con este banco NO se modificarán.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self._bm.bancos = [b for b in self._bm.bancos if b["id"] != banco["id"]]
            self._bm._guardar()
            self._cargar_tabla()
            QMessageBox.information(self, "Eliminado",
                                    f"Banco «{banco['nombre']}» eliminado.")
