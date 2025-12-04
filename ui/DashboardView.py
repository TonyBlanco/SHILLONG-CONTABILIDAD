# -*- coding: utf-8 -*-
"""
DashboardView.py — SHILLONG CONTABILIDAD v3.7.8 PRO
✅ AUTO-REFRESH cada 5 segundos
✅ BOTÓN DEPURAR integrado
✅ Totales anuales en tarjetas
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QScrollArea, QPushButton, QComboBox, QListWidget, 
    QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet, 
    QBarCategoryAxis, QValueAxis
)

import datetime
from collections import defaultdict
from pathlib import Path
import json
import os

print(">>> DASHBOARD CARGADO DESDE:", __file__)


class DashboardView(QWidget):
    navegar_a = Signal(str)

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.año_sistema = datetime.date.today().year
        self.reglas_cache = self._cargar_reglas()
        
        # 🔥 NUEVO: Timer para auto-refresh
        self.timer_auto_refresh = QTimer(self)
        self.timer_auto_refresh.timeout.connect(self._auto_actualizar)
        
        self._build_ui()
        self.actualizar_datos()
        
        # 🔥 Iniciar auto-refresh cada 5 segundos
        self.timer_auto_refresh.start(5000)

    def showEvent(self, event):
        self.actualizar_datos()
        # Reactivar timer al mostrar
        if not self.timer_auto_refresh.isActive():
            self.timer_auto_refresh.start(5000)
        super().showEvent(event)

    def hideEvent(self, event):
        # Pausar timer al ocultar (opcional, para ahorrar recursos)
        self.timer_auto_refresh.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.timer_auto_refresh.stop()
        super().closeEvent(event)

    def _cargar_reglas(self):
        try:
            if os.path.exists("data/reglas_conceptos.json"):
                with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"[DashboardView] Error cargando reglas: {e}")
        return {}

    def _categoria_de_cuenta(self, cuenta):
        cuenta_str = str(cuenta).split(" ")[0].strip()
        if cuenta_str in self.reglas_cache:
            cat = self.reglas_cache[cuenta_str].get("categoria", "").upper()
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD", "ALIMENTACIÓN": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE", "FARMACIA": "MEDICINE",
                "MEDICAMENTOS": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE", "LIMPIEZA": "HYGIENE", 
                "LAVANDERÍA": "HYGIENE", "HIGIENE": "HYGIENE", "ASEO PERSONAL": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY", "NOMINAS": "SALARY",
                "TELEFONÍA E INTERNET": "ONLINE", "INTERNET": "ONLINE", 
                "TELEFONO": "ONLINE", "TERAPIAS": "THERAPEUTIC", "DIETA": "DIET"
            }
            if cat in mapeo: return mapeo[cat]
            return "OTROS"
        return "OTROS"

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #f8fafc;")
        
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # HEADER
        header_row = QHBoxLayout()
        v_tit = QVBoxLayout()
        self.lbl_titulo = QLabel("Panel de Control")
        self.lbl_titulo.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b;")
        
        h_ano = QHBoxLayout()
        h_ano.addWidget(QLabel("Ejercicio Fiscal:"))
        self.cbo_año = QComboBox()
        self.cbo_año.setStyleSheet("background: white; border-radius: 5px; padding: 5px; font-weight: bold;")
        for a in range(2020, 2031): self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_sistema))
        self.cbo_año.currentTextChanged.connect(self.actualizar_datos)
        h_ano.addWidget(self.cbo_año)
        h_ano.addStretch()
        
        v_tit.addWidget(self.lbl_titulo)
        v_tit.addLayout(h_ano)
        header_row.addLayout(v_tit)
        header_row.addStretch()

        btn_style = """
            QPushButton { 
                background: white; 
                border: 1px solid #cbd5e1; 
                border-radius: 8px; 
                padding: 8px 15px; 
                font-weight: bold; 
                color: #475569; 
            }
            QPushButton:hover { 
                background: #eff6ff; 
                border-color: #3b82f6; 
                color: #1d4ed8; 
            }
        """
        
        # 🔥 NUEVO: Botón Depurar
        self.btn_depurar = QPushButton("🔧 Depurar")
        self.btn_depurar.setStyleSheet("""
            QPushButton { 
                background: #fef2f2; 
                border: 1px solid #fecaca; 
                border-radius: 8px; 
                padding: 8px 15px; 
                font-weight: bold; 
                color: #dc2626; 
            }
            QPushButton:hover { 
                background: #fee2e2; 
                border-color: #ef4444; 
            }
        """)
        self.btn_depurar.clicked.connect(self._depurar_datos)
        
        self.btn_new = QPushButton("＋ Registrar")
        self.btn_new.setStyleSheet(btn_style)
        self.btn_new.clicked.connect(lambda: self.navegar_a.emit("registrar"))
        
        self.btn_conciliar = QPushButton("🏦 Conciliar")
        self.btn_conciliar.setStyleSheet(btn_style)
        self.btn_conciliar.clicked.connect(lambda: self.navegar_a.emit("tools"))

        header_row.addWidget(self.btn_depurar)  # 🔥 NUEVO
        header_row.addWidget(self.btn_new)
        header_row.addWidget(self.btn_conciliar)
        
        self.layout.addLayout(header_row)

        # 🔥 NUEVO: Indicador de Auto-Refresh
        self.lbl_status = QLabel("🟢 Auto-actualización activa")
        self.lbl_status.setStyleSheet(
            "color: #10b981; font-size: 11px; padding: 5px; "
            "background: #f0fdf4; border-radius: 5px; border: 1px solid #bbf7d0;"
        )
        self.layout.addWidget(self.lbl_status)

        # KPIs (Tarjetas Superiores)
        self.kpi_layout = QHBoxLayout()
        self.card_ingreso = self._crear_kpi_card("Ingresos (Año)", "#10b981", "⬆")
        self.card_gasto = self._crear_kpi_card("Gastos (Año)", "#ef4444", "⬇")
        self.card_neto = self._crear_kpi_card("Resultado Anual", "#3b82f6", "∑")
        self.card_proyeccion = self._crear_kpi_card("Proyección (30d)", "#8b5cf6", "🔮")
        
        self.kpi_layout.addWidget(self.card_ingreso)
        self.kpi_layout.addWidget(self.card_gasto)
        self.kpi_layout.addWidget(self.card_neto)
        self.kpi_layout.addWidget(self.card_proyeccion)
        self.layout.addLayout(self.kpi_layout)

        # ZONA CENTRAL
        mid_layout = QHBoxLayout()
        
        # Alertas
        alertas_frame = QFrame()
        alertas_frame.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        alertas_vbox = QVBoxLayout(alertas_frame)
        lbl_alerta = QLabel("🔔 Pendientes & Alertas")
        lbl_alerta.setStyleSheet("font-size: 16px; font-weight: bold; color: #334155;")
        alertas_vbox.addWidget(lbl_alerta)
        self.lista_alertas = QListWidget()
        self.lista_alertas.setStyleSheet("border: none; background: transparent;")
        alertas_vbox.addWidget(self.lista_alertas)
        mid_layout.addWidget(alertas_frame, 2)

        # Bancos
        bancos_frame = QFrame()
        bancos_frame.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        bancos_vbox = QVBoxLayout(bancos_frame)
        lbl_banco = QLabel("💰 Tesorería (Saldo Real)")
        lbl_banco.setStyleSheet("font-size: 16px; font-weight: bold; color: #334155;")
        bancos_vbox.addWidget(lbl_banco)
        self.grid_bancos = QGridLayout()
        bancos_vbox.addLayout(self.grid_bancos)
        bancos_vbox.addStretch()
        mid_layout.addWidget(bancos_frame, 3)
        self.layout.addLayout(mid_layout)

        # GRÁFICOS
        graficos_layout = QHBoxLayout()
        self.chart_barras = self._crear_chart_barras()
        view_barras = QChartView(self.chart_barras)
        view_barras.setRenderHint(QPainter.Antialiasing)
        view_barras.setMinimumHeight(300)
        view_barras.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        graficos_layout.addWidget(view_barras, 2)

        self.chart_pie = self._crear_chart_pie()
        view_pie = QChartView(self.chart_pie)
        view_pie.setRenderHint(QPainter.Antialiasing)
        view_pie.setMinimumHeight(300)
        view_pie.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
        graficos_layout.addWidget(view_pie, 1)

        self.layout.addLayout(graficos_layout)
        self.layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    # 🔥 NUEVO: Auto-actualización silenciosa
    def _auto_actualizar(self):
        """Actualización automática cada 5 segundos."""
        try:
            # Recargar datos desde el archivo
            self.data.cargar_datos()
            
            # Actualizar vista
            self.actualizar_datos()
            
            # Actualizar timestamp
            ahora = datetime.datetime.now().strftime("%H:%M:%S")
            self.lbl_status.setText(f"🟢 Actualizado: {ahora}")
            self.lbl_status.setStyleSheet(
                "color: #10b981; font-size: 11px; padding: 5px; "
                "background: #f0fdf4; border-radius: 5px; border: 1px solid #bbf7d0;"
            )
        except Exception as e:
            self.lbl_status.setText(f"🔴 Error: {str(e)[:30]}...")
            self.lbl_status.setStyleSheet(
                "color: #dc2626; font-size: 11px; padding: 5px; "
                "background: #fef2f2; border-radius: 5px; border: 1px solid #fecaca;"
            )

    # 🔥 NUEVO: Depuración integrada
    def _depurar_datos(self):
        """Ejecuta la depuración automática de DEBE/HABER."""
        respuesta = QMessageBox.question(
            self,
            "Depurar Datos",
            "¿Desea ejecutar la depuración automática?\n\n"
            "Esto corregirá automáticamente:\n"
            "• Gastos registrados en HABER (deberían estar en DEBE)\n"
            "• Inversiones registradas en HABER (deberían estar en DEBE)\n\n"
            "Los datos se guardarán automáticamente.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta != QMessageBox.Yes:
            return

        try:
            corregidos = self._ejecutar_depuracion()
            
            if corregidos > 0:
                # Recargar datos
                self.data.cargar_datos()
                self.actualizar_datos()
                
                QMessageBox.information(
                    self,
                    "✅ Depuración Completada",
                    f"Se han corregido {corregidos} movimiento(s).\n\n"
                    "Los datos se han actualizado correctamente."
                )
            else:
                QMessageBox.information(
                    self,
                    "✅ Sin Errores",
                    "No se encontraron movimientos con errores DEBE/HABER.\n\n"
                    "Todos los registros están correctos."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error durante la depuración:\n{str(e)}"
            )

    def _ejecutar_depuracion(self):
        """Lógica de depuración (basada en fix_data.py)."""
        archivo = Path("data/shillong_2026.json")
        
        if not archivo.exists():
            raise FileNotFoundError(f"No se encuentra el archivo: {archivo}")

        # Cargar datos
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)

        movimientos = data.get("movimientos", [])
        corregidos = 0

        # Recorrer y corregir
        for m in movimientos:
            cuenta = str(m.get("cuenta", ""))
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))

            # CRITERIO: Cuentas de Gasto (6...) o Inversión (2...) 
            # con HABER > 0 y DEBE = 0 están MAL
            if (cuenta.startswith("6") or cuenta.startswith("2")) and haber > 0 and debe == 0:
                # Corregir: mover de HABER a DEBE
                m["debe"] = haber
                m["haber"] = 0.0
                m["saldo"] = -haber
                corregidos += 1

        # Guardar si hubo cambios
        if corregidos > 0:
            data["fecha_guardado"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        return corregidos

    def actualizar_datos(self):
        try:
            año = int(self.cbo_año.currentText())
        except (ValueError, TypeError):
            año = self.año_sistema
        
        self.lbl_titulo.setText(f"Panel de Control {año}")
        
        hoy = QDate.currentDate()
        
        t_ing_anual, t_gas_anual = 0, 0
        ing_meses, gas_meses = [0]*12, [0]*12
        cats_anual = defaultdict(float)
        pendientes_proyeccion = 0
        alertas = []
        
        saldos = {b: 0.0 for b in self._obtener_bancos()}

        for m in self.data.movimientos:
            f_raw = str(m.get("fecha",""))
            try:
                if "/" in f_raw:
                    d, mm, a = map(int, f_raw.split("/"))
                elif "-" in f_raw:
                    p = f_raw.split("-")
                    a, mm, d = (int(p[0]), int(p[1]), int(p[2])) if len(p[0]) == 4 else (int(p[2]), int(p[1]), int(p[0]))
                else:
                    continue
                fecha_obj = QDate(a, mm, d)
            except (ValueError, IndexError):
                continue

            try:
                h = float(str(m.get("haber", 0)).replace(",", "."))
                d_val = float(str(m.get("debe", 0)).replace(",", "."))
            except (ValueError, TypeError):
                h, d_val = 0, 0
            
            banco = m.get("banco", "Caja")
            estado = str(m.get("estado","")).lower()

            # 1. Saldos Bancos (Histórico completo, solo pagados)
            if banco in saldos and estado == "pagado":
                saldos[banco] += (h - d_val)

            # 2. Datos del AÑO SELECCIONADO (KPIs y Gráficos)
            if a == año:
                # Sumamos para KPIs Anuales
                t_ing_anual += h
                t_gas_anual += d_val
                
                # Desglose mensual para gráfico
                if 1 <= mm <= 12:
                    ing_meses[mm-1] += h
                    gas_meses[mm-1] += d_val
                
                # Categorías anuales
                if d_val > 0:
                    cat = self._categoria_de_cuenta(m.get("cuenta"))
                    cats_anual[cat] += d_val

            # 3. Proyección (Pendientes futuros cercanos)
            if estado == "pendiente":
                dias_diff = hoy.daysTo(fecha_obj)
                if 0 <= dias_diff <= 30:
                    pendientes_proyeccion += (h - d_val)
                
                if dias_diff < 0:
                    alertas.append(f"⚠️ VENCIDA ({abs(dias_diff)}d): {m.get('concepto')}")
                elif dias_diff <= 7:
                    alertas.append(f"⏰ Vence pronto ({dias_diff}d): {m.get('concepto')}")

        # Actualizar KPIs
        self._update_kpi(self.card_ingreso, t_ing_anual)
        self._update_kpi(self.card_gasto, t_gas_anual)
        self._update_kpi(self.card_neto, t_ing_anual - t_gas_anual)
        
        lbl_proy = self.card_proyeccion.findChild(QLabel, "val")
        lbl_proy.setText(f"{pendientes_proyeccion:+,.2f}")
        lbl_proy.setStyleSheet(f"font-size:26px; font-weight:800; color:{'#10b981' if pendientes_proyeccion>=0 else '#ef4444'};")

        self._update_bancos(saldos)
        self._update_alertas(alertas)
        self._update_chart_barras(ing_meses, gas_meses)
        self._update_chart_pie(cats_anual)

    def _crear_kpi_card(self, tit, col, icon):
        card = QFrame()
        card.setStyleSheet(f"background:white; border-radius:12px; border:1px solid #e2e8f0; border-bottom: 4px solid {col};")
        card.setMinimumHeight(110)
        l = QVBoxLayout(card)
        top = QHBoxLayout()
        lbl_t = QLabel(tit)
        lbl_t.setStyleSheet("color:#64748b; font-weight:bold; font-size:13px;")
        lbl_i = QLabel(icon)
        lbl_i.setStyleSheet(f"color:{col}; font-size:18px; font-weight:bold;")
        top.addWidget(lbl_t)
        top.addStretch()
        top.addWidget(lbl_i)
        lbl_val = QLabel("0.00")
        lbl_val.setObjectName("val")
        lbl_val.setStyleSheet(f"font-size:26px; font-weight:800; color:#1e293b;")
        l.addLayout(top)
        l.addWidget(lbl_val)
        return card

    def _update_kpi(self, card, val):
        card.findChild(QLabel, "val").setText(f"{val:,.2f}")

    def _update_bancos(self, saldos):
        while self.grid_bancos.count():
            it = self.grid_bancos.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        r, c = 0, 0
        for b, s in saldos.items():
            f = QFrame()
            f.setStyleSheet("background:#f8fafc; border-radius:8px; padding:10px; border:1px solid #e2e8f0;")
            l = QVBoxLayout(f)
            l.setSpacing(2); l.setContentsMargins(10,10,10,10)
            l.addWidget(QLabel(b, styleSheet="font-size:12px; color:#64748b; font-weight:600;"))
            lbl_s = QLabel(f"{s:,.2f}")
            color = "#10b981" if s >= 0 else "#ef4444"
            lbl_s.setStyleSheet(f"font-size:16px; font-weight:bold; color:{color};")
            l.addWidget(lbl_s)
            self.grid_bancos.addWidget(f, r, c)
            c+=1
            if c>1: c,r = 0,r+1

    def _update_alertas(self, alertas):
        self.lista_alertas.clear()
        if not alertas:
            item = QListWidgetItem("✅ Todo al día.")
            item.setForeground(QColor("#10b981"))
            self.lista_alertas.addItem(item)
            return
        for a in alertas:
            item = QListWidgetItem(a)
            if "VENCIDA" in a: item.setForeground(QColor("#ef4444")); item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            else: item.setForeground(QColor("#f59e0b"))
            self.lista_alertas.addItem(item)

    def _crear_chart_barras(self):
        c = QChart()
        c.setTitle("Evolución Anual")
        c.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
        c.setAnimationOptions(QChart.SeriesAnimations)
        c.legend().setAlignment(Qt.AlignBottom)
        return c

    def _update_chart_barras(self, i, g):
        self.chart_barras.removeAllSeries()
        si = QBarSet("Ingresos"); si.append(i); si.setColor(QColor("#10b981"))
        sg = QBarSet("Gastos"); sg.append(g); sg.setColor(QColor("#ef4444"))
        s = QBarSeries(); s.append(si); s.append(sg)
        self.chart_barras.addSeries(s)
        
        cats = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        ax = QBarCategoryAxis(); ax.append(cats)
        for x in self.chart_barras.axes(): self.chart_barras.removeAxis(x)
        self.chart_barras.addAxis(ax, Qt.AlignBottom); s.attachAxis(ax)
        ay = QValueAxis(); self.chart_barras.addAxis(ay, Qt.AlignLeft); s.attachAxis(ay)

    def _crear_chart_pie(self):
        c = QChart()
        c.setTitle("Gastos por Categoría (Año)")
        c.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
        c.setAnimationOptions(QChart.SeriesAnimations)
        c.legend().setAlignment(Qt.AlignRight)
        return c

    def _update_chart_pie(self, cats):
        self.chart_pie.removeAllSeries()
        s = QPieSeries(); s.setHoleSize(0.40)
        sorted_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:5]
        cols = ["#3b82f6", "#ef4444", "#f59e0b", "#10b981", "#8b5cf6", "#64748b"]
        for idx, (k, v) in enumerate(sorted_cats):
            sl = s.append(k, v); sl.setLabel(k); sl.setLabelVisible(True); sl.setColor(QColor(cols[idx%len(cols)]))
        if not sorted_cats: s.append("Sin datos", 1)
        self.chart_pie.addSeries(s)

    def _obtener_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return [b["nombre"] for b in json.load(f).get("banks", [])]
        except (IOError, json.JSONDecodeError, KeyError):
            return ["Caja"]