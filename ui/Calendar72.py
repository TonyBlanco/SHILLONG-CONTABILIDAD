# =====================================================================
#  CLASE DIÁLOGO CALENDARIO (LÓGICA ACTUALIZADA + SÁBADOS NEUTROS)
# =====================================================================
class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calendario Cabalístico - Energía Diaria")
        self.resize(700, 650)
        self.setStyleSheet("background-color: #121212; color: white;") # Estilo oscuro como la App de la foto
        
        # Variables de estado
        hoy = date.today()
        self.anio_actual = hoy.year
        self.mes_actual = hoy.month
        self.dia_hoy = hoy
        
        layout = QVBoxLayout(self)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        
        btn_prev = QPushButton("◀")
        btn_prev.setCursor(Qt.PointingHandCursor)
        btn_prev.clicked.connect(self._mes_anterior)
        btn_prev.setStyleSheet("background: transparent; color: white; font-size: 18px; border: none;")
        
        self.lbl_titulo = QLabel()
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: white; text-transform: uppercase; letter-spacing: 2px;")
        
        btn_next = QPushButton("▶")
        btn_next.setCursor(Qt.PointingHandCursor)
        btn_next.clicked.connect(self._mes_siguiente)
        btn_next.setStyleSheet("background: transparent; color: white; font-size: 18px; border: none;")
        
        header_layout.addWidget(btn_prev)
        header_layout.addWidget(self.lbl_titulo, 1)
        header_layout.addWidget(btn_next)
        
        layout.addLayout(header_layout)
        
        # --- GRID DE DÍAS ---
        # Usamos un Frame negro
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: #000000; border-radius: 10px;")
        self.grid = QGridLayout(grid_frame)
        self.grid.setSpacing(2)
        layout.addWidget(grid_frame)
        
        # --- FOOTER ---
        lbl_footer = QLabel("Sábado (Shabbat) es Neutro para acciones materiales.\n(+) Energía Positiva  (-) Energía Negativa  (~) Neutro")
        lbl_footer.setAlignment(Qt.AlignCenter)
        lbl_footer.setStyleSheet("color: #888; font-size: 11px; margin-top: 10px;")
        layout.addWidget(lbl_footer)
        
        self._actualizar_calendario()

    def _actualizar_calendario(self):
        # Limpiar grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Título
        nombre_mes = calendar.month_name[self.mes_actual]
        self.lbl_titulo.setText(f"{nombre_mes} {self.anio_actual}")
        
        # Encabezados (DOM, LUN...)
        dias_semana = ["D", "L", "M", "X", "J", "V", "S"]
        for i, d in enumerate(dias_semana):
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignCenter)
            # Sábado (S) en blanco, resto gris, domingo rojo suave
            color = "#ff5555" if i == 0 else "#ffffff"
            lbl.setStyleSheet(f"font-weight: bold; color: {color}; padding-bottom: 5px;")
            self.grid.addWidget(lbl, 0, i)
            
        calendar.setfirstweekday(6) # Domingo primero
        matriz_mes = calendar.monthcalendar(self.anio_actual, self.mes_actual)
        
        fila = 1
        for semana in matriz_mes:
            for col, dia_num in enumerate(semana):
                if dia_num != 0:
                    fecha_dia = date(self.anio_actual, self.mes_actual, dia_num)
                    btn = self._crear_boton_dia(fecha_dia, dia_num)
                    self.grid.addWidget(btn, fila, col)
            fila += 1

    def _mes_anterior(self):
        if self.mes_actual == 1:
            self.mes_actual = 12
            self.anio_actual -= 1
        else:
            self.mes_actual -= 1
        self._actualizar_calendario()

    def _mes_siguiente(self):
        if self.mes_actual == 12:
            self.mes_actual = 1
            self.anio_actual += 1
        else:
            self.mes_actual += 1
        self._actualizar_calendario()

    # --- LÓGICA DE CÁLCULO MEJORADA ---
    def _get_info_dia(self, fecha):
        # 1. IDENTIFICAR EL NOMBRE DE DIOS (Ciclo 72 días)
        idx = (fecha - date(2000, 1, 1)).days % 72
        nombre = NOMBRES_72[idx]
        dia = fecha.day
        
        # 2. REGLA SUPREMA: SÁBADO (Shabbat)
        # Python: Lunes=0 ... Sábado=5 ... Domingo=6
        es_sabado = (fecha.weekday() == 5)
        
        if es_sabado:
            # Sábado siempre es NEUTRO (~) visualmente en la App para "hacer" cosas
            return "~", "#1e1e1e", "#ffffff", nombre, "SHABBAT - NEUTRO"

        # 3. CÁLCULO DE FASE LUNAR SIMPLE (Aproximación para detectar Luna Nueva)
        # Un ciclo lunar medio es 29.53059 días.
        dias_desde_base = (fecha - date(2000, 1, 6)).days
        edad_luna = dias_desde_base % 29.53059
        
        # Luna Nueva (Día 0-1 del ciclo) = Siempre POSITIVO (+)
        es_luna_nueva = (edad_luna < 1.5)
        
        if es_luna_nueva:
             return "+", "#003300", "#4ade80", nombre, "LUNA NUEVA (ROSH JODESH)"

        # 4. RESTO DE DÍAS (Usamos listas + lógica de la foto)
        # Ajustamos los colores para que se parezcan a la App (Fondo Negro, signo blanco)
        
        if dia in DIAS_NEGATIVOS:
            return "-", "#1e1e1e", "#f87171", nombre, "DÍA NEGATIVO" # Rojo suave
        elif dia in DIAS_NEUTROS:
            return "~", "#1e1e1e", "#9ca3af", nombre, "DÍA NEUTRO" # Gris
        else:
            return "+", "#1e1e1e", "#4ade80", nombre, "DÍA POSITIVO" # Verde suave

    def _crear_boton_dia(self, fecha_dia, numero_dia):
        signo, bg_color, fg_color, nombre, estado_texto = self._get_info_dia(fecha_dia)
        
        es_hoy = (fecha_dia == self.dia_hoy)
        
        # Si es hoy, resaltamos con un borde rojo o fondo rojo como en la App
        bg_final = "#d32f2f" if es_hoy else "#000000" # Rojo oscuro si es hoy, negro si no
        fg_num = "#ffffff" # Número siempre blanco
        
        # El signo (+ - ~) tiene el color energético
        
        # Diseño del contenido del botón (Número arriba, Signo abajo)
        btn = QPushButton()
        btn.setFixedSize(60, 60)
        btn.setCursor(Qt.PointingHandCursor)
        
        # Usamos layouts dentro del botón no es posible directo, así que usamos saltos de línea y fuentes
        # O mejor, construimos el texto
        btn.setText(f"{numero_dia}\n{signo}")
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_final};
                color: {fg_num};
                font-family: 'Arial';
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #333333; 
            }}
        """)
        
        # Hack para colorear solo el signo: No se puede en QPushButton simple CSS.
        # Así que usamos el color del texto general según la energía, salvo si es hoy.
        if not es_hoy:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: black;
                    color: {fg_color}; /* El color indica la energía (+ verde, - rojo) */
                    font-size: 16px;
                    font-weight: bold;
                    border: none;
                }}
                QPushButton:hover {{ background-color: #222; }}
            """)
        
        btn.clicked.connect(lambda: self._mostrar_detalle(fecha_dia, nombre, estado_texto))
        return btn

    def _mostrar_detalle(self, fecha, nombre, tipo):
        msg = f"Fecha: {fecha.strftime('%d de %B de %Y')}\n"
        msg += f"--------------------------------\n"
        msg += f"Energía: {tipo}\n\n"
        msg += f"Nombre de Dios (Shem HaMephorash):\n"
        msg += f"--- {nombre} ---\n\n"
        
        QMessageBox.information(self, "Energía Diaria", msg)