# -*- coding: utf-8 -*-
"""
SaldosMensuales.py — SHILLONG CONTABILIDAD v3.8.0 PRO
Sistema de gestión automática de saldos mensuales
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple


class SaldosMensuales:
    """
    Gestor de saldos iniciales y finales por mes/banco.
    Permite el arrastre automático de saldos entre meses.
    """

    def __init__(self, archivo="data/saldos_mensuales.json"):
        self.archivo = Path(archivo)
        self.saldos = {}
        self._cargar()

    # ============================================================
    # CARGA Y GUARDADO
    # ============================================================
    def _cargar(self):
        """Carga el archivo JSON de saldos mensuales."""
        if not self.archivo.exists():
            print("[SaldosMensuales] Archivo no existe, creando estructura inicial...")
            self._crear_inicial()
            return

        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.saldos = data.get("saldos", {})
            print(f"[SaldosMensuales] Cargados {len(self.saldos)} meses.")
        except (IOError, json.JSONDecodeError) as e:
            print(f"[SaldosMensuales] Error al cargar: {e}")
            self.saldos = {}

    def _guardar(self):
        """Guarda los saldos en el archivo JSON."""
        try:
            # Crear directorio si no existe
            self.archivo.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0",
                "ultima_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "saldos": self.saldos
            }

            with open(self.archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"[SaldosMensuales] Guardado OK: {len(self.saldos)} meses.")
        except Exception as e:
            print(f"[SaldosMensuales] ERROR al guardar: {e}")

    def _crear_inicial(self):
        """
        Crea estructura inicial con Noviembre 2024 pre-configurado
        según el análisis del Excel.
        """
        # Saldos iniciales confirmados de Noviembre
        self.saldos = {
            "2024-11": {
                "Caja": {
                    "inicial": -39421.0,
                    "final": -142129.0,
                    "ingresos": 0.0,
                    "gastos": 102708.0
                },
                "Union Bank": {
                    "inicial": 0.0,
                    "final": -9237.9,
                    "ingresos": 20000.0,
                    "gastos": 29237.9
                },
                "Federal Bank": {
                    "inicial": 0.0,
                    "final": 0.0,
                    "ingresos": 0.0,
                    "gastos": 0.0
                },
                "SBI": {
                    "inicial": 0.0,
                    "final": 0.0,
                    "ingresos": 0.0,
                    "gastos": 0.0
                },
                "Otro": {
                    "inicial": 0.0,
                    "final": 0.0,
                    "ingresos": 0.0,
                    "gastos": 0.0
                },
                "fecha_cierre": "30/11/2024",
                "cerrado": True
            }
        }
        self._guardar()
        print("[SaldosMensuales] ✅ Estructura inicial creada con Noviembre 2024")

    # ============================================================
    # CONSULTA DE SALDOS
    # ============================================================
    def obtener_saldo_inicial(self, mes: int, año: int, banco: str) -> Optional[float]:
        """
        Obtiene el saldo inicial de un banco para un mes/año dado.
        
        Args:
            mes: Número del mes (1-12)
            año: Año (ej: 2024)
            banco: Nombre del banco (ej: "Caja", "Union Bank")
            
        Returns:
            Saldo inicial o None si no existe
        """
        clave = f"{año}-{mes:02d}"

        # Si el mes existe en el sistema, devolver su saldo inicial
        if clave in self.saldos:
            banco_data = self.saldos[clave].get(banco)
            if banco_data and isinstance(banco_data, dict):
                return float(banco_data.get("inicial", 0.0))

        # Si no existe, intentar arrastrar del mes anterior
        return self._arrastrar_saldo_anterior(mes, año, banco)

    def obtener_saldo_final(self, mes: int, año: int, banco: str) -> Optional[float]:
        """
        Obtiene el saldo final de un banco para un mes/año dado.
        
        Returns:
            Saldo final o None si no existe
        """
        clave = f"{año}-{mes:02d}"

        if clave in self.saldos:
            banco_data = self.saldos[clave].get(banco)
            if banco_data and isinstance(banco_data, dict):
                return float(banco_data.get("final", 0.0))

        return None

    def _arrastrar_saldo_anterior(self, mes: int, año: int, banco: str) -> Optional[float]:
        """
        Busca el saldo final del mes anterior para usarlo como saldo inicial.
        
        Returns:
            Saldo final del mes anterior o None
        """
        # Calcular mes/año anterior
        if mes == 1:
            mes_ant = 12
            año_ant = año - 1
        else:
            mes_ant = mes - 1
            año_ant = año

        clave_ant = f"{año_ant}-{mes_ant:02d}"

        if clave_ant in self.saldos:
            if self.saldos[clave_ant].get("cerrado"):
                banco_data = self.saldos[clave_ant].get(banco)
                if banco_data and isinstance(banco_data, dict):
                    saldo_final = float(banco_data.get("final", 0.0))
                    print(f"[SaldosMensuales] 🔄 Arrastrando saldo de {clave_ant}: {saldo_final}")
                    return saldo_final

        return None

    # ============================================================
    # CIERRE DE MES
    # ============================================================
    def cerrar_mes(self, mes: int, año: int, saldos_finales: Dict[str, Dict]) -> bool:
        """
        Cierra un mes guardando los saldos finales de todos los bancos.
        
        Args:
            mes: Número del mes
            año: Año
            saldos_finales: Dict con estructura:
                {
                    "Caja": {"inicial": X, "final": Y, "ingresos": Z, "gastos": W},
                    "Union Bank": {...},
                    ...
                }
                
        Returns:
            True si se guardó correctamente
        """
        clave = f"{año}-{mes:02d}"

        # Crear o actualizar entrada
        self.saldos[clave] = saldos_finales.copy()
        self.saldos[clave]["fecha_cierre"] = datetime.now().strftime("%d/%m/%Y")
        self.saldos[clave]["cerrado"] = True

        self._guardar()
        print(f"[SaldosMensuales] ✅ Mes {clave} cerrado correctamente")
        return True

    def mes_cerrado(self, mes: int, año: int) -> bool:
        """
        Verifica si un mes está cerrado.
        
        Returns:
            True si el mes está cerrado
        """
        clave = f"{año}-{mes:02d}"
        return self.saldos.get(clave, {}).get("cerrado", False)

    def reabrir_mes(self, mes: int, año: int) -> bool:
        """
        Reabre un mes cerrado (para correcciones).
        
        Returns:
            True si se reabrió correctamente
        """
        clave = f"{año}-{mes:02d}"

        if clave in self.saldos:
            self.saldos[clave]["cerrado"] = False
            self.saldos[clave]["fecha_reapertura"] = datetime.now().strftime("%d/%m/%Y")
            self._guardar()
            print(f"[SaldosMensuales] 🔓 Mes {clave} reabierto")
            return True

        return False

    # ============================================================
    # EDICIÓN MANUAL
    # ============================================================
    def editar_saldo_inicial(self, mes: int, año: int, banco: str, nuevo_saldo: float) -> bool:
        """
        Permite editar manualmente el saldo inicial de un banco/mes.
        Útil para correcciones.
        
        Returns:
            True si se editó correctamente
        """
        clave = f"{año}-{mes:02d}"

        # Crear entrada si no existe
        if clave not in self.saldos:
            self.saldos[clave] = {}

        # Crear datos del banco si no existen
        if banco not in self.saldos[clave]:
            self.saldos[clave][banco] = {
                "inicial": 0.0,
                "final": 0.0,
                "ingresos": 0.0,
                "gastos": 0.0
            }

        # Actualizar saldo inicial
        self.saldos[clave][banco]["inicial"] = float(nuevo_saldo)
        self._guardar()

        print(f"[SaldosMensuales] ✏️ Saldo inicial editado: {banco} {clave} = {nuevo_saldo}")
        return True

    # ============================================================
    # UTILIDADES
    # ============================================================
    def obtener_todos_los_bancos(self) -> list:
        """
        Obtiene lista de todos los bancos registrados en el sistema.
        
        Returns:
            Lista de nombres de bancos
        """
        bancos = set()

        for mes_data in self.saldos.values():
            for key in mes_data.keys():
                if key not in ["fecha_cierre", "cerrado", "fecha_reapertura"]:
                    bancos.add(key)

        return sorted(list(bancos))

    def obtener_resumen_mes(self, mes: int, año: int) -> Optional[Dict]:
        """
        Obtiene el resumen completo de un mes.
        
        Returns:
            Dict con todos los datos del mes o None
        """
        clave = f"{año}-{mes:02d}"
        return self.saldos.get(clave)

    def limpiar_cache(self):
        """Recarga los saldos desde el archivo (útil después de ediciones externas)."""
        self._cargar()

    # ============================================================
    # EDICION / ELIMINACION COMPLETA
    # ============================================================
    def actualizar_saldo_completo(self, mes: int, año: int, banco: str, inicial: float, ingresos: float, gastos: float, final: float):
        """Permite editar todos los campos de un banco en un mes."""
        clave = f"{año}-{mes:02d}"
        if clave not in self.saldos:
            self.saldos[clave] = {}
        if banco not in self.saldos[clave]:
            self.saldos[clave][banco] = {}
        self.saldos[clave][banco].update({
            "inicial": float(inicial),
            "ingresos": float(ingresos),
            "gastos": float(gastos),
            "final": float(final)
        })
        self._guardar()
        print(f"[SaldosMensuales] ✅ Saldo actualizado {banco} {clave}: ini={inicial}, ing={ingresos}, gas={gastos}, fin={final}")

    def eliminar_saldo_banco(self, mes: int, año: int, banco: str) -> bool:
        """Elimina el registro de un banco en un mes. Si el mes queda vacío, se elimina la entrada."""
        clave = f"{año}-{mes:02d}"
        if clave not in self.saldos or banco not in self.saldos[clave]:
            return False
        self.saldos[clave].pop(banco, None)
        # Si solo quedan campos meta, eliminar mes
        restantes = {k: v for k, v in self.saldos[clave].items() if k not in ["fecha_cierre", "fecha_reapertura", "cerrado"]}
        if not restantes:
            self.saldos.pop(clave, None)
        self._guardar()
        print(f"[SaldosMensuales] ✅ Banco {banco} eliminado de {clave}")
        return True
