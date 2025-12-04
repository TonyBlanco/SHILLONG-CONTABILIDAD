# -*- coding: utf-8 -*-
"""
PendientesView — SHILLONG CONTABILIDAD v3 PRO
Vista profesional de movimientos pendientes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog

import datetime
import json

from models.ExportadorExcelMensual import ExportadorExcelMensual


class PendientesView(QWidget):

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
        except (IOError, json.JSONDecodeError, KeyError):
            return ["Todos", "Caja"]

    def _cargar_cuentas(self):
        cuentas = ["Todas"]
        try:
            with open("data/plan_contable_v3.json", "r", encoding="utf-8") as f:
                plan = json.load(f)
                cuentas.extend([f"{k} – {v['nombre']}" for k, v in plan.items()])
        except (IOError, json.JSONDecodeError, KeyError):
            pass
        return cuentas

    def _categoria_de_cuenta(self, cuenta):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                reglas = json.load(f)
        except (IOError, json.JSONDecodeError):
            reglas = {}

        cuenta_str = str(cuenta).strip()

        if cuenta_str in reglas:
            cat = reglas[cuenta_str].get("categoria", "").upper()
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE",
                "LAVANDERÍA": "HYGIENE",
                "ASEO PERSONAL": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY",
                "TELEFONÍA E INTERNET": "ONLINE"
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
        except (ValueError, TypeError):
            pass

        return "OTROS"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("PENDIENTES — MOVIMIENTOS SIN PAGAR")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        layout.addWidget(titulo)

        filtros = QHBoxLayout()

        filtros.addWidget(QLabel("Mes:"))
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems(["Todos", "Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        self.cbo_mes.setCurrentIndex(self.mes_actual)
        filtros.addWidget(self.cbo_mes)

        filtros.addWidget(QLabel("Año:"))
        self.cbo_año = QComboBox()
        for a in range(2020, 2036):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        filtros.addWidget(self.cbo_año)

        filtros.addWidget(QLabel("Banco:"))
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)
        filtros.addWidget(self.cbo_banco)

        filtros.addWidget(QLabel("Cuenta:"))
        self.cbo_cuenta = QComboBox()
        self.cbo_cuenta.addItems(self.cuentas)
        filtros.addWidget(self.cbo_cuenta)

        filtros.addWidget(QLabel("Categoría:"))
        self.cbo_categoria = QComboBox()
        self.cbo_categoria.addItems(["Todas","FOOD","MEDICINE","HYGIENE","SALARY","ONLINE","THERAPEUTIC","DIET","OTROS"])
        filtros.addWidget(self.cbo_categoria)

        filtros.addWidget(QLabel("Tipo:"))
        self.cbo_tipo = QComboBox()
        self.cbo_tipo.addItems(["Todos","Solo gastos","Solo ingresos"])
        filtros.addWidget(self.cbo_tipo)

        filtros.addStretch()

        # Conectar filtros
        for w in [self.cbo_mes, self.cbo_año, self.cbo_banco,
                  self.cbo_cuenta, self.cbo_categoria, self.cbo_tipo]:
            w.currentIndexChanged.connect(self.actualizar)

        btn_marcar = QPushButton("Marcar como pagado")
        btn_marcar.clicked.connect(self._marcar_pagado)

        btn_refresh = QPushButton("Refrescar lista")
        btn_refresh.clicked.connect(self.actualizar)

        btn_preview = QPushButton("Vista previa PDF")
        btn_preview.clicked.connect(self.vista_previa)

        btn_print = QPushButton("Imprimir PDF")
        btn_print.clicked.connect(self.imprimir)

        btn_export = QPushButton("Exportar Excel")
        btn_export.clicked.connect(self.exportar_excel)

        for b in [btn_marcar, btn_refresh, btn_preview, btn_print, btn_export]:
            filtros.addWidget(b)

        layout.addLayout(filtros)

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar en pendientes...")
        self.buscador.textChanged.connect(self.actualizar)
        layout.addWidget(self.buscador)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha","Documento","Concepto","Cuenta","Nombre Cuenta",
            "Debe","Haber","Banco","Estado","Saldo Acum."
        ])
        layout.addWidget(self.tabla)

        # Totales
        self.lbl_totales = QLabel()
        self.lbl_totales.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1e293b; padding: 15px;"
            "background: #e0e7ff; border-radius: 12px;"
        )
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_totales)

    def _fmt(self, n):
        return f"{float(n):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _aplicar_filtros(self, movimientos):

        mes = self.cbo_mes.currentIndex()
        año = self.cbo_año.currentText()
        banco = self.cbo_banco.currentText()
        cuenta_txt = self.cbo_cuenta.currentText()
        cuenta = cuenta_txt.split(" – ")[0] if " – " in cuenta_txt else None
        categoria = self.cbo_categoria.currentText()
        tipo = self.cbo_tipo.currentText()
        texto = self.buscador.text().lower()

        filtrados = []

        for m in movimientos:
            if m.get("estado", "").lower() != "pendiente":
                continue

            if mes > 0:
                try:
                    _, mm, _ = m.get("fecha", "").split("/")
                    if int(mm) != mes:
                        continue
                except (ValueError, AttributeError):
                    continue

            if año != "Todos" and not m.get("fecha", "").endswith(año):
                continue

            if banco != "Todos" and m.get("banco", "") != banco:
                continue

            if cuenta and str(m.get("cuenta", "")) != cuenta:
                continue

            if categoria != "Todas" and self._categoria_de_cuenta(m.get("cuenta")) != categoria:
                continue

            if tipo == "Solo gastos" and float(m.get("debe", 0)) == 0:
                continue

            if tipo == "Solo ingresos" and float(m.get("haber", 0)) == 0:
                continue

            if texto:
                valores = [str(v).lower() for v in m.values()]
                nombre = self.data.obtener_nombre_cuenta(m.get("cuenta", "")).lower()
                if texto not in nombre and not any(texto in v for v in valores):
                    continue

            filtrados.append(m)

        return filtrados

    def actualizar(self):
        pendientes = [m for m in self.data.movimientos if m.get("estado", "").lower() == "pendiente"]
        filtrados = self._aplicar_filtros(pendientes)

        # ORDENAR POR FECHA DESCENDENTE
        def fecha_key(m):
            try:
                d, mm, a = m.get("fecha", "01/01/1900").split("/")
                return datetime.datetime(int(a), int(mm), int(d))
            except (ValueError, AttributeError):
                return datetime.datetime(1900, 1, 1)

        filtrados.sort(key=fecha_key, reverse=True)
        self.filtrados_actuales = filtrados

        self.tabla.setRowCount(0)
        saldo_acum = total_debe = total_haber = 0

        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))

            saldo_acum += haber - debe
            total_debe += debe
            total_haber += haber

            # Días transcurridos
            try:
                d, mm, a = m.get("fecha", "").split("/")
                fecha_mov = datetime.datetime(int(a), int(mm), int(d))
                dias = (self.hoy - fecha_mov.date()).days
            except (ValueError, AttributeError):
                dias = 999

            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)

            items = [
                m.get("fecha", ""),
                m.get("documento", ""),
                m.get("concepto", ""),
                str(m.get("cuenta", "")),
                self.data.obtener_nombre_cuenta(m.get("cuenta")),
                self._fmt(debe),
                self._fmt(haber),
                m.get("banco", "Caja"),
                m.get("estado", ""),
                self._fmt(saldo_acum)
            ]

            for col, val in enumerate(items):
                item = QTableWidgetItem(val)

                if dias > 30:
                    item.setBackground(QColor("#fee2e2"))  # rojo suave vencido
                else:
                    item.setBackground(QColor("#fef9c3"))  # amarillo suave

                if col == 5 and debe > 0:
                    item.setForeground(QColor("#dc2626"))

                if col == 6 and haber > 0:
                    item.setForeground(QColor("#16a34a"))

                self.tabla.setItem(fila, col, item)

        self.lbl_totales.setText(
            f"TOTAL PENDIENTE (DEBE): {self._fmt(total_debe)}   |   "
            f"TOTAL PENDIENTE (HABER): {self._fmt(total_haber)}   |   "
            f"SALDO PENDIENTE: {self._fmt(total_haber - total_debe)}"
        )

    def _marcar_pagado(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Seleccionar", "Seleccione un movimiento pendiente.")
            return

        mov = self.filtrados_actuales[row]

        mov["estado"] = "pagado"
        self.data.guardar()

        QMessageBox.information(self, "Actualizado", "Movimiento marcado como pagado.")
        self.actualizar()

    def _generar_html(self):
        filtrados = self.filtrados_actuales

        mes_str = self.cbo_mes.currentText()
        año = self.cbo_año.currentText()

        html = """
        <html><head><style>
            body {font-family: Arial; margin:40px;}
            h1 {text-align:center; font-size:24px;}
            table {width:100%; border-collapse:collapse; margin:20px 0;}
            th {background:#e5e7eb; padding:12px; text-align:center; border:2px solid #000;}
            td {padding:8px; border:1px solid #000;}
            .num {text-align:right;}
            .total {background:#FFF2CC; font-weight:bold;}
        </style></head><body>
        """

        html += f"<h1>PENDIENTES — {mes_str} {año}</h1>"
        html += "<table><tr><th>Fecha</th><th>Documento</th><th>Concepto</th><th>Cuenta</th><th>Nombre Cuenta</th><th>Debe</th><th>Haber</th><th>Banco</th><th>Estado</th><th>Saldo</th></tr>"

        saldo_acum = total_debe = total_haber = 0

        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))

            saldo_acum += haber - debe
            total_debe += debe
            total_haber += haber

            html += f"""
            <tr>
                <td>{m.get('fecha','')}</td>
                <td>{m.get('documento','')}</td>
                <td>{m.get('concepto','')}</td>
                <td>{m.get('cuenta','')}</td>
                <td>{self.data.obtener_nombre_cuenta(m.get('cuenta'))}</td>
                <td class='num'>{debe:,.2f}</td>
                <td class='num'>{haber:,.2f}</td>
                <td>{m.get('banco','')}</td>
                <td>{m.get('estado','')}</td>
                <td class='num'>{saldo_acum:,.2f}</td>
            </tr>
            """

        html += "</table></body></html>"
        return html

    def vista_previa(self):
        html = self._generar_html()
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: QTextDocument(html).print_(p))
        preview.exec()

    def imprimir(self):
        html = self._generar_html()
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec():
            QTextDocument(html).print_(printer)

    def exportar_excel(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Pendientes", "Pendientes.xlsx", "Excel (*.xlsx)")

        if not ruta:
            return

        datos = []
        saldo_acum = 0

        for m in self.filtrados_actuales:
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
            ExportadorExcelMensual.exportar(ruta, datos)
            QMessageBox.information(self, "OK", "Exportado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
