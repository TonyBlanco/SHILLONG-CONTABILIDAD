*** Begin Patch
*** Update File: ui/LibroMensualView.py
@@
 class LibroMensualView(QWidget):
     def __init__(self, data):
         super().__init__()
         self.data = data
@@
         self.bancos = self._cargar_bancos()
         self.reglas_cache = self._cargar_reglas()
+        self.saldos_iniciales = {}  # {(año, mes): saldo}
@@
-    def _solicitar_saldo_inicial(self):
-        """Solicita al usuario el saldo inicial para la exportación."""
-        saldo_inicial, ok = QInputDialog.getDouble(
-            self, 
-            "Saldo Inicial Requerido",
-            "Ingrese el saldo inicial del mes:",
-            value=0.0,
-            decimals=2
-        )
-        if not ok:
-            return None
-        return saldo_inicial
+    def _solicitar_saldo_inicial(self, mes, año):
+        """Solicita al usuario el saldo inicial del mes (solo una vez)."""
+        clave = (año, mes)
+        if clave in self.saldos_iniciales:
+            return self.saldos_iniciales[clave]
+
+        fecha_prev = datetime.date(año, mes, 1) - datetime.timedelta(days=1)
+        prompt = f"Saldo arrastrado del mes anterior ({fecha_prev.strftime('%d/%m/%Y')}):"
+        saldo_inicial, ok = QInputDialog.getDouble(
+            self,
+            "Saldo inicial requerido",
+            prompt,
+            value=0.0,
+            decimals=2
+        )
+        if not ok:
+            return None
+        self.saldos_iniciales[clave] = saldo_inicial
+        return saldo_inicial
@@
     def actualizar(self):
         mes = self.cbo_mes.currentIndex() + 1
         año = int(self.cbo_año.currentText())
         banco_filtro = self.cbo_banco.currentText()
-        
-        movs = self.data.movimientos_por_mes(mes, año)
-        
-        self.tabla.setRowCount(0)
-        saldo_acum = 0
-        total_debe = 0
-        total_haber = 0
-        
-        for m in movs:
+        saldo_inicial = self._solicitar_saldo_inicial(mes, año)
+        if saldo_inicial is None:
+            QMessageBox.warning(self, "Atención", "Debe introducir el saldo arrastrado del mes anterior.")
+            return
+
+        movs = self.data.movimientos_por_mes(mes, año)
+
+        self.tabla.setRowCount(0)
+        saldo_acum = saldo_inicial
+        total_debe = 0
+        total_haber = 0
+
+        # Fila saldo inicial
+        fila0 = [
+            f"01/{mes:02d}/{año}", "", "Saldo inicial", "", "",
+            f"{0.0:,.2f}", f"{0.0:,.2f}", f"{saldo_acum:,.2f}",
+            "Caja" if banco_filtro == "Todos" else banco_filtro, "", ""
+        ]
+        self.tabla.insertRow(0)
+        for c, val in enumerate(fila0):
+            it = QTableWidgetItem(str(val))
+            if c in [5, 6, 7]:
+                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
+                if c == 7:
+                    it.setFont(QFont("Arial", 9, QFont.Bold))
+            self.tabla.setItem(0, c, it)
+
+        for m in movs:
             if banco_filtro != "Todos" and m.get("banco") != banco_filtro:
                 continue
-                
-            row = self.tabla.rowCount()
-            self.tabla.insertRow(row)
-            
+
+            row = self.tabla.rowCount()
+            self.tabla.insertRow(row)
+
             try:
                 debe = float(m.get("debe", 0))
             except (ValueError, TypeError):
                 debe = 0.0
             try:
@@
-            total_debe += debe
-            total_haber += haber
-            saldo_acum += haber - debe
+            total_debe += debe
+            total_haber += haber
+            saldo_acum += haber - debe
@@
-        self._update_card(self.card_gasto, total_debe)
-        self._update_card(self.card_ingreso, total_haber)
-        self._update_card(self.card_saldo, total_haber - total_debe)
+        self._update_card(self.card_gasto, total_debe)
+        self._update_card(self.card_ingreso, total_haber)
+        self._update_card(self.card_saldo, saldo_inicial + total_haber - total_debe)
@@
-        # Solicitar saldo inicial
-        saldo_inicial = self._solicitar_saldo_inicial()
-        if saldo_inicial is None:
-            QMessageBox.warning(self, "Exportación cancelada", "El saldo inicial es requerido para la exportación.")
-            return
+        # Solicitar/reutilizar saldo inicial
+        saldo_inicial = self._solicitar_saldo_inicial(mes, año)
+        if saldo_inicial is None:
+            QMessageBox.warning(self, "Exportación cancelada", "El saldo inicial es requerido para la exportación.")
+            return
@@
-        # Recopilar datos filtrados
-        mes = self.cbo_mes.currentIndex() + 1
-        año = int(self.cbo_año.currentText())
-        banco_filtro = self.cbo_banco.currentText()
-        
-        movs_raw = self.data.movimientos_por_mes(mes, año)
-        datos_prep = []
-        
-        # Insertar fila de saldo inicial al inicio
-        fila_saldo_inicial = {
-            "cuenta": "",
-            "fecha": f"01/{mes:02d}/{año}",
-            "concepto": "SALDO INICIAL",
-            "debe": 0.0,
-            "haber": 0.0,
-            "estado": "",
-            "documento": "",
-            "nombre_cuenta": "",
-            "saldo": saldo_inicial,
-            "banco": banco_filtro if banco_filtro != "Todos" else "",
-            "categoria": ""
-        }
-        datos_prep.append(fila_saldo_inicial)
-        
-        # Inicializar saldo con el saldo inicial
-        saldo = saldo_inicial
+        # Recopilar datos filtrados
+        movs_raw = self.data.movimientos_por_mes(mes, año)
+        datos_prep = []
+
+        # Insertar fila de saldo inicial al inicio
+        fila_saldo_inicial = {
+            "cuenta": "",
+            "fecha": f"01/{mes:02d}/{año}",
+            "categoria": "",
+            "concepto": "Saldo inicial",
+            "debe": 0.0,
+            "haber": 0.0,
+            "saldo": saldo_inicial,
+            "banco": "Caja" if banco_filtro == "Todos" else banco_filtro,
+            "documento": "",
+            "nombre_cuenta": "",
+            "estado": "",
+        }
+        datos_prep.append(fila_saldo_inicial)
+
+        # Inicializar saldo con el saldo inicial
+        saldo = saldo_inicial
*** End Patch
