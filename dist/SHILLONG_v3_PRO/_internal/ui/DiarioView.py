# -*- coding: utf-8 -*-
"""
DiarioView — SHILLONG CONTABILIDAD v3.6.1 PRO
Versión FIXED: Corrección de Dialog (Indentación) y Filtros Robustos para Excel.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMenu, QMessageBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QDoubleSpinBox, QRadioButton, QButtonGroup, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor, QFont
import json

# ============================================================================
# 1. CLASE DEL DIÁLOGO (VENTANA FLOTANTE)
# ============================================================================
class EditarMovimientoDialog(QDialog):
    def __init__(self, parent, movimiento, lista_cuentas, lista_bancos):
        super().__init__(parent)
        self.setWindowTitle("✏️ Editar Movimiento")
        self.resize(450, 400)
        self.movimiento = movimiento
        
        layout = QFormLayout(self)
        
        # CAMPO FECHA
        self.inp_fecha = QDateEdit()
        self.inp_fecha.setDisplayFormat("dd/MM/yyyy")
        self.inp_fecha.setCalendarPopup(True)
        # Llamamos al helper interno
        self._set_fecha_segura(movimiento.get("fecha", ""))
        layout.addRow("Fecha:", self.inp_fecha)

        self.inp_doc = QLineEdit(movimiento.get("documento", ""))
        layout.addRow("Documento:", self.inp_doc)

        self.inp_concepto = QLineEdit(movimiento.get("concepto", ""))
        layout.addRow("Concepto:", self.inp_concepto)

        self.inp_cuenta = QComboBox()
        self.inp_cuenta.addItems(lista_cuentas)
        # Seleccionar cuenta actual
        cuenta_actual = str(movimiento.get("cuenta", ""))
        for i in range(self.inp_cuenta.count()):
            if self.inp_cuenta.itemText(i).startswith(cuenta_actual):
                self.inp_cuenta.setCurrentIndex(i)
                break
        layout.addRow("Cuenta:", self.inp_cuenta)

        # Importes (Conversión segura)
        self.inp_debe = QDoubleSpinBox()
        self.inp_debe.setRange(0, 999999999)
        try:
            d = float(str(movimiento.get("debe", 0)).replace(",", "."))
        except (ValueError, TypeError):
            d = 0.0
        self.inp_debe.setValue(d)
        layout.addRow("Debe (Gasto):", self.inp_debe)

        self.inp_haber = QDoubleSpinBox()
        self.inp_haber.setRange(0, 999999999)
        try:
            h = float(str(movimiento.get("haber", 0)).replace(",", "."))
        except (ValueError, TypeError):
            h = 0.0
        self.inp_haber.setValue(h)
        layout.addRow("Haber (Ingreso):", self.inp_haber)

        self.inp_banco = QComboBox()
        self.inp_banco.addItems(lista_bancos)
        self.inp_banco.setCurrentText(movimiento.get("banco", "Caja"))
        layout.addRow("Banco:", self.inp_banco)

        self.inp_estado = QComboBox()
        self.inp_estado.addItems(["pagado", "pendiente"])
        self.inp_estado.setCurrentText(movimiento.get("estado", "pagado").lower())
        layout.addRow("Estado:", self.inp_estado)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

    # --- ESTE MÉTODO AHORA ESTÁ DENTRO DE LA CLASE (INDENTADO) ---
    def _set_fecha_segura(self, f_str):
        try:
            f_str = str(f_str).strip()
            # Formato ES: 30/11/2025
            if "/" in f_str: 
                d,m,a = map(int, f_str.split("/"))
            # Formato Excel/ISO: 2025-11-30
            elif "-" in f_str: 
                p = f_str.split("-")
                if len(p[0])==4: a,m,d = map(int, p) # YYYY-MM-DD
                else: d,m,a = map(int, p) # DD-MM-YYYY
            else: 
                raise ValueError("Invalid date format")
            self.inp_fecha.setDate(QDate(a, m, d))
        except (ValueError, IndexError):
            self.inp_fecha.setDate(QDate.currentDate())

    def get_data(self):
        return {
            "fecha": self.inp_fecha.date().toString("dd/MM/yyyy"),
            "documento": self.inp_doc.text(),
            "concepto": self.inp_concepto.text(),
            "cuenta": self.inp_cuenta.currentText().split(" – ")[0], 
            "debe": self.inp_debe.value(),
            "haber": self.inp_haber.value(),
            "banco": self.inp_banco.currentText(),
            "estado": self.inp_estado.currentText(),
            "moneda": "INR" 
        }

# ============================================================================
# 2. CLASE DE LA VISTA PRINCIPAL
# ============================================================================
class DiarioView(QWidget):
    
    signal_ir_a_registrar = Signal()

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.movimientos_actuales = [] 
        self.cuentas_cache = self._cargar_cuentas()
        self.bancos_cache = self._cargar_bancos()

        self._build_ui()
        
        # INICIO:
        self.rb_todo.setChecked(True)
        self._toggle_fechas()
        self._filtrar()

    def _cargar_cuentas(self):
        l = []
        try:
            with open("data/plan_contable_v3.json", "r", encoding="utf-8") as f:
                plan = json.load(f)
                for c, d in plan.items():
                    l.append(f"{c} – {d['nombre']}")
        except (IOError, json.JSONDecodeError, KeyError):
            l = ["S/N – Desconocida"]
        return sorted(l)

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return [b["nombre"] for b in json.load(f).get("banks", [])]
        except (IOError, json.JSONDecodeError, KeyError):
            return ["Caja"]

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # HEADER
        header = QHBoxLayout()
        header.addWidget(QLabel("📘 Diario General", styleSheet="font-size:26px; font-weight:800; color:#1e293b;"))
        header.addStretch()
        btn_add = QPushButton("➕ Nuevo Movimiento", cursor=Qt.PointingHandCursor)
        btn_add.setStyleSheet("background:#2563eb; color:white; font-weight:bold; padding:8px 20px; border-radius:6px;")
        btn_add.clicked.connect(self.signal_ir_a_registrar.emit)
        header.addWidget(btn_add)
        layout.addLayout(header)

        # FILTROS
        panel = QGroupBox("Filtros")
        panel.setStyleSheet("QGroupBox { font-weight:bold; border:1px solid #cbd5e1; border-radius:8px; margin-top:10px; }")
        panel_layout = QHBoxLayout(panel)
        panel_layout.setSpacing(20)

        self.bg_filtro = QButtonGroup(self)
        self.rb_todo = QRadioButton("Ver Todo")
        self.rb_mes = QRadioButton("Este Mes")
        self.rb_rango = QRadioButton("Rango:")
        
        self.bg_filtro.addButton(self.rb_todo)
        self.bg_filtro.addButton(self.rb_mes)
        self.bg_filtro.addButton(self.rb_rango)

        panel_layout.addWidget(self.rb_todo)
        panel_layout.addWidget(self.rb_mes)
        panel_layout.addWidget(self.rb_rango)

        self.date_desde = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setDisplayFormat("dd/MM/yyyy")
        self.date_desde.setEnabled(False)

        self.date_hasta = QDateEdit(QDate.currentDate())
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setDisplayFormat("dd/MM/yyyy")
        self.date_hasta.setEnabled(False)

        panel_layout.addWidget(self.date_desde)
        panel_layout.addWidget(QLabel("➡"))
        panel_layout.addWidget(self.date_hasta)

        panel_layout.addStretch()
        panel_layout.addWidget(QLabel("🔍"))
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar texto...")
        self.txt_buscar.setFixedWidth(200)
        panel_layout.addWidget(self.txt_buscar)

        btn_go = QPushButton("Filtrar")
        btn_go.setCursor(Qt.PointingHandCursor)
        btn_go.setStyleSheet("background:#3b82f6; color:white; font-weight:bold; padding:6px 15px; border-radius:4px;")
        btn_go.clicked.connect(self._filtrar)
        panel_layout.addWidget(btn_go)

        layout.addWidget(panel)

        self.bg_filtro.buttonClicked.connect(self._toggle_fechas)
        self.txt_buscar.returnPressed.connect(self._filtrar)

        # TABLA
        self.tabla = QTableWidget(0, 10)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Doc", "Concepto", "Cuenta", "Nombre", "Debe", "Haber", "Banco", "Estado", "Saldo"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setStyleSheet("QHeaderView::section { background:#f1f5f9; padding:6px; border:none; font-weight:bold; color:#64748b; }")
        
        self.tabla.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla.customContextMenuRequested.connect(self._menu_contextual)
        self.tabla.cellDoubleClicked.connect(lambda r, c: self._editar(r))
        
        layout.addWidget(self.tabla)

        self.lbl_totales = QLabel("...")
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        self.lbl_totales.setStyleSheet("font-weight:bold; font-size:14px; padding:10px; background:#e0e7ff; border-radius:6px; color:#1e3a8a;")
        layout.addWidget(self.lbl_totales)

    # ============================================================
    # LÓGICA DE FILTRADO Y TABLA
    # ============================================================
    def _toggle_fechas(self):
        activo = self.rb_rango.isChecked()
        self.date_desde.setEnabled(activo)
        self.date_hasta.setEnabled(activo)
        self._filtrar()

    def _filtrar(self):
        res = []
        texto = self.txt_buscar.text().lower().strip()
        modo = "todo"
        if self.rb_mes.isChecked(): modo = "mes"
        elif self.rb_rango.isChecked(): modo = "rango"

        hoy = QDate.currentDate()

        for m in self.data.movimientos:
            # 1. Parseo Fecha (Seguro)
            f_str = str(m.get("fecha", "")).strip()
            fecha_mov = None
            try:
                if "/" in f_str: 
                    d, mm, aa = map(int, f_str.split("/"))
                    fecha_mov = QDate(aa, mm, d)
                elif "-" in f_str: 
                    p = f_str.split("-")
                    if len(p[0]) == 4:
                        fecha_mov = QDate(int(p[0]), int(p[1]), int(p[2]))
                    else:
                        fecha_mov = QDate(int(p[2]), int(p[1]), int(p[0]))
            except (ValueError, IndexError):
                pass

            # 2. Filtro Fecha
            mostrar = True
            if fecha_mov and fecha_mov.isValid():
                if modo == "mes":
                    if not (fecha_mov.month() == hoy.month() and fecha_mov.year() == hoy.year()): mostrar = False
                elif modo == "rango":
                    if not (self.date_desde.date() <= fecha_mov <= self.date_hasta.date()): mostrar = False
            else:
                if modo != "todo": mostrar = False # Si la fecha es mala, solo sale en "todo"

            if not mostrar: continue

            # 3. Filtro Texto
            if texto:
                full = " ".join([str(m.get(k,'')) for k in ['concepto','cuenta','documento','banco']]).lower()
                if texto not in full: continue

            res.append(m)

        # Ordenar y Mostrar
        res.sort(key=lambda x: self._fecha_key(x), reverse=True)
        self._llenar_tabla(res)

    def _fecha_key(self, m):
        try:
            f = str(m.get("fecha", "")).replace("-", "/")
            if "/" in f: 
                p = f.split("/")
                return QDate(int(p[2]), int(p[1]), int(p[0]))
        except (ValueError, IndexError):
            pass
        return QDate(1900, 1, 1)

    def _llenar_tabla(self, movs):
        self.tabla.setRowCount(0)
        self.movimientos_actuales = movs
        td, th = 0, 0
        
        for m in movs:
            r = self.tabla.rowCount()
            self.tabla.insertRow(r)
            try:
                d = float(str(m.get("debe", 0)).replace(",", "."))
            except (ValueError, TypeError):
                d = 0.0
            try:
                h = float(str(m.get("haber", 0)).replace(",", "."))
            except (ValueError, TypeError):
                h = 0.0
            td+=d; th+=h
            
            nom = self.data.obtener_nombre_cuenta(m.get("cuenta"))
            vals = [
                m.get("fecha"), m.get("documento"), m.get("concepto"), 
                m.get("cuenta"), nom, 
                f"{d:,.2f}", f"{h:,.2f}", 
                m.get("banco"), m.get("estado"), f"{(h-d):,.2f}"
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(str(v))
                if c in [5,6,9]: 
                    it.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    if c==5 and d>0: it.setForeground(QColor("#dc2626"))
                    if c==6 and h>0: it.setForeground(QColor("#16a34a"))
                self.tabla.setItem(r, c, it)
        
        self.lbl_totales.setText(f"Registros: {len(movs)}  |  Gastos: {td:,.2f}  |  Ingresos: {th:,.2f}")

    # ============================================================
    # INTERACCIÓN MENÚ Y GUARDADO
    # ============================================================
    def _menu_contextual(self, pos):
        # FIX: Seleccionar fila bajo el cursor antes de abrir menú
        row = self.tabla.rowAt(pos.y())
        if row < 0: return
        self.tabla.selectRow(row)
        
        menu = QMenu()
        act_edit = menu.addAction("✏️ Editar")
        act_del = menu.addAction("🗑️ Eliminar")
        action = menu.exec(self.tabla.viewport().mapToGlobal(pos))
        
        if action == act_edit: self._editar(row)
        elif action == act_del: self._eliminar(row)

    def _editar(self, row):
        if row < 0: return
        mov = self.movimientos_actuales[row]
        dlg = EditarMovimientoDialog(self, mov, self.cuentas_cache, self.bancos_cache)
        if dlg.exec():
            mov.update(dlg.get_data())
            self._guardar()
            QMessageBox.information(self, "OK", "Movimiento actualizado.")

    def _eliminar(self, row):
        if row < 0: return
        mov = self.movimientos_actuales[row]
        if QMessageBox.question(self, "Confirmar", "¿Eliminar registro?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            if mov in self.data.movimientos:
                self.data.movimientos.remove(mov)
                self._guardar()
                QMessageBox.information(self, "OK", "Eliminado.")

    def _guardar(self):
        if hasattr(self.data, "guardar_datos"): self.data.guardar_datos()
        elif hasattr(self.data, "guardar"): self.data.guardar()
        self._filtrar()