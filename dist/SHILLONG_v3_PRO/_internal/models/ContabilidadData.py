# -*- coding: utf-8 -*-
"""
ContabilidadData — SHILLONG CONTABILIDAD v3.7.8 PRO
Versión original restaurada + features modernos integrados.
Compatible con: RegistrarView, Dashboard, LibroMensual, Importador, ToolsView.
"""

import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# Ruta segura para EXE y desarrollo
try:
    from utils.rutas import ruta_recurso
except ImportError:
    def ruta_recurso(p): return Path(p)


class ContabilidadData:

    # ============================================================
    # INIT
    # ============================================================
    def __init__(self, archivo_json="shillong_2026.json"):

        # Carpeta DATA garantizada
        self.carpeta_data = Path("data")
        self.carpeta_data.mkdir(exist_ok=True)

        # Archivo JSON real
        self.archivo_json = self.carpeta_data / Path(archivo_json).name
        print(f"[ContabilidadData] Base de datos: {self.archivo_json}")

        self.movimientos = []
        self.cuentas = self._cargar_plan_contable()
        
        self.cargar()
        self.guardar_datos = self.guardar   # Alias compatibilidad
        self.cargar_datos = self.cargar     # Alias compatibilidad para DashboardView

    # ============================================================
    # CARGAR PLAN CONTABLE
    # ============================================================
    def _cargar_plan_contable(self):
        """
        Carga plan contable desde plan_contable_v3.json
        Retorna dict: {codigo: {nombre, permitidos}}
        """
        # Buscar dentro del EXE
        path = ruta_recurso("data/plan_contable_v3.json")
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"[ContabilidadData] Error cargando plan contable: {e}")

        # Fallback local
        local = Path("data/plan_contable_v3.json")
        if local.exists():
            with open(local, "r", encoding="utf-8") as f:
                return json.load(f)

        print("[ContabilidadData] ⚠ No se encontró plan contable.")
        return {}

    # ============================================================
    # CARGAR / GUARDAR
    # ============================================================
    def cargar(self):
        """Carga movimientos desde JSON."""
        try:
            if not self.archivo_json.exists():
                print("[ContabilidadData] Creando archivo nuevo.")
                self.movimientos = []
                self.guardar()
                return

            with open(self.archivo_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Compatibilidad con estructuras antiguas
            if isinstance(data, list):
                self.movimientos = data
            else:
                self.movimientos = data.get("movimientos", [])

            print(f"[ContabilidadData] Cargados {len(self.movimientos)} movimientos.")

        except Exception as e:
            print("[ContabilidadData] ERROR al cargar:", e)
            self.movimientos = []

    def guardar(self):
        """Guarda JSON con metadatos."""
        try:
            paquete = {
                "version": "3.7.8 PRO",
                "fecha_guardado": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "movimientos": self.movimientos
            }

            with open(self.archivo_json, "w", encoding="utf-8") as f:
                json.dump(paquete, f, indent=4, ensure_ascii=False)

            print(f"[ContabilidadData] Guardado OK ({len(self.movimientos)} movimientos).")

        except Exception as e:
            print("[ContabilidadData] CRASH al guardar:", e)

    def asignar_archivo(self, nueva_ruta):
        """Cambia el archivo JSON activo y recarga datos."""
        self.archivo_json = Path(nueva_ruta)
        self.cargar()

    # ============================================================
    # AGREGAR MOVIMIENTO (con features)
    # ============================================================
    def agregar_movimiento(self, fecha, documento, concepto, cuenta,
                           debe, haber, moneda="INR", banco="Caja", estado="pagado"):

        # Regla: gasto SIEMPRE INR
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
            "estado": estado.lower(),
            "banco": banco,
            # Feature añadido → saldo por movimiento
            "saldo": float(haber or 0) - float(debe or 0)
        }

        self.movimientos.append(mov)
        self.guardar()

    # ============================================================
    # OBTENER NOMBRE DE CUENTA  (original + safe-fix)
    # ============================================================
    def obtener_nombre_cuenta(self, cuenta):
        data = self.cuentas.get(str(cuenta))

        if data is None:
            return "Cuenta desconocida"

        if isinstance(data, dict):
            return data.get("nombre", "Cuenta sin nombre")

        return str(data)

    # ============================================================
    # FILTROS BÁSICOS
    # ============================================================
    def movimientos_por_fecha(self, fecha):
        return [m for m in self.movimientos if m.get("fecha") == fecha]

    def movimientos_por_cuenta(self, cuenta):
        return [m for m in self.movimientos if m.get("cuenta") == str(cuenta)]

    def pendientes(self):
        return [m for m in self.movimientos if m.get("estado", "").lower() == "pendiente"]

    def get_movimientos_rango(self, fecha_inicio, fecha_fin):
        """
        Obtiene movimientos entre dos fechas (objetos date).
        Requerido por InformesView para el Diario General.
        """
        from datetime import datetime
        resultado = []
        for m in self.movimientos:
            try:
                f_str = m.get("fecha", "")
                if "/" in f_str:
                    d, mm, a = map(int, f_str.split("/"))
                    fecha_mov = datetime(a, mm, d).date()
                elif "-" in f_str:
                    parts = f_str.split("-")
                    if len(parts[0]) == 4:
                        a, mm, d = map(int, parts)
                    else:
                        d, mm, a = map(int, parts)
                    fecha_mov = datetime(a, mm, d).date()
                else:
                    continue
                
                if fecha_inicio <= fecha_mov <= fecha_fin:
                    resultado.append(m)
            except (ValueError, IndexError):
                continue
        return resultado

    # ============================================================
    # LIBRO MENSUAL
    # ============================================================
    def movimientos_por_mes(self, mes, año):
        """
        Obtiene movimientos para un mes y año específicos, manejando varios formatos de fecha.
        Formatos soportados: DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY.
        """
        lista = []
        for m in self.movimientos:
            try:
                f_str = m.get("fecha", "")
                fecha_obj = None

                if "/" in f_str:
                    # Formato: DD/MM/YYYY
                    fecha_obj = datetime.strptime(f_str, "%d/%m/%Y")
                elif "-" in f_str:
                    try:
                        # Formato: YYYY-MM-DD
                        fecha_obj = datetime.strptime(f_str, "%Y-%m-%d")
                    except ValueError:
                        # Formato: DD-MM-YYYY
                        fecha_obj = datetime.strptime(f_str, "%d-%m-%Y")

                if fecha_obj and fecha_obj.month == mes and fecha_obj.year == año:
                    lista.append(m)

            except (ValueError, AttributeError, IndexError):
                # Ignora movimientos con formato de fecha inválido o ausente
                continue
        return lista

    def totales_mes(self, mes, año):
        datos = self.movimientos_por_mes(mes, año)
        gasto = sum(float(m.get("debe", 0)) for m in datos)
        ingreso = sum(float(m.get("haber", 0)) for m in datos)
        return gasto, ingreso, ingreso - gasto

    # ============================================================
    # MULTIMONEDA / RESÚMENES
    # ============================================================
    def ingresos_por_moneda(self, moneda):
        return sum(float(m.get("haber", 0)) for m in self.movimientos
                   if m.get("moneda", "INR").upper() == moneda.upper())

    def gastos_por_moneda(self, moneda):
        return sum(float(m.get("debe", 0)) for m in self.movimientos
                   if m.get("moneda", "INR").upper() == moneda.upper())

    def get_gasto_total(self):
        return self.gastos_por_moneda("INR")

    def get_ingreso_total(self):
        return sum(float(m.get("haber", 0)) for m in self.movimientos)

    def get_top_cuentas_anuales(self, año, limite=5):
        resumen = defaultdict(float)

        for m in self.movimientos:
            try:
                d, mm, aa = m["fecha"].split("/")
                if int(aa) == año:
                    resumen[str(m["cuenta"])] += float(m.get("debe", 0))
            except (ValueError, KeyError, TypeError):
                pass

        top = sorted(resumen.items(), key=lambda x: x[1], reverse=True)[:limite]

        salida = []
        for cuenta, total in top:
            nombre = self.obtener_nombre_cuenta(cuenta)
            salida.append((cuenta, nombre, total))

        return salida
