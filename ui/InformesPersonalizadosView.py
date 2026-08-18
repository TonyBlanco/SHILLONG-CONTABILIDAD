# -*- coding: utf-8 -*-
"""
InformesPersonalizadosView.py — SHILLONG CONTABILIDAD v3.8.3 PRO
Generador de Informes Personalizados con filtros dinámicos
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDateEdit, QComboBox,
    QCheckBox, QGroupBox, QScrollArea, QLineEdit, QFileDialog,
    QMessageBox, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, QDate
import datetime
import json


class InformesPersonalizadosView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Título
        titulo = QLabel("📊 GENERADOR DE INFORMES PERSONALIZADOS")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b;")
        layout.addWidget(titulo)

        # Contenedor principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        contenedor = QWidget()
        contenedor_layout = QVBoxLayout(contenedor)

        # Panel de columnas
        columnas_box = self._crear_panel_columnas()
        contenedor_layout.addWidget(columnas_box)

        # Panel de filtros
        filtros_box = self._crear_panel_filtros()
        contenedor_layout.addWidget(filtros_box)

        scroll.setWidget(contenedor)
        layout.addWidget(scroll, 1)

        # Botones de acción
        botones_layout = QHBoxLayout()

        self.btn_generar = QPushButton("🔍 Generar Reporte")
        self.btn_generar.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: white; padding: 12px 24px;
                font-weight: bold; font-size: 14px; border-radius: 8px;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_generar.clicked.connect(self._generar_reporte)

        self.btn_exportar = QPushButton("📄 Exportar a Excel")
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background: #7030A0; color: white; padding: 12px 24px;
                font-weight: bold; font-size: 14px; border-radius: 8px;
            }
            QPushButton:hover { background: #5a2580; }
        """)
        self.btn_exportar.clicked.connect(self._exportar_excel)
        self.btn_exportar.setEnabled(False)

        self.btn_limpiar = QPushButton("🔄 Limpiar Filtros")
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                background: #64748b; color: white; padding: 12px 24px;
                font-weight: bold; font-size: 14px; border-radius: 8px;
            }
            QPushButton:hover { background: #475569; }
        """)
        self.btn_limpiar.clicked.connect(self._limpiar_filtros)

        botones_layout.addWidget(self.btn_generar)
        botones_layout.addWidget(self.btn_exportar)
        botones_layout.addWidget(self.btn_limpiar)
        botones_layout.addStretch()

        layout.addLayout(botones_layout)

        # Herramientas de estilo/exportación (como Libro Mensual)
        opciones_layout = QHBoxLayout()
        self.chk_export_invertido = QCheckBox("Exportar con columnas invertidas (ShillongStyle)")
        self.chk_estilo_shillong = QCheckBox("Estilo SHILLONG (Invertir Columnas: Entra=Debe, Sale=Haber)")
        self.chk_estilo_shillong.stateChanged.connect(self._on_estilo_shillong_changed)
        opciones_layout.addWidget(self.chk_export_invertido)
        opciones_layout.addWidget(self.chk_estilo_shillong)
        opciones_layout.addStretch()
        layout.addLayout(opciones_layout)

        # Tabla de resultados
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.setStyleSheet("""
            QTableWidget { font-size: 13px; gridline-color: #e2e8f0; }
            QHeaderView::section {
                background: #f8fafc; padding: 8px;
                font-weight: bold; border: none;
            }
        """)
        layout.addWidget(self.tabla_resultados, 2)

        # Label de totales
        self.lbl_totales = QLabel()
        self.lbl_totales.setStyleSheet("""
            font-size: 16px; font-weight: bold; color: #1e293b;
            padding: 15px; background: #e0e7ff; border-radius: 8px;
        """)
        self.lbl_totales.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_totales)

    def _crear_panel_columnas(self):
        box = QGroupBox("Columnas a Mostrar")
        box.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 14px;
                border: 2px solid #cbd5e1; border-radius: 8px;
                padding: 15px; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        """)

        layout = QGridLayout()

        # Definir todas las columnas posibles
        columnas = [
            ("Fecha", True), ("Concepto", True), ("Cuenta", True),
            ("Nombre Cuenta", True), ("Debe", True), ("Haber", True),
            ("Saldo", True), ("Banco", True), ("Documento", False),
            ("Estado", False), ("Categoría", False)
        ]

        self.columnas_checks = {}
        row, col = 0, 0

        for nombre, default in columnas:
            chk = QCheckBox(nombre)
            chk.setChecked(default)
            chk.setStyleSheet("font-weight: normal;")
            self.columnas_checks[nombre] = chk
            layout.addWidget(chk, row, col)

            col += 1
            if col > 3:
                col = 0
                row += 1

        box.setLayout(layout)
        return box

    def _crear_panel_filtros(self):
        box = QGroupBox("Filtros")
        box.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 14px;
                border: 2px solid #cbd5e1; border-radius: 8px;
                padding: 15px; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
        """)

        layout = QGridLayout()
        row = 0

        # Rango de fechas
        layout.addWidget(QLabel("Fecha Inicio:"), row, 0)
        self.fecha_ini = QDateEdit()
        self.fecha_ini.setCalendarPopup(True)
        self.fecha_ini.setDate(QDate.currentDate().addMonths(-1))
        layout.addWidget(self.fecha_ini, row, 1)

        layout.addWidget(QLabel("Fecha Fin:"), row, 2)
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate())
        layout.addWidget(self.fecha_fin, row, 3)
        row += 1

        # Banco
        layout.addWidget(QLabel("Banco:"), row, 0)
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItem("Todos")
        self._cargar_bancos()
        layout.addWidget(self.cbo_banco, row, 1)

        # Cuenta
        layout.addWidget(QLabel("Cuenta:"), row, 2)
        self.cbo_cuenta = QComboBox()
        self.cbo_cuenta.addItem("Todas")
        self._cargar_cuentas()
        layout.addWidget(self.cbo_cuenta, row, 3)
        row += 1

        # Categoría
        layout.addWidget(QLabel("Categoría:"), row, 0)
        self.cbo_categoria = QComboBox()
        self.cbo_categoria.addItems([
            "Todas", "FOOD", "MEDICINE", "HYGIENE", "SALARY",
            "ONLINE", "THERAPEUTIC", "DIET", "OTROS"
        ])
        layout.addWidget(self.cbo_categoria, row, 1)

        # Estado
        layout.addWidget(QLabel("Estado:"), row, 2)
        self.cbo_estado = QComboBox()
        self.cbo_estado.addItems(["Todos", "Pagado", "Pendiente"])
        layout.addWidget(self.cbo_estado, row, 3)
        row += 1

        # Tipo de movimiento
        layout.addWidget(QLabel("Tipo:"), row, 0)
        self.cbo_tipo = QComboBox()
        self.cbo_tipo.addItems(["Todos", "Solo Ingresos", "Solo Gastos"])
        layout.addWidget(self.cbo_tipo, row, 1)

        # Monto mínimo
        layout.addWidget(QLabel("Monto Mín:"), row, 2)
        self.txt_monto_min = QLineEdit()
        self.txt_monto_min.setPlaceholderText("0.00")
        layout.addWidget(self.txt_monto_min, row, 3)
        row += 1

        # Monto máximo
        layout.addWidget(QLabel("Monto Máx:"), row, 0)
        self.txt_monto_max = QLineEdit()
        self.txt_monto_max.setPlaceholderText("999999.99")
        layout.addWidget(self.txt_monto_max, row, 1)

        # Búsqueda por texto
        layout.addWidget(QLabel("Buscar:"), row, 2)
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Concepto, documento...")
        layout.addWidget(self.txt_buscar, row, 3)

        box.setLayout(layout)
        return box

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                bancos_data = json.load(f)
                for b in bancos_data.get("banks", []):
                    self.cbo_banco.addItem(b.get("nombre", ""))
        except (IOError, json.JSONDecodeError):
            self.cbo_banco.addItem("Caja")
            self.cbo_banco.addItem("Cambio Euros")
            self.cbo_banco.addItem("Contrapartida")

    def _cargar_cuentas(self):
        for cta, info in self.data.cuentas.items():
            nombre = info.get("nombre", "")
            self.cbo_cuenta.addItem(f"{cta} — {nombre}")

    def _limpiar_filtros(self):
        self.fecha_ini.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_fin.setDate(QDate.currentDate())
        self.cbo_banco.setCurrentIndex(0)
        self.cbo_cuenta.setCurrentIndex(0)
        self.cbo_categoria.setCurrentIndex(0)
        self.cbo_estado.setCurrentIndex(0)
        self.cbo_tipo.setCurrentIndex(0)
        self.txt_monto_min.clear()
        self.txt_monto_max.clear()
        self.txt_buscar.clear()
        if hasattr(self, "chk_export_invertido"):
            self.chk_export_invertido.setChecked(False)
        if hasattr(self, "chk_estilo_shillong"):
            self.chk_estilo_shillong.setChecked(False)

        self.tabla_resultados.setRowCount(0)
        self.lbl_totales.clear()
        self.btn_exportar.setEnabled(False)

    def _usar_inversion_exportacion(self):
        return bool(
            (getattr(self, "chk_export_invertido", None) and self.chk_export_invertido.isChecked())
            or (getattr(self, "chk_estilo_shillong", None) and self.chk_estilo_shillong.isChecked())
        )

    def _on_estilo_shillong_changed(self, _state):
        activo = self.chk_estilo_shillong.isChecked()
        if self.chk_export_invertido.isChecked() != activo:
            self.chk_export_invertido.blockSignals(True)
            self.chk_export_invertido.setChecked(activo)
            self.chk_export_invertido.blockSignals(False)
        if hasattr(self, "datos_actuales") and hasattr(self, "columnas_actuales"):
            self._mostrar_resultados(self.datos_actuales, self.columnas_actuales)

    def _generar_reporte(self):
        filtros = self._obtener_filtros()

        if hasattr(self.data, 'consulta_personalizada'):
            movimientos = self.data.consulta_personalizada(filtros)
        else:
            movimientos = self._aplicar_filtros_manual(self.data.movimientos, filtros)

        columnas = [k for k, v in self.columnas_checks.items() if v.isChecked()]

        if not columnas:
            QMessageBox.warning(self, "Sin Columnas", "Debe seleccionar al menos una columna.")
            return

        self._mostrar_resultados(movimientos, columnas)
        self.datos_actuales = movimientos
        self.columnas_actuales = columnas
        self.btn_exportar.setEnabled(len(movimientos) > 0)

    def _obtener_filtros(self):
        filtros = {}
        filtros['fecha_inicio'] = self.fecha_ini.date().toPython()
        filtros['fecha_fin'] = self.fecha_fin.date().toPython()

        if self.cbo_banco.currentText() != "Todos":
            filtros['banco'] = self.cbo_banco.currentText()

        if self.cbo_cuenta.currentText() != "Todas":
            cuenta_texto = self.cbo_cuenta.currentText().split(" — ")[0]
            filtros['cuenta'] = cuenta_texto

        if self.cbo_categoria.currentText() != "Todas":
            filtros['categoria'] = self.cbo_categoria.currentText()

        if self.cbo_estado.currentText() != "Todos":
            filtros['estado'] = self.cbo_estado.currentText().lower()

        if self.cbo_tipo.currentIndex() == 1:
            filtros['tipo'] = 'ingresos'
        elif self.cbo_tipo.currentIndex() == 2:
            filtros['tipo'] = 'gastos'

        try:
            if self.txt_monto_min.text():
                filtros['monto_min'] = float(self.txt_monto_min.text())
        except ValueError:
            pass

        try:
            if self.txt_monto_max.text():
                filtros['monto_max'] = float(self.txt_monto_max.text())
        except ValueError:
            pass

        if self.txt_buscar.text():
            filtros['buscar'] = self.txt_buscar.text().lower()

        return filtros

    def _aplicar_filtros_manual(self, movimientos, filtros):
        resultado = []

        for m in movimientos:
            fecha_str = m.get("fecha", "")
            try:
                if "/" in fecha_str:
                    d, mm, a = fecha_str.split("/")
                    fecha_mov = datetime.date(int(a), int(mm), int(d))
                elif "-" in fecha_str:
                    parts = fecha_str.split("-")
                    if int(parts[0]) > 1000:
                        fecha_mov = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                    else:
                        fecha_mov = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                else:
                    continue

                if fecha_mov < filtros['fecha_inicio'] or fecha_mov > filtros['fecha_fin']:
                    continue
            except (ValueError, IndexError):
                continue

            if 'banco' in filtros and m.get("banco") != filtros['banco']:
                continue

            if 'cuenta' in filtros and str(m.get("cuenta")) != filtros['cuenta']:
                continue

            if 'estado' in filtros and m.get("estado", "").lower() != filtros['estado']:
                continue

            debe = float(m.get("debe", 0) or 0)
            haber = float(m.get("haber", 0) or 0)

            if 'tipo' in filtros:
                if filtros['tipo'] == 'ingresos' and haber == 0:
                    continue
                if filtros['tipo'] == 'gastos' and debe == 0:
                    continue

            monto = debe if debe > 0 else haber
            if 'monto_min' in filtros and monto < filtros['monto_min']:
                continue
            if 'monto_max' in filtros and monto > filtros['monto_max']:
                continue

            if 'buscar' in filtros:
                buscar = filtros['buscar']
                if buscar not in str(m.get("concepto", "")).lower() and \
                   buscar not in str(m.get("documento", "")).lower():
                    continue

            resultado.append(m)

        return resultado

    def _mostrar_resultados(self, movimientos, columnas):
        invertir = self._usar_inversion_exportacion()
        columnas_vista = [
            "Entra" if (invertir and c == "Debe") else
            "Sale" if (invertir and c == "Haber") else c
            for c in columnas
        ]
        self.tabla_resultados.setRowCount(0)
        self.tabla_resultados.setColumnCount(len(columnas_vista))
        self.tabla_resultados.setHorizontalHeaderLabels(columnas_vista)

        total_debe = 0.0
        total_haber = 0.0
        saldo_acum = 0.0

        for m in movimientos:
            debe_orig = float(m.get("debe", 0) or 0)
            haber_orig = float(m.get("haber", 0) or 0)
            if invertir:
                debe = haber_orig
                haber = debe_orig
                saldo_acum += debe - haber
            else:
                debe = debe_orig
                haber = haber_orig
                saldo_acum += haber - debe
            total_debe += debe
            total_haber += haber

            row = self.tabla_resultados.rowCount()
            self.tabla_resultados.insertRow(row)

            for col, nombre_col in enumerate(columnas):
                valor = self._obtener_valor_columna(m, nombre_col, saldo_acum, invertir)
                item = QTableWidgetItem(str(valor))

                if nombre_col in ["Debe", "Haber", "Saldo"]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.tabla_resultados.setItem(row, col, item)

        self.lbl_totales.setText(
            f"📊 Movimientos: {len(movimientos)} | "
            f"{'Entra' if invertir else 'Debe'}: {total_debe:,.2f} | "
            f"{'Sale' if invertir else 'Haber'}: {total_haber:,.2f} | "
            f"Saldo Neto: {saldo_acum:,.2f}"
        )

    def _obtener_valor_columna(self, mov, nombre_col, saldo_acum, invertir=False):
        debe_orig = float(mov.get('debe', 0) or 0)
        haber_orig = float(mov.get('haber', 0) or 0)
        debe = haber_orig if invertir else debe_orig
        haber = debe_orig if invertir else haber_orig
        mapeo = {
            "Fecha": mov.get("fecha", ""),
            "Concepto": mov.get("concepto", ""),
            "Cuenta": mov.get("cuenta", ""),
            "Nombre Cuenta": self.data.obtener_nombre_cuenta(mov.get("cuenta")),
            "Debe": f"{debe:,.2f}",
            "Haber": f"{haber:,.2f}",
            "Entra": f"{debe:,.2f}",
            "Sale": f"{haber:,.2f}",
            "Saldo": f"{saldo_acum:,.2f}",
            "Banco": mov.get("banco", ""),
            "Documento": mov.get("documento", ""),
            "Estado": mov.get("estado", ""),
            "Categoría": self._obtener_categoria(mov.get("cuenta"))
        }
        return mapeo.get(nombre_col, "")

    def _obtener_categoria(self, cuenta):
        try:
            c = int(str(cuenta).split()[0])
            # Comestibles (603000) y limpieza/aseo (6024xx) están dentro de
            # 600000-609999 (farmacia), así que se evalúan antes que MEDICINE
            if 603000 <= c <= 603999:
                return "FOOD"
            if 602400 <= c <= 602499:
                return "HYGIENE"
            if 620401 <= c <= 620499:
                return "HYGIENE"
            if 600000 <= c <= 609999:
                return "MEDICINE"
            if 629200 <= c <= 629299:
                return "ONLINE"
            if 640000 <= c <= 649999:
                return "SALARY"
        except (ValueError, TypeError, IndexError):
            pass
        return "OTROS"

    def _exportar_excel(self):
        if not hasattr(self, 'datos_actuales') or not self.datos_actuales:
            QMessageBox.warning(self, "Sin Datos", "Genere un reporte primero.")
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte", "Reporte_Personalizado.xlsx", "Excel (*.xlsx)"
        )

        if not ruta:
            return

        try:
            from models.ExportadorExcelMensual import ExportadorExcelMensual
            invertir = self._usar_inversion_exportacion()

            datos_export = []
            saldo = 0.0

            for m in self.datos_actuales:
                debe_orig = float(m.get("debe", 0) or 0)
                haber_orig = float(m.get("haber", 0) or 0)
                if invertir:
                    debe = haber_orig
                    haber = debe_orig
                    saldo += debe - haber
                else:
                    debe = debe_orig
                    haber = haber_orig
                    saldo += haber - debe

                item = m.copy()
                item["debe"] = debe
                item["haber"] = haber
                item["saldo"] = saldo
                item["categoria"] = self._obtener_categoria(m.get("cuenta"))
                item["nombre_cuenta"] = self.data.obtener_nombre_cuenta(m.get("cuenta"))
                datos_export.append(item)

            periodo = f"{self.fecha_ini.date().toString('dd/MM/yyyy')} - {self.fecha_fin.date().toString('dd/MM/yyyy')}"
            ExportadorExcelMensual.exportar_general(ruta, datos_export, periodo)

            QMessageBox.information(self, "Éxito", "Reporte exportado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {str(e)}")
