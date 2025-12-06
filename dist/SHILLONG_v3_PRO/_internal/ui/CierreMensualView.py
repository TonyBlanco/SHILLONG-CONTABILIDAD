# -*- coding: utf-8 -*-
"""
CierreMensualView — SHILLONG CONTABILIDAD v3.8 PRO
---------------------------------------------------------
Versión corregida con el FORMATO OFICIAL “LIBRO TEST”
para que la pantalla y el Excel coincidan EXACTAMENTE
con el libro mensual perfecto solicitado por las Hermanas.
---------------------------------------------------------
"""

import datetime
import json
from collections import defaultdict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QMenu, QHeaderView,
    QFrame, QFileDialog, QMessageBox, QInputDialog, QLineEdit
)
from PySide6.QtCore import Qt, QMarginsF
from PySide6.QtGui import QColor, QFont, QPainter, QTextDocument, QPageLayout
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis

try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None


class CierreMensualView(QWidget):

    # ---------------------------------------------------------
    # INIT
    # ---------------------------------------------------------
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year
        self._pwd = "menni1234"
        self._auth_ok = False

        self.bancos = self._cargar_bancos()
        self.cuentas = self._cargar_cuentas()
        self.reglas_cache = self._cargar_reglas()

        self._build_ui()
        self.actualizar()

    # ---------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------
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

    def _cargar_reglas(self):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {}

    def _pedir_password(self):
        pwd, ok = QInputDialog.getText(
            self,
            "Autorización requerida",
            "Ingrese la contraseña:",
            QLineEdit.Password
        )
        if not ok:
            return False
        if pwd.strip() == self._pwd:
            self._auth_ok = True
            return True
        QMessageBox.warning(self, "Acceso denegado", "Contraseña incorrecta.")
        return False

    def _asegurar_password(self):
        if self._auth_ok:
            return True
        return self._pedir_password()

    def _cargar_saldos_iniciales(self, año, mes):
        """Carga saldos iniciales desde saldos_mensuales.json para un mes/año."""
        ruta = "data/saldos_mensuales.json"
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            clave = f"{año}-{mes:02d}"
            return {
                banco: vals.get("inicial", 0.0)
                for banco, vals in data.get("saldos", {}).get(clave, {}).items()
            }
        except (IOError, json.JSONDecodeError, AttributeError):
            return {}

    def _pedir_password(self):
        """Solicita la contraseña y devuelve True si es correcta."""
        pwd, ok = QInputDialog.getText(
            self,
            "Autorización requerida",
            "Ingrese la contraseña para continuar:",
            QLineEdit.Password
        )
        if not ok:
            return False
        if pwd.strip() == self._pwd:
            self._auth_ok = True
            return True
        QMessageBox.warning(self, "Acceso denegado", "Contraseña incorrecta.")
        return False

    def _asegurar_password(self):
        if self._auth_ok:
            return True
        return self._pedir_password()

    # ---------------------------------------------------------
    # CATEGORÍAS
    # ---------------------------------------------------------
    def _categoria_de_cuenta(self, cuenta):
        cuenta_str = str(cuenta).split(" ")[0].strip()

        if cuenta_str in self.reglas_cache:
            cat = self.reglas_cache[cuenta_str].get("categoria", "").upper()

            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD",
                "ALIMENTACIÓN": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE",
                "MEDICINA": "MEDICINE",
                "MEDICAMENTOS": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE",
                "LIMPIEZA": "HYGIENE",
                "ASEO PERSONAL": "HYGIENE",
                "LAVANDERÍA": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY",
                "TELEFONÍA E INTERNET": "ONLINE",
                "INTERNET": "ONLINE",
                "TELEFONO": "ONLINE",
                "FORMACIÓN": "TRAINING"
            }
            return mapeo.get(cat, cat)

        # Rango contable genérico
        try:
            c = int(cuenta_str)
            if 603000 <= c <= 603999: return "FOOD"
            if 600000 <= c <= 609999: return "MEDICINE"
            if 602400 <= c <= 602499: return "HYGIENE"
            if 629200 <= c <= 629299: return "ONLINE"
        except (ValueError, TypeError):
            pass

        return "OTROS"

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # ------------------------
        # TÍTULO
        # ------------------------
        h = QHBoxLayout()
        tit = QLabel("📆 Cierre Mensual")
        tit.setStyleSheet("font-size: 28px; font-weight: 900; color: #0f172a;")
        h.addWidget(tit)
        h.addStretch()

        self.btn_auditar = QPushButton("🔎 Auditar mes")
        self.btn_auditar.setStyleSheet(
            "background-color: #0ea5e9; color: white; font-weight:bold; padding:8px 15px; border-radius:6px;"
        )
        self.btn_auditar.clicked.connect(self._auditar_mes)
        h.addWidget(self.btn_auditar)

        # Botón exportación
        self.btn_exportar_menu = QPushButton("📤 Exportar ▼")
        self.btn_exportar_menu.setStyleSheet(
            "background-color: #2563eb; color: white; font-weight:bold; padding:8px 15px; border-radius:6px;"
        )
        self.menu_exp = QMenu(self)
        self.menu_exp.addAction("📊 Excel General", self._exportar_excel_general)
        self.menu_exp.addAction("📂 Excel por Categorías", self._exportar_excel_categorias)
        self.menu_exp.addAction("🔢 Excel por Cuentas", self._exportar_excel_cuentas)
        self.menu_exp.addSeparator()
        self.menu_exp.addAction("📄 PDF Estándar", self._exportar_pdf_estandar)
        self.menu_exp.addAction("📘 PDF Oficial Azul", self._exportar_pdf_azul)
        self.btn_exportar_menu.setMenu(self.menu_exp)

        h.addWidget(self.btn_exportar_menu)
        layout.addLayout(h)

        # ------------------------
        # FILTROS
        # ------------------------
        filtros = QGridLayout()
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems([
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)

        self.cbo_año = QComboBox()
        for a in range(2020, 2036):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))

        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)

        self.cbo_cuenta = QComboBox()
        self.cbo_cuenta.addItems(self.cuentas)

        filtros.addWidget(QLabel("Mes:"), 0, 0)
        filtros.addWidget(self.cbo_mes, 0, 1)
        filtros.addWidget(QLabel("Año:"), 0, 2)
        filtros.addWidget(self.cbo_año, 0, 3)
        filtros.addWidget(QLabel("Banco:"), 1, 0)
        filtros.addWidget(self.cbo_banco, 1, 1)
        filtros.addWidget(QLabel("Cuenta:"), 1, 2)
        filtros.addWidget(self.cbo_cuenta, 1, 3)

        for w in [self.cbo_mes, self.cbo_año, self.cbo_banco, self.cbo_cuenta]:
            w.currentIndexChanged.connect(self.actualizar)

        layout.addLayout(filtros)

        # ------------------------
        # KPI
        # ------------------------
        kpi = QHBoxLayout()
        self.card_gasto = self._kpi("Gastos", "#dc2626")
        self.card_ingreso = self._kpi("Ingresos", "#16a34a")
        self.card_saldo = self._kpi("Saldo", "#2563eb")
        kpi.addWidget(self.card_gasto)
        kpi.addWidget(self.card_ingreso)
        kpi.addWidget(self.card_saldo)
        layout.addLayout(kpi)

        # ------------------------
        # TABLA — FORMATO OFICIAL
        # ------------------------
        self.tabla = QTableWidget(0, 10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Doc", "Concepto", "Cuenta", "Nombre", 
            "Debe", "Haber", "Banco", "Estado", "Saldo"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        # ------------------------
        # GRÁFICOS + ANOMALÍAS
        # ------------------------
        bot = QHBoxLayout()
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(250)
        bot.addWidget(self.chart_view, 2)

        anom = QFrame()
        av = QVBoxLayout(anom)
        av.addWidget(QLabel("⚠️ Anomalías:"))
        self.txt_anom = QTextEdit()
        self.txt_anom.setReadOnly(True)
        av.addWidget(self.txt_anom)
        bot.addWidget(anom, 1)

        layout.addLayout(bot)

    # ---------------------------------------------------------
    # KPI CARD
    # ---------------------------------------------------------
    def _kpi(self, t, c):
        f = QFrame()
        f.setStyleSheet(
            f"background:white; border:1px solid #ddd; "
            f"border-radius:10px; border-left:5px solid {c};"
        )
        v = QVBoxLayout(f)
        l1 = QLabel(t)
        l2 = QLabel("0.00")
        l2.setStyleSheet(
            f"font-size:24px; font-weight:bold; color:{c};"
        )
        l2.setObjectName("val")
        v.addWidget(l1)
        v.addWidget(l2)
        f.val = l2
        return f

    # ---------------------------------------------------------
    # ACTUALIZAR VISTA
    # ---------------------------------------------------------
    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco = self.cbo_banco.currentText()

        cta_filt = None
        if " – " in self.cbo_cuenta.currentText():
            cta_filt = self.cbo_cuenta.currentText().split(" – ")[0]

        movs = self.data.movimientos_por_mes(mes, año)
        self.filtrados = []

        for m in movs:
            if banco != "Todos" and m.get("banco") != banco:
                continue
            if cta_filt and str(m.get("cuenta")) != cta_filt:
                continue
            self.filtrados.append(m)

        gas = sum(float(m.get("debe", 0)) for m in self.filtrados)
        ing = sum(float(m.get("haber", 0)) for m in self.filtrados)

        self.card_gasto.val.setText(f"{gas:,.2f}")
        self.card_ingreso.val.setText(f"{ing:,.2f}")
        self.card_saldo.val.setText(f"{ing - gas:,.2f}")

        # TABLA
        self.tabla.setRowCount(0)
        saldo = 0

        for m in self.filtrados:
            d = float(m.get("debe", 0))
            h = float(m.get("haber", 0))
            saldo += h - d

            cuenta_id = str(m.get("cuenta", ""))
            nombre_cuenta = self.data.cuentas.get(cuenta_id, {}).get("nombre", "DESCONOCIDA")

            row = [
                m.get("fecha"),
                m.get("documento"),
                m.get("concepto"),
                m.get("cuenta"),
                nombre_cuenta,
                f"{d:,.2f}",
                f"{h:,.2f}",
                m.get("banco"),
                m.get("estado"),
                f"{saldo:,.2f}"
            ]

            r = self.tabla.rowCount()
            self.tabla.insertRow(r)

            for c, val in enumerate(row):
                it = QTableWidgetItem(str(val))
                
                # Ajustar alineación para las nuevas columnas numéricas
                if c in [5, 6, 9]:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if c == 5 and d > 0: it.setForeground(QColor("#dc2626"))
                    if c == 6 and h > 0: it.setForeground(QColor("#16a34a"))
                
                self.tabla.setItem(r, c, it)

        self._graficos(self.filtrados)

        # Anomalías
        anomalies = []
        docs = []
        for idx, m in enumerate(self.filtrados, 1):
            doc = str(m.get("documento", "")).strip()
            cuenta = str(m.get("cuenta", "")).strip()
            banco = str(m.get("banco", "")).strip()
            debe = float(m.get("debe", 0) or 0)
            haber = float(m.get("haber", 0) or 0)

            if doc and "SIN-DOC" not in doc:
                docs.append(doc)
            if not doc:
                anomalies.append(f"Fila {idx}: sin documento")
            if not cuenta:
                anomalies.append(f"Fila {idx}: sin cuenta")
            if not banco:
                anomalies.append(f"Fila {idx}: sin banco")
            if (debe > 0 and haber > 0) or (debe == 0 and haber == 0):
                anomalies.append(f"Fila {idx}: Debe/Haber inválidos (debe={debe}, haber={haber})")
            try:
                c_int = int(cuenta.split(" ")[0])
                if (600000 <= c_int <= 699999 or 200000 <= c_int <= 299999) and haber > 0 and debe == 0:
                    anomalies.append(f"Fila {idx}: posible gasto en Haber (cuenta {cuenta}, haber={haber})")
            except ValueError:
                pass

        if len(docs) != len(set(docs)):
            anomalies.append("Documentos duplicados detectados.")

        if anomalies:
            self.txt_anom.setText("\n".join(anomalies))
        else:
            self.txt_anom.setText("✅ Todo correcto.")

    # ---------------------------------------------------------
    # GRAFICOS
    # ---------------------------------------------------------
    def _graficos(self, movs):
        cats = defaultdict(float)
        for m in movs:
            if float(m.get("debe", 0)) > 0:
                cats[self._categoria_de_cuenta(m.get("cuenta"))] += float(m.get("debe", 0))

        if not cats:
            self.chart_view.setChart(QChart())
            return

        s = QBarSet("Gasto")
        c = []
        for k, v in cats.items():
            s.append(v)
            c.append(k)

        bs = QBarSeries()
        bs.append(s)
        ch = QChart()
        ch.addSeries(bs)
        ch.setTitle("Gastos por Categoría")
        ax = QBarCategoryAxis()
        ax.append(c)
        ch.addAxis(ax, Qt.AlignBottom)
        bs.attachAxis(ax)
        self.chart_view.setChart(ch)

    # ---------------------------------------------------------
    # PDF (sin cambios, separado del formato libro)
    # ---------------------------------------------------------
    def _exportar_pdf_estandar(self):
        if not self._asegurar_password():
            return
        self._render_pdf(azul=False)

    def _exportar_pdf_azul(self):
        if not self._asegurar_password():
            return
        self._render_pdf(azul=True)

    # ---------------------------------------------------------
    # EXPORTACIÓN EXCEL — FORMATO LIBRO TEST
    # ---------------------------------------------------------
    def _exportar_excel_general(self):
        if not self._asegurar_password():
            return
        self._exportar_excel_base("general")

    def _exportar_excel_categorias(self):
        if not self._asegurar_password():
            return
        self._exportar_excel_base("categoria")

    def _exportar_excel_cuentas(self):
        if not self._asegurar_password():
            return
        self._exportar_excel_base("cuenta")

    def _exportar_excel_base(self, modo):
        if not ExportadorExcelMensual:
            return

        nombres = {
            "general": "Cierre",
            "categoria": "PorCategorias",
            "cuenta": "PorCuentas"
        }
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Excel",
            f"{nombres[modo]}_{self.cbo_mes.currentText()}.xlsx",
            "Excel (*.xlsx)"
        )
        if not ruta:
            return

        prep = []
        saldo = 0

        # ORDEN OFICIAL
        for m in self.filtrados:
            d = float(m.get("debe", 0))
            h = float(m.get("haber", 0))
            saldo += h - d

            # FIX: Obtener nombre de cuenta de forma robusta
            cuenta_id = str(m.get("cuenta", ""))
            nombre_cuenta = self.data.cuentas.get(cuenta_id, {}).get("nombre", "DESCONOCIDA")

            it = {
                "fecha": m.get("fecha"),
                "cuenta": m.get("cuenta"),
                "categoria": self._categoria_de_cuenta(m.get("cuenta")),
                "concepto": m.get("concepto"),
                "debe": d,
                "haber": h,
                "saldo": saldo,
                "banco": m.get("banco"),
                "documento": m.get("documento")
            }

            prep.append(it)

        per = f"{self.cbo_mes.currentText()} {self.cbo_año.currentText()}"

        try:
            if modo == "general":
                ExportadorExcelMensual.exportar_general(ruta, prep, per)

            elif modo == "categoria":
                g = defaultdict(list)
                for x in prep:
                    g[x["categoria"]].append(x)
                ExportadorExcelMensual.exportar_agrupado(
                    ruta, dict(sorted(g.items())), per, "Categoría"
                )

            elif modo == "cuenta":
                g = defaultdict(list)
                for x in prep:
                    g[f"{x['cuenta']} - {x['categoria']}"].append(x)
                ExportadorExcelMensual.exportar_agrupado(
                    ruta, dict(sorted(g.items())), per, "Cuenta"
                )

            QMessageBox.information(self, "OK", "Excel exportado correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------------------------------------------------------
    # AUDITORÍA DEL MES
    # ---------------------------------------------------------
    def _auditar_mes(self):
        if not self._asegurar_password():
            return

        if not hasattr(self, "filtrados") or not self.filtrados:
            QMessageBox.information(self, "Auditoría", "No hay movimientos filtrados para auditar.")
            return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco_filtro = self.cbo_banco.currentText()

        saldos_init_map = self._cargar_saldos_iniciales(año, mes)
        saldo_inicial = sum(saldos_init_map.values()) if banco_filtro == "Todos" else saldos_init_map.get(banco_filtro, 0.0)

        total_debe = total_haber = 0.0
        anomalies = []

        for idx, m in enumerate(self.filtrados, 1):
            cuenta = str(m.get("cuenta", "")).strip()
            banco = m.get("banco", "").strip() or "SIN_BANCO"
            doc = m.get("documento", "").strip()
            try:
                debe = float(m.get("debe", 0) or 0)
                haber = float(m.get("haber", 0) or 0)
            except (ValueError, TypeError):
                debe = haber = 0.0

            total_debe += debe
            total_haber += haber

            if not cuenta:
                anomalies.append(f"Fila {idx}: sin cuenta")
            if not banco:
                anomalies.append(f"Fila {idx}: sin banco")
            if not doc:
                anomalies.append(f"Fila {idx}: sin documento")
            if (debe > 0 and haber > 0) or (debe == 0 and haber == 0):
                anomalies.append(f"Fila {idx}: Debe/Haber inválidos (debe={debe}, haber={haber})")

            try:
                c_int = int(cuenta.split(" ")[0])
                if (600000 <= c_int <= 699999 or 200000 <= c_int <= 299999) and haber > 0 and debe == 0:
                    anomalies.append(f"Fila {idx}: posible gasto en Haber (cuenta {cuenta}, haber={haber})")
            except ValueError:
                pass

        saldo_final_estimado = saldo_inicial + total_haber - total_debe
        resumen = [
            f"Total Debe: {total_debe:,.2f}",
            f"Total Haber: {total_haber:,.2f}",
            f"Saldo inicial: {saldo_inicial:,.2f}",
            f"Saldo final estimado: {saldo_final_estimado:,.2f}"
        ]

        if banco_filtro != "Todos" and banco_filtro not in saldos_init_map:
            anomalies.append(f"No hay saldo inicial definido para {banco_filtro} en {mes:02d}/{año}.")

        if anomalies:
            detalle = "\n".join(anomalies[:15])
            if len(anomalies) > 15:
                detalle += f"\n... ({len(anomalies)-15} más)"
            QMessageBox.warning(
                self,
                "Auditoría con observaciones",
                "\n".join(resumen + ["", "Anomalías:", detalle])
            )
        else:
            QMessageBox.information(
                self,
                "Auditoría completada",
                "\n".join(resumen + ["", "Sin anomalías detectadas."])
            )
