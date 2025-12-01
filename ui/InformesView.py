# -*- coding: utf-8 -*-
"""
InformesView.py — SHILLONG CONTABILIDAD v3.7.7 PRO
---------------------------------------------------------
FIX FINAL BLINDADO:
- Protección contra rangos de fechas sin datos.
- Inicialización segura de variables.
- Manejo de errores en exportación.
---------------------------------------------------------
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QFrame, 
    QHeaderView, QMessageBox, QFileDialog, QMenu, QDateEdit,
    QGridLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QFont, QTextDocument
from PySide6.QtPrintSupport import QPrinter

import datetime
import json
from collections import defaultdict

# Intentamos importar el motor de exportación
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class InformesView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.datos_actuales = [] # Inicializamos vacío para evitar errores
        
        # Carga segura de auxiliares
        self.reglas_cache = self._cargar_reglas()
        self.cuentas = self._cargar_cuentas()
        
        self._build_ui()
        
        # Intentamos cargar el reporte inicial protegiendo fallos
        try:
            self.actualizar_reporte()
        except Exception as e:
            print(f"Aviso: No se pudo cargar el reporte inicial: {e}")

    def _cargar_reglas(self):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}

    def _cargar_cuentas(self):
        cuentas = []
        try:
            with open("data/plan_contable_v3.json", "r", encoding="utf-8") as f:
                plan = json.load(f)
                cuentas = [f"{k} – {v['nombre']}" for k, v in plan.items()]
        except: pass
        return cuentas

    def _categoria_de_cuenta(self, cuenta):
        cta = str(cuenta).split(" ")[0].strip()
        if cta in self.reglas_cache:
            cat = self.reglas_cache[cta].get("categoria","").upper()
            mapeo = {"COMESTIBLES Y BEBIDAS":"FOOD", "ALIMENTACIÓN":"FOOD", "FARMACIA":"MEDICINE", "SUELDOS Y SALARIOS":"SALARY"}
            if cat in mapeo: return mapeo[cat]
            return cat
        return "OTROS"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # Header
        h = QHBoxLayout()
        tit = QLabel("📈 Informes & Business Intelligence")
        tit.setStyleSheet("font-size: 26px; font-weight: 800; color: #1e293b;")
        h.addWidget(tit); h.addStretch()

        # Botón Exportar
        self.btn_exportar = QPushButton("📤 Exportar Reporte ▼")
        self.btn_exportar.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px;")
        
        self.menu_exp = QMenu(self)
        self.menu_exp.addAction("📄 PDF Reporte Actual", self._pdf)
        self.menu_exp.addSeparator()
        self.menu_exp.addAction("📊 Excel General", lambda: self._excel("general"))
        self.menu_exp.addAction("📂 Excel Agrupado (Cat)", lambda: self._excel("categoria"))
        
        self.btn_exportar.setMenu(self.menu_exp)
        h.addWidget(self.btn_exportar)
        layout.addLayout(h)

        # Panel Filtros
        panel = QFrame()
        panel.setStyleSheet("background:white; border:1px solid #e2e8f0; border-radius:10px;")
        pl = QGridLayout(panel); pl.setContentsMargins(15,15,15,15)

        pl.addWidget(QLabel("Tipo de Informe:"), 0, 0)
        self.cbo_tipo = QComboBox()
        self.cbo_tipo.addItems(["📘 Diario General (Rango)", "📒 Libro Mayor (Por Cuenta)", "⚖️ Balance de Sumas y Saldos"])
        self.cbo_tipo.currentIndexChanged.connect(self._cambiar_modo)
        pl.addWidget(self.cbo_tipo, 0, 1)

        # Fechas
        pl.addWidget(QLabel("Desde:"), 0, 2)
        # Fecha inicio: 1 del mes actual para evitar rangos vacíos
        hoy = QDate.currentDate()
        inicio_mes = QDate(hoy.year(), hoy.month(), 1)
        self.date_ini = QDateEdit(inicio_mes) 
        self.date_ini.setCalendarPopup(True)
        pl.addWidget(self.date_ini, 0, 3)

        pl.addWidget(QLabel("Hasta:"), 0, 4)
        self.date_fin = QDateEdit(hoy)
        self.date_fin.setCalendarPopup(True)
        pl.addWidget(self.date_fin, 0, 5)

        # Cuenta
        self.lbl_cta = QLabel("Cuenta:")
        self.cbo_cta = QComboBox()
        self.cbo_cta.addItems(self.cuentas)
        self.cbo_cta.setEnabled(False)
        pl.addWidget(self.lbl_cta, 1, 0)
        pl.addWidget(self.cbo_cta, 1, 1, 1, 3)

        btn_gen = QPushButton("🔍 Generar Informe")
        btn_gen.setStyleSheet("background:#3b82f6; color:white; font-weight:bold; border-radius:6px; padding:6px;")
        btn_gen.clicked.connect(self.actualizar_reporte)
        pl.addWidget(btn_gen, 1, 4, 1, 2)

        layout.addWidget(panel)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("QHeaderView::section { background-color: #f1f5f9; font-weight: bold; border: none; padding: 6px; }")
        layout.addWidget(self.tabla)

        # Totales
        self.lbl_totales = QLabel("Totales: ---")
        self.lbl_totales.setStyleSheet("font-size: 16px; font-weight: bold; color: #334155; padding: 10px; background: #e2e8f0; border-radius: 6px;")
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_totales)

    def _cambiar_modo(self):
        modo = self.cbo_tipo.currentText()
        if "Mayor" in modo:
            self.cbo_cta.setEnabled(True)
            self.lbl_cta.setStyleSheet("color: black;")
        else:
            self.cbo_cta.setEnabled(False)
            self.lbl_cta.setStyleSheet("color: gray;")

    def _parse_fecha(self, f_str):
        try:
            if "/" in f_str: d,m,a = map(int, f_str.split("/"))
            elif "-" in f_str: 
                p=list(map(int, f_str.split("-")))
                a,m,d = p if p[0]>1000 else (p[2],p[1],p[0])
            else: return None
            return datetime.date(a,m,d)
        except: return None

    def actualizar_reporte(self):
        try:
            modo = self.cbo_tipo.currentText()
            d_ini = self.date_ini.date().toPython()
            d_fin = self.date_fin.date().toPython()
            
            self.datos_actuales = [] 

            if "Sumas y Saldos" in modo:
                self._generar_sumas_saldos(d_ini, d_fin)
            elif "Mayor" in modo:
                self._generar_mayor(d_ini, d_fin)
            else:
                self._generar_diario(d_ini, d_fin)
        except Exception as e:
            print(f"Error generando reporte: {e}")
            self.lbl_totales.setText("Error al procesar datos. Revise fechas.")

    def _generar_diario(self, ini, fin):
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Concepto", "Cuenta", "Nombre", "Debe", "Haber", "Categoría"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        datos = []
        t_debe, t_haber = 0, 0
        
        for m in self.data.movimientos:
            f = self._parse_fecha(m.get("fecha",""))
            if f and ini <= f <= fin:
                d = float(m.get("debe",0))
                h = float(m.get("haber",0))
                t_debe += d; t_haber += h
                
                m_copy = m.copy()
                m_copy["categoria"] = self._categoria_de_cuenta(m.get("cuenta"))
                m_copy["nombre_cuenta"] = self.data.obtener_nombre_cuenta(m.get("cuenta"))
                datos.append(m_copy)

        datos.sort(key=lambda x: self._parse_fecha(x["fecha"]) or datetime.date.min)
        self.datos_actuales = datos

        self.tabla.setRowCount(len(datos))
        for r, m in enumerate(datos):
            self.tabla.setItem(r,0, QTableWidgetItem(m.get("fecha","")))
            self.tabla.setItem(r,1, QTableWidgetItem(m.get("concepto","")))
            self.tabla.setItem(r,2, QTableWidgetItem(str(m.get("cuenta",""))))
            self.tabla.setItem(r,3, QTableWidgetItem(m.get("nombre_cuenta","")))
            self.tabla.setItem(r,4, QTableWidgetItem(f"{m.get('debe',0):,.2f}"))
            self.tabla.setItem(r,5, QTableWidgetItem(f"{m.get('haber',0):,.2f}"))
            self.tabla.setItem(r,6, QTableWidgetItem(m.get("categoria","")))

        self.lbl_totales.setText(f"TOTAL DEBE: {t_debe:,.2f}  |  TOTAL HABER: {t_haber:,.2f}  |  BALANCE: {t_haber-t_debe:,.2f}")

    def _generar_mayor(self, ini, fin):
        txt_cta = self.cbo_cta.currentText()
        if not txt_cta: return # Protección
        cuenta_target = txt_cta.split(" – ")[0]
        
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Doc", "Concepto", "Debe", "Haber", "Saldo Acum."])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        datos = []
        saldo = 0
        t_debe, t_haber = 0, 0
        
        temp = []
        for m in self.data.movimientos:
            f = self._parse_fecha(m.get("fecha",""))
            if f and ini <= f <= fin and str(m.get("cuenta")) == cuenta_target:
                temp.append(m)
        temp.sort(key=lambda x: self._parse_fecha(x["fecha"]) or datetime.date.min)
        
        self.tabla.setRowCount(len(temp))
        for r, m in enumerate(temp):
            d = float(m.get("debe",0))
            h = float(m.get("haber",0))
            saldo += (h - d)
            t_debe += d; t_haber += h
            
            m_copy = m.copy()
            m_copy["saldo_acum"] = saldo
            self.datos_actuales.append(m_copy)

            self.tabla.setItem(r,0, QTableWidgetItem(m.get("fecha","")))
            self.tabla.setItem(r,1, QTableWidgetItem(m.get("documento","")))
            self.tabla.setItem(r,2, QTableWidgetItem(m.get("concepto","")))
            self.tabla.setItem(r,3, QTableWidgetItem(f"{d:,.2f}"))
            self.tabla.setItem(r,4, QTableWidgetItem(f"{h:,.2f}"))
            
            it_sal = QTableWidgetItem(f"{saldo:,.2f}")
            if saldo < 0: it_sal.setForeground(QColor("red"))
            self.tabla.setItem(r,5, it_sal)

        nomb = self.data.obtener_nombre_cuenta(cuenta_target)
        self.lbl_totales.setText(f"MAYOR DE: {nomb}  |  TOTAL DEBE: {t_debe:,.2f}  |  TOTAL HABER: {t_haber:,.2f}  |  SALDO FINAL: {saldo:,.2f}")

    def _generar_sumas_saldos(self, ini, fin):
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Cuenta", "Nombre", "Suma Debe", "Suma Haber", "Saldo Final"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        agrupado = defaultdict(lambda: {"d":0.0, "h":0.0})
        
        for m in self.data.movimientos:
            f = self._parse_fecha(m.get("fecha",""))
            if f and ini <= f <= fin:
                c = str(m.get("cuenta"))
                agrupado[c]["d"] += float(m.get("debe",0))
                agrupado[c]["h"] += float(m.get("haber",0))
        
        lista = []
        t_d, t_h = 0, 0
        for cta, vals in agrupado.items():
            saldo = vals["h"] - vals["d"]
            lista.append({
                "cuenta": cta,
                "nombre": self.data.obtener_nombre_cuenta(cta),
                "debe": vals["d"],
                "haber": vals["h"],
                "saldo": saldo
            })
            t_d += vals["d"]; t_h += vals["h"]
            
        lista.sort(key=lambda x: x["cuenta"])
        self.datos_actuales = lista 
        
        self.tabla.setRowCount(len(lista))
        for r, item in enumerate(lista):
            self.tabla.setItem(r,0, QTableWidgetItem(item["cuenta"]))
            self.tabla.setItem(r,1, QTableWidgetItem(item["nombre"]))
            self.tabla.setItem(r,2, QTableWidgetItem(f"{item['debe']:,.2f}"))
            self.tabla.setItem(r,3, QTableWidgetItem(f"{item['haber']:,.2f}"))
            
            it_s = QTableWidgetItem(f"{item['saldo']:,.2f}")
            if item["saldo"] < 0: it_s.setForeground(QColor("red"))
            elif item["saldo"] > 0: it_s.setForeground(QColor("green"))
            self.tabla.setItem(r,4, it_s)
            
        self.lbl_totales.setText(f"BALANCE GLOBAL  |  DEBE: {t_d:,.2f}  |  HABER: {t_h:,.2f}  |  NETO: {t_h-t_d:,.2f}")

    def _pdf(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "PDF", "Informe.pdf", "PDF (*.pdf)")
        if not ruta: return
        
        html = """<h1>Informe Contable</h1><table border=1 cellspacing=0 cellpadding=5 width="100%">"""
        html += "<tr>"
        for c in range(self.tabla.columnCount()):
            it = self.tabla.horizontalHeaderItem(c)
            html += f"<th bgcolor='#eee'>{it.text() if it else ''}</th>"
        html += "</tr>"
        
        for r in range(self.tabla.rowCount()):
            html += "<tr>"
            for c in range(self.tabla.columnCount()):
                it = self.tabla.item(r, c)
                txt = it.text() if it else ""
                align = "right" if c > 1 else "left"
                html += f"<td align='{align}'>{txt}</td>"
            html += "</tr>"
        html += "</table>"
        html += f"<br><h3>{self.lbl_totales.text()}</h3>"

        doc = QTextDocument(); doc.setHtml(html)
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(ruta)
        doc.print_(printer)
        QMessageBox.information(self, "OK", "PDF Generado.")

    def _excel(self, modo):
        if not ExportadorExcelMensual: return
        ruta, _ = QFileDialog.getSaveFileName(self, "Excel", "Informe.xlsx", "Excel (*.xlsx)")
        if not ruta: return
        
        tipo_rep = self.cbo_tipo.currentText()
        datos_export = []
        
        if "Sumas" in tipo_rep:
            for row in self.datos_actuales:
                datos_export.append({
                    "fecha": "-", "documento": "-", "concepto": "Balance", 
                    "cuenta": row.get("cuenta",""), "nombre_cuenta": row.get("nombre",""),
                    "debe": row.get("debe",0), "haber": row.get("haber",0),
                    "saldo": row.get("saldo",0), "banco": "-", "estado": "-", "categoria": "-"
                })
        else:
            datos_export = self.datos_actuales

        try:
            ExportadorExcelMensual.exportar_general(ruta, datos_export, f"Informe: {tipo_rep}")
            QMessageBox.information(self, "OK", "Excel generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))