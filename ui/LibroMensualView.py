# -*- coding: utf-8 -*-
"""
LibroMensualView.py — SHILLONG CONTABILIDAD v3.8.0 PRO
---------------------------------------------------------
✅ Sistema de saldos mensuales automáticos
✅ Arrastre de saldos entre meses
✅ Botón de cierre de mes
✅ Debe/Haber alineado con contabilidad (gasto=Debe, ingreso=Haber)
---------------------------------------------------------
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QFileDialog, QMessageBox, QHeaderView, QMenu, QInputDialog, QCheckBox, QLineEdit,
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QFont, QTextDocument, QDesktopServices
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog

import datetime
import json
import os
from collections import defaultdict
from pathlib import Path

# Importar el nuevo sistema de saldos
try:
    from models.SaldosMensuales import SaldosMensuales
    SALDOS_DISPONIBLE = True
except ImportError:
    SALDOS_DISPONIBLE = False
    print("[LibroMensualView] ⚠️ Sistema de saldos no disponible")

# Intentamos importar el motor de Excel
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class LibroMensualView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year
        self._pwd = "menni1234"
        self._auth_ok = False
        self.modo_flujo = False  # Visualizar Debe/Haber como flujo (entra/sale)
        
        self.bancos = self._cargar_bancos()
        self.reglas_cache = self._cargar_reglas()
        
        # 🆕 Inicializar sistema de saldos
        if SALDOS_DISPONIBLE:
            self.saldos_sistema = SaldosMensuales()
        else:
            self.saldos_sistema = None
        
        self._build_ui()
        self.actualizar()

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except (IOError, json.JSONDecodeError, KeyError):
            return ["Todos", "Caja"]

    def _cargar_reglas(self):
        try:
            if os.path.exists("data/reglas_conceptos.json"):
                with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return {}

    def _cargar_saldos_iniciales(self, año, mes):
        """Carga saldos iniciales por banco desde saldos_mensuales.json."""
        ruta = Path("data/saldos_mensuales.json")
        if not ruta.exists():
            return {}
        try:
            data = json.loads(ruta.read_text(encoding="utf-8"))
            clave = f"{año}-{mes:02d}"
            return {b: vals.get("inicial", 0.0) for b, vals in data.get("saldos", {}).get(clave, {}).items()}
        except (json.JSONDecodeError, OSError, AttributeError):
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

    # --- LÓGICA DE CATEGORÍAS (ROBUSTA) ---
    def _categoria_de_cuenta(self, cuenta):
        # 1. Limpieza del input
        cuenta_str = str(cuenta).split(" ")[0].strip()
        
        # 2. Búsqueda directa en reglas (Cache)
        if cuenta_str in self.reglas_cache:
            cat_original = self.reglas_cache[cuenta_str].get("categoria", "")
            cat_upper = cat_original.upper()
            
            # Mapeo de categorías en español a códigos internos en inglés
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD", "ALIMENTACIÓN": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE", "FARMACIA": "MEDICINE",
                "MEDICAMENTOS": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE", "LIMPIEZA": "HYGIENE", 
                "LAVANDERÍA": "HYGIENE", "HIGIENE": "HYGIENE", "ASEO PERSONAL": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY", "NOMINAS": "SALARY",
                "TELEFONÍA E INTERNET": "ONLINE", "INTERNET": "ONLINE", 
                "TELEFONO": "ONLINE",
                "TERAPIAS": "THERAPEUTIC", "DIETA": "DIET"
            }
            
            if cat_upper in mapeo: return mapeo[cat_upper]
            return cat_original

        # 3. Fallback por rangos numéricos
        try:
            c = int(cuenta_str)
            if 600000 <= c <= 609999: return "MEDICINE"
            if 603000 <= c <= 603999: return "FOOD"
            if 602400 <= c <= 602499: return "HYGIENE"
            if 620401 <= c <= 620499: return "HYGIENE"
            if 640000 <= c <= 649999 or (750000 <= c <= 759999): return "SALARY"
            if 629200 <= c <= 629299: return "ONLINE"
        except (ValueError, TypeError):
            pass
            
        return "OTROS"

    # 🆕 GESTIÓN DE SALDOS INICIALES
    def _solicitar_saldo_inicial(self, mes, año, banco):
        """
        Obtiene el saldo inicial del mes/año/banco.
        Primero busca en el sistema de saldos.
        Si no existe, solicita al usuario.
        """
        # Si no hay sistema de saldos, no interrumpir: devolvemos 0 para no bloquear la app.
        if not self.saldos_sistema:
            return 0.0

        saldo_auto = self.saldos_sistema.obtener_saldo_inicial(mes, año, banco)
        if saldo_auto is not None:
            print(f"[LibroMensual] ✅ Saldo automático: {banco} {mes}/{año} = {saldo_auto}")
            return saldo_auto

        # Proponer usar el cierre anterior
        if mes == 1:
            mes_ant, año_ant = 12, año - 1
        else:
            mes_ant, año_ant = mes - 1, año
        saldo_prev = self.saldos_sistema.obtener_saldo_final(mes_ant, año_ant, banco)
        if saldo_prev is not None:
            # Sin preguntar: auto-arrastrar para no molestar al usuario en el arranque.
            self.saldos_sistema.editar_saldo_inicial(mes, año, banco, saldo_prev)
            return saldo_prev

        # Si no hay datos previos, no interrumpir: devolver 0 y que el usuario ajuste luego en el gestor.
        return 0.0

    # ------------------------------------------------------------
    # Gestor de saldos manual (editar / eliminar / usar cierre previo)
    # ------------------------------------------------------------
    def _abrir_editor_saldos(self, mes_pref=None, año_pref=None, banco_pref=None):
        if not self.saldos_sistema:
            QMessageBox.warning(self, "Sistema no disponible", "El sistema de saldos no está disponible.")
            return
        if not self._asegurar_password():
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Gestor de saldos")
        v = QVBoxLayout(dlg)

        form = QFormLayout()
        current_year = datetime.date.today().year
        sp_anio = QSpinBox()
        sp_anio.setRange(2023, current_year + 2)
        sp_anio.setValue(año_pref or int(self.cbo_año.currentText()) if hasattr(self, "cbo_año") else current_year)

        cb_mes = QComboBox()
        meses_txt = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        cb_mes.addItems(meses_txt)
        cb_mes.setCurrentIndex((mes_pref or self.cbo_mes.currentIndex()+1) - 1)

        cb_banco = QComboBox()
        cb_banco.addItems([b for b in self.bancos if b != "Todos"])
        if banco_pref:
            idx = cb_banco.findText(banco_pref)
            if idx >= 0:
                cb_banco.setCurrentIndex(idx)

        sp_ini = QDoubleSpinBox(); sp_ini.setMaximum(1e9); sp_ini.setDecimals(2)
        sp_ing = QDoubleSpinBox(); sp_ing.setMaximum(1e9); sp_ing.setDecimals(2)
        sp_gas = QDoubleSpinBox(); sp_gas.setMaximum(1e9); sp_gas.setDecimals(2)
        sp_fin = QDoubleSpinBox(); sp_fin.setMaximum(1e9); sp_fin.setDecimals(2)

        form.addRow("Año", sp_anio)
        form.addRow("Mes", cb_mes)
        form.addRow("Banco", cb_banco)
        form.addRow("Saldo inicial", sp_ini)
        form.addRow("Ingresos", sp_ing)
        form.addRow("Gastos", sp_gas)
        form.addRow("Saldo final", sp_fin)

        v.addLayout(form)

        info = QLabel("Tip: puede cargar desde el cierre previo y luego guardar.")
        v.addWidget(info)

        btns = QHBoxLayout()
        btn_cargar = QPushButton("Cargar")
        btn_prev = QPushButton("Usar cierre previo")
        btn_guardar = QPushButton("Guardar")
        btn_borrar = QPushButton("Eliminar banco en mes")
        btn_cerrar = QPushButton("Cerrar")
        for b in [btn_cargar, btn_prev, btn_guardar, btn_borrar, btn_cerrar]:
            b.setCursor(Qt.PointingHandCursor)
        btns.addWidget(btn_cargar)
        btns.addWidget(btn_prev)
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_borrar)
        btns.addWidget(btn_cerrar)
        v.addLayout(btns)

        def cargar():
            anio = sp_anio.value()
            mes = cb_mes.currentIndex() + 1
            banco = cb_banco.currentText()
            resumen = self.saldos_sistema.obtener_resumen_mes(mes, anio) or {}
            data = resumen.get(banco, {})
            sp_ini.setValue(float(data.get("inicial", 0.0)))
            sp_ing.setValue(float(data.get("ingresos", 0.0)))
            sp_gas.setValue(float(data.get("gastos", 0.0)))
            sp_fin.setValue(float(data.get("final", 0.0)))

        def usar_prev():
            anio = sp_anio.value()
            mes = cb_mes.currentIndex() + 1
            banco = cb_banco.currentText()
            if mes == 1:
                mes_ant, anio_ant = 12, anio - 1
            else:
                mes_ant, anio_ant = mes - 1, anio
            saldo_prev = self.saldos_sistema.obtener_saldo_final(mes_ant, anio_ant, banco)
            if saldo_prev is None:
                QMessageBox.information(dlg, "Sin datos", "No hay saldo final del mes anterior.")
                return
            sp_ini.setValue(float(saldo_prev))
            QMessageBox.information(dlg, "Listo", f"Saldo inicial cargado desde {mes_ant:02d}/{anio_ant}: {saldo_prev:,.2f}")

        def guardar():
            anio = sp_anio.value()
            mes = cb_mes.currentIndex() + 1
            banco = cb_banco.currentText()
            self.saldos_sistema.actualizar_saldo_completo(
                mes, anio, banco,
                sp_ini.value(), sp_ing.value(), sp_gas.value(), sp_fin.value()
            )
            QMessageBox.information(dlg, "Guardado", "Saldo actualizado.")

        def eliminar():
            anio = sp_anio.value()
            mes = cb_mes.currentIndex() + 1
            banco = cb_banco.currentText()
            resp = QMessageBox.question(dlg, "Eliminar", f"¿Eliminar el saldo de {banco} en {mes:02d}/{anio}?")
            if resp == QMessageBox.Yes:
                ok = self.saldos_sistema.eliminar_saldo_banco(mes, anio, banco)
                if ok:
                    QMessageBox.information(dlg, "Eliminado", "Registro eliminado.")
                else:
                    QMessageBox.information(dlg, "Sin cambios", "No había registro para eliminar.")

        btn_cargar.clicked.connect(cargar)
        btn_prev.clicked.connect(usar_prev)
        btn_guardar.clicked.connect(guardar)
        btn_borrar.clicked.connect(eliminar)
        btn_cerrar.clicked.connect(dlg.accept)

        # Auto cargar al abrir
        cargar()
        dlg.exec()


    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # HEADER
        h_layout = QHBoxLayout()
        lbl_titulo = QLabel("📖 Libro Diario Mensual")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        h_layout.addWidget(lbl_titulo)
        h_layout.addStretch()

        btn_preview = QPushButton("📄 Vista Previa")
        # Conectar con fallback para evitar crash si la función no está disponible en tiempo de ejecución
        btn_preview.clicked.connect(getattr(self, "vista_previa", self._vista_previa_fallback))
        
        btn_print = QPushButton("🖨️ Imprimir")
        btn_print.clicked.connect(self.imprimir)

        # Gestor de saldos
        self.btn_saldos = QPushButton("💰 Saldos")
        self.btn_saldos.setStyleSheet("background-color:#0ea5e9; color:white; font-weight:bold; padding:6px 12px; border-radius:6px;")
        self.btn_saldos.clicked.connect(self._abrir_editor_saldos)

        # --- BOTÓN RESTAURADO: MENÚ DESPLEGABLE ---
        self.btn_exportar_menu = QPushButton("📤 Exportar como… ▼")
        self.btn_exportar_menu.setStyleSheet("""
            QPushButton {
                background-color: #16a34a; color: white; font-weight: bold;
                padding: 6px 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #15803d; }
            QPushButton::menu-indicator { image: none; }
        """)
        
        # Menú
        self.menu_exportar = QMenu(self)
        self.menu_exportar.addAction("📊 Excel Detallado (General)", self._exportar_excel_general)
        self.menu_exportar.addSeparator()
        self.menu_exportar.addAction("📂 Excel por Categorías", self._exportar_excel_categorias)
        self.menu_exportar.addAction("🔢 Excel por Cuentas", self._exportar_excel_cuentas)
        
        # Asignar menú al botón
        self.btn_exportar_menu.setMenu(self.menu_exportar)

        # 🆕 BOTÓN CERRAR MES
        self.btn_cerrar_mes = QPushButton("🔒 Cerrar Mes")
        self.btn_cerrar_mes.setStyleSheet("""
            QPushButton {
                background-color: #dc2626; color: white; font-weight: bold;
                padding: 6px 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        self.btn_cerrar_mes.clicked.connect(self._cerrar_mes_actual)

        # Auditoría y edición protegida
        self.btn_auditar = QPushButton("🔎 Auditar")
        self.btn_auditar.setStyleSheet("background-color:#0ea5e9; color:white; font-weight:bold; padding:6px 12px; border-radius:6px;")
        self.btn_auditar.clicked.connect(self._auditar_mes)

        self.btn_editar_json = QPushButton("✏️ Editar JSON")
        self.btn_editar_json.setStyleSheet("background-color:#475569; color:white; font-weight:bold; padding:6px 12px; border-radius:6px;")
        self.btn_editar_json.clicked.connect(self._guardar_json_manual)

        self.btn_editar = QPushButton("📝 Editar selección")
        self.btn_editar.setStyleSheet("background-color:#6366f1; color:white; font-weight:bold; padding:6px 12px; border-radius:6px;")
        self.btn_editar.clicked.connect(self._editar_seleccion)

        self.btn_borrar = QPushButton("🗑️ Borrar selección")
        self.btn_borrar.setStyleSheet("background-color:#ef4444; color:white; font-weight:bold; padding:6px 12px; border-radius:6px;")
        self.btn_borrar.clicked.connect(self._borrar_seleccion)

        for b in [btn_preview, btn_print, self.btn_saldos, self.btn_exportar_menu, self.btn_cerrar_mes, self.btn_auditar, self.btn_editar_json, self.btn_editar, self.btn_borrar]:
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(35)
            if not b.styleSheet():
                b.setStyleSheet("padding: 5px 15px; border-radius: 6px; background: #f1f5f9; border: 1px solid #cbd5e1;")
            h_layout.addWidget(b)

        layout.addLayout(h_layout)

        # Barra de auditoría rápida
        self.lbl_auditoria = QLabel("Auditoría pendiente")
        self.lbl_auditoria.setStyleSheet("font-weight:bold; color:#64748b; padding:6px;")
        layout.addWidget(self.lbl_auditoria)

        # FILTROS
        filtros = QFrame()
        filtros.setStyleSheet("background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;")
        f_layout = QHBoxLayout(filtros)
        f_layout.setContentsMargins(10, 10, 10, 10)
        
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems(["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)
        
        self.cbo_año = QComboBox()
        self.cbo_año.addItems([str(x) for x in range(2020, 2036)])
        self.cbo_año.setCurrentText(str(self.año_actual))
        
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)

        btn_ver = QPushButton("🔄 Actualizar")
        btn_ver.setStyleSheet("background:#3b82f6; color:white; font-weight:bold; padding:5px 15px; border-radius:4px;")
        btn_ver.clicked.connect(self.actualizar)

        f_layout.addWidget(QLabel("Mes:"))
        f_layout.addWidget(self.cbo_mes)
        f_layout.addSpacing(15)
        f_layout.addWidget(QLabel("Año:"))
        f_layout.addWidget(self.cbo_año)
        f_layout.addSpacing(15)
        f_layout.addWidget(QLabel("Banco:"))
        f_layout.addWidget(self.cbo_banco)
        f_layout.addSpacing(15)
        f_layout.addWidget(btn_ver)
        f_layout.addStretch()
        layout.addWidget(filtros)

        # Toggle de visualización Debe/Haber (flujo)
        self.chk_flujo = QCheckBox("Ver como flujo (Entra=Debe, Sale=Haber)")
        self.chk_flujo.stateChanged.connect(self.actualizar)
        layout.addWidget(self.chk_flujo)
        # Toggle exportación invertida
        self.chk_export_invertido = QCheckBox("Exportar con columnas invertidas (ShillongStyle)")
        layout.addWidget(self.chk_export_invertido)

        # CARDS
        cards = QHBoxLayout()
        self.card_gasto = self._crear_card("Total Gastos", "#ef4444")
        self.card_ingreso = self._crear_card("Total Ingresos", "#10b981")
        self.card_saldo = self._crear_card("Saldo del Mes", "#3b82f6")
        cards.addWidget(self.card_gasto)
        cards.addWidget(self.card_ingreso)
        cards.addWidget(self.card_saldo)
        layout.addLayout(cards)

        # TABLA
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Doc", "Concepto", "Cuenta", "Nombre", 
            "Debe", "Haber", "Saldo", "Banco", "Estado", "Categoría"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("QHeaderView::section { background-color: #f1f5f9; font-weight: bold; border: none; padding: 6px; }")
        layout.addWidget(self.tabla)

    def _crear_card(self, titulo, color):
        card = QFrame()
        card.setStyleSheet(f"background: white; border: 1px solid #e2e8f0; border-radius: 10px; border-left: 5px solid {color};")
        card.setMinimumHeight(80)
        l = QVBoxLayout(card)
        l.addWidget(QLabel(titulo))
        lbl_val = QLabel("0.00")
        lbl_val.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        lbl_val.setObjectName("val")
        l.addWidget(lbl_val)
        return card

    def _update_card(self, card, valor):
        lbl = card.findChild(QLabel, "val")
        if lbl: lbl.setText(f"{valor:,.2f}")

    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco_filtro = self.cbo_banco.currentText()

        self.row_records = []
        
        # Solicitar saldo inicial (automático o manual)
        if banco_filtro == "Todos":
            # Usar saldo de Caja como referencia para "Todos"
            saldo_inicial = self._solicitar_saldo_inicial(mes, año, "Caja") or 0.0
        else:
            saldo_inicial = self._solicitar_saldo_inicial(mes, año, banco_filtro)
        
        if saldo_inicial is None:
            QMessageBox.warning(self, "Atención", "Debe introducir el saldo inicial para visualizar el mes.")
            return

        movs = self.data.movimientos_por_mes(mes, año)

        self.tabla.setRowCount(0)
        saldo_acum = saldo_inicial
        total_debe = 0
        total_haber = 0

        # Fila saldo inicial
        fila0 = [
            f"01/{mes:02d}/{año}", "", "Saldo inicial", "", "",
            f"{0.0:,.2f}", f"{0.0:,.2f}", f"{saldo_acum:,.2f}",
            "Caja" if banco_filtro == "Todos" else banco_filtro, "", ""
        ]
        self.tabla.insertRow(0)
        self.row_records.append(None)
        for c, val in enumerate(fila0):
            it = QTableWidgetItem(str(val))
            if c in [5, 6, 7]:
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if c == 7:
                    it.setFont(QFont("Arial", 9, QFont.Bold))
            self.tabla.setItem(0, c, it)

        for m in movs:
            if banco_filtro != "Todos" and m.get("banco") != banco_filtro:
                continue

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            try:
                debe = float(m.get("debe", 0))
            except (ValueError, TypeError):
                debe = 0.0
            try:
                haber = float(m.get("haber", 0))
            except (ValueError, TypeError):
                haber = 0.0
            
            # Mostrar valores: contable estándar o modo flujo (entra/sale)
            if self.chk_flujo.isChecked():
                # Modo flujo: ingresos como Debe (entra), gastos como Haber (sale)
                debe_mostrar = haber
                haber_mostrar = debe
                saldo_acum += debe_mostrar - haber_mostrar
            else:
                # Contable estándar: gasto=Debe, ingreso=Haber
                debe_mostrar = debe
                haber_mostrar = haber
                saldo_acum += haber_mostrar - debe_mostrar

            total_debe += debe_mostrar
            total_haber += haber_mostrar
            
            cat = self._categoria_de_cuenta(m.get("cuenta"))
            nombre_cuenta = self.data.obtener_nombre_cuenta(m.get("cuenta"))

            items = [
                m.get("fecha", ""), m.get("documento", ""), m.get("concepto", ""),
                str(m.get("cuenta", "")), nombre_cuenta,
                f"{debe_mostrar:,.2f}", f"{haber_mostrar:,.2f}", f"{saldo_acum:,.2f}",
                m.get("banco", ""), m.get("estado", ""), cat
            ]

            for c, val in enumerate(items):
                it = QTableWidgetItem(str(val))
                if c in [5,6,7]: 
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if c == 7: it.setFont(QFont("Arial", 9, QFont.Bold))

                if c == 10:
                    if val == "OTROS": it.setForeground(QColor("#94a3b8"))
                    else: it.setForeground(QColor("#16a34a"))
                    it.setFont(QFont("Arial", 9, QFont.Bold))

                self.tabla.setItem(row, c, it)
            self.row_records.append(m)

        self._update_card(self.card_gasto, total_debe)     # gastos (Debe)
        self._update_card(self.card_ingreso, total_haber)  # ingresos (Haber)
        self._update_card(self.card_saldo, saldo_acum)

        # Actualiza resumen de auditoría básica en la barra
        self.lbl_auditoria.setText(
            f"Auditoría rápida: Debe {total_debe:,.2f} | Haber {total_haber:,.2f} | Saldo {saldo_acum:,.2f}"
        )

        # 🆕 Actualizar estado del botón cerrar mes
        self._actualizar_boton_cerrar_mes(mes, año)

    def _actualizar_boton_cerrar_mes(self, mes, año):
        """Actualiza el texto y estilo del botón según el estado del mes."""
        if not self.saldos_sistema:
            return

        if self.saldos_sistema.mes_cerrado(mes, año):
            self.btn_cerrar_mes.setText("🔓 Reabrir Mes")
            self.btn_cerrar_mes.setStyleSheet("""
                QPushButton {
                    background-color: #f59e0b; color: white; font-weight: bold;
                    padding: 6px 15px; border-radius: 6px;
                }
                QPushButton:hover { background-color: #d97706; }
            """)
        else:
            self.btn_cerrar_mes.setText("🔒 Cerrar Mes")
            self.btn_cerrar_mes.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626; color: white; font-weight: bold;
                    padding: 6px 15px; border-radius: 6px;
                }
                QPushButton:hover { background-color: #b91c1c; }
            """)

    # 🆕 CERRAR MES
    def _cerrar_mes_actual(self):
        if not self._asegurar_password():
            return

        """Cierra el mes actual guardando los saldos finales."""
        if not self.saldos_sistema:
            QMessageBox.warning(self, "Sistema no disponible", "El sistema de saldos no está disponible.")
            return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())

        # Verificar si ya está cerrado
        if self.saldos_sistema.mes_cerrado(mes, año):
            # Reabrir
            respuesta = QMessageBox.question(
                self,
                "Reabrir mes",
                f"¿Desea reabrir el mes {mes:02d}/{año}?\n\n"
                "Esto permitirá editar movimientos y saldos.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                self.saldos_sistema.reabrir_mes(mes, año)
                self._actualizar_boton_cerrar_mes(mes, año)
                QMessageBox.information(self, "Éxito", f"Mes {mes:02d}/{año} reabierto correctamente.")
            return

        # Confirmar cierre
        respuesta = QMessageBox.question(
            self,
            "Cerrar mes",
            f"¿Desea cerrar el mes {mes:02d}/{año}?\n\n"
            "Esto guardará los saldos finales y permitirá\n"
            "que el siguiente mes los arrastre automáticamente.",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        # Resumen y firma
        movs_mes = self.data.movimientos_por_mes(mes, año)
        total_debe = sum(float(m.get("debe", 0)) for m in movs_mes)
        total_haber = sum(float(m.get("haber", 0)) for m in movs_mes)
        saldo_inicial_global = sum(
            self.saldos_sistema.obtener_saldo_inicial(mes, año, b) or 0.0
            for b in self.bancos if b != "Todos"
        )
        saldo_final_est = saldo_inicial_global + total_haber - total_debe

        firmante, ok = QInputDialog.getText(
            self,
            "Responsable del cierre",
            f"Ingrese su nombre para firmar el cierre {mes:02d}/{año}:\n"
            f"Debe: {total_debe:,.2f} | Haber: {total_haber:,.2f}\n"
            f"Saldo inicial: {saldo_inicial_global:,.2f} | Saldo estimado: {saldo_final_est:,.2f}",
            QLineEdit.Normal
        )
        if not ok or not firmante.strip():
            QMessageBox.information(self, "Cancelado", "Cierre cancelado: falta firma.")
            return
        firma = firmante.strip()

        # Calcular saldos finales de todos los bancos
        saldos_finales = {}

        for banco in self.bancos:
            if banco == "Todos":
                continue

            saldo_inicial = self._solicitar_saldo_inicial(mes, año, banco) or 0.0
            
            # Calcular movimientos del banco
            movs = self.data.movimientos_por_mes(mes, año)
            ingresos = sum(float(m.get("haber", 0)) for m in movs if m.get("banco") == banco)
            gastos = sum(float(m.get("debe", 0)) for m in movs if m.get("banco") == banco)
            saldo_final = saldo_inicial + ingresos - gastos

            saldos_finales[banco] = {
                "inicial": saldo_inicial,
                "final": saldo_final,
                "ingresos": ingresos,
                "gastos": gastos,
                "firma": firma
            }

        saldos_finales["_firma"] = firma

        # Guardar en el sistema
        self.saldos_sistema.cerrar_mes(mes, año, saldos_finales)
        self._actualizar_boton_cerrar_mes(mes, año)

        QMessageBox.information(
            self,
            "✅ Mes cerrado",
            f"Mes {mes:02d}/{año} cerrado correctamente.\n\n"
            "Los saldos finales se usarán automáticamente\n"
            "como saldos iniciales del próximo mes."
        )

    # ============================================================
    # MÉTODOS DE EXPORTACIÓN (ORDEN ESTRICTO A-G)
    # ============================================================
    def _exportar_excel_general(self):
        self._exportar_excel_base("general")

    def _exportar_excel_categorias(self):
        self._exportar_excel_base("categoria")

    def _exportar_excel_cuentas(self):
        self._exportar_excel_base("cuenta")

    def _exportar_excel_base(self, modo):
        """Método centralizado con ORDEN EXACTO SOLICITADO + Saldo inicial + inversión Debe/Haber."""
        if ExportadorExcelMensual is None:
            QMessageBox.critical(self, "Error", "Falta el módulo ExportadorExcelMensual.")
            return

        # Obtener datos actuales
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco_filtro = self.cbo_banco.currentText()

        # Obtener saldo inicial
        if banco_filtro == "Todos":
            saldo_inicial = self._solicitar_saldo_inicial(mes, año, "Caja") or 0.0
        else:
            saldo_inicial = self._solicitar_saldo_inicial(mes, año, banco_filtro)
        
        if saldo_inicial is None:
            QMessageBox.warning(self, "Exportación cancelada", "El saldo inicial es requerido para la exportación.")
            return

        # Pedir ruta
        nombres = {
            "general": f"Libro_{self.cbo_mes.currentText()}.xlsx",
            "categoria": f"Resumen_Categorias_{self.cbo_mes.currentText()}.xlsx",
            "cuenta": f"Resumen_Cuentas_{self.cbo_mes.currentText()}.xlsx"
        }
        
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Excel", nombres[modo], "Excel (*.xlsx)")
        if not ruta: return

        # Organizar en reportes/<YYYY-MM>/<categoria|otros>
        mes_dir = f"{año}-{mes:02d}"
        categoria_dir = "categoria" if modo == "categoria" else ("cuenta" if modo == "cuenta" else "general")
        base_dir = Path("reportes") / mes_dir / categoria_dir
        base_dir.mkdir(parents=True, exist_ok=True)
        ruta = str(base_dir / Path(ruta).name)

        # Recopilar datos filtrados
        movs_raw = self.data.movimientos_por_mes(mes, año)
        datos_prep = []

        # Insertar fila de saldo inicial al inicio
        fila_saldo_inicial = {
            "cuenta": "",
            "fecha": f"01/{mes:02d}/{año}",
            "categoria": "",
            "concepto": "Saldo inicial",
            "debe": 0.0,
            "haber": 0.0,
            "saldo": saldo_inicial,
            "banco": banco_filtro if banco_filtro != "Todos" else "Caja",
            "documento": "",
            "nombre_cuenta": "",
            "estado": "",
        }
        datos_prep.append(fila_saldo_inicial)

        # Inicializar saldo con el saldo inicial
        saldo = saldo_inicial
        
        for m in movs_raw:
            if banco_filtro != "Todos" and m.get("banco") != banco_filtro: continue
            
            # Valores internos (originales)
            debe_interno = float(m.get("debe", 0))
            haber_interno = float(m.get("haber", 0))

            if self.chk_export_invertido.isChecked():
                # Columnas invertidas (ellos): ingresos en Debe, gastos en Haber
                debe_export = haber_interno
                haber_export = debe_interno
                saldo += debe_export - haber_export
            else:
                debe_export = debe_interno
                haber_export = haber_interno
                saldo += haber_interno - debe_interno
            
            # --- CONSTRUCCIÓN ORDENADA ESTRICTA ---
            item_ordenado = {}
            
            # COLUMNAS SOLICITADAS (A-G)
            item_ordenado["cuenta"] = str(m.get("cuenta", ""))    # A: Cuenta
            item_ordenado["fecha"] = m.get("fecha", "")           # B: Fecha
            item_ordenado["concepto"] = m.get("concepto", "")     # C: Concepto
            item_ordenado["debe"] = debe_export                   # D: Debe (invertido)
            item_ordenado["haber"] = haber_export                 # E: Haber (invertido)
            item_ordenado["estado"] = m.get("estado", "")         # F: Estado
            item_ordenado["documento"] = m.get("documento", "")   # G: Documento
            
            # DATOS ADICIONALES (Necesarios para agrupación, puestos al final)
            item_ordenado["nombre_cuenta"] = self.data.obtener_nombre_cuenta(m.get("cuenta"))
            item_ordenado["saldo"] = saldo
            item_ordenado["banco"] = m.get("banco", "")
            item_ordenado["categoria"] = self._categoria_de_cuenta(m.get("cuenta"))
            
            datos_prep.append(item_ordenado)

        try:
            periodo = f"{self.cbo_mes.currentText()} {año}"
            
            if modo == "general":
                ExportadorExcelMensual.exportar_general(ruta, datos_prep, periodo)
                
            elif modo == "categoria":
                # Agrupar por categoría
                grupos = defaultdict(list)
                for x in datos_prep: 
                    cat = x["categoria"] if x["categoria"] else "SIN_CATEGORIA"
                    grupos[cat].append(x)
                # Ordenar por nombre de categoría
                grupos_ord = dict(sorted(grupos.items()))
                ExportadorExcelMensual.exportar_agrupado(ruta, grupos_ord, periodo, "Categoría")
                
            elif modo == "cuenta":
                # Agrupar por Cuenta
                grupos = defaultdict(list)
                for x in datos_prep: 
                    # Usamos cuenta + nombre para la cabecera del grupo
                    clave = f"{x['cuenta']} - {x['nombre_cuenta']}" if x['cuenta'] else "SALDO_INICIAL"
                    grupos[clave].append(x)
                # Ordenar por número de cuenta
                grupos_ord = dict(sorted(grupos.items()))
                ExportadorExcelMensual.exportar_agrupado(ruta, grupos_ord, periodo, "Cuenta")

            QMessageBox.information(self, "Éxito", f"Reporte '{modo}' generado correctamente.")
            abrir = QMessageBox.question(
                self,
                "Abrir reporte",
                "¿Desea abrir el archivo generado?",
                QMessageBox.Yes | QMessageBox.No
            )
            if abrir == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al exportar: {e}")

    # ============================================================
    # IMPRESIÓN Y PDF
    # ============================================================
    def _vista_previa_fallback(self):
        """Mensaje de seguridad si la función de vista previa no está disponible."""
        QMessageBox.warning(self, "Vista previa no disponible", "La función de vista previa no está cargada en esta sesión.")

    def _generar_html(self):
        mes = self.cbo_mes.currentText()
        año = self.cbo_año.currentText()
        html = f"<html><head><style>body{{font-family:Arial;}} table{{width:100%;border-collapse:collapse;}} th{{background:#eee;}} td,th{{border:1px solid #ccc;padding:5px;}} .num{{text-align:right;}}</style></head><body><h1>Libro {mes} {año}</h1><table><tr><th>Fecha</th><th>Concepto</th><th>Cuenta</th><th>Debe</th><th>Haber</th></tr>"
        for r in range(self.tabla.rowCount()):
            html += f"<tr><td>{self.tabla.item(r,0).text()}</td><td>{self.tabla.item(r,2).text()}</td><td>{self.tabla.item(r,3).text()}</td><td class='num'>{self.tabla.item(r,5).text()}</td><td class='num'>{self.tabla.item(r,6).text()}</td></tr>"
        html += "</table></body></html>"
        return html

    def vista_previa(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        
        def print_request(p):
            doc = QTextDocument()
            doc.setHtml(self._generar_html())
            doc.print_(p)

        preview.paintRequested.connect(print_request)
        preview.exec()

    def imprimir(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            doc = QTextDocument()
            doc.setHtml(self._generar_html())
            doc.print_(printer)

    # ============================================================
    # AUDITORÍA Y EDICIÓN PROTEGIDA
    # ============================================================
    def _auditar_mes(self):
        if not self._asegurar_password():
            return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco_filtro = self.cbo_banco.currentText()

        saldos_init_map = self._cargar_saldos_iniciales(año, mes)
        saldo_inicial = sum(saldos_init_map.values()) if banco_filtro == "Todos" else saldos_init_map.get(banco_filtro, 0.0)

        total_debe = total_haber = 0.0
        anomalies = []

        for idx, m in enumerate(self.data.movimientos_por_mes(mes, año), 1):
            banco = m.get("banco", "").strip() or "SIN_BANCO"
            if banco_filtro != "Todos" and banco != banco_filtro:
                continue

            try:
                debe = float(m.get("debe", 0) or 0)
                haber = float(m.get("haber", 0) or 0)
            except (ValueError, TypeError):
                debe = haber = 0.0

            total_debe += debe
            total_haber += haber

            doc = m.get("documento", "").strip()
            cuenta = str(m.get("cuenta", "")).strip()

            if not doc:
                anomalies.append(f"Fila {idx}: sin documento")
            if not cuenta:
                anomalies.append(f"Fila {idx}: sin cuenta")

            try:
                c_int = int(cuenta.split(" ")[0])
                if (600000 <= c_int <= 699999 or 200000 <= c_int <= 299999) and haber > 0 and debe == 0:
                    anomalies.append(f"Fila {idx}: posible gasto en Haber (cuenta {cuenta}, haber={haber})")
            except ValueError:
                pass

        saldo_final = saldo_inicial + total_haber - total_debe
        resumen = [
            f"Total Debe: {total_debe:,.2f}",
            f"Total Haber: {total_haber:,.2f}",
            f"Saldo inicial: {saldo_inicial:,.2f}",
            f"Saldo final estimado: {saldo_final:,.2f}",
            f"Anomalías detectadas: {len(anomalies)}"
        ]

        self.lbl_auditoria.setText(" | ".join(resumen))

        if anomalies:
            detalle = "\n".join(anomalies[:15])
            if len(anomalies) > 15:
                detalle += f"\n... ({len(anomalies)-15} más)"
            QMessageBox.warning(self, "Auditoría con observaciones", "\n".join(resumen + ["", "Anomalías:", detalle]))
        else:
            QMessageBox.information(self, "Auditoría OK", "\n".join(resumen + ["", "Sin anomalías."]))

    def _guardar_json_manual(self):
        if not self._asegurar_password():
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar copia de datos",
            "data/shillong_2026.json.backup",
            "JSON (*.json)"
        )
        if not ruta:
            return
        try:
            data = {
                "version": getattr(self.data, "version", ""),
                "fecha_guardado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "movimientos": self.data.movimientos
            }
            Path(ruta).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            QMessageBox.information(self, "Guardado", f"Datos guardados en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el JSON:\n{e}")

    def _borrar_seleccion(self):
        if not self._asegurar_password():
            return
        row = self.tabla.currentRow()
        if row <= 0:
            QMessageBox.information(self, "Borrar", "Seleccione un movimiento (no el saldo inicial).")
            return
        record = self.row_records[row] if row < len(self.row_records) else None
        if not record:
            QMessageBox.warning(self, "Borrar", "No se pudo identificar el movimiento seleccionado.")
            return
        # Buscar en data.movimientos
        idx = self._buscar_indice_record(record)
        if idx is None:
            QMessageBox.warning(self, "Borrar", "No se encontró el movimiento en la base de datos.")
            return
        resp = QMessageBox.question(self, "Confirmar", "¿Desea borrar el movimiento seleccionado?", QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        try:
            self.data.movimientos.pop(idx)
            self.data.guardar()
            self.actualizar()
            QMessageBox.information(self, "Borrar", "Movimiento eliminado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo borrar: {e}")

    def _editar_seleccion(self):
        if not self._asegurar_password():
            return
        row = self.tabla.currentRow()
        if row <= 0:
            QMessageBox.information(self, "Editar", "Seleccione un movimiento (no el saldo inicial).")
            return
        record = self.row_records[row] if row < len(self.row_records) else None
        if not record:
            QMessageBox.warning(self, "Editar", "No se pudo identificar el movimiento seleccionado.")
            return
        idx = self._buscar_indice_record(record)
        if idx is None:
            QMessageBox.warning(self, "Editar", "No se encontró el movimiento en la base de datos.")
            return

        m = dict(self.data.movimientos[idx])
        campos = [
            ("Concepto", m.get("concepto", "")),
            ("Documento", m.get("documento", "")),
            ("Cuenta", str(m.get("cuenta", ""))),
            ("Debe", str(m.get("debe", ""))),
            ("Haber", str(m.get("haber", ""))),
            ("Banco", m.get("banco", "")),
            ("Estado", m.get("estado", "")),
        ]

        for nombre, valor in campos:
            texto, ok = QInputDialog.getText(self, "Editar", f"{nombre}:", text=str(valor))
            if not ok:
                return
            if nombre == "Debe":
                try: m["debe"] = float(texto)
                except: m["debe"] = 0.0
            elif nombre == "Haber":
                try: m["haber"] = float(texto)
                except: m["haber"] = 0.0
            elif nombre == "Cuenta":
                m["cuenta"] = texto.strip()
            else:
                m[nombre.lower()] = texto.strip()

        self.data.movimientos[idx] = m
        try:
            self.data.guardar()
            self.actualizar()
            QMessageBox.information(self, "Editar", "Movimiento actualizado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def _buscar_indice_record(self, record):
        for i, mov in enumerate(self.data.movimientos):
            if (
                mov.get("fecha") == record.get("fecha") and
                mov.get("documento") == record.get("documento") and
                mov.get("concepto") == record.get("concepto") and
                str(mov.get("cuenta","")) == str(record.get("cuenta","")) and
                float(mov.get("debe",0)) == float(record.get("debe",0)) and
                float(mov.get("haber",0)) == float(record.get("haber",0)) and
                mov.get("banco","") == record.get("banco","")
            ):
                return i
        return None
