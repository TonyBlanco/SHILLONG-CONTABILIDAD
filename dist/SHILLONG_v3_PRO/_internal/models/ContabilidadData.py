# -*- coding: utf-8 -*-
import json
from collections import defaultdict
from pathlib import Path
import sys
import os
from datetime import datetime

# Mantenemos utils.rutas solo para leer recursos internos (plan contable)
try:
    from utils.rutas import ruta_recurso
except ImportError:
    # Fallback por si falla la importación
    def ruta_recurso(p): return Path(p)

class ContabilidadData:

    def __init__(self, archivo_json="shillong_2026.json"):
        # ============================================================
        # CAMBIO IMPORTANTE: RUTA LOCAL FIJA
        # ============================================================
        # Forzamos que el archivo se guarde SIEMPRE en la carpeta "data" 
        # local del proyecto, para que puedas verlo y editarlo fácilmente.
        self.carpeta_data = Path("data")
        self.carpeta_data.mkdir(exist_ok=True) # Crea carpeta 'data' si no existe
        
        nombre_limpio = Path(archivo_json).name
        self.archivo_json = self.carpeta_data / nombre_limpio
        
        print(f"--> [ContabilidadData] Usando base de datos en: {self.archivo_json.absolute()}")
        # ============================================================

        self.movimientos = []
        self.cuentas = self._cargar_plan_contable()
        self.cargar()
        
        # Alias para compatibilidad con ImportadorExcelDialog
        self.guardar_datos = self.guardar 

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
        # Fallback local
        local_path = Path("data/plan_contable_v3.json")
        if local_path.exists():
             with open(local_path, "r", encoding="utf-8") as f:
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
                    
                # Soporte para estructura antigua (lista directa) vs nueva (diccionario)
                if isinstance(data, list):
                    self.movimientos = data
                elif isinstance(data, dict):
                    self.movimientos = data.get("movimientos", [])
                
                print(f"--> [ContabilidadData] Datos cargados: {len(self.movimientos)} movimientos.")
            else:
                print("--> [ContabilidadData] No existe archivo, creando nuevo.")
                self.movimientos = []
                self.guardar() # Crea archivo vacío si no existe

        except Exception as e:
            print("--> [ERROR] Cargando JSON:", e)
            self.movimientos = []

    def guardar(self):
        try:
            # Estructura robusta con metadatos
            export_data = {
                "version": "3.6 PRO",
                "fecha_guardado": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "movimientos": self.movimientos
            }
            
            with open(self.archivo_json, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
                
            print(f"--> [GUARDADO] {len(self.movimientos)} movimientos guardados correctamente.")
            
        except Exception as e:
            print("--> [ERROR CRÍTICO] Guardando JSON:", e)

    def asignar_archivo(self, nueva_ruta):
        """Permite cambiar el archivo de datos en caliente"""
        self.archivo_json = Path(nueva_ruta)
        self.cargar()

    # ============================================================
    # AGREGAR MOVIMIENTO
    # ============================================================
    def agregar_movimiento(self, fecha, documento, concepto, cuenta, debe, haber, moneda="INR", banco="Caja", estado="pagado"):
        # Si es gasto → siempre INR (Regla de negocio)
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
            # Calculamos saldo línea a línea (opcional, pero útil)
            "saldo": float(haber or 0) - float(debe or 0) 
        }

        self.movimientos.append(movimiento)
        
        # GUARDADO INMEDIATO PARA SEGURIDAD
        self.guardar()

    # ============================================================
    # NOMBRE DE CUENTA
    # ============================================================
    def obtener_nombre_cuenta(self, cuenta):
        info = self.cuentas.get(str(cuenta))
        if info is None:
            return "Cuenta desconocida"
        if isinstance(info, dict):
            return info.get("nombre", "Cuenta sin nombre")
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
    # LIBRO MENSUAL
    # ============================================================
    def movimientos_por_mes(self, mes, año):
        lista = []
        for m in self.movimientos:
            try:
                # Soporte robusto para fechas
                f_str = m.get("fecha", "")
                if "/" in f_str:
                    d, mm, aa = f_str.split("/")
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
    # MULTIMONEDA & EXTRAS
    # ============================================================
    def ingresos_por_moneda(self, moneda):
        return sum(float(m.get("haber", 0)) for m in self.movimientos if m.get("moneda", "INR").upper() == moneda.upper())

    def gastos_por_moneda(self, moneda):
        return sum(float(m.get("debe", 0)) for m in self.movimientos if m.get("moneda", "INR").upper() == moneda.upper())

    def get_gasto_total(self):
        return self.gastos_por_moneda("INR")

    def get_ingreso_total(self):
        return sum(float(m.get("haber", 0)) for m in self.movimientos)
    
    # ... Resto de métodos de trimestre y top cuentas se mantienen iguales ...
    def get_top_cuentas_anuales(self, año, limite=5):
        resumen = defaultdict(float)
        for mov in self.movimientos:
            try:
                d, m, a = mov["fecha"].split("/")
                if int(a) == año:
                    resumen[str(mov["cuenta"])] += float(mov.get("debe", 0))
            except:
                pass
        top = sorted(resumen.items(), key=lambda t: t[1], reverse=True)[:limite]
        salida = []
        for cuenta, total in top:
            nombre = self.obtener_nombre_cuenta(cuenta)
            salida.append((cuenta, nombre, total))
        return salida