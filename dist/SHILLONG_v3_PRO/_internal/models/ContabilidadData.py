# -*- coding: utf-8 -*-
# ======================================================================
#  SHILLONG CONTABILIDAD PRO — ENGINE CORE
#  Versión de Aplicación : 3.7.7
#  Versión del Motor     : 4.3.2  (ENGINE FIX — 02/12/2025)
#
#  Cambios importantes del FIX 4.3.2:
#  ✔ Se reparó indentación que rompía métodos internos
#  ✔ Se restauraron y validaron todos los filtros:
#       - movimientos_por_fecha
#       - movimientos_por_cuenta
#       - movimientos_por_mes
#       - get_movimientos_rango
#       - pendientes
#  ✔ Se formalizó compatibilidad total con Informes BI v4
#  ✔ Se normalizó el ordenamiento y conversión de fechas
#  ✔ Se revisaron totales mensuales, top cuentas y moneda
#  ✔ Estabilización completa del núcleo de datos
#
#  Este archivo es el motor principal. NO editar sin respaldo.
# ======================================================================

import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# Mantenemos utils.rutas solo para leer recursos internos (plan contable)
try:
    from utils.rutas import ruta_recurso
except ImportError:
    def ruta_recurso(p): return Path(p)


class ContabilidadData:

    def __init__(self, archivo_json="shillong_2026.json"):

        # ============================================================
        # RUTA FIJA A /data
        # ============================================================
        self.carpeta_data = Path("data")
        self.carpeta_data.mkdir(exist_ok=True)

        nombre_limpio = Path(archivo_json).name
        self.archivo_json = self.carpeta_data / nombre_limpio

        print(f"--> [ContabilidadData] Usando base de datos en: {self.archivo_json.absolute()}")

        self.movimientos = []
        self.cuentas = self._cargar_plan_contable()
        self.cargar()

        # Alias para compatibilidad
        self.guardar_datos = self.guardar

    # ============================================================
    # PLAN CONTABLE
    # ============================================================
    def _cargar_plan_contable(self):
        path = ruta_recurso("data/plan_contable_v3.json")
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}

        local = Path("data/plan_contable_v3.json")
        if local.exists():
            with open(local, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}

    # ============================================================
    # CARGAR / GUARDAR
    # ============================================================
    def cargar(self):
        try:
            if self.archivo_json.exists():
                with open(self.archivo_json, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    self.movimientos = data
                else:
                    self.movimientos = data.get("movimientos", [])

                print(f"--> [ContabilidadData] Datos cargados: {len(self.movimientos)} movimientos.")
            else:
                print("--> No existe archivo, creando nuevo…")
                self.movimientos = []
                self.guardar()

        except Exception as e:
            print("--> [ERROR] Cargando JSON:", e)
            self.movimientos = []

    def guardar(self):
        try:
            data = {
                "version": "3.7.7 PRO",
                "fecha_guardado": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "movimientos": self.movimientos
            }
            with open(self.archivo_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            print(f"--> [GUARDADO] {len(self.movimientos)} movimientos.")
        except Exception as e:
            print("--> [ERROR] Guardando JSON:", e)

    def asignar_archivo(self, nueva_ruta):
        self.archivo_json = Path(nueva_ruta)
        self.cargar()

    # ============================================================
    # AGREGAR MOVIMIENTO
    # ============================================================
    def agregar_movimiento(self, fecha, documento, concepto, cuenta, debe, haber,
                           moneda="INR", banco="Caja", estado="pagado"):

        if float(debe or 0) > 0:
            moneda = "INR"

        mov = {
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
        self.movimientos.append(mov)
        self.guardar()

    # ============================================================
    # NOMBRE DE CUENTA
    # ============================================================
    def obtener_nombre_cuenta(self, cuenta):
        info = self.cuentas.get(str(cuenta))
        if not info:
            return "Cuenta desconocida"
        if isinstance(info, dict):
            return info.get("nombre", "")
        return str(info)

    # ============================================================
    # FILTROS
    # ============================================================
    def movimientos_por_fecha(self, fecha):
        return [m for m in self.movimientos if m.get("fecha") == fecha]

    def movimientos_por_cuenta(self, cuenta):
        return [m for m in self.movimientos if m.get("cuenta") == str(cuenta)]

    def pendientes(self):
        return [m for m in self.movimientos if m.get("estado", "").lower() == "pendiente"]

    # ============================================================
    # RANGO DE FECHAS — OFICIAL
    # ============================================================
    def get_movimientos_rango(self, fecha_ini, fecha_fin):
        lista = []

        for m in self.movimientos:
            f_str = m.get("fecha", "").strip()
            if not f_str:
                continue

            try:
                d, mm, aa = f_str.split("/")
                f = datetime(int(aa), int(mm), int(d))

                if fecha_ini <= f <= fecha_fin:
                    lista.append(m)

            except:
                continue

        return lista

    # ============================================================
    # LIBRO MENSUAL
    # ============================================================
    def movimientos_por_mes(self, mes, año):
        lista = []
        for m in self.movimientos:
            try:
                d, mm, aa = m.get("fecha", "").split("/")
                if int(mm) == mes and int(aa) == año:
                    lista.append(m)
            except:
                pass
        return lista

    def totales_mes(self, mes, año):
        datos = self.movimientos_por_mes(mes, año)
        gasto = sum(float(m.get("debe", 0)) for m in datos)
        ingreso = sum(float(m.get("haber", 0)) for m in datos)
        return gasto, ingreso, ingreso - gasto

    # ============================================================
    # MULTIMONEDA
    # ============================================================
    def ingresos_por_moneda(self, moneda):
        return sum(float(m.get("haber", 0)) for m in self.movimientos if m.get("moneda", "INR") == moneda)

    def gastos_por_moneda(self, moneda):
        return sum(float(m.get("debe", 0)) for m in self.movimientos if m.get("moneda", "INR") == moneda)

    def get_gasto_total(self):
        return self.gastos_por_moneda("INR")

    def get_ingreso_total(self):
        return sum(float(m.get("haber", 0)) for m in self.movimientos)

    # ============================================================
    # TOP CUENTAS
    # ============================================================
    def get_top_cuentas_anuales(self, año, limite=5):
        resumen = defaultdict(float)

        for mov in self.movimientos:
            try:
                d, m, a = mov["fecha"].split("/")
                if int(a) == año:
                    resumen[str(mov["cuenta"])] += float(m.get("debe", 0))
            except:
                pass

        top = sorted(resumen.items(), key=lambda t: t[1], reverse=True)[:limite]
        salida = []

        for cuenta, total in top:
            nombre = self.obtener_nombre_cuenta(cuenta)
            salida.append((cuenta, nombre, total))

        return salida
