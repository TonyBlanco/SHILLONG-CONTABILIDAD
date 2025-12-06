# -*- coding: utf-8 -*-
"""
ToolsView.py — SHILLONG CONTABILIDAD v3.7.7 PRO (FINAL CON RECONCILIACIÓN)
---------------------------------------------------------
ESTADO: MASTER FINAL + ENGINE v4.3.2 + RECONCILIACIÓN DE DATOS RESTAURADA
---------------------------------------------------------
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QGridLayout, QScrollArea,
    QComboBox, QApplication, QDialog
)
from PySide6.QtGui import QColor, QPalette, QDesktopServices
from PySide6.QtCore import Qt, QUrl, QDate 
from datetime import date, datetime
from zoneinfo import ZoneInfo
import calendar
import locale
import os
import shutil
import random
import json
from collections import Counter

# --- IMPORTACIONES ---
try:
    from ui.Dialogs.ImportarExcelDialog import ImportarExcelDialog
except ImportError:
    ImportarExcelDialog = None

try:
    from core.updater import check_for_updates, get_update_info, get_local_version
    from core.version import APP_VERSION, get_full_version
except ImportError:
    check_for_updates = None
    get_update_info = None
    get_local_version = lambda: "3.7.8"
    APP_VERSION = "3.7.8"
    get_full_version = lambda: f"v{APP_VERSION} PRO"

try:
    from models.fix_data import reparar_json
except ImportError:
    reparar_json = None

try:
    from models.auto_learn import ejecutar_aprendizaje
except ImportError:
    ejecutar_aprendizaje = None

try:
    # --- NUEVO: Importación segura del diálogo de auditoría ---
    from ui.Dialogs.VerificadorBalanceDialog import VerificadorBalanceDialog
except ImportError:
    VerificadorBalanceDialog = None
# ---------------------------------------------
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    pass

# =====================================================================
# LÓGICA CABALÍSTICA Y CALENDARIO
# =====================================================================

NOMBRES_72_FALLBACK = [
    "והו","ילי","סיט","עלם","מהש","להל","אכא","כהת","הזי","אלד","לאו","ההע","יזל","מבה","הרי","הקם",
    "לאו","כלי","לוו","פהל","נלך","ייי","מלה","חהו","נתה","האא","ירת","שאה","ריי","אום","להח","כוק",
    "מנד","אני","חעם","רהע","ייז","ההה","מיכ","וול","ילה","סאל","ערי","עשל","מיה","והו","דני","החש",
    "עמם","ננא","נית","מום","פוי","נמם","ייל","הרח","מזר","ומב","יהה","ענו","מחי","דמב","מנק","איע",
    "חבו","ראה","יבמ","היי","לוו"
]

RED_DAYS = {
    (2025, 12): (27, "-"), (2026, 1): (26, "-"), (2026, 2): (23, "+"),
    (2026, 3): (24, "+"), (2026, 4): (23, "-"), (2026, 5): (22, "-"),
    (2026, 6): (21, "~"), (2026, 7): (20, "-"), (2026, 8): (19, "-"),
    (2026, 9): (18, "+"), (2026, 10): (17, "+"), (2026, 11): (16, "-"),
    (2026, 12): (15, "+")
}

EXACT_DATA = {
    (2025, 12, 1): "-", (2025, 12, 7): "-", (2025, 12, 13): "-",
    (2025, 12, 24): "-", (2025, 12, 28): "~", (2025, 12, 30): "-",
    (2025, 12, 31): "-", (2026, 1, 29): "~",
}

# =====================================================================
# DIALOGOS AUXILIARES
# =====================================================================

class DateSelectorDialog(QDialog):
    def __init__(self, current_month, current_year, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ir a fecha")
        self.setFixedSize(300, 150)
        self.setStyleSheet("background-color: white; color: black;")
        l = QVBoxLayout(self)
        l.addWidget(QLabel("Selecciona Mes y Año:", styleSheet="font-weight: bold; font-size: 14px; color: #333;"))
        h = QHBoxLayout()
        self.c_mes = QComboBox()
        self.c_mes.addItems([calendar.month_name[i].capitalize() for i in range(1, 13)])
        self.c_mes.setCurrentIndex(current_month - 1)
        self.c_anio = QComboBox()
        self.c_anio.addItems([str(y) for y in range(2024, 2031)])
        self.c_anio.setCurrentText(str(current_year))
        st = "padding: 5px; border: 1px solid #ccc; border-radius: 4px;"
        self.c_mes.setStyleSheet(st); self.c_anio.setStyleSheet(st)
        h.addWidget(self.c_mes); h.addWidget(self.c_anio)
        l.addLayout(h)
        btn = QPushButton("IR A FECHA")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.accept)
        btn.setStyleSheet("background-color: #ed1c24; color: white; font-weight: bold; padding: 10px; border-radius: 5px; margin-top: 10px;")
        l.addWidget(btn)

    def get_data(self):
        return self.c_mes.currentIndex() + 1, int(self.c_anio.currentText())

class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calendario Cabalístico")
        self.resize(500, 680)
        self.setStyleSheet("QDialog { background-color: #ffffff; color: #000000; } QLabel { color: #000000; font-family: 'Arial'; } QPushButton { border: none; background: transparent; }")
        
        self.dia_hoy = date.today()
        self.anio_actual = self.dia_hoy.year
        self.mes_actual = self.dia_hoy.month
        
        self.nombres_list = NOMBRES_72_FALLBACK
        try:
            if os.path.exists("data/kabbalah_72.json"):
                with open("data/kabbalah_72.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.nombres_list = [d["nombre"] for d in data]
                    while len(self.nombres_list) < 72:
                        self.nombres_list.append("???")
        except (IOError, json.JSONDecodeError, KeyError):
            pass
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(0)
        
        self.lbl_today = QLabel(f"TODAY IS {self.dia_hoy.strftime('%B %d, %Y').upper()}")
        self.lbl_today.setAlignment(Qt.AlignCenter)
        self.lbl_today.setStyleSheet("font-size: 11px; font-weight: bold; color: #888; letter-spacing: 1px; margin-bottom: 5px;")
        layout.addWidget(self.lbl_today)
        
        nav = QHBoxLayout()
        nav.setContentsMargins(10, 0, 10, 20)
        
        b_prev = QPushButton("❮")
        b_prev.clicked.connect(self._prev)
        b_prev.setFixedSize(40, 40)
        b_prev.setStyleSheet("font-size:24px;color:#ccc;")
        
        b_next = QPushButton("❯")
        b_next.clicked.connect(self._next)
        b_next.setFixedSize(40, 40)
        b_next.setStyleSheet("font-size:24px;color:#ccc;")
        
        self.b_tit = QPushButton()
        self.b_tit.clicked.connect(self._sel)
        self.b_tit.setStyleSheet("font-size:30px; font-weight:800; color:#000;")
        
        nav.addWidget(b_prev)
        nav.addWidget(self.b_tit, 1)
        nav.addWidget(b_next)
        layout.addWidget(QWidget(layout=nav))
        
        self.grid_frame = QWidget()
        self.grid = QGridLayout(self.grid_frame)
        self.grid.setContentsMargins(15, 0, 15, 0)
        self.grid.setSpacing(0)
        layout.addWidget(self.grid_frame)
        layout.addStretch()
        self._render()

    def _render(self):
        while self.grid.count():
            it = self.grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
                
        self.b_tit.setText(f"{calendar.month_name[self.mes_actual]} {self.anio_actual}")
        for i, d in enumerate(["S","M","T","W","T","F","S"]):
            l = QLabel(d)
            l.setAlignment(Qt.AlignCenter)
            l.setStyleSheet("font-weight:900; padding-bottom:20px;")
            self.grid.addWidget(l, 0, i)
            
        calendar.setfirstweekday(6)
        cal = calendar.monthcalendar(self.anio_actual, self.mes_actual)
        red = RED_DAYS.get((self.anio_actual, self.mes_actual), (-99, ""))[0]
        
        for r, week in enumerate(cal, 1):
            for c, day in enumerate(week):
                if day != 0:
                    dt = date(self.anio_actual, self.mes_actual, day)
                    self.grid.addWidget(self._make_btn(dt, day, day == red), r, c)
                else:
                    l = QLabel()
                    l.setStyleSheet("border-bottom: 1px solid #eee;")
                    self.grid.addWidget(l, r, c)

    def _prev(self):
        self.mes_actual -= 1
        if self.mes_actual < 1:
            self.mes_actual = 12
            self.anio_actual -= 1
        self._render()

    def _next(self):
        self.mes_actual += 1
        if self.mes_actual > 12:
            self.mes_actual = 1
            self.anio_actual += 1
        self._render()

    def _sel(self):
        dlg = DateSelectorDialog(self.mes_actual, self.anio_actual, self)
        if dlg.exec():
            m, y = dlg.get_data()
            self.mes_actual = m
            self.anio_actual = y
            self._render()

    def _make_btn(self, dt, day, is_red):
        idx = (dt - date(2000, 1, 1)).days % 72
        name = self.nombres_list[idx]
        
        signo, info = "+", "Positivo"
        if dt.weekday() == 5:
            signo, info = "", "SHABBAT"
        elif is_red:
            signo, info = RED_DAYS.get((dt.year, dt.month), ("", ""))[1], "ROSH CHODESH"
        elif (dt.year, dt.month, dt.day) in EXACT_DATA:
            signo, info = EXACT_DATA[(dt.year, dt.month, dt.day)], "Especial"

        btn = QPushButton(f"{day}\n{signo}" if signo else f"{day}")
        btn.setFixedSize(58, 62)
        btn.setCursor(Qt.PointingHandCursor)
        
        st = "border:none; border-bottom:1px solid #eee;"
        if is_red:
            st = "background-color:#ed1c24; color:white; font-weight:bold;"
        elif dt == self.dia_hoy:
            st = "background-color:#fff0f0; border:2px solid #ed1c24; font-weight:900; border-radius:6px;"
        
        btn.setStyleSheet(st)
        btn.clicked.connect(lambda: QMessageBox.information(self, f"{dt}", f"Energía: {info}\nNombre: {name}"))
        return btn

# =====================================================================
# CLASE PRINCIPAL TOOLSVIEW
# =====================================================================
class ToolsView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.data_kabbalah = []
        self._cargar_kabbalah()

        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        self.layout.addWidget(QLabel("Herramientas", styleSheet="font-size:22px; font-weight:800; color:#1e293b;"))

        self._setup_salmo(self.layout)

        self.layout.addWidget(QLabel("Calendarios", styleSheet="font-weight:bold; margin-top:10px;"))
        b_cal = QPushButton("ABRIR CALENDARIO KABBALAH")
        b_cal.setCursor(Qt.PointingHandCursor)
        b_cal.setFixedHeight(45)
        b_cal.clicked.connect(lambda: CalendarDialog(self).exec())
        b_cal.setStyleSheet("background-color:#000; color:#fff; font-weight:bold; border-radius:6px;")
        self.layout.addWidget(b_cal)

        lbl_data = QLabel("Gestión de Datos")
        lbl_data.setStyleSheet("font-size: 14px; font-weight: bold; color: #475569; margin-top: 10px;")
        self.layout.addWidget(lbl_data)
        self.layout.addWidget(self._panel_datos())

        lbl_sys = QLabel("Sistema")
        lbl_sys.setStyleSheet("font-size: 14px; font-weight: bold; color: #475569; margin-top: 10px;")
        self.layout.addWidget(lbl_sys)
        self.layout.addWidget(self._panel_sistema())

        self.layout.addStretch()
        scroll.setWidget(content)
        main_l.addWidget(scroll)
        self._new_msg()

    def _cargar_kabbalah(self):
        try:
            path = "data/kabbalah_72.json"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.data_kabbalah = json.load(f)
        except (IOError, json.JSONDecodeError):
            self.data_kabbalah = []

    def _setup_salmo(self, l):
        card = QFrame()
        card.setStyleSheet("background-color:#fefce8; border:1px solid #fde047; border-radius:10px;")
        card.setMaximumHeight(100)
        h = QHBoxLayout(card)
        h.setContentsMargins(15, 10, 15, 10)
        
        self.lbl_h = QLabel()
        self.lbl_h.setStyleSheet("font-size:24px; font-weight:bold; color:#1e3a8a;")
        
        self.lbl_m = QLabel()
        self.lbl_m.setStyleSheet("font-size:13px; font-style:italic; color:#451a03;")
        self.lbl_m.setWordWrap(True)
        
        btn = QPushButton("Nueva inspiración")
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._new_msg)
        btn.setStyleSheet("border:1px solid #b45309; border-radius:15px; color:#b45309;")
        
        h.addWidget(self.lbl_h)
        h.addWidget(self.lbl_m, 1)
        h.addWidget(btn)
        l.addWidget(card)

    def _new_msg(self):
        if self.data_kabbalah:
            item = random.choice(self.data_kabbalah)
            self.lbl_h.setText(item.get("nombre", "???"))
            self.lbl_m.setText(f"{item.get('salmo', 'Salmo desconocido')}\n({item.get('significado', '')})")
        else:
            self.lbl_h.setText("יהוה")
            self.lbl_m.setText("El Señor es mi pastor, nada me falta.")

    def _estilo_btn(self, col):
        return f"""
            QPushButton {{
                background-color: {col};
                color: white;
                font-weight: 600;
                border-radius: 6px;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """

    def _reconciliar_duplicados(self):
        """Busca y reporta movimientos duplicados en la base de datos de contabilidad."""
        # NOTA: ASUMIMOS que self.data.movimientos es una lista de objetos con atributos .fecha, .concepto, .valor, .tipo
        if not hasattr(self.data, 'movimientos') or not self.data.movimientos:
            QMessageBox.information(self, "Reconciliación", "La base de datos está vacía. No hay datos que reconciliar.")
            return

        huellas = {}
        duplicados = []
        
        # Un duplicado se define por la combinación de Fecha, Concepto y Valor
        for i, mov in enumerate(self.data.movimientos):
            try:
                # Creando una huella única (hash)
                huella = (
                    mov.fecha, 
                    mov.concepto, 
                    mov.valor, 
                    mov.tipo 
                )
            except AttributeError:
                # Si falta algún atributo, saltar el movimiento (o loguear el error)
                continue
            
            if huella in huellas:
                duplicados.append((i, mov))
            else:
                huellas[huella] = i
        
        if duplicados:
            mensaje = f"⚠️ Se encontraron {len(duplicados)} movimientos duplicados potenciales.\n"
            mensaje += "Se recomienda revisar el archivo de origen (JSON) y eliminar los movimientos redundantes antes de importar.\n"
            
            detalles = "\nDetalles de Duplicados Encontrados (Índice | Fecha | Concepto | Valor):\n"
            for i, mov in duplicados:
                fecha_str = mov.fecha.strftime('%Y-%m-%d') if hasattr(mov, 'fecha') else 'N/A'
                concepto_str = str(mov.concepto)[:30] + '...' if hasattr(mov, 'concepto') else 'N/A'
                valor_str = f"{mov.valor:.2f}" if hasattr(mov, 'valor') else 'N/A'
                
                detalles += f"Índice {i}: {fecha_str} | {concepto_str} | {valor_str}\n"
            
            QMessageBox.warning(self, "DUPLICADOS DETECTADOS", mensaje, QMessageBox.Open | QMessageBox.Close)
            
            # Muestra los detalles en una ventana separada
            detalles_msg = QMessageBox(self)
            detalles_msg.setWindowTitle("Detalles de Duplicados")
            detalles_msg.setText("Se encontraron duplicados, revisa la lista para depurar.")
            detalles_msg.setDetailedText(detalles)
            detalles_msg.exec()

        else:
            QMessageBox.information(self, "Reconciliación", "✅ Base de datos limpia: No se encontraron movimientos duplicados.")


    def _panel_datos(self):
        f = QFrame()
        f.setStyleSheet("background:white; border:1px solid #e2e8f0; border-radius:8px;")
        g = QGridLayout(f)
        g.setContentsMargins(15, 15, 15, 15)
        g.setSpacing(10)

        def mk_btn(txt, func, col):
            b = QPushButton(txt)
            b.clicked.connect(func)
            b.setStyleSheet(self._estilo_btn(col))
            b.setFixedHeight(40)
            b.setCursor(Qt.PointingHandCursor)
            return b

        g.addWidget(mk_btn("Backup", self._backup, "#16a34a"), 0, 0)
        g.addWidget(mk_btn("Restaurar", self._restore, "#ea580c"), 0, 1)
        g.addWidget(mk_btn("Importar Excel", self._excel, "#0d9488"), 1, 0)
        g.addWidget(mk_btn("Abrir Carpeta", self._carpeta, "#3b82f6"), 1, 1)
        g.addWidget(mk_btn("Auto-Aprender Conceptos", self._aprender, "#8b5cf6"), 2, 0)
        g.addWidget(mk_btn("Reparar Debe/Haber", self._reparar, "#db2777"), 2, 1)
        # --- NUEVA HERRAMIENTA 1: Reconciliación (EXISTENTE) ---
        g.addWidget(mk_btn("Reconciliar/Depurar Datos", self._reconciliar_duplicados, "#059669"), 3, 0, 1, 2)
        # --- NUEVA HERRAMIENTA 2: Auditoría Debe/Haber (AÑADIDA) ---
        g.addWidget(mk_btn("Auditoría Balance (Corregir Debe/Haber)", self._abrir_verificador, "#3b82f6"), 4, 0, 1, 2) 
        # --- NUEVA HERRAMIENTA 3: Auditoría rápida de datos ---
        g.addWidget(mk_btn("Auditoría Rápida (datos)", self._auditoria_ligera, "#2563eb"), 5, 0, 1, 2)
        # -----------------------------------
        return f

    # PANEL DE SISTEMA SIN RELOJ MUNDIAL
    def _panel_sistema(self):
        f = QFrame()
        f.setStyleSheet("background:white; border:1px solid #e2e8f0; border-radius:8px;")
        h = QHBoxLayout(f)
        h.setContentsMargins(15, 15, 15, 15)
        h.setSpacing(10)

        def mk_btn(txt, func, col):
            b = QPushButton(txt)
            b.clicked.connect(func)
            b.setStyleSheet(self._estilo_btn(col))
            b.setFixedHeight(40)
            b.setCursor(Qt.PointingHandCursor)
            return b

        h.addWidget(mk_btn("Tema", self._tema, "#475569"))
        h.addWidget(mk_btn("Updates", self._update, "#7c3aed"))
        h.addWidget(mk_btn("Verificar JSON", self._verificar_json, "#059669"))
        h.addWidget(mk_btn("Importar JSON", self._importar_json, "#7c3aed"))
        h.addWidget(mk_btn("Calculadora", self._abrir_calculadora, "#dc2626")) 
        return f

    # ================================================================
    # LÓGICA DE AUDITORÍA (NUEVO CÓDIGO AÑADIDO)
    # ================================================================
    def _auditar_movimientos(self):
        """Busca errores de Debe/Haber y devuelve una lista."""
        errores = []
        
        # Función local para normalizar los valores del JSON (que vienen como strings)
        def _normalizar(txt):
            try:
                # Esta función es crucial si los valores en el JSON están como "1.550,00" o "1550"
                return float(str(txt).replace(",", "."))
            except (ValueError, TypeError):
                return 0.0

        if not hasattr(self.data, 'movimientos'):
            QMessageBox.critical(self, "Error de Datos", "La propiedad 'movimientos' no está disponible en self.data.")
            return []
            
        for i, mov in enumerate(self.data.movimientos):
            debe = _normalizar(mov.get("debe", "0.00"))
            haber = _normalizar(mov.get("haber", "0.00"))
            
            error_msg = None
            
            # Regla A: Ambos son cero (No es un movimiento contable válido)
            if debe == 0.0 and haber == 0.0:
                error_msg = "Ambos Debe y Haber son CERO."
            
            # Regla B: Ambos son mayores que cero (Rompe la partida doble a nivel de registro simple)
            elif debe > 0.0 and haber > 0.0:
                error_msg = "Debe y Haber coexisten (> 0)."
            
            if error_msg:
                errores.append({
                    "index": i,
                    "movimiento": mov,
                    "error": error_msg,
                })
                
        return errores

    def _auditoria_ligera(self):
        """Chequeo rápido de datos faltantes/duplicados con resumen de totales."""
        movs = getattr(self.data, "movimientos", [])
        if not movs:
            QMessageBox.information(self, "Auditoría", "No hay movimientos cargados.")
            return

        total_debe = total_haber = 0.0
        anomalies = []
        docs = []

        for idx, m in enumerate(movs, 1):
            debe = float(m.get("debe", 0) or 0)
            haber = float(m.get("haber", 0) or 0)
            total_debe += debe
            total_haber += haber

            doc = str(m.get("documento", "")).strip()
            cuenta = str(m.get("cuenta", "")).strip()
            banco = str(m.get("banco", "")).strip()

            if doc:
                docs.append(doc)
            else:
                anomalies.append(f"Fila {idx}: sin documento")
            if not cuenta:
                anomalies.append(f"Fila {idx}: sin cuenta")
            if not banco:
                anomalies.append(f"Fila {idx}: sin banco")
            if (debe > 0 and haber > 0) or (debe == 0 and haber == 0):
                anomalies.append(f"Fila {idx}: Debe/Haber inválidos (debe={debe}, haber={haber})")

        # Duplicados de documentos
        c_docs = Counter(docs)
        dupes = [d for d, c in c_docs.items() if c > 1]
        if dupes:
            anomalies.append(f"Documentos duplicados: {', '.join(dupes)}")

        diff = total_haber - total_debe
        resumen = (
            f"Total Debe: {total_debe:,.2f}\n"
            f"Total Haber: {total_haber:,.2f}\n"
            f"Diferencia (H-D): {diff:,.2f}"
        )

        if anomalies:
            detalle = "\n".join(anomalies[:30])  # limitar para no saturar
            QMessageBox.warning(
                self,
                "Auditoría con observaciones",
                f"{resumen}\n\nSe detectaron {len(anomalies)} observaciones:\n{detalle}"
            )
        else:
            QMessageBox.information(
                self,
                "Auditoría OK",
                f"{resumen}\n\nTodo correcto. No se detectaron anomalías de datos."
            )

    def _abrir_verificador(self):
        """Ejecuta la auditoría y muestra la ventana de corrección si hay errores."""
        if VerificadorBalanceDialog is None:
            QMessageBox.critical(self, "Error", "No se encontró el módulo VerificadorBalanceDialog.py. Asegúrese de crearlo.")
            return

        errores = self._auditar_movimientos()
        
        if not errores:
            QMessageBox.information(self, "Verificación OK", "🎉 ¡Base de Datos limpia! No se encontraron errores de Debe/Haber.")
            return

        # Abrir la ventana de corrección
        dlg = VerificadorBalanceDialog(self.data, errores, self)
        if dlg.exec():
            # Si el usuario hace clic en Guardar
            if hasattr(self.parent(), "actualizar_vistas"):
                 self.parent().actualizar_vistas()
                 
    # ================================================================
    # CALCULADORA DEL SISTEMA (FUNCIÓN RESTAURADA)
    # ================================================================
    def _abrir_calculadora(self):
        try:
            if os.name == 'nt':  # Windows
                os.startfile('calc.exe')
            elif os.name == 'posix':
                if shutil.which('gnome-calculator'):
                    os.system('gnome-calculator &')
                elif shutil.which('kcalc'):
                    os.system('kcalc &')
                elif os.uname().sysname == 'Darwin':
                    os.system('open -a Calculator')
                else:
                    QMessageBox.information(self, "Calculadora", "Calculadora abierta (si está disponible).")
            QMessageBox.information(self, "Calculadora", "Calculadora del sistema abierta.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir la calculadora:\n{e}")

    # ================================================================
    # FUNCIONES RESTANTES (EXISTENTES)
    # ================================================================
    def _verificar_json(self):
        ruta = str(self.data.archivo_json)
        if not os.path.exists(ruta):
            QMessageBox.warning(self, "JSON no encontrado", f"El archivo no existe:\n{ruta}")
            return

        tamaño = os.path.getsize(ruta)
        mod = datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%d/%m/%Y %H:%M:%S")
        mensaje = f"""
        <h2>Estado del archivo JSON</h2>
        <b>Ruta:</b> {ruta}<br>
        <b>Tamaño:</b> {tamaño/1024:.2f} KB<br>
        <b>Última modificación:</b> {mod}<br>
        <b>Movimientos cargados:</b> {len(self.data.movimientos)}
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Estado del archivo JSON")
        msg.setTextFormat(Qt.RichText)
        msg.setText(mensaje)
        msg.exec()

    def _importar_json(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo JSON de SHILLONG", "", "JSON (*.json)")
        if not ruta:
            return
        try:
            backup = str(self.data.archivo_json) + ".backup"
            if os.path.exists(self.data.archivo_json):
                shutil.copy2(self.data.archivo_json, backup)
            self.data.asignar_archivo(ruta)
            QMessageBox.information(self, "JSON Importado", f"Nuevo archivo cargado:\n{ruta}\n\nBackup creado:\n{backup}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo importar:\n{e}")

    def _backup(self):
        try:
            name = f"backup_{datetime.now().strftime('%Y%m%d')}.json"
            dest, _ = QFileDialog.getSaveFileName(self, "Guardar backup", name, "JSON (*.json)")
            if dest:
                shutil.copy2(self.data.archivo_json, dest)
                QMessageBox.information(self, "OK", "Backup creado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _restore(self):
        f, _ = QFileDialog.getOpenFileName(self, "Restaurar backup", "", "JSON (*.json)")
        if f and QMessageBox.question(self, "Confirmar", "¿Restaurar datos antiguos?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            shutil.copy2(f, self.data.archivo_json)
            self.data.cargar()
            QMessageBox.information(self, "OK", "Datos restaurados. Reinicia la app.")

    def _excel(self):
        if ImportarExcelDialog:
            if ImportarExcelDialog(self, self.data).exec():
                QMessageBox.information(self, "OK", "Datos importados desde Excel.")
        else:
            QMessageBox.warning(self, "Error", "Módulo de importación no disponible.")

    def _carpeta(self):
        path = os.path.abspath("data")
        os.makedirs(path, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _tema(self):
        app = QApplication.instance()
        p = app.palette()
        oscuro = p.color(QPalette.Window).lightness() > 128
        bg = QColor(30, 41, 59) if oscuro else QColor(248, 250, 252)
        txt = QColor(255, 255, 255) if oscuro else QColor(15, 23, 42)
        p.setColor(QPalette.Window, bg)
        p.setColor(QPalette.WindowText, txt)
        app.setPalette(p)

    def _update(self):
        """Check for updates and notify user."""
        if check_for_updates is None or get_update_info is None:
            QMessageBox.information(
                self, 
                "Versión", 
                f"SHILLONG CONTABILIDAD v{APP_VERSION}\nEngine v4.3.2\n\n"
                "⚠️ El verificador de actualizaciones no está disponible."
            )
            return
        
        # Show loading cursor
        self.setCursor(Qt.WaitCursor)
        
        try:
            info = get_update_info()
            self.setCursor(Qt.ArrowCursor)
            
            if info["available"]:
                # Update available - show detailed dialog
                msg = QMessageBox(self)
                msg.setWindowTitle("🎉 ¡Actualización Disponible!")
                msg.setIcon(QMessageBox.Information)
                msg.setText(
                    f"<h3>Nueva versión disponible: v{info['remote_version']}</h3>"
                    f"<p>Tu versión actual: v{info['local_version']}</p>"
                )
                
                # Add release notes if available
                if info.get("release_notes"):
                    notes = info["release_notes"][:400]
                    if len(info["release_notes"]) > 400:
                        notes += "..."
                    msg.setInformativeText(f"📋 Notas de la versión:\n{notes}")
                
                # Add buttons
                btn_download = msg.addButton("⬇️ Descargar Ahora", QMessageBox.AcceptRole)
                btn_later = msg.addButton("Más Tarde", QMessageBox.RejectRole)
                
                msg.exec()
                
                if msg.clickedButton() == btn_download:
                    # Open download URL in browser
                    if info.get("download_url"):
                        QDesktopServices.openUrl(QUrl(info["download_url"]))
                        QMessageBox.information(
                            self,
                            "Descarga Iniciada",
                            "Se ha abierto tu navegador para descargar la actualización.\n\n"
                            "Después de instalar, reinicia SHILLONG para aplicar los cambios."
                        )
            else:
                # No update available
                QMessageBox.information(
                    self,
                    "✅ Versión Actualizada",
                    f"<h3>Estás usando la última versión</h3>"
                    f"<p><b>Versión:</b> v{info['local_version']} PRO</p>"
                    f"<p><b>Engine:</b> v4.3.2</p>"
                    f"<p>No hay actualizaciones disponibles.</p>"
                )
                
        except Exception as e:
            self.setCursor(Qt.ArrowCursor)
            QMessageBox.warning(
                self,
                "Error de Conexión",
                f"No se pudo verificar actualizaciones.\n\n"
                f"Versión actual: v{APP_VERSION} PRO\n\n"
                f"Error: {str(e)[:100]}"
            ) 

    def _reparar(self):
        if reparar_json and QMessageBox.question(self, "Reparar", "¿Corregir Debe/Haber invertidos?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            reparar_json(str(self.data.archivo_json))
            self.data.cargar()
            QMessageBox.information(self, "OK", "Base de datos reparada.")

    def _aprender(self):
        if not ejecutar_aprendizaje:
            QMessageBox.warning(self, "Error", "Módulo de auto-aprendizaje no encontrado.")
            return
        self.setCursor(Qt.WaitCursor)
        num, msg = ejecutar_aprendizaje(str(self.data.archivo_json))
        self.setCursor(Qt.ArrowCursor)
        titulo = "Aprendizaje completado" if num > 0 else "Sin cambios"
        QMessageBox.information(self, titulo, msg)
