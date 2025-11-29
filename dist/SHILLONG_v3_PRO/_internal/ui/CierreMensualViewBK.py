# -*- coding: utf-8 -*-
"""
CierreMensualView — SHILLONG CONTABILIDAD v3.6 PRO PDF ULTIMATE
Módulo profesional de cierre mensual con todo incluido
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog,
    QMessageBox, QFrame, QScrollArea, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextDocument, QFont
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QLineSeries, QValueAxis, QBarCategoryAxis

import datetime
import json
import os
from collections import defaultdict


class CierreMensualView(QWidget):

    COLORES = {
        "FOOD": "#fef3c7", "MEDICINE": "#ffe4e6", "HYGIENE": "#e0f2fe",
        "SALARY": "#ede9fe", "ONLINE": "#cffafe", "THERAPEUTIC": "#fae8ff",
        "DIET": "#dcfce7", "OTROS": "#ffffff"
    }

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year
        self.bancos = self._cargar_bancos()
        self.cuentas = self._cargar_cuentas()
        self._build_ui()
        self.actualizar()

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except:
            return ["Todos", "Caja"]

    def _cargar_cuentas(self):
        cuentas = ["Todas"]
        try:
            with open("data/plan_contable_v3.json", "r", encoding="utf-8") as f:
                plan = json.load(f)
                cuentas.extend([f"{k} – {v['nombre']}" for k, v in plan.items()])
        except:
            pass
        return cuentas

    def _categoria_de_cuenta(self, cuenta):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                reglas = json.load(f)
        except:
            reglas = {}
        cuenta_str = str(cuenta).strip()
        if cuenta_str in reglas:
            cat = reglas[cuenta_str].get("categoria", "").upper()
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD", "FARMACIA Y MATERIAL SANITARIO": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE", "LAVANDERÍA": "HYGIENE", "ASEO PERSONAL": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY", "TELEFONÍA E INTERNET": "ONLINE"
            }
            return mapeo.get(cat, "OTROS")
        try:
            c = int(cuenta)
            if 600000 <= c <= 609999: return "FOOD"
            if 610000 <= c <= 619999: return "MEDICINE"
            if 620000 <= c <= 629999: return "HYGIENE"
            if 750000 <= c <= 759999: return "SALARY"
            if 770000 <= c <= 779999: return "ONLINE"
            if 780000 <= c <= 789999: return "THERAPEUTIC"
            if 790000 <= c <= 799999: return "DIET"
        except: pass
        return "OTROS"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("CIERRE MENSUAL — SHILLONG CONTABILIDAD v3.6 PRO")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        layout.addWidget(titulo)

        filtros = QGridLayout()
        filtros.addWidget(QLabel("Mes:"), 0, 0)
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems(["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)
        filtros.addWidget(self.cbo_mes, 0, 1)

        filtros.addWidget(QLabel("Año:"), 0, 2)
        self.cbo_año = QComboBox()
        for a in range(2020, 2036): self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        filtros.addWidget(self.cbo_año, 0, 3)

        filtros.addWidget(QLabel("Banco:"), 0, 4)
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)
        filtros.addWidget(self.cbo_banco, 0, 5)

        filtros.addWidget(QLabel("Cuenta:"), 1, 0)
        self.cbo_cuenta = QComboBox()
        self.cbo_cuenta.addItems(self.cuentas)
        filtros.addWidget(self.cbo_cuenta, 1, 1, 1, 2)

        filtros.addWidget(QLabel("Categoría:"), 1, 3)
        self.cbo_categoria = QComboBox()
        self.cbo_categoria.addItems(["Todas", "FOOD", "MEDICINE", "HYGIENE", "SALARY", "ONLINE", "THERAPEUTIC", "DIET", "OTROS"])
        filtros.addWidget(self.cbo_categoria, 1, 4)

        filtros.addWidget(QLabel("Tipo:"), 1, 5)
        self.cbo_tipo = QComboBox()
        self.cbo_tipo.addItems(["Todos", "Solo gastos", "Solo ingresos"])
        filtros.addWidget(self.cbo_tipo, 1, 6)

        for w in [self.cbo_mes, self.cbo_año, self.cbo_banco, self.cbo_cuenta, self.cbo_categoria, self.cbo_tipo]:
            w.currentIndexChanged.connect(self.actualizar)

        layout.addLayout(filtros)

        # KPIs
        kpi_layout = QHBoxLayout()
        self.card_gasto = self._crear_kpi_card("Total Gastos", "0,00", "#dc2626")
        self.card_ingreso = self._crear_kpi_card("Total Ingresos", "0,00", "#16a34a")
        self.card_saldo = self._crear_kpi_card("Saldo Final", "0,00", "#2563eb")
        kpi_layout.addWidget(self.card_gasto)
        kpi_layout.addWidget(self.card_ingreso)
        kpi_layout.addWidget(self.card_saldo)
        layout.addLayout(kpi_layout)

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar en cierre mensual...")
        self.buscador.textChanged.connect(self.actualizar)
        layout.addWidget(self.buscador)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha","Documento","Concepto","Cuenta","Nombre Cuenta",
            "Debe","Haber","Banco","Estado","Saldo Acum.","Categoría"
        ])
        layout.addWidget(self.tabla)

        # Gráficos
        graficos = QHBoxLayout()
        self.chart_categoria = QChartView()
        self.chart_evolucion = QChartView()
        graficos.addWidget(self.chart_categoria)
        graficos.addWidget(self.chart_evolucion)
        layout.addLayout(graficos)

        # Anomalías
        self.anomalias = QTextEdit()
        self.anomalias.setMaximumHeight(120)
        self.anomalias.setReadOnly(True)
        layout.addWidget(QLabel("Anomalías detectadas:"))
        layout.addWidget(self.anomalias)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_preview = QPushButton("Vista previa PDF")
        self.btn_print = QPushButton("Imprimir PDF")
        self.btn_export = QPushButton("Exportar Excel")
        self.btn_asientos = QPushButton("Generar Asientos de Cierre")
        self.btn_guardar = QPushButton("Guardar Cierre")
        self.btn_bloquear = QPushButton("BLOQUEAR MES")
        self.btn_desbloquear = QPushButton("DESBLOQUEAR MES")

        for btn in [self.btn_preview, self.btn_print, self.btn_export, self.btn_asientos,
                    self.btn_guardar, self.btn_bloquear, self.btn_desbloquear]:
            btn_layout.addWidget(btn)

        self.btn_preview.clicked.connect(self.vista_previa)
        self.btn_print.clicked.connect(self.imprimir)
        self.btn_export.clicked.connect(self.exportar_excel)
        self.btn_asientos.clicked.connect(self._generar_asientos_cierre)
        self.btn_guardar.clicked.connect(self._guardar_cierre)
        self.btn_bloquear.clicked.connect(self._bloquear_mes)
        self.btn_desbloquear.clicked.connect(self._desbloquear_mes)

        layout.addLayout(btn_layout)

    def _crear_kpi_card(self, titulo, valor, color):
        card = QFrame()
        card.setStyleSheet("background:#fff; border:1px solid #d1d5db; border-radius:12px; padding:20px;")
        card.setMinimumHeight(140)
        v = QVBoxLayout(card)
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("font-size:16px; font-weight:bold; color:#475569;")
        lbl_val = QLabel(valor)
        lbl_val.setStyleSheet(f"font-size:36px; font-weight:800; color:{color};")
        v.addWidget(lbl_tit)
        v.addWidget(lbl_val)
        return card

    def _fmt(self, n):
        return f"{float(n):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _aplicar_filtros(self, movimientos):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco = self.cbo_banco.currentText()
        cuenta = self.cbo_cuenta.currentText().split(" – ")[0] if " – " in self.cbo_cuenta.currentText() else None
        categoria = self.cbo_categoria.currentText()
        tipo = self.cbo_tipo.currentText()
        texto = self.buscador.text().lower()

        filtrados = []
        for m in movimientos:
            try:
                _, m_mes, m_año = m.get("fecha", "").split("/")
                if int(m_mes) != mes or int(m_año) != año: continue
            except: continue
            if banco != "Todos" and m.get("banco", "") != banco: continue
            if cuenta and str(m.get("cuenta", "")) != cuenta: continue
            if categoria != "Todas" and self._categoria_de_cuenta(m.get("cuenta")) != categoria: continue
            if tipo == "Solo gastos" and float(m.get("debe", 0)) == 0: continue
            if tipo == "Solo ingresos" and float(m.get("haber", 0)) == 0: continue
            if texto:
                valores = [str(v).lower() for v in m.values()] + [self.data.obtener_nombre_cuenta(m.get("cuenta", "")).lower()]
                if not any(texto in v for v in valores): continue
            filtrados.append(m)
        return filtrados

    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)

        gasto = sum(float(m.get("debe", 0)) for m in filtrados)
        ingreso = sum(float(m.get("haber", 0)) for m in filtrados)
        saldo = ingreso - gasto

        self.card_gasto.layout().itemAt(1).widget().setText(self._fmt(gasto))
        self.card_ingreso.layout().itemAt(1).widget().setText(self._fmt(ingreso))
        self.card_saldo.layout().itemAt(1).widget().setText(self._fmt(saldo))
        color = "#16a34a" if saldo >= 0 else "#dc2626"
        self.card_saldo.layout().itemAt(1).widget().setStyleSheet(f"font-size:36px; font-weight:800; color:{color};")

        self.tabla.setRowCount(0)
        saldo_acum = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            cat = self._categoria_de_cuenta(m.get("cuenta"))
            color = QColor(self.COLORES.get(cat, "#ffffff"))
            fila = [
                m.get("fecha", ""),
                m.get("documento", ""),
                m.get("concepto", ""),
                str(m.get("cuenta", "")),
                self.data.obtener_nombre_cuenta(m.get("cuenta")),
                self._fmt(debe),
                self._fmt(haber),
                m.get("banco", ""),
                m.get("estado", ""),
                self._fmt(saldo_acum),
                cat
            ]
            self.tabla.insertRow(self.tabla.rowCount())
            for col, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setBackground(color)
                if col == 5 and debe > 0: item.setForeground(QColor("#dc2626"))
                if col == 6 and haber > 0: item.setForeground(QColor("#16a34a"))
                self.tabla.setItem(self.tabla.rowCount()-1, col, item)

        self._graficos(filtrados)
        self._detectar_anomalias(filtrados)

    def _graficos(self, movimientos):
        # Gráfico por categoría
        cats = ["FOOD","MEDICINE","HYGIENE","SALARY","ONLINE","THERAPEUTIC","DIET","OTROS"]
        valores = [sum(float(m.get("debe", 0)) for m in movimientos if self._categoria_de_cuenta(m.get("cuenta")) == c) for c in cats]
        set1 = QBarSet("Gastos")
        set1.append(valores)
        series = QBarSeries()
        series.append(set1)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Gastos por categoría")
        axis_x = QBarCategoryAxis()
        axis_x.append(cats)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        self.chart_categoria.setChart(chart)

        # Evolución 3 meses
        series_line = QLineSeries()
        series_line.setName("Saldo")
        for offset in range(-2, 1):
            m = self.mes_actual + offset
            a = self.año_actual
            if m <= 0: m, a = 12, a-1
            if m > 12: m, a = 1, a+1
            movs = self.data.movimientos_por_mes(m, a)
            saldo = sum(float(x.get("haber", 0)) - float(x.get("debe", 0)) for x in movs)
            series_line.append(offset, saldo)
        chart2 = QChart()
        chart2.addSeries(series_line)
        chart2.setTitle("Evolución Saldo (3 meses)")
        self.chart_evolucion.setChart(chart2)

    def _detectar_anomalias(self, movimientos):
        anomalias = []
        docs = [m.get("documento", "") for m in movimientos]
        duplicados = {x for x in docs if docs.count(x) > 1 and x}
        if duplicados: anomalias.append(f"Documentos duplicados: {', '.join(duplicados)}")
        for m in movimientos:
            if float(m.get("debe", 0)) == 0 and float(m.get("haber", 0)) == 0:
                anomalias.append(f"Movimiento sin importe: {m.get('documento')}")
            if m.get("estado", "").lower() == "pendiente":
                anomalias.append(f"Movimiento pendiente: {m.get('documento')}")
        self.anomalias.setText("\n".join(anomalias) if anomalias else "Ninguna anomalía detectada")

    def _generar_asientos_cierre(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)
        gastos = sum(float(m.get("debe", 0)) for m in filtrados if str(m.get("cuenta", "")).startswith(("6", "7")))
        ingresos = sum(float(m.get("haber", 0)) for m in filtrados if str(m.get("cuenta", "")).startswith(("7")))
        resultado = ingresos - gastos

        fecha = f"30/{mes:02d}/{año}"
        doc = f"CIERRE-{año}-{mes:02d}"

        # Asiento regularización
        if gastos > 0:
            self.data.agregar_movimiento(fecha, doc + "-REG", "Regularización gastos", "129000", gastos, 0, "INR", "Cierre", "pagado")
        if ingresos > 0:
            self.data.agregar_movimiento(fecha, doc + "-REG", "Regularización ingresos", "129000", 0, ingresos, "INR", "Cierre", "pagado")

        # Asiento cierre
        if resultado != 0:
            concepto = "Resultado positivo" if resultado > 0 else "Resultado negativo"
            self.data.agregar_movimiento(fecha, doc, f"Asiento de cierre - {concepto}", "129000", 0 if resultado > 0 else abs(resultado), abs(resultado) if resultado > 0 else 0, "INR", "Cierre", "pagado")

        QMessageBox.information(self, "Asientos generados", "Asientos de cierre creados correctamente.")
        self.actualizar()

    def _guardar_cierre(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)
        gasto = sum(float(m.get("debe", 0)) for m in filtrados)
        ingreso = sum(float(m.get("haber", 0)) for m in filtrados)
        saldo = ingreso - gasto

        cierre = {
            "mes": mes,
            "año": año,
            "total_gasto": gasto,
            "total_ingreso": ingreso,
            "saldo_final": saldo,
            "anomalías": self.anomalias.toPlainText().split("\n"),
            "resumen": "Cierre mensual generado automáticamente",
            "asientos_cierre": [],
            "bloqueado": False
        }

        os.makedirs(f"data/cierres/{año}", exist_ok=True)
        with open(f"data/cierres/{año}/{mes:02d}.json", "w", encoding="utf-8") as f:
            json.dump(cierre, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "Guardado", "Cierre mensual guardado correctamente.")

    def _bloquear_mes(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        os.makedirs(f"data/cierres/{año}", exist_ok=True)
        with open(f"data/cierres/{año}/{mes:02d}.lock", "w") as f:
            f.write("BLOQUEADO")
        QMessageBox.information(self, "Bloqueado", "Mes bloqueado correctamente.")

    def _desbloquear_mes(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        lock_path = f"data/cierres/{año}/{mes:02d}.lock"
        if os.path.exists(lock_path):
            os.remove(lock_path)
            QMessageBox.information(self, "Desbloqueado", "Mes desbloqueado.")
        else:
            QMessageBox.warning(self, "Error", "El mes no estaba bloqueado.")

    def vista_previa(self):
        html = self._generar_html()
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: QTextDocument().setHtml(html) or QTextDocument().print_(p))
        preview.exec()

    def imprimir(self):
        html = self._generar_html()
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print_(printer)

    def exportar_excel(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Cierre", f"Cierre_{self.cbo_mes.currentText()}_{self.cbo_año.currentText()}.xlsx", "Excel (*.xlsx)")
        if not ruta:
            return
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)
        datos = []
        saldo_acum = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            datos.append({
                "cuenta": str(m.get("cuenta", "")),
                "nombre_cuenta": self.data.obtener_nombre_cuenta(m.get("cuenta")),
                "fecha": m.get("fecha", ""),
                "concepto": m.get("concepto", ""),
                "debe": debe,
                "haber": haber,
                "saldo_acumulado": saldo_acum,
                "banco": m.get("banco", ""),
                "estado": m.get("estado", ""),
                "documento": m.get("documento", "")
            })
        try:
            from models.ExportadorExcelMensual import ExportadorExcelMensual
            ExportadorExcelMensual.exportar(ruta, datos)
            QMessageBox.information(self, "OK", "Exportado correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _generar_html(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)
        mes_str = self.cbo_mes.currentText()
        fecha_emision = datetime.date.today().strftime("%d/%m/%Y")

        html = f"""
        <html><head><style>
            body {{font-family: Arial; margin:40px;}}
            h1, h2 {{text-align:center;}}
            table {{width:100%; border-collapse:collapse; margin:30px 0;}}
            th {{background:#e0e7ff; padding:12px; border:2px solid #000;}}
            td {{padding:8px; border:1px solid #000;}}
            .num {{text-align:right;}}
            .total {{background:#FFF2CC; font-weight:bold;}}
        </style></head><body>
            <h1>CIERRE MENSUAL — SHILLONG CONTABILIDAD</h1>
            <h2>{mes_str} {año} — Fecha emisión: {fecha_emision}</h2>
            <table>
                <tr><th>Fecha</th><th>Documento</th><th>Concepto</th><th>Cuenta</th><th>Nombre</th><th>Debe</th><th>Haber</th><th>Banco</th><th>Estado</th><th>Saldo</th></tr>
        """
        saldo_acum = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            html += f"<tr><td>{m.get('fecha','')}</td><td>{m.get('documento','')}</td><td>{m.get('concepto','')}</td><td>{m.get('cuenta','')}</td><td>{self.data.obtener_nombre_cuenta(m.get('cuenta'))}</td><td class='num'>{debe:,.2f}</td><td class='num'>{haber:,.2f}</td><td>{m.get('banco','')}</td><td>{m.get('estado','')}</td><td class='num'>{saldo_acum:,.2f}</td></tr>"
        html += "</table></body></html>"
        return html