# -*- coding: utf-8 -*-
"""
LIBRO MENSUAL — SHILLONG CONTABILIDAD v3.2 PRO++ (FORMATO FINAL PERFECTO)
Actualizado para usar el nuevo Motor de Exportación 2025.
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument, QColor, QFont
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PySide6.QtCharts import QChart, QChartView, QBarCategoryAxis, QValueAxis, QBarSet, QBarSeries

import datetime
import json

# Importamos el nuevo motor
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None


class LibroMensualView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        hoy = datetime.date.today()
        self.mes_actual = hoy.month
        self.año_actual = hoy.year
        self.bancos = self._cargar_bancos()
        self._build_ui()
        self.actualizar()

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except:
            return ["Todos", "Caja"]

    def _categoria_de_cuenta(self, cuenta):
        """Helper para determinar categoría (necesario para el Excel bonito)"""
        try:
            c = int(cuenta)
            if 600000 <= c <= 609999: return "FOOD"
            if 610000 <= c <= 619999: return "MEDICINE"
            if 620000 <= c <= 629999: return "HYGIENE"
            if 750000 <= c <= 759999: return "SALARY"
            if 770000 <= c <= 779999: return "ONLINE"
            if 780000 <= c <= 789999: return "THERAPEUTIC"
            if 790000 <= c <= 799999: return "DIET"
        except:
            pass
        return "OTROS"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- HEADER (Título y Botones) ---
        header_layout = QHBoxLayout()
        
        # Título
        lbl_titulo = QLabel("📖 Libro Diario Mensual")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        header_layout.addWidget(lbl_titulo)
        
        header_layout.addStretch() # Espacio flexible

        # Botones de Acción (Movidios ARRIBA)
        btn_print = QPushButton("🖨️ Imprimir PDF")
        btn_print.setStyleSheet("""
            QPushButton {
                background-color: #64748b; color: white; font-weight: bold; 
                padding: 8px 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #475569; }
        """)
        btn_print.clicked.connect(self.imprimir_pdf)

        btn_excel = QPushButton("📤 Exportar Excel Oficial")
        btn_excel.setStyleSheet("""
            QPushButton {
                background-color: #16a34a; color: white; font-weight: bold; 
                padding: 8px 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #15803d; }
        """)
        btn_excel.clicked.connect(self.exportar_excel)

        header_layout.addWidget(btn_print)
        header_layout.addWidget(btn_excel)
        
        layout.addLayout(header_layout)

        # --- FILTROS ---
        filtros_frame = QFrame()
        filtros_frame.setStyleSheet("background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;")
        filtros_layout = QHBoxLayout(filtros_frame)
        filtros_layout.setContentsMargins(15, 10, 15, 10)

        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems(["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)
        
        self.cbo_año = QComboBox()
        self.cbo_año.addItems([str(x) for x in range(2020, 2031)])
        self.cbo_año.setCurrentText(str(self.año_actual))
        
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)

        btn_refresh = QPushButton("🔄 Filtrar")
        btn_refresh.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold; padding: 5px 15px; border-radius: 4px;")
        btn_refresh.clicked.connect(self.actualizar)

        filtros_layout.addWidget(QLabel("<b>Mes:</b>"))
        filtros_layout.addWidget(self.cbo_mes)
        filtros_layout.addSpacing(15)
        filtros_layout.addWidget(QLabel("<b>Año:</b>"))
        filtros_layout.addWidget(self.cbo_año)
        filtros_layout.addSpacing(15)
        filtros_layout.addWidget(QLabel("<b>Banco:</b>"))
        filtros_layout.addWidget(self.cbo_banco)
        filtros_layout.addSpacing(15)
        filtros_layout.addWidget(btn_refresh)
        filtros_layout.addStretch()
        
        layout.addWidget(filtros_frame)

        # --- TABLA ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Doc", "Concepto", "Cuenta", "Debe", "Haber", "Saldo", "Banco", "Estado"])
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("QHeaderView::section { background-color: #f1f5f9; font-weight: bold; border: none; padding: 6px; }")
        layout.addWidget(self.tabla)

    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)

        self.tabla.setRowCount(0)
        saldo_acum = 0
        
        for m in filtrados:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe

            items = [
                m.get("fecha"),
                m.get("documento"),
                m.get("concepto"),
                str(m.get("cuenta")),
                f"{debe:,.2f}",
                f"{haber:,.2f}",
                f"{saldo_acum:,.2f}",
                m.get("banco"),
                m.get("estado")
            ]

            for col, val in enumerate(items):
                it = QTableWidgetItem(str(val))
                if col in [4, 5, 6]: # Numeros a la derecha
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if col == 6: # Color al saldo
                        # CORRECCIÓN: Usar setForeground en lugar de setFont para cambiar color
                        it.setForeground(QColor("#1e3a8a"))
                        it.setFont(QFont("Arial", 9, QFont.Bold)) # Opcional: poner en negrita también
                self.tabla.setItem(row, col, it)

    def _aplicar_filtros(self, movs):
        banco = self.cbo_banco.currentText()
        res = []
        for m in movs:
            if banco != "Todos" and m.get("banco") != banco:
                continue
            res.append(m)
        return res

    def imprimir_pdf(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            # Aquí podrías conectar con un generador de reportes PDF si lo tienes
            pass

    def exportar_excel(self):
        """Versión corregida que usa ExportadorExcelMensual.exportar_general"""
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Libro Mensual", "Libro_Mensual.xlsx", "Excel (*.xlsx)")
        if not ruta:
            return

        if ExportadorExcelMensual is None:
            QMessageBox.critical(self, "Error", "Falta el módulo ExportadorExcelMensual o openpyxl.")
            return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)
        
        datos_para_excel = []
        saldo_acum = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            
            # Adaptamos el diccionario a lo que espera el motor nuevo
            item = m.copy()
            item["saldo"] = saldo_acum
            item["categoria"] = self._categoria_de_cuenta(m.get("cuenta"))
            datos_para_excel.append(item)

        try:
            periodo_str = f"{self.cbo_mes.currentText()} {año}"
            ExportadorExcelMensual.exportar_general(ruta, datos_para_excel, periodo_str)
            QMessageBox.information(self, "Éxito", "Libro mensual exportado correctamente con formato profesional.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{str(e)}")