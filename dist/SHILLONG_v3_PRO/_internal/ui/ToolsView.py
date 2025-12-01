# -*- coding: utf-8 -*-
"""
ToolsView.py — SHILLONG CONTABILIDAD v3.6.1 PRO
---------------------------------------------------------
ESTADO: MASTER FINAL + CALENDARIO RESTAURADO + JSON 72 NOMBRES
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
import calendar
import locale
import os
import shutil
import random
import json

# --- IMPORTACIONES ---
try:
    from ui.Dialogs.ImportarExcelDialog import ImportarExcelDialog
except ImportError:
    ImportarExcelDialog = None

try:
    from updater import Updater
    from version import APP_VERSION
except ImportError:
    Updater = None
    APP_VERSION = "3.6.1"

# Scripts de Mantenimiento
try:
    from models.fix_data import reparar_json
except ImportError:
    reparar_json = None

try:
    from models.auto_learn import ejecutar_aprendizaje
except ImportError:
    ejecutar_aprendizaje = None

# Configuración de fecha
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass

# =====================================================================
#  LÓGICA CABALÍSTICA Y CALENDARIO (RESTAURADO)
# =====================================================================

# Lista de reserva por si falla el JSON
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
        
        # Cargar nombres del JSON si existen
        self.nombres_list = NOMBRES_72_FALLBACK
        try:
            if os.path.exists("data/kabbalah_72.json"):
                with open("data/kabbalah_72.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Extraer solo los nombres hebreos para el calendario
                    self.nombres_list = [d["nombre"] for d in data]
                    # Rellenar hasta 72 si faltan
                    while len(self.nombres_list) < 72: self.nombres_list.append("???")
        except: pass
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(0)
        
        self.lbl_today = QLabel(f"TODAY IS {self.dia_hoy.strftime('%B %d, %Y').upper()}")
        self.lbl_today.setAlignment(Qt.AlignCenter)
        self.lbl_today.setStyleSheet("font-size: 11px; font-weight: bold; color: #888; letter-spacing: 1px; margin-bottom: 5px;")
        layout.addWidget(self.lbl_today)
        
        nav = QHBoxLayout()
        nav.setContentsMargins(10, 0, 10, 20)
        
        b_prev = QPushButton("❮"); b_prev.clicked.connect(self._prev)
        b_prev.setFixedSize(40,40); b_prev.setStyleSheet("font-size:24px;color:#ccc;")
        
        b_next = QPushButton("❯"); b_next.clicked.connect(self._next)
        b_next.setFixedSize(40,40); b_next.setStyleSheet("font-size:24px;color:#ccc;")
        
        self.b_tit = QPushButton(); self.b_tit.clicked.connect(self._sel)
        self.b_tit.setStyleSheet("font-size:30px; font-weight:800; color:#000;")
        
        nav.addWidget(b_prev); nav.addWidget(self.b_tit, 1); nav.addWidget(b_next)
        layout.addWidget(QWidget(layout=nav))
        
        self.grid_frame = QWidget()
        self.grid = QGridLayout(self.grid_frame)
        self.grid.setContentsMargins(15, 0, 15, 0); self.grid.setSpacing(0)
        layout.addWidget(self.grid_frame)
        
        layout.addStretch()
        self._render()

    def _render(self):
        while self.grid.count(): 
            it = self.grid.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            
        self.b_tit.setText(f"{calendar.month_name[self.mes_actual]} {self.anio_actual}")
        for i, d in enumerate(["S","M","T","W","T","F","S"]):
            l = QLabel(d); l.setAlignment(Qt.AlignCenter); l.setStyleSheet("font-weight:900; padding-bottom:20px;")
            self.grid.addWidget(l, 0, i)
            
        calendar.setfirstweekday(6)
        cal = calendar.monthcalendar(self.anio_actual, self.mes_actual)
        red = RED_DAYS.get((self.anio_actual, self.mes_actual), (-99, ""))[0]
        
        for r, week in enumerate(cal, 1):
            for c, day in enumerate(week):
                if day != 0:
                    dt = date(self.anio_actual, self.mes_actual, day)
                    self.grid.addWidget(self._make_btn(dt, day, day==red), r, c)
                else:
                    l = QLabel(); l.setStyleSheet("border-bottom: 1px solid #eee;")
                    self.grid.addWidget(l, r, c)

    def _prev(self):
        self.mes_actual -= 1
        if self.mes_actual < 1: self.mes_actual=12; self.anio_actual-=1
        self._render()
    def _next(self):
        self.mes_actual += 1
        if self.mes_actual > 12: self.mes_actual=1; self.anio_actual+=1
        self._render()
    def _sel(self):
        dlg = DateSelectorDialog(self.mes_actual, self.anio_actual, self)
        if dlg.exec(): m, y = dlg.get_data(); self.mes_actual=m; self.anio_actual=y; self._render()

    def _make_btn(self, dt, day, is_red):
        idx = (dt - date(2000,1,1)).days % 72
        # USAR LISTA CORRECTA
        name = self.nombres_list[idx]
        
        signo, info = "+", "Positivo"
        if dt.weekday() == 5: signo, info = "", "SHABBAT"
        elif is_red: signo, info = RED_DAYS.get((dt.year, dt.month))[1], "ROSH CHODESH"
        elif (dt.year, dt.month, dt.day) in EXACT_DATA: signo, info = EXACT_DATA[(dt.year, dt.month, dt.day)], "Especial"

        btn = QPushButton(f"{day}\n{signo}" if signo else f"{day}")
        btn.setFixedSize(58, 62)
        btn.setCursor(Qt.PointingHandCursor)
        
        st = "border:none; border-bottom:1px solid #eee;"
        if is_red: st = "background-color:#ed1c24; color:white; font-weight:bold;"
        elif dt == self.dia_hoy: st = "background-color:#fff0f0; border:2px solid #ed1c24; font-weight:900; border-radius:6px;"
        
        btn.setStyleSheet(st)
        btn.clicked.connect(lambda: QMessageBox.information(self, f"{dt}", f"Energía: {info}\nNombre: {name}"))
        return btn

# =====================================================================
#  CLASE PRINCIPAL TOOLSVIEW
# =====================================================================
class ToolsView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        
        # Cargar datos cabalísticos del JSON
        self.data_kabbalah = []
        self._cargar_kabbalah()

        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0,0,0,0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(30,30,30,30)
        self.layout.setSpacing(20) 
        
        self.layout.addWidget(QLabel("🛠️ Herramientas", styleSheet="font-size:22px; font-weight:800; color:#1e293b;"))

        # 1. INSPIRACIÓN (Conectada al JSON)
        self._setup_salmo(self.layout)

        # 2. CALENDARIO
        self.layout.addWidget(QLabel("📅 Calendarios", styleSheet="font-weight:bold; margin-top:10px;"))
        b_cal = QPushButton("ABRIR CALENDARIO KABBALAH")
        b_cal.setCursor(Qt.PointingHandCursor)
        b_cal.setFixedHeight(45)
        b_cal.clicked.connect(lambda: CalendarDialog(self).exec())
        b_cal.setStyleSheet("background-color:#000; color:#fff; font-weight:bold; border-radius:6px;")
        self.layout.addWidget(b_cal)

        # 3. PANELES
        lbl_data = QLabel("Gestión de Datos")
        lbl_data.setStyleSheet("font-size: 14px; font-weight: bold; color: #475569; margin-top: 10px;")
        self.layout.addWidget(lbl_data)
        self.layout.addWidget(self._panel_datos())

        lbl_sys = QLabel("Sistema")
        lbl_sys.setStyleSheet("font-size: 14px; font-weight: bold; color: #475569; margin-top: 10px;")
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
        except:
            self.data_kabbalah = []

    # --- UI HELPERS ---
    def _setup_salmo(self, l):
        card = QFrame()
        card.setStyleSheet("background-color:#fefce8; border:1px solid #fde047; border-radius:10px;")
        card.setMaximumHeight(100) 
        h = QHBoxLayout(card)
        h.setContentsMargins(15,10,15,10)
        
        self.lbl_h = QLabel()
        self.lbl_h.setStyleSheet("font-size:24px; font-weight:bold; color:#1e3a8a;")
        
        self.lbl_m = QLabel()
        self.lbl_m.setStyleSheet("font-size:13px; font-style:italic; color:#451a03;")
        self.lbl_m.setWordWrap(True)
        
        btn = QPushButton("✨")
        btn.setFixedSize(30,30)
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
            nombre = item.get("nombre", "???")
            salmo = item.get("salmo", "Salmo desconocido")
            sig = item.get("significado", "")
            self.lbl_h.setText(nombre)
            self.lbl_m.setText(f"{salmo}\n({sig})")
        else:
            # Fallback
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

    def _panel_datos(self):
        f = QFrame()
        f.setStyleSheet("background:white; border:1px solid #e2e8f0; border-radius:8px;")
        g = QGridLayout(f)
        g.setContentsMargins(15,15,15,15)
        g.setSpacing(10)

        def mk_btn(txt, func, col):
            b = QPushButton(txt)
            b.clicked.connect(func)
            b.setStyleSheet(self._estilo_btn(col))
            b.setFixedHeight(40) 
            b.setCursor(Qt.PointingHandCursor)
            return b

        g.addWidget(mk_btn("📦 Backup", self._backup, "#16a34a"), 0, 0)
        g.addWidget(mk_btn("♻️ Restaurar", self._restore, "#ea580c"), 0, 1)
        g.addWidget(mk_btn("📥 Importar Excel", self._excel, "#0d9488"), 1, 0)
        g.addWidget(mk_btn("📂 Abrir Carpeta", self._carpeta, "#3b82f6"), 1, 1)

        b_learn = mk_btn("🧠 Auto-Aprender Conceptos", self._aprender, "#8b5cf6") 
        g.addWidget(b_learn, 2, 0)

        b_fix = mk_btn("🔧 Reparar Debe/Haber", self._reparar, "#db2777") 
        g.addWidget(b_fix, 2, 1)
        
        return f

    def _panel_sistema(self):
        f = QFrame()
        f.setStyleSheet("background:white; border:1px solid #e2e8f0; border-radius:8px;")
        h = QHBoxLayout(f)
        h.setContentsMargins(15,15,15,15)
        h.setSpacing(10)
        
        def mk_btn(txt, func, col):
            b = QPushButton(txt)
            b.clicked.connect(func)
            b.setStyleSheet(self._estilo_btn(col))
            b.setFixedHeight(40)
            b.setCursor(Qt.PointingHandCursor)
            return b
        
        h.addWidget(mk_btn("🌗 Tema", self._tema, "#475569"))
        h.addWidget(mk_btn("🔄 Updates", self._update, "#7c3aed"))
        return f

    # --- LÓGICA ---
    def _backup(self):
        try:
            name = f"backup_{datetime.now().strftime('%Y%m%d')}.json"
            dest, _ = QFileDialog.getSaveFileName(self, "Guardar", name, "JSON (*.json)")
            if dest:
                shutil.copy2(self.data.archivo_json, dest)
                QMessageBox.information(self, "OK", "Backup creado.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _restore(self):
        f, _ = QFileDialog.getOpenFileName(self, "Abrir", "", "JSON (*.json)")
        if f and QMessageBox.question(self,"?","¿Restaurar datos antiguos?",QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            shutil.copy2(f, self.data.archivo_json)
            self.data.cargar()
            QMessageBox.information(self, "OK", "Datos restaurados. Reinicia si es necesario.")

    def _excel(self):
        if ImportarExcelDialog: 
            if ImportarExcelDialog(self, self.data).exec(): 
                QMessageBox.information(self, "OK", "Importado.")
        else: QMessageBox.warning(self, "Error", "Falta ImportarExcelDialog")

    def _carpeta(self):
        path = os.path.abspath("data")
        if not os.path.exists(path): os.makedirs(path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _tema(self):
        app = QApplication.instance(); p = app.palette()
        c = QColor(30,41,59) if p.color(QPalette.Window).lightness() > 128 else QColor(248,250,252)
        p.setColor(QPalette.Window, c); p.setColor(QPalette.WindowText, QColor(255,255,255) if c.lightness()<128 else QColor(15,23,42))
        app.setPalette(p)

    def _update(self):
        QMessageBox.information(self, "Info", f"Versión actual: {APP_VERSION}")

    def _reparar(self):
        if reparar_json:
            if QMessageBox.question(self, "?", "¿Reparar Debe/Haber invertidos?", QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
                reparar_json(str(self.data.archivo_json))
                self.data.cargar()
                QMessageBox.information(self, "OK", "Reparado.")
        else:
            QMessageBox.warning(self, "Error", "Script no encontrado")

    def _aprender(self):
        if ejecutar_aprendizaje is None:
            QMessageBox.warning(self, "Error", "No se encuentra models/auto_learn.py")
            return
        
        ruta_json = str(self.data.archivo_json)
        self.setCursor(Qt.WaitCursor)
        num, mensaje = ejecutar_aprendizaje(ruta_movimientos=ruta_json)
        self.setCursor(Qt.ArrowCursor)
        
        if num > 0:
            QMessageBox.information(self, "Aprendizaje", f"✅ {mensaje}")
        else:
            QMessageBox.information(self, "Info", f"ℹ️ {mensaje}")