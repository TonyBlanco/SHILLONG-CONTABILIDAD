# -*- coding: utf-8 -*-
"""
CONTABILIDAD DATA — SHILLONG CONTABILIDAD v3 PRO
Multimoneda + Gestión de Bancos + Totales + Trimestre
Versión final, completa y estable (COMPATIBLE CON EXE)
"""

import json
from collections import defaultdict
from utils.rutas import ruta_recurso


class ContabilidadData:

    def __init__(self, archivo_json="shillong_2026.json"):
        self.archivo_json = ruta_recurso(f"data/{archivo_json}")
        self.movimientos = []

        # Cargar plan contable
        self.cuentas = self._cargar_plan_contable()

        # Cargar movimientos JSON
        self.cargar()

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
        return {}

    # ============================================================
    # CARGAR / GUARDAR
    # ============================================================
    def cargar(self):
        try:
            if self.archivo_json.exists():
                with open(self.archivo_json, "r", encoding="utf-8") as f:
                    self.movimientos = json.load(f)

                # Actualizar movimientos antiguos sin nuevos campos
                for m in self.movimientos:
                    m.setdefault("moneda", "INR")
                    m.setdefault("banco", "Caja")
            else:
                self.movimientos = []

        except Exception as e:
            print("Error cargando JSON:", e)
            self.movimientos = []

    def guardar(self):
        try:
            with open(self.archivo_json, "w", encoding="utf-8") as f:
                json.dump(self.movimientos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error guardando JSON:", e)

    # ============================================================
    # AGREGAR MOVIMIENTO (ACTUALIZADO)
    # ============================================================
    def agregar_movimiento(self, fecha, documento, concepto, cuenta, debe, haber, moneda, banco, estado="pagado"):
        if float(debe) > 0:
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

        # Actualizar saldo del banco
        try:
            from models.BankManager import BankManager
            bm = BankManager()

            id_banco = {
                "Federal Bank": 1, "SBI": 2, "Union Bank": 3,
                "Otro": 4, "Caja": 5
            }.get(banco, None)

            if id_banco is not None and estado.lower() == "pagado":
                saldo_actual = bm.get_saldo(id_banco)
                nuevo_saldo = saldo_actual + float(haber) - float(debe)
                bm.actualizar_saldo(id_banco, nuevo_saldo)

        except Exception as e:
            print("Error actualizando saldo del banco:", e)

    # ============================================================
    # OBTENER NOMBRE DE CUENTA
    # ============================================================
    def obtener_nombre_cuenta(self, cuenta):
        info = self.cuentas.get(str(cuenta))
        if info is None:
            return "Cuenta sin nombre"
        if isinstance(info, dict):
            return info.get("nombre", "Cuenta sin nombre")
        return str(info)

    # ============================================================
    # FILTROS BÁSICOS
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
        ingreso_total = sum(m["haber"] for m in datos)
        return gasto, ingreso_total, ingreso_total - gasto

    # ============================================================
    # MULTIMONEDA
    # ============================================================
    def ingresos_por_moneda(self, moneda):
        return sum(m["haber"] for m in self.movimientos if str(m.get("moneda", "INR")).upper() == moneda.upper())

    def gastos_por_moneda(self, moneda):
        return sum(m["debe"] for m in self.movimientos if str(m.get("moneda", "INR")).upper() == moneda.upper())

    def get_gasto_total(self):
        return self.gastos_por_moneda("INR")

    def get_ingreso_total(self):
        return sum(m["haber"] for m in self.movimientos)

    # ============================================================
    # TRIMESTRE
    # ============================================================
    def _rango_trimestre(self, mes):
        if mes <= 3: return 1, 3
        elif mes <= 6: return 4, 6
        elif mes <= 9: return 7, 9
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
    # TOP CUENTAS ANUAL
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