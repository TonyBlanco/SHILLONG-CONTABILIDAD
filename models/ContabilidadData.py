# -*- coding: utf-8 -*-
import json
from collections import defaultdict
from pathlib import Path
import sys
import os

# Importamos AMBAS funciones (Asegúrate de haber actualizado utils/rutas.py)
from utils.rutas import ruta_recurso, ruta_datos_usuario

class ContabilidadData:

    def __init__(self, archivo_json="shillong_2026.json"):
        # --- FIX PARA EL BUG DE RUTAS (DATA/DATA) ---
        # 1. Limpiamos el nombre por si viene como "data/shillong..."
        nombre_limpio = Path(archivo_json).name
        
        # 2. Usamos el helper nuevo para obtener la ruta absoluta perfecta
        self.archivo_json = ruta_datos_usuario(nombre_limpio)
        # --------------------------------------------
        
        # Crear carpeta si no existe
        self.archivo_json.parent.mkdir(exist_ok=True, parents=True)

        self.movimientos = []
        self.cuentas = self._cargar_plan_contable()
        self.cargar()

    # ============================================================
    # PLAN CONTABLE
    # ============================================================
    def _cargar_plan_contable(self):
        # Usamos ruta_recurso para buscar dentro del EXE si hace falta
        path = ruta_recurso("data/plan_contable_v3.json")
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    # ============================================================
    # CARGAR / GUARDAR
    # ============================================================
    def cargar(self):
        try:
            if self.archivo_json.exists():
                with open(self.archivo_json, "r", encoding="utf-8") as f:
                    self.movimientos = json.load(f)

                # Normalizar datos antiguos (Tu código original)
                for m in self.movimientos:
                    m.setdefault("moneda", "INR")
                    m.setdefault("banco", "Caja")
                    m.setdefault("estado", "pagado")
            else:
                self.movimientos = []
                self.guardar() # Crea archivo vacío si no existe

        except Exception as e:
            print("Error cargando JSON:", e)
            self.movimientos = []

    def guardar(self):
        try:
            with open(self.archivo_json, "w", encoding="utf-8") as f:
                json.dump(self.movimientos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error guardando JSON:", e)

    def asignar_archivo(self, nueva_ruta):
        """Permite cambiar el archivo de datos en caliente"""
        self.archivo_json = Path(nueva_ruta)
        self.cargar()

    # ============================================================
    # AGREGAR MOVIMIENTO
    # ============================================================
    def agregar_movimiento(self, fecha, documento, concepto, cuenta, debe, haber, moneda, banco, estado="pagado"):
        # Si es gasto → siempre INR
        if float(debe or 0) > 0:
            moneda = "INR"

        movimiento = {
            "fecha": fecha,
            "documento": documento,
            "concepto": concepto,
            "cuenta": str(cuenta),
            "debe": float(debe or 0),
            "haber": float(haber or 0),
            "moneda": moneda,
            "estado": estado,
            "banco": banco,
            "saldo": float(haber or 0) - float(debe or 0)
        }

        self.movimientos.append(movimiento)
        self.guardar()

    # ============================================================
    # NOMBRE DE CUENTA
    # ============================================================
    def obtener_nombre_cuenta(self, cuenta):
        info = self.cuentas.get(str(cuenta))
        if info is None:
            return "Cuenta sin nombre"
        if isinstance(info, dict):
            return info.get("nombre", "Cuenta sin nombre")
        return str(info)

    # ============================================================
    # FILTROS (Tus funciones originales recuperadas)
    # ============================================================
    def movimientos_por_fecha(self, fecha):
        return [m for m in self.movimientos if m.get("fecha") == fecha]

    def movimientos_por_cuenta(self, cuenta):
        return [m for m in self.movimientos if m.get("cuenta") == str(cuenta)]

    def pendientes(self):
        return [m for m in self.movimientos if m.get("estado", "").lower() == "pendiente"]

    # ============================================================
    # LIBRO MENSUAL
    # ============================================================
    def movimientos_por_mes(self, mes, año):
        lista = []
        for m in self.movimientos:
            try:
                d, mm, aa = m["fecha"].split("/")
                if int(mm) == mes and int(aa) == año:
                    lista.append(m)
            except:
                pass
        return lista

    def totales_mes(self, mes, año):
        datos = self.movimientos_por_mes(mes, año)
        gasto = sum(m["debe"] for m in datos)
        ingreso = sum(m["haber"] for m in datos)
        return gasto, ingreso, ingreso - gasto

    # ============================================================
    # MULTIMONEDA (Tus funciones originales)
    # ============================================================
    def ingresos_por_moneda(self, moneda):
        return sum(m["haber"] for m in self.movimientos if m.get("moneda", "INR").upper() == moneda.upper())

    def gastos_por_moneda(self, moneda):
        return sum(m["debe"] for m in self.movimientos if m.get("moneda", "INR").upper() == moneda.upper())

    def get_gasto_total(self):
        return self.gastos_por_moneda("INR")

    def get_ingreso_total(self):
        return sum(m["haber"] for m in self.movimientos)

    # ============================================================
    # TRIMESTRE (Tus funciones originales)
    # ============================================================
    def _rango_trimestre(self, mes):
        if mes <= 3: return 1, 3
        if mes <= 6: return 4, 6
        if mes <= 9: return 7, 9
        return 10, 12

    def get_gasto_trimestre(self, mes, año):
        ini, fin = self._rango_trimestre(mes)
        total = 0
        for m in range(ini, fin + 1):
            total += sum(x["debe"] for x in self.movimientos_por_mes(m, año))
        return total

    def ingresos_trimestre_por_moneda(self, mes, año, moneda):
        ini, fin = self._rango_trimestre(mes)
        total = 0
        for m in range(ini, fin + 1):
            total += self.ingresos_por_moneda(moneda)
        return total

    # ============================================================
    # TOP CUENTAS ANUALES (Tus funciones originales)
    # ============================================================
    def get_top_cuentas_anuales(self, año, limite=5):
        resumen = defaultdict(float)

        for mov in self.movimientos:
            try:
                d, m, a = mov["fecha"].split("/")
                if int(a) == año:
                    resumen[str(mov["cuenta"])] += mov["debe"]
            except:
                pass
        
        top = sorted(resumen.items(), key=lambda t: t[1], reverse=True)[:limite]

        salida = []
        for cuenta, total in top:
            nombre = self.obtener_nombre_cuenta(cuenta)
            salida.append((cuenta, nombre, total))

        return salida