# -*- coding: utf-8 -*-
"""
CierreMensualView — SHILLONG CONTABILIDAD v3.7.6 PRO
---------------------------------------------------------
FIX FINAL: Corrección de márgenes PDF para compatibilidad Qt6.
Se soluciona el error "too many arguments" empaquetando los
márgenes en QMarginsF.
---------------------------------------------------------
"""

import datetime
import json
from collections import defaultdict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QMenu, QHeaderView,
    QFrame, QFileDialog, QMessageBox
)
# --- FIX IMPORTS ---
from PySide6.QtCore import Qt, QMarginsF
from PySide6.QtGui import QColor, QFont, QPainter, QTextDocument, QPageLayout
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis

try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class CierreMensualView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year
        
        self.bancos = self._cargar_bancos()
        self.cuentas = self._cargar_cuentas()
        self.reglas_cache = self._cargar_reglas()
        
        self._build_ui()
        self.actualizar()

    # --- CARGA DE DATOS ---
    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except: return ["Todos", "Caja"]

    def _cargar_cuentas(self):
        cuentas = ["Todas"]
        try:
            with open("data/plan_contable_v3.json", "r", encoding="utf-8") as f:
                plan = json.load(f)
                cuentas.extend([f"{k} – {v['nombre']}" for k, v in plan.items()])
        except: pass
        return cuentas

    def _cargar_reglas(self):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}

    # --- CATEGORÍAS ROBUSTAS ---
    def _categoria_de_cuenta(self, cuenta):
        cuenta_str = str(cuenta).split(" ")[0].strip()
        if cuenta_str in self.reglas_cache:
            cat = self.reglas_cache[cuenta_str].get("categoria", "").upper()
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD", "ALIMENTACIÓN": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE", "FARMACIA": "MEDICINE",
                "MEDICAMENTOS": "MEDICINE", "MATERIAL DE LIMPIEZA": "HYGIENE", 
                "LIMPIEZA": "HYGIENE", "LAVANDERÍA": "HYGIENE", "HIGIENE": "HYGIENE",
                "ASEO PERSONAL": "HYGIENE", "SUELDOS Y SALARIOS": "SALARY", 
                "NOMINAS": "SALARY", "TELEFONÍA E INTERNET": "ONLINE", 
                "INTERNET": "ONLINE", "TELEFONO": "ONLINE", 
                "TERAPIAS": "THERAPEUTIC", "DIETA": "DIET"
            }
            if cat in mapeo: return mapeo[cat]
            return cat
        
        try:
            c = int(cuenta_str)
            if 600000 <= c <= 609999: return "MEDICINE"
            if 603000 <= c <= 603999: return "FOOD"
            if 602400 <= c <= 602499: return "HYGIENE"
            if 620401 <= c <= 620499: return "HYGIENE"
            if 640000 <= c <= 649999: return "SALARY"
            if 629200 <= c <= 629299: return "ONLINE"
        except: pass
        return "OTROS"

    # --- UI ---
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        h = QHBoxLayout()
        tit = QLabel("📆 Cierre Mensual")
        tit.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        h.addWidget(tit); h.addStretch()

        self.btn_exportar_menu = QPushButton("📤 Exportar Reportes ▼")
        self.btn_exportar_menu.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 8px 15px; border-radius: 6px;")
        
        self.menu_exp = QMenu(self)
        self.menu_exp.addAction("📄 PDF Estándar (B/N)", self._exportar_pdf_estandar)
        self.menu_exp.addAction("📘 PDF Oficial (Azul)", self._exportar_pdf_azul)
        self.menu_exp.addSeparator()
        self.menu_exp.addAction("📊 Excel General", self._exportar_excel_general)
        self.menu_exp.addAction("📂 Excel por Categorías", self._exportar_excel_categorias)
        self.menu_exp.addAction("🔢 Excel por Cuentas", self._exportar_excel_cuentas)
        self.btn_exportar_menu.setMenu(self.menu_exp)
        
        h.addWidget(self.btn_exportar_menu)
        layout.addLayout(h)

        filtros = QGridLayout()
        self.cbo_mes = QComboBox(); self.cbo_mes.addItems(["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)
        self.cbo_año = QComboBox(); 
        for a in range(2020, 2036): self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        self.cbo_banco = QComboBox(); self.cbo_banco.addItems(self.bancos)
        self.cbo_cuenta = QComboBox(); self.cbo_cuenta.addItems(self.cuentas)
        
        filtros.addWidget(QLabel("Mes:"),0,0); filtros.addWidget(self.cbo_mes,0,1)
        filtros.addWidget(QLabel("Año:"),0,2); filtros.addWidget(self.cbo_año,0,3)
        filtros.addWidget(QLabel("Banco:"),0,4); filtros.addWidget(self.cbo_banco,0,5)
        filtros.addWidget(QLabel("Cuenta:"),1,0); filtros.addWidget(self.cbo_cuenta,1,1,1,2)
        
        for w in [self.cbo_mes, self.cbo_año, self.cbo_banco, self.cbo_cuenta]:
            w.currentIndexChanged.connect(self.actualizar)
        layout.addLayout(filtros)

        kpi = QHBoxLayout()
        self.card_gasto = self._kpi("Gastos", "#dc2626")
        self.card_ingreso = self._kpi("Ingresos", "#16a34a")
        self.card_saldo = self._kpi("Saldo", "#2563eb")
        kpi.addWidget(self.card_gasto); kpi.addWidget(self.card_ingreso); kpi.addWidget(self.card_saldo)
        layout.addLayout(kpi)

        self.tabla = QTableWidget(0, 11)
        self.tabla.setHorizontalHeaderLabels(["Fecha","Doc","Concepto","Cuenta","Nombre","Debe","Haber","Banco","Estado","Saldo","Cat"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        bot = QHBoxLayout()
        self.chart_view = QChartView(); self.chart_view.setRenderHint(QPainter.Antialiasing); self.chart_view.setMinimumHeight(250)
        bot.addWidget(self.chart_view, 2)
        
        anom_frame = QFrame(); anom_l = QVBoxLayout(anom_frame)
        anom_l.addWidget(QLabel("⚠️ Anomalías:"))
        self.txt_anom = QTextEdit(); self.txt_anom.setReadOnly(True)
        anom_l.addWidget(self.txt_anom)
        bot.addWidget(anom_frame, 1)
        layout.addLayout(bot)

    def _kpi(self, t, c):
        f = QFrame(); f.setStyleSheet(f"background:white; border:1px solid #ddd; border-radius:10px; border-left:5px solid {c};")
        v = QVBoxLayout(f); l1 = QLabel(t); l2 = QLabel("0.00")
        l2.setStyleSheet(f"font-size:24px; font-weight:bold; color:{c};"); l2.setObjectName("val")
        v.addWidget(l1); v.addWidget(l2)
        f.val = l2
        return f

    def actualizar(self):
        mes = self.cbo_mes.currentIndex()+1; año = int(self.cbo_año.currentText())
        banco = self.cbo_banco.currentText()
        cta_filt = self.cbo_cuenta.currentText().split(" – ")[0] if " – " in self.cbo_cuenta.currentText() else None
        
        movs = self.data.movimientos_por_mes(mes, año)
        self.filtrados = [] # Guardar para PDF
        
        for m in movs:
            if banco != "Todos" and m.get("banco")!=banco: continue
            if cta_filt and str(m.get("cuenta"))!=cta_filt: continue
            self.filtrados.append(m)
            
        gas = sum(float(m.get("debe",0)) for m in self.filtrados)
        ing = sum(float(m.get("haber",0)) for m in self.filtrados)
        
        self.card_gasto.val.setText(f"{gas:,.2f}")
        self.card_ingreso.val.setText(f"{ing:,.2f}")
        self.card_saldo.val.setText(f"{ing-gas:,.2f}")
        
        self.tabla.setRowCount(0); sal = 0
        for m in self.filtrados:
            d = float(m.get("debe",0)); h = float(m.get("haber",0)); sal += h-d
            r = self.tabla.rowCount(); self.tabla.insertRow(r)
            cat = self._categoria_de_cuenta(m.get("cuenta"))
            items = [
                m.get("fecha"), m.get("documento"), m.get("concepto"), m.get("cuenta"),
                self.data.obtener_nombre_cuenta(m.get("cuenta")),
                f"{d:,.2f}", f"{h:,.2f}", m.get("banco"), m.get("estado"), f"{sal:,.2f}", cat
            ]
            for c, val in enumerate(items):
                it = QTableWidgetItem(str(val))
                if c in [5,6,9]: it.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                if c==10 and val!="OTROS": it.setForeground(QColor("#16a34a")); it.setFont(QFont("Arial",9,QFont.Bold))
                self.tabla.setItem(r,c,it)
                
        self._graficos(self.filtrados)
        
        # Anomalías
        dups = [m.get("documento") for m in self.filtrados if m.get("documento") and "SIN-DOC" not in str(m.get("documento"))]
        msg = "✅ Todo correcto."
        if len(dups)!=len(set(dups)): msg = "⚠️ Documentos duplicados detectados."
        self.txt_anom.setText(msg)

    def _graficos(self, movs):
        cats = defaultdict(float)
        for m in movs:
            if float(m.get("debe",0))>0: cats[self._categoria_de_cuenta(m.get("cuenta"))] += float(m.get("debe",0))
        
        s = QBarSet("Gasto"); c = []
        for k,v in cats.items(): s.append(v); c.append(k)
        
        bs = QBarSeries(); bs.append(s)
        ch = QChart(); ch.addSeries(bs); ch.setTitle("Gastos por Categoría")
        ax = QBarCategoryAxis(); ax.append(c); ch.addAxis(ax, Qt.AlignBottom); bs.attachAxis(ax)
        self.chart_view.setChart(ch)

    # ============================================================
    # PDF ENGINE FIX (Qt6 Compatible)
    # ============================================================
    def _exportar_pdf_estandar(self): self._render_pdf(azul=False)
    def _exportar_pdf_azul(self): self._render_pdf(azul=True)

    def _render_pdf(self, azul=False):
        ruta, _ = QFileDialog.getSaveFileName(self, "PDF", "Reporte.pdf", "PDF (*.pdf)")
        if not ruta: return

        bg_head = "#1e3a8a" if azul else "#f3f4f6"
        txt_head = "white" if azul else "black"
        titulo = f"CIERRE {self.cbo_mes.currentText().upper()} {self.cbo_año.currentText()}"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; font-size: 10pt; }}
                h1 {{ color: {bg_head if azul else 'black'}; text-align: center; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background-color: {bg_head}; color: {txt_head}; padding: 8px; border: 1px solid #ccc; }}
                td {{ padding: 6px; border: 1px solid #ccc; font-size: 9pt; }}
                .num {{ text-align: right; }}
                .total {{ font-weight: bold; background-color: #eee; }}
                .neg {{ color: red; }}
                .pos {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>{titulo}</h1>
            <p><b>Banco:</b> {self.cbo_banco.currentText()} | <b>Cuenta:</b> {self.cbo_cuenta.currentText()}</p>
            
            <table>
                <thead>
                    <tr>
                        <th width="12%">Fecha</th>
                        <th width="35%">Concepto</th>
                        <th width="20%">Cuenta</th>
                        <th width="10%">Debe</th>
                        <th width="10%">Haber</th>
                        <th width="13%">Saldo</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        t_d, t_h, sal = 0, 0, 0
        for m in self.filtrados:
            d = float(m.get("debe",0))
            h = float(m.get("haber",0))
            sal += h-d
            t_d += d; t_h += h
            
            cta_nom = self.data.obtener_nombre_cuenta(m.get("cuenta"))
            color_sal = "neg" if sal < 0 else "pos"
            
            html += f"""
            <tr>
                <td>{m.get("fecha")}</td>
                <td>{m.get("concepto")}</td>
                <td>{m.get("cuenta")}<br><small>{cta_nom[:20]}</small></td>
                <td class="num">{d:,.2f}</td>
                <td class="num">{h:,.2f}</td>
                <td class="num {color_sal}">{sal:,.2f}</td>
            </tr>
            """
            
        neto = t_h - t_d
        html += f"""
                <tr class="total">
                    <td colspan="3" style="text-align:right;">TOTALES</td>
                    <td class="num">{t_d:,.2f}</td>
                    <td class="num">{t_h:,.2f}</td>
                    <td class="num {'neg' if neto < 0 else 'pos'}">{neto:,.2f}</td>
                </tr>
                </tbody>
            </table>
            <br>
            <p style="font-size:8pt; color:#666; text-align:center;">Generado por Shillong Contabilidad v3.7 PRO</p>
        </body>
        </html>
        """

        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(ruta)
        
        # --- FIX: QMarginsF ---
        margins = QMarginsF(10, 10, 10, 10)
        printer.setPageMargins(margins, QPageLayout.Unit.Millimeter)
        
        doc.print_(printer)
        QMessageBox.information(self, "Éxito", "PDF Generado correctamente.")

    # --- EXCEL ---
    def _exportar_excel_general(self): self._exportar_excel_base("general")
    def _exportar_excel_categorias(self): self._exportar_excel_base("categoria")
    def _exportar_excel_cuentas(self): self._exportar_excel_base("cuenta")

    def _exportar_excel_base(self, modo):
        if not ExportadorExcelMensual: return
        nombres = {"general":"Cierre","categoria":"PorCategorias","cuenta":"PorCuentas"}
        ruta, _ = QFileDialog.getSaveFileName(self, "Excel", f"{nombres[modo]}_{self.cbo_mes.currentText()}.xlsx", "Excel (*.xlsx)")
        if not ruta: return
        
        prep = []
        sal = 0
        for m in self.filtrados:
            d = float(m.get("debe",0)); h = float(m.get("haber",0)); sal += h-d
            it = m.copy(); it["saldo"] = sal
            it["categoria"] = self._categoria_de_cuenta(m.get("cuenta"))
            it["nombre_cuenta"] = self.data.obtener_nombre_cuenta(m.get("cuenta"))
            prep.append(it)
            
        per = f"{self.cbo_mes.currentText()} {self.cbo_año.currentText()}"
        try:
            if modo=="general": ExportadorExcelMensual.exportar_general(ruta, prep, per)
            elif modo=="categoria":
                g = defaultdict(list)
                for x in prep: g[x["categoria"]].append(x)
                ExportadorExcelMensual.exportar_agrupado(ruta, dict(sorted(g.items())), per, "Categoría")
            elif modo=="cuenta":
                g = defaultdict(list)
                for x in prep: g[f"{x['cuenta']} - {x['nombre_cuenta']}"].append(x)
                ExportadorExcelMensual.exportar_agrupado(ruta, dict(sorted(g.items())), per, "Cuenta")
            QMessageBox.information(self, "OK", "Excel Exportado.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _generar_asientos_cierre(self): QMessageBox.information(self, "Asientos", "Asientos generados.")
    def _guardar_cierre(self): QMessageBox.information(self, "Guardado", "Cierre guardado.")