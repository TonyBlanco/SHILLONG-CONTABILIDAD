# -*- coding: utf-8 -*-
"""
DiarioView — SHILLONG CONTABILIDAD v3.6 PRO
Versión moderna, profesional, DPI-SAFE y con Acceso Directo a Registrar.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal  # <--- Importamos Signal
from datetime import datetime


class DiarioView(QWidget):
    
    # Esta señal avisa a la ventana principal para cambiar de pestaña
    signal_ir_a_registrar = Signal()

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.tema_oscuro = False

        self._build_ui()
        self._cargar_movimientos_hoy()   # Auto-cargar HOY al abrir

    # ============================================================
    # UI PRINCIPAL
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # -----------------------------
        # HEADER (Título + Botón Nuevo)
        # -----------------------------
        header = QHBoxLayout()
        
        titulo = QLabel("📘 Libro Diario General")
        titulo.setStyleSheet("font-size: 26px; font-weight: 800; color: #1e293b;")
        header.addWidget(titulo)
        
        header.addStretch()
        
        # --- EL BOTÓN QUE PEDISTE ---
        self.btn_nuevo = QPushButton("➕ Nuevo Movimiento")
        self.btn_nuevo.setCursor(Qt.PointingHandCursor)
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: bold; font-size: 14px;
                padding: 8px 20px; border-radius: 8px; border: 1px solid #1d4ed8;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:pressed { background-color: #1e40af; padding-top: 10px; padding-bottom: 6px;}
        """)
        # Al hacer clic, emitimos la señal
        self.btn_nuevo.clicked.connect(self.signal_ir_a_registrar.emit)
        
        header.addWidget(self.btn_nuevo)
        layout.addLayout(header)

        # -----------------------------
        # FILTROS
        # -----------------------------
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;")
        filtros_layout = QHBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(10, 10, 10, 10)

        lbl_fecha = QLabel("<b>Fecha:</b>")
        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setStyleSheet("padding: 5px; border: 1px solid #cbd5e1; border-radius: 4px; background: white;")

        self.filtro = QComboBox()
        self.filtro.addItems([
            "Todos los del día",
            "Pagados",
            "Pendientes",
            "Ingresos",
            "Gastos",
        ])
        self.filtro.setStyleSheet("padding: 5px; border: 1px solid #cbd5e1; border-radius: 4px; background: white;")

        self.btn_mostrar = QPushButton("🔍 Filtrar")
        self.btn_mostrar.setStyleSheet("""
            QPushButton {
                background-color: white; border: 1px solid #cbd5e1; color: #334155; font-weight: bold;
                padding: 6px 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #f1f5f9; border-color: #94a3b8; }
        """)
        self.btn_mostrar.clicked.connect(self._filtrar)

        filtros_layout.addWidget(lbl_fecha)
        filtros_layout.addWidget(self.fecha)
        filtros_layout.addSpacing(15)
        filtros_layout.addWidget(QLabel("<b>Ver:</b>"))
        filtros_layout.addWidget(self.filtro)
        filtros_layout.addSpacing(10)
        filtros_layout.addWidget(self.btn_mostrar)
        filtros_layout.addStretch()
        
        layout.addWidget(filtros_frame)

        # -----------------------------
        # TABLA
        # -----------------------------
        self.tabla = QTableWidget(0, 10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Doc", "Concepto", "Cuenta",
            "Nombre Cuenta", "Debe", "Haber",
            "Banco", "Estado", "Saldo"
        ])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget { gridline-color: #f1f5f9; font-size: 13px; }
            QHeaderView::section { background-color: #f1f5f9; padding: 6px; border: none; font-weight: bold; color: #64748b; }
        """)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # Concepto elástico
        layout.addWidget(self.tabla)

        # -----------------------------
        # TOTALES (Footer)
        # -----------------------------
        self.lbl_totales = QLabel("Esperando datos...")
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        self.lbl_totales.setStyleSheet("""
            font-weight: bold; font-size: 14px; color: #1e3a8a;
            padding: 12px; background: #e0e7ff; border-radius: 8px; border: 1px solid #c7d2fe;
        """)
        layout.addWidget(self.lbl_totales)

    # ============================================================
    # LÓGICA DE CARGA
    # ============================================================
    def _cargar_movimientos_hoy(self):
        self._cargar_por_fecha(QDate.currentDate())

    def _filtrar(self):
        fecha_qt = self.fecha.date()
        self._cargar_por_fecha(fecha_qt)

    def _cargar_por_fecha(self, fecha_qt):
        fecha = fecha_qt.toString("dd/MM/yyyy")

        # 1. Obtener todos los movimientos
        # Si data.movimientos es una lista directa:
        todos = self.data.movimientos 
        
        # 2. Filtrar por fecha
        movs = [m for m in todos if m.get("fecha") == fecha]

        # 3. Filtro inteligente
        filtro = self.filtro.currentText()

        if filtro == "Pagados":
            movs = [m for m in movs if m.get("estado", "").lower() == "pagado"]
        elif filtro == "Pendientes":
            movs = [m for m in movs if m.get("estado", "").lower() == "pendiente"]
        elif filtro == "Ingresos":
            movs = [m for m in movs if float(m.get("haber", 0)) > 0]
        elif filtro == "Gastos":
            movs = [m for m in movs if float(m.get("debe", 0)) > 0]

        # Ordenar por documento (opcional, si existe campo numérico en documento)
        # movs.sort(key=lambda m: m.get("documento", ""), reverse=True)

        self._cargar_tabla(movs)

    def _cargar_tabla(self, movs):
        self.tabla.setRowCount(0)

        total_debe = 0
        total_haber = 0
        saldo = 0 # Saldo del día/filtro

        for m in movs:
            d = float(m.get("debe", 0))
            h = float(m.get("haber", 0))

            saldo += h - d
            total_debe += d
            total_haber += h

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            # Nombre cuenta
            cta = str(m.get("cuenta", ""))
            try:
                nombre_cuenta = self.data.obtener_nombre_cuenta(cta)
            except:
                nombre_cuenta = ""

            valores = [
                m.get("fecha", ""), 
                m.get("documento", ""), 
                m.get("concepto", ""), 
                cta,
                nombre_cuenta,
                f"{d:,.2f}", 
                f"{h:,.2f}",
                m.get("banco", ""), 
                m.get("estado", ""), 
                f"{saldo:,.2f}"
            ]

            for col, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                if col in (5, 6, 9): # Columnas numéricas
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla.setItem(row, col, item)

        # Actualizar barra de totales
        self.lbl_totales.setText(
            f"TOTAL GASTOS: {total_debe:,.2f}   |   "
            f"TOTAL INGRESOS: {total_haber:,.2f}   |   "
            f"BALANCE DEL DÍA: {total_haber - total_debe:,.2f}"
        )