# -*- coding: utf-8 -*-
"""
CierreView.py — SHILLONG CONTABILIDAD v3.6 PRO
Dashboard de Cierre Anual: Visión global del ejercicio.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QFrame, 
    QHeaderView, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

import datetime
from collections import defaultdict

# Intentamos importar el motor de exportación para generar el evolutivo
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class CierreView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.año_actual = datetime.date.today().year
        self._build_ui()
        self.actualizar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- HEADER ---
        header = QHBoxLayout()
        lbl_titulo = QLabel("📅 Cierre Anual del Ejercicio")
        lbl_titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b;")
        header.addWidget(lbl_titulo)
        
        header.addStretch()
        
        self.btn_exportar = QPushButton("📊 Exportar Evolutivo Anual")
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: bold; 
                padding: 10px 20px; border-radius: 8px; font-size: 14px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_exportar.clicked.connect(self._exportar_evolutivo)
        header.addWidget(self.btn_exportar)
        
        layout.addLayout(header)

        # --- FILTRO AÑO ---
        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Seleccionar Año Fiscal:"))
        self.cbo_año = QComboBox()
        for a in range(2020, 2031):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        self.cbo_año.currentTextChanged.connect(self.actualizar)
        filtro_layout.addWidget(self.cbo_año)
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)

        # --- TARJETAS KPI (Resumen Anual) ---
        kpi_layout = QHBoxLayout()
        self.kpi_ingresos = self._crear_kpi("INGRESOS ANUALES", "#16a34a")
        self.kpi_gastos = self._crear_kpi("GASTOS ANUALES", "#dc2626")
        self.kpi_resultado = self._crear_kpi("RESULTADO EJERCICIO", "#2563eb")
        
        kpi_layout.addWidget(self.kpi_ingresos)
        kpi_layout.addWidget(self.kpi_gastos)
        kpi_layout.addWidget(self.kpi_resultado)
        layout.addLayout(kpi_layout)

        # --- TABLA RESUMEN MENSUAL ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Mes", "Ingresos", "Gastos", "Saldo Mensual"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget { font-size: 14px; gridline-color: #e2e8f0; }
            QHeaderView::section { background: #f8fafc; padding: 8px; font-weight: bold; border: none; }
        """)
        layout.addWidget(self.tabla)

    def _crear_kpi(self, titulo, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white; border: 1px solid #e2e8f0; border-radius: 12px;
                border-left: 6px solid {color};
            }}
        """)
        vbox = QVBoxLayout(card)
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("color: #64748b; font-weight: bold; font-size: 12px;")
        
        lbl_val = QLabel("0.00")
        lbl_val.setStyleSheet(f"color: {color}; font-weight: 800; font-size: 32px;")
        
        vbox.addWidget(lbl_tit)
        vbox.addWidget(lbl_val)
        card.valor_lbl = lbl_val
        return card

    def actualizar(self):
        año = int(self.cbo_año.currentText())
        
        total_ingresos = 0
        total_gastos = 0
        
        self.tabla.setRowCount(0)
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        for i, nombre_mes in enumerate(meses):
            num_mes = i + 1
            movs = self.data.movimientos_por_mes(num_mes, año)
            
            ing = sum(float(m.get("haber", 0)) for m in movs)
            gas = sum(float(m.get("debe", 0)) for m in movs)
            sal = ing - gas
            
            total_ingresos += ing
            total_gastos += gas
            
            # Añadir fila solo si hay movimiento (opcional, aquí mostramos todos para ver el año completo)
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            
            self.tabla.setItem(row, 0, QTableWidgetItem(nombre_mes))
            
            item_ing = QTableWidgetItem(f"{ing:,.2f}")
            item_ing.setForeground(QColor("#16a34a"))
            item_ing.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 1, item_ing)
            
            item_gas = QTableWidgetItem(f"{gas:,.2f}")
            item_gas.setForeground(QColor("#dc2626"))
            item_gas.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 2, item_gas)
            
            item_sal = QTableWidgetItem(f"{sal:,.2f}")
            item_sal.setFont(QFont("Arial", 9, QFont.Bold))
            item_sal.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 3, item_sal)

        # Actualizar KPIs
        self.kpi_ingresos.valor_lbl.setText(f"{total_ingresos:,.2f}")
        self.kpi_gastos.valor_lbl.setText(f"{total_gastos:,.2f}")
        resultado = total_ingresos - total_gastos
        self.kpi_resultado.valor_lbl.setText(f"{resultado:,.2f}")
        
        color_res = "#16a34a" if resultado >= 0 else "#dc2626"
        self.kpi_resultado.valor_lbl.setStyleSheet(f"color: {color_res}; font-weight: 800; font-size: 32px;")

    def _exportar_evolutivo(self):
        # Reutilizamos la lógica del Informe Evolutivo si existe el motor
        año = int(self.cbo_año.currentText())
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Evolutivo Anual", f"Evolutivo_{año}.xlsx", "Excel (*.xlsx)")
        
        if not archivo: return
        if ExportadorExcelMensual is None:
            QMessageBox.critical(self, "Error", "Motor de exportación no disponible.")
            return

        # Preparar datos
        matriz = defaultdict(lambda: [0.0]*12)
        nombres = {}
        for m in range(1, 13):
            movs = self.data.movimientos_por_mes(m, año)
            for x in movs:
                if float(x.get("debe", 0)) > 0:
                    cta = str(x.get("cuenta", "S/N"))
                    nombres[cta] = self.data.obtener_nombre_cuenta(cta)
                    matriz[cta][m-1] += float(x["debe"])
        
        datos = {k: (nombres.get(k, ""), v, sum(v)) for k, v in matriz.items()}
        
        try:
            ExportadorExcelMensual.exportar_evolutivo_anual(archivo, dict(sorted(datos.items())), año)
            QMessageBox.information(self, "Éxito", "Evolutivo generado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))