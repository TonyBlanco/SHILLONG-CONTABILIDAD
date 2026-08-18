# -*- coding: utf-8 -*-
"""
TesoreriaView — SHILLONG CONTABILIDAD v3.8.0 PRO
RESUMEN DE TESORERÍA (saldo acumulado por mes) como pestaña independiente
en el hub de cierres. Comparte la lógica con InformesView (models/tesoreria.py).
"""

import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from models.tesoreria import datos_tesoreria, exportar_excel_tesoreria

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


class TesoreriaView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.año = datetime.date.today().year
        self.bancos = []
        self.acum = {}
        self._build_ui()
        self.actualizar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("💶 RESUMEN DE TESORERÍA")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        layout.addWidget(titulo)

        barra = QHBoxLayout()
        barra.addWidget(QLabel("Año:"))
        self.cbo_anio = QComboBox()
        for a in range(2020, 2036):
            self.cbo_anio.addItem(str(a))
        self.cbo_anio.setCurrentText(str(self.año))
        self.cbo_anio.currentIndexChanged.connect(self.actualizar)
        barra.addWidget(self.cbo_anio)
        barra.addStretch()

        self.btn_exportar = QPushButton("📄 Exportar a Excel")
        self.btn_exportar.setStyleSheet(
            "background:#7030A0; color:white; padding:8px 18px; "
            "font-weight:bold; border-radius:6px;"
        )
        self.btn_exportar.clicked.connect(self._exportar_excel)
        barra.addWidget(self.btn_exportar)
        layout.addLayout(barra)

        self.tabla = QTableWidget(0, 13)
        self.tabla.setHorizontalHeaderLabels(["BANCO / TESORERÍA"] + MESES)
        self.tabla.setAlternatingRowColors(True)
        layout.addWidget(self.tabla, 1)

        self.lbl_nota = QLabel()
        self.lbl_nota.setStyleSheet("color:#475569; font-style:italic;")
        layout.addWidget(self.lbl_nota)

    def actualizar(self):
        """Recalcula los saldos del año seleccionado y repinta la tabla."""
        self.año = int(self.cbo_anio.currentText())
        self.bancos, self.acum = datos_tesoreria(self.data.movimientos, self.año)
        self._render()

    def _render(self):
        self.tabla.setRowCount(0)
        totales = [None] * 12  # None = mes sin data real (celda vacía)

        for banco in self.bancos:
            vals = self.acum[banco]
            r = self.tabla.rowCount()
            self.tabla.insertRow(r)
            self.tabla.setItem(r, 0, QTableWidgetItem(banco))
            for c in range(12):
                v = vals[c]
                if v is None:
                    continue  # mes sin movimientos → celda vacía
                if totales[c] is None:
                    totales[c] = 0.0
                totales[c] += v
                it = QTableWidgetItem(f"{v:,.2f}")
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla.setItem(r, c + 1, it)

        # Fila TOTAL
        r = self.tabla.rowCount()
        self.tabla.insertRow(r)
        item_total = QTableWidgetItem("TOTAL")
        f = item_total.font()
        f.setBold(True)
        item_total.setFont(f)
        self.tabla.setItem(r, 0, item_total)
        for c in range(12):
            v = totales[c]
            if v is None:
                continue  # ningún banco tiene data en ese mes → TOTAL vacío
            it = QTableWidgetItem(f"{v:,.2f}")
            it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            f = it.font()
            f.setBold(True)
            it.setFont(f)
            self.tabla.setItem(r, c + 1, it)

        self.lbl_nota.setText(
            f"Saldo acumulado de {self.año} = saldo inicial real del primer mes "
            "disponible del año en saldos_mensuales.json (o 0 si no hay saldo "
            "registrado) + ingresos − gastos de todos los meses hasta el mes "
            "indicado (solo pagados)."
        )

    def _exportar_excel(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Exportar Resumen de Tesorería",
            f"Tesorería_{self.año}.xlsx", "Excel (*.xlsx)"
        )
        if not ruta:
            return
        try:
            exportar_excel_tesoreria(ruta, self.año, self.bancos, self.acum)
            QMessageBox.information(
                self, "Éxito", "Resumen de Tesorería exportado correctamente."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")
