# -*- coding: utf-8 -*-
"""
RegistrarView — SHILLONG CONTABILIDAD v3.7.8 PRO
Versión COMPLETAMENTE CORREGIDA
"""

from models.CuentasMotor import MotorCuentas
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QCompleter, QHeaderView, QAbstractItemView,
    QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QDate, QLocale
from datetime import datetime
import random

try:
    from ui.Dialogs.ImportarExcelDialog import ImportarExcelDialog
except ImportError:
    ImportarExcelDialog = None


class RegistrarView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.motor = MotorCuentas()
        self.locale = QLocale(QLocale.Spanish)
        self.tema_oscuro = False
        self.movimientos_filtrados = []

        self.setStyleSheet(self._estilo_claro())
        self._build_ui()
        self._cargar_ultimos()

    # ============================================================
    # ESTILOS
    # ============================================================
    def _estilo_claro(self):
        return """
        QWidget { background: #f8fafc; font-family:'Segoe UI'; }
        QLabel { color:#1e293b; font-size:14px; }
        QLineEdit, QDateEdit, QComboBox {
            padding:10px; border:2px solid #e2e8f0;
            border-radius:8px; background:white;
        }
        QPushButton {
            padding:10px 20px; border-radius:10px;
            color:white; font-weight:bold;
        }
        QPushButton#guardar { background:#2563eb; }
        QPushButton#nuevo { background:#059669; }
        QPushButton#limpiar { background:#0ea5e9; }
        QPushButton#limpiar_dh { background:#64748b; }
        QPushButton#duplicar { background:#7c3aed; }
        QPushButton#refresh { background:#475569; }
        """

    def _estilo_oscuro(self):
        return """
        QWidget { background:#0f172a; color:#e2e8f0; }
        QLabel { color:#e2e8f0; }
        QLineEdit, QDateEdit, QComboBox {
            background:#1e293b; color:#e2e8f0;
            border:2px solid #334155; padding:10px;
            border-radius:8px;
        }
        """

    def _cambiar_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        self.setStyleSheet(
            self._estilo_oscuro() if self.tema_oscuro else self._estilo_claro()
        )
        self.btn_tema.setText(
            "Modo claro" if self.tema_oscuro else "Modo oscuro"
        )

    # ============================================================
    # UI PRINCIPAL
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,20,30,20)

        # --------------------------
        # Título y botones superiores
        # --------------------------
        top = QHBoxLayout()
        titulo = QLabel("REGISTRAR MOVIMIENTO")
        titulo.setStyleSheet("font-size:26px;font-weight:800;")

        self.btn_importar = QPushButton("📥 Importar Excel")
        self.btn_importar.setObjectName("importar")
        self.btn_importar.clicked.connect(self._abrir_importador)

        self.btn_tema = QPushButton("Modo oscuro")
        self.btn_tema.setObjectName("tema")
        self.btn_tema.clicked.connect(self._cambiar_tema)

        top.addWidget(titulo)
        top.addStretch()
        top.addWidget(self.btn_importar)
        top.addWidget(self.btn_tema)
        layout.addLayout(top)

        # -------------------------------------
        # FORMULARIO PRINCIPAL
        # -------------------------------------
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Fecha
        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setDate(QDate.currentDate())
        form.addRow("Fecha:", self.fecha)

        # Documento
        self.documento = QLineEdit()
        self.documento.setPlaceholderText("Opcional — se genera uno si está vacío")
        form.addRow("Documento:", self.documento)

        # Cuenta contable
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.setEditable(True)

        opciones = []
        try:
            opciones = self.motor.todas_las_opciones()
        except (AttributeError, Exception) as e:
            print(f"[RegistrarView] Error cargando opciones de cuentas: {e}")

        self.cuenta_combo.addItems(opciones)

        comp = QCompleter(opciones, self)
        comp.setFilterMode(Qt.MatchContains)
        comp.setCaseSensitivity(Qt.CaseInsensitive)
        self.cuenta_combo.setCompleter(comp)
        self.cuenta_combo.currentTextChanged.connect(self._on_cuenta_changed)
        form.addRow("Cuenta:", self.cuenta_combo)

        # Nombre cuenta
        self.lbl_nombre = QLabel("Seleccione una cuenta")
        self.lbl_nombre.setStyleSheet("font-style:italic;color:#64748b;")
        form.addRow("", self.lbl_nombre)

        # Concepto
        self.concepto = QLineEdit()
        self.concepto.setPlaceholderText("Descripción…")
        self.concepto.textChanged.connect(self._validar_concepto_live)
        form.addRow("Concepto:", self.concepto)

        # --------------------------------------------------------
        # DEBE / HABER (INTERFAZ CORRECTA)
        # --------------------------------------------------------
        box_dh = QVBoxLayout()

        # INGRESO (HABER contable)
        fila_ing = QHBoxLayout()
        fila_ing.addWidget(QLabel("ENTRADA / INGRESO (+ dinero):"))
        self.ui_ingreso = QLineEdit("0,00")
        self.ui_ingreso.textChanged.connect(self._calcular_importe)
        fila_ing.addWidget(self.ui_ingreso)

        info_ing = QLabel("→ Todo lo que entra (donaciones, ventas).")
        info_ing.setStyleSheet("color:#059669;font-size:12px;")

        # GASTO (DEBE contable)
        fila_gas = QHBoxLayout()
        fila_gas.addWidget(QLabel("SALIDA / GASTO (- dinero):"))
        self.ui_gasto = QLineEdit("0,00")
        self.ui_gasto.textChanged.connect(self._calcular_importe)
        fila_gas.addWidget(self.ui_gasto)

        info_gas = QLabel("→ Todo lo que sale (compras, pagos).")
        info_gas.setStyleSheet("color:#dc2626;font-size:12px;")

        box_dh.addLayout(fila_ing)
        box_dh.addWidget(info_ing)
        box_dh.addLayout(fila_gas)
        box_dh.addWidget(info_gas)

        form.addRow("Importe:", box_dh)

        # --------------------------------------------------------
        # BANCO / ESTADO
        # --------------------------------------------------------
        banco_estado = QHBoxLayout()

        # Bancos
        banco_layout = QHBoxLayout()
        self.banco_buttons = QButtonGroup(self)

        estilo_chip = """
            QRadioButton {
                padding:6px 14px; border-radius:16px;
                background:#f1f5f9; border:1px solid #cbd5e1;
            }
            QRadioButton:checked {
                background:#3b82f6; color:white; font-weight:bold;
            }
            QRadioButton::indicator { width:0;height:0; }
        """

        for b in ["Caja","Federal Bank","SBI","Union Bank","Otro"]:
            rb = QRadioButton(b)
            rb.setStyleSheet(estilo_chip)
            banco_layout.addWidget(rb)
            self.banco_buttons.addButton(rb)
            if b == "Caja":
                rb.setChecked(True)

        banco_estado.addLayout(banco_layout)

        # Estado (Pagado/Pendiente)
        estado_layout = QHBoxLayout()
        self.estado_buttons = QButtonGroup(self)

        estilo_estado = """
            QRadioButton {
                padding:6px 14px; border-radius:16px;
                background:#f1f5f9; border:1px solid #cbd5e1;
            }
            QRadioButton:checked {
                background:#10b981; color:white; font-weight:bold;
            }
            QRadioButton::indicator { width:0;height:0; }
        """

        for e in ["Pagado","Pendiente"]:
            rb = QRadioButton(e)
            rb.setStyleSheet(estilo_estado)
            estado_layout.addWidget(rb)
            self.estado_buttons.addButton(rb)
            if e == "Pagado":
                rb.setChecked(True)

        banco_estado.addLayout(estado_layout)
        form.addRow("Banco / Estado:", banco_estado)

        layout.addLayout(form)

        # --------------------------------------------------------
        # BOTONES
        # --------------------------------------------------------
        botones = QHBoxLayout()

        self.btn_refresh = QPushButton("Actualizar lista")
        self.btn_refresh.setObjectName("refresh")
        self.btn_refresh.clicked.connect(self._cargar_ultimos)

        self.btn_duplicar = QPushButton("Duplicar")
        self.btn_duplicar.setObjectName("duplicar")
        self.btn_duplicar.clicked.connect(self._duplicar)

        self.btn_guardar = QPushButton("Guardar Movimiento")
        self.btn_guardar.setObjectName("guardar")
        self.btn_guardar.clicked.connect(self._guardar)

        self.btn_limpiar = QPushButton("Limpiar Formulario")
        self.btn_limpiar.setObjectName("limpiar")
        self.btn_limpiar.clicked.connect(self._limpiar_formulario)

        self.btn_limpiar_dh = QPushButton("Limpiar Debe/Haber")
        self.btn_limpiar_dh.setObjectName("limpiar_dh")
        self.btn_limpiar_dh.clicked.connect(self._limpiar_dh)

        self.btn_nuevo = QPushButton("Nuevo Registro")
        self.btn_nuevo.setObjectName("nuevo")
        self.btn_nuevo.clicked.connect(self._limpiar_formulario)

        for w in [
            self.btn_refresh, self.btn_duplicar, self.btn_guardar,
            self.btn_limpiar, self.btn_limpiar_dh, self.btn_nuevo
        ]:
            botones.addWidget(w)

        layout.addLayout(botones)

        # BUSCADOR
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar…")
        self.buscador.textChanged.connect(self._filtrar_tabla)
        layout.addWidget(self.buscador)

        # TABLA
        self.tabla = QTableWidget(0,10)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha","Documento","Concepto","Cuenta",
            "Nombre Cuenta","Debe","Haber",
            "Banco","Estado","Saldo"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.tabla)

        # TOTALES
        self.lbl_totales = QLabel()
        self.lbl_totales.setAlignment(Qt.AlignCenter)
        self.lbl_totales.setStyleSheet(
            "font-size:15px;font-weight:bold;padding:10px;background:#e0e7ff;"
            "border-radius:8px;"
        )
        layout.addWidget(self.lbl_totales)

    # ============================================================
    # PARSEOS
    # ============================================================
    def _parse_float(self, txt):
        """
        Parse float from string handling both Spanish and standard decimal formats.
        Spanish: 1.234,56 → 1234.56
        Standard: 1234.56 → 1234.56
        US: 1,234.56 → 1234.56
        """
        if not txt:
            return 0.0
        
        # Handle numeric types directly
        if isinstance(txt, (int, float)):
            return float(txt)
        
        txt = str(txt).strip()
        try:
            # Count separators to determine format
            dot_count = txt.count(".")
            comma_count = txt.count(",")
            
            # Standard decimal format: "1234.56" (no comma, one dot)
            if comma_count == 0 and dot_count == 1:
                return float(txt)
            
            # US format with thousands: "1,234.56" (dot is after comma)
            if comma_count >= 1 and dot_count == 1 and txt.rfind(".") > txt.rfind(","):
                return float(txt.replace(",", ""))
            
            # Simple Spanish decimal: "1234,56" (no dot, one comma)
            if dot_count == 0 and comma_count == 1:
                return float(txt.replace(",", "."))
            
            # Full Spanish format: "1.234,56" (comma is after dot)
            if dot_count >= 1 and comma_count == 1 and txt.rfind(",") > txt.rfind("."):
                return float(txt.replace(".", "").replace(",", "."))
            
            # Integer or simple number
            return float(txt)
        except (ValueError, TypeError):
            return 0.0

    def _fmt(self, v):
        try:
            return self.locale.toString(float(v), 'f', 2)
        except (ValueError, TypeError):
            return "0,00"

    # ============================================================
    # IMPORTADOR
    # ============================================================
    def _abrir_importador(self):
        if ImportarExcelDialog is None:
            QMessageBox.critical(
                self,"Error",
                "No se encontró ImportarExcelDialog en ui/Dialogs/"
            )
            return
        try:
            dlg = ImportarExcelDialog(self, self.data)
            if dlg.exec():
                self._cargar_ultimos()
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))

    # ============================================================
    # GUARDAR MOVIMIENTO (FIX DEFINITIVO DE DEBE/HABER)
    # ============================================================
    def _guardar(self):

        documento = self.documento.text().strip() or \
                    f"SIN-DOC-{random.randint(10000,99999)}"

        concepto = self.concepto.text().strip()
        if not concepto:
            QMessageBox.warning(self,"Atención","El concepto no puede estar vacío.")
            return

        # -------------------------------------------------------
        # FIX DEFINITIVO: INGRESO = HABER, GASTO = DEBE
        # -------------------------------------------------------
        try:
            ingreso_ui = self._parse_float(self.ui_ingreso.text())
            gasto_ui   = self._parse_float(self.ui_gasto.text())

            haber = ingreso_ui  # INGRESO → HABER
            debe  = gasto_ui    # GASTO → DEBE

        except Exception as e:
            QMessageBox.critical(
                self,"Error",
                f"Error al procesar importes:\n{str(e)}"
            )
            return

        # Reglas básicas
        if debe == 0 and haber == 0:
            QMessageBox.warning(
                self,"Atención","Debe ingresar un importe en DEBE o HABER."
            )
            return

        if debe > 0 and haber > 0:
            QMessageBox.critical(
                self,"Error Fatal",
                "Un movimiento no puede tener valores en DEBE y HABER simultáneamente."
            )
            return

        # Cuenta contable
        cuenta_txt = self.cuenta_combo.currentText()
        if " – " not in cuenta_txt:
            QMessageBox.warning(self,"Error","Seleccione una cuenta válida.")
            return

        codigo = cuenta_txt.split(" – ")[0]

        # Banco y estado
        banco = next(
            (b.text() for b in self.banco_buttons.buttons() if b.isChecked()), 
            "Caja"
        )

        estado = (
            "pagado" if any(
                rb.text()=="Pagado" and rb.isChecked()
                for rb in self.estado_buttons.buttons()
            ) else "pendiente"
        )

        fecha_str = self.fecha.date().toString("dd/MM/yyyy")

        # -------------------------------------------------------
        # Autocorrección: gasto colocado por error en ingreso
        # -------------------------------------------------------
        gasto_keywords = [
            "vegetable","milk","fish","rice","bread","egg","onion",
            "chicken","medicine","medical","clean","gas","taxi",
            "gasto","pago","compra","servicio","equipo"
        ]

        if haber > 0 and any(k in concepto.lower() for k in gasto_keywords):
            msg = QMessageBox(self)
            msg.setWindowTitle("⚠️ ERROR CONTABLE DETECTADO")
            msg.setText(
                "Se detectó un GASTO pero el importe está como INGRESO.\n"
                "¿Desea moverlo al DEBE?"
            )
            msg.setIcon(QMessageBox.Warning)
            btn_si = msg.addButton("Sí, mover a DEBE", QMessageBox.YesRole)
            btn_no = msg.addButton("Cancelar", QMessageBox.NoRole)
            msg.exec()

            if msg.clickedButton() == btn_si:
                debe = haber
                haber = 0.0
            else:
                return

        # -------------------------------------------------------
        # Crear movimiento limpio
        # -------------------------------------------------------
        movimiento = {
            "fecha": fecha_str,
            "documento": documento,
            "concepto": concepto,
            "cuenta": codigo,
            "debe": f"{debe:.2f}",
            "haber": f"{haber:.2f}",
            "moneda": "INR",
            "banco": banco,
            "estado": estado
        }

        # Guardar
        try:
            self.data.agregar_movimiento(**movimiento)
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))
            return

        self._limpiar_formulario()
        self._cargar_ultimos()

        QMessageBox.information(
            self,"Éxito","Movimiento guardado correctamente."
        )

    # ============================================================
    # AUXILIARES
    # ============================================================
    def _on_cuenta_changed(self, texto):
        if " – " not in texto:
            self.lbl_nombre.setText("Seleccione una cuenta")
            return

        codigo = texto.split(" – ")[0]
        try:
            nombre = self.motor.get_nombre(codigo)
            self.lbl_nombre.setText("→ " + nombre)
        except (AttributeError, KeyError):
            self.lbl_nombre.setText("→ Cuenta desconocida")

    def _validar_concepto_live(self):
        concepto_txt = self.concepto.text().lower()
        cuenta_txt = self.cuenta_combo.currentText()

        if " – " not in cuenta_txt:
            self.concepto.setStyleSheet("")
            return

        codigo = cuenta_txt.split(" – ")[0]

        try:
            if self.motor.es_concepto_valido(codigo, concepto_txt):
                self.concepto.setStyleSheet(
                    "border:2px solid #22c55e;background:#f0fdf4;"
                )
            else:
                self.concepto.setStyleSheet(
                    "border:2px solid #facc15;background:#fffbeb;"
                )
        except (AttributeError, KeyError):
            self.concepto.setStyleSheet("")

    def _calcular_importe(self):
        """Evita que ambos campos tengan valor simultáneo."""
        try:
            ing = self._parse_float(self.ui_ingreso.text())
            gas = self._parse_float(self.ui_gasto.text())

            if ing > 0 and gas > 0:
                self.ui_gasto.setText("0,00")

        except (ValueError, TypeError):
            pass

    def _duplicar(self):
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.information(self,"Duplicar","Seleccione un movimiento.")
            return

        if not self.movimientos_filtrados:
            return

        m = self.movimientos_filtrados[row]

        self.fecha.setDate(QDate.fromString(m["fecha"],"dd/MM/yyyy"))
        self.documento.clear()
        self.concepto.setText(m.get("concepto",""))

        try:
            nombre = self.data.obtener_nombre_cuenta(m["cuenta"])
            self.cuenta_combo.setCurrentText(f"{m['cuenta']} – {nombre}")
        except (KeyError, AttributeError):
            pass

        # Convert to string using _fmt to handle both float and string values
        self.ui_ingreso.setText(self._fmt(m.get("haber", 0)))
        self.ui_gasto.setText(self._fmt(m.get("debe", 0)))

        for rb in self.banco_buttons.buttons():
            if rb.text() == m.get("banco","Caja"):
                rb.setChecked(True)
                break

        estado_txt = m.get("estado","pagado").capitalize()
        for rb in self.estado_buttons.buttons():
            if rb.text() == estado_txt:
                rb.setChecked(True)
                break

    def _limpiar_formulario(self):
        self.fecha.setDate(QDate.currentDate())
        self.documento.clear()
        self.concepto.clear()
        self.ui_ingreso.setText("0,00")
        self.ui_gasto.setText("0,00")
        self.cuenta_combo.setCurrentIndex(-1)
        self.lbl_nombre.setText("Seleccione una cuenta")
        self.concepto.setStyleSheet("")

    def _limpiar_dh(self):
        self.ui_ingreso.setText("0,00")
        self.ui_gasto.setText("0,00")

    # ============================================================
    # TABLA + FILTRO + TOTALES
    # ============================================================
    def _cargar_ultimos(self):
        try:
            movs = sorted(
                self.data.movimientos,
                key=lambda m: datetime.strptime(m["fecha"], "%d/%m/%Y"),
                reverse=True
            )[:20]
        except (ValueError, KeyError, TypeError):
            movs = self.data.movimientos[:20]

        self.movimientos_filtrados = movs
        self.tabla.setRowCount(0)

        total_debe = 0
        total_haber = 0
        saldo = 0

        for m in movs:
            d = self._parse_float(m.get("debe","0"))
            h = self._parse_float(m.get("haber","0"))

            saldo += h - d  # SALDO = HABER - DEBE (ingresos - gastos)
            total_debe += d
            total_haber += h

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            try:
                nombre_cta = self.data.obtener_nombre_cuenta(m["cuenta"])
            except (KeyError, AttributeError):
                nombre_cta = "Desconocida"

            datos = [
                m.get("fecha",""),
                m.get("documento",""),
                m.get("concepto",""),
                m.get("cuenta",""),
                nombre_cta,
                self._fmt(d),
                self._fmt(h),
                m.get("banco","Caja"),
                m.get("estado","pagado"),
                self._fmt(saldo)
            ]

            for col,val in enumerate(datos):
                item = QTableWidgetItem(str(val))
                if col in (5,6,9):
                    item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.tabla.setItem(row,col,item)

        self.lbl_totales.setText(
            f"TOTAL DEBE: {self._fmt(total_debe)}  |  "
            f"TOTAL HABER: {self._fmt(total_haber)}  |  "
            f"SALDO NETO: {self._fmt(total_haber-total_debe)}"  # SALDO = HABER - DEBE
        )

    def _filtrar_tabla(self):
        txt = self.buscador.text().lower()

        for row in range(self.tabla.rowCount()):
            mostrar = False
            for col in range(self.tabla.columnCount()):
                it = self.tabla.item(row,col)
                if it and txt in it.text().lower():
                    mostrar = True
                    break
            self.tabla.setRowHidden(row, not mostrar)
