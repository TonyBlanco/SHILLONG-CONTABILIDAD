# -*- coding: utf-8 -*-
"""
ImportarExcelDialog — SHILLONG CONTABILIDAD v3 PRO (2025 FINAL)
Importador profesional robusto, sin errores y totalmente compatible
"""

import pandas as pd
from datetime import datetime
import os
import json

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QTabWidget, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from models.CuentasMotor import MotorCuentas


class ImportarExcelDialog(QDialog):
    def __init__(self, parent, data_model):
        super().__init__(parent)
        self.data = data_model
        self.motor = MotorCuentas()
        self.df = None
        self.resultado_validacion = None
        self.bancos = self._cargar_bancos()

        self.setWindowTitle("Importar Excel — SHILLONG v3 PRO")
        self.resize(1150, 720)

        self._build_ui()

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return [b["nombre"] for b in data.get("banks", [])] + ["Caja"]
        except:
            return ["Caja", "Federal Bank", "SBI", "Union Bank", "Otro"]

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1 - Selección
        self.tab1 = QWidget()
        self._build_tab1()
        self.tabs.addTab(self.tab1, "1. Seleccionar archivo")

        # Tab 2 - Validación
        self.tab2 = QWidget()
        self._build_tab2()
        self.tabs.addTab(self.tab2, "2. Validación")
        self.tabs.setTabEnabled(1, False)

        # Tab 3 - Importar
        self.tab3 = QWidget()
        self._build_tab3()
        self.tabs.addTab(self.tab3, "3. Importar datos")
        self.tabs.setTabEnabled(2, False)

    def _build_tab1(self):
        layout = QVBoxLayout(self.tab1)
        layout.setSpacing(20)

        lbl = QLabel("Seleccione el archivo Excel para importar")
        lbl.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(lbl)

        btn = QPushButton("Seleccionar archivo Excel")
        btn.clicked.connect(self._seleccionar_archivo)
        btn.setStyleSheet("padding:14px; font-size:16px;")
        layout.addWidget(btn)

        self.lbl_archivo = QLabel("Ningún archivo seleccionado")
        self.lbl_archivo.setStyleSheet("color:#64748b; font-size:14px;")
        layout.addWidget(self.lbl_archivo)

        layout.addStretch()

    def _build_tab2(self):
        layout = QVBoxLayout(self.tab2)

        lbl = QLabel("Vista previa y validación de datos")
        lbl.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.preview = QTableWidget()
        scroll.setWidget(self.preview)
        layout.addWidget(scroll)

    def _build_tab3(self):
        layout = QVBoxLayout(self.tab3)
        layout.setSpacing(20)

        lbl = QLabel("Configuración final de importación")
        lbl.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(lbl)

        form = QHBoxLayout()
        form.addWidget(QLabel("Banco:"))
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)
        self.cbo_banco.setCurrentText("Caja")
        form.addWidget(self.cbo_banco)

        form.addWidget(QLabel("Moneda (ingresos):"))
        self.cbo_moneda = QComboBox()
        self.cbo_moneda.addItems(["INR", "EUR", "USD"])
        self.cbo_moneda.setCurrentText("INR")
        form.addWidget(self.cbo_moneda)

        form.addStretch()
        layout.addLayout(form)

        self.lbl_resumen = QLabel()
        self.lbl_resumen.setStyleSheet("font-size:16px; padding:10px; background:#f3f4f6; border-radius:8px;")
        layout.addWidget(self.lbl_resumen)

        btn = QPushButton("Importar movimientos válidos")
        btn.clicked.connect(self._importar)
        btn.setStyleSheet("background:#16a34a; color:white; padding:14px; font-size:16px;")
        layout.addWidget(btn)

        layout.addStretch()

    def _seleccionar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar Excel", "", "Excel (*.xlsx *.xls)")
        if not ruta:
            return

        self.lbl_archivo.setText(os.path.basename(ruta))
        try:
            self.df = pd.read_excel(ruta, header=None, dtype=str)
            self._procesar_excel()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo:\n{str(e)}")

    def _buscar_fila_cabecera(self):
        for i in range(min(15, len(self.df))):
            row_text = " ".join(self.df.iloc[i].astype(str).str.lower())
            if all(word in row_text for word in ["fecha", "concepto", "cuenta"]) or \
               all(word in row_text for word in ["date", "description", "account"]):
                return i
        return 0

    def _ajustar_cabecera(self):
        header = self.df.iloc[self.cabecera_idx]
        mapping = {}
        for idx, val in enumerate(header):
            txt = str(val).lower()
            if any(k in txt for k in ["fecha", "date", "day"]):
                mapping[idx] = "fecha"
            elif any(k in txt for k in ["concepto", "descrip", "detalle", "description", "concept"]):
                mapping[idx] = "concepto"
            elif any(k in txt for k in ["cuenta", "account", "ledger"]):
                mapping[idx] = "cuenta"
            elif any(k in txt for k in ["debe", "debit", "dr"]):
                mapping[idx] = "debe"
            elif any(k in txt for k in ["haber", "credit", "cr", "amount"]):
                mapping[idx] = "haber"
            elif any(k in txt for k in ["estado", "status"]):
                mapping[idx] = "estado"
        new_cols = [mapping.get(i, f"col_{i}") for i in range(len(header))]
        self.df.columns = new_cols

    def _limpiar_columnas(self):
        validas = ["fecha", "concepto", "cuenta", "debe", "haber", "estado"]
        existentes = [c for c in validas if c in self.df.columns]
        self.df = self.df[existentes]

    def _procesar_excel(self):
        self.cabecera_idx = self._buscar_fila_cabecera()
        self.df = self.df.iloc[self.cabecera_idx + 1:].copy()
        self.df.reset_index(drop=True, inplace=True)
        self._ajustar_cabecera()
        self._limpiar_columnas()

        # Eliminar filas basura
        self.df = self.df.dropna(how="all")
        basura = ["saldo anterior", "balance", "total", "subtotal", "resultado"]
        mask = self.df["concepto"].astype(str).str.lower().str.contains("|".join(basura), na=False)
        self.df = self.df[~mask]

        self._validar()
        self.tabs.setTabEnabled(1, True)
        self.tabs.setCurrentIndex(1)

    def _validar(self):
        df = self.df.copy()
        df["error"] = ""

        for idx in df.index:
            errores = []

            # Fecha
            if "fecha" not in df.columns or pd.isna(df.at[idx, "fecha"]) or str(df.at[idx, "fecha"]).strip() == "":
                df.at[idx, "fecha"] = datetime.today().strftime("%d/%m/%Y")
            else:
                try:
                    pd.to_datetime(df.at[idx, "fecha"], dayfirst=True)
                except:
                    errores.append("Fecha inválida")

            # Concepto
            if "concepto" not in df.columns or pd.isna(df.at[idx, "concepto"]) or str(df.at[idx, "concepto"]).strip() == "":
                errores.append("Falta concepto")

            # Cuenta
            if "cuenta" not in df.columns or pd.isna(df.at[idx, "cuenta"]) or str(df.at[idx, "cuenta"]).strip() == "":
                errores.append("Falta cuenta")
            else:
                cuenta = str(df.at[idx, "cuenta"]).strip()
                if not cuenta.isdigit():
                    errores.append("Cuenta no numérica")
                elif not self.motor.get_nombre(cuenta):
                    errores.append("Cuenta inexistente")
                elif "concepto" in df.columns and not self.motor.es_concepto_valido(cuenta, str(df.at[idx, "concepto"])):
                    errores.append("Concepto no permitido")

            # Debe/Haber
            debe = float(df.at[idx, "debe"]) if "debe" in df.columns and pd.notna(df.at[idx, "debe"]) else 0.0
            haber = float(df.at[idx, "haber"]) if "haber" in df.columns and pd.notna(df.at[idx, "haber"]) else 0.0
            try:
                debe = float(debe)
                haber = float(haber)
            except:
                errores.append("Importe inválido")
                debe = haber = 0.0

            if debe == 0 and haber == 0:
                errores.append("Importe cero")

            # Estado
            if "estado" not in df.columns or pd.isna(df.at[idx, "estado"]):
                df.at[idx, "estado"] = "pagado"

            if errores:
                df.at[idx, "error"] = " | ".join(errores)

        self.resultado_validacion = df.reset_index(drop=True)
        self._pintar_tabla()
        self._ir_a_tab3()

    def _pintar_tabla(self):
        df = self.resultado_validacion
        self.preview.setRowCount(len(df))
        self.preview.setColumnCount(len(df.columns))
        self.preview.setHorizontalHeaderLabels(df.columns.tolist())

        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                val = df.iat[i, j]
                item = QTableWidgetItem("" if pd.isna(val) else str(val))
                if df.iat[i, df.columns.get_loc("error")]:
                    item.setBackground(QColor("#fee2e2"))
                    item.setForeground(QColor("#dc2626"))
                self.preview.setItem(i, j, item)

        self.preview.resizeColumnsToContents()

    def _ir_a_tab3(self):
        df = self.resultado_validacion
        errores = (df["error"] != "").sum()
        validas = len(df) - errores
        self.lbl_resumen.setText(f"Movimientos válidos: {validas}\nMovimientos con errores: {errores}")
        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentIndex(2)

    def _importar(self):
        df = self.resultado_validacion[self.resultado_validacion["error"] == ""]
        if df.empty:
            QMessageBox.warning(self, "Sin datos", "No hay movimientos válidos para importar.")
            return

        saldo_actual = 0
        if self.data.movimientos:
            saldo_actual = self.data.movimientos[-1].get("saldo", 0)

        for idx in df.index:
            row = df.loc[idx]
            debe = float(row.get("debe", 0))
            haber = float(row.get("haber", 0))
            moneda = "INR" if debe > 0 else self.cbo_moneda.currentText()
            saldo_actual += haber - debe

            mov = {
                "fecha": pd.to_datetime(row["fecha"], dayfirst=True).strftime("%d/%m/%Y"),
                "documento": "",
                "concepto": str(row["concepto"]),
                "cuenta": str(row["cuenta"]).strip(),
                "debe": debe,
                "haber": haber,
                "estado": str(row.get("estado", "pagado")).lower(),
                "moneda": moneda,
                "banco": self.cbo_banco.currentText(),
                "saldo": saldo_actual
            }
            self.data.movimientos.append(mov)

        self.data.guardar()
        QMessageBox.information(self, "Éxito", "Importación completada correctamente.")
        self.accept()