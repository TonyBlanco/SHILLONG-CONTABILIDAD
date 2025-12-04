# -*- coding: utf-8 -*-
"""
MotorCuentas — SHILLONG CONTABILIDAD v3.7.8 PRO
Motor estable, limpio y 100% compatible con RegistrarView, LibroMensualView y Dashboard
"""

import json
from pathlib import Path

class MotorCuentas:

    def __init__(self, archivo="data/plan_contable_v3.json"):
        self.archivo = Path(archivo)
        self.cuentas = {}
        self.reglas = {}

        self.cargar_cuentas()

    # ============================================================
    # CARGA DE CUENTAS
    # ============================================================
    def cargar_cuentas(self):
        """Carga los datos del plan contable en memoria."""
        if not self.archivo.exists():
            print(f"[MotorCuentas] ERROR: No existe {self.archivo}")
            return

        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle BOTH formats:
            # Format 1 (old): {"cuentas": [{"codigo": "100", "nombre": "..."}, ...]}
            # Format 2 (actual): {"206000": {"nombre": "..."}, "211000": {...}, ...}
            
            if "cuentas" in data and isinstance(data.get("cuentas"), list):
                # Old format with list
                for c in data.get("cuentas", []):
                    codigo = str(c.get("codigo", "")).strip()
                    nombre = c.get("nombre", "Cuenta sin nombre")
                    permitidos = c.get("permitidos", [])

                    if codigo:
                        self.cuentas[codigo] = nombre
                        self.reglas[codigo] = {"permitidos": permitidos}
            else:
                # Actual format: dictionary with codes as keys
                for codigo, info in data.items():
                    if isinstance(info, dict) and "nombre" in info:
                        codigo_str = str(codigo).strip()
                        nombre = info.get("nombre", "Cuenta sin nombre")
                        permitidos = info.get("permitidos", [])
                        
                        self.cuentas[codigo_str] = nombre
                        self.reglas[codigo_str] = {"permitidos": permitidos}

            print(f"[MotorCuentas] {len(self.cuentas)} cuentas cargadas.")

        except Exception as e:
            print(f"[MotorCuentas] ERROR al cargar cuentas: {e}")

    # ============================================================
    # LISTA COMPLETA PARA COMBOBOX
    # ============================================================
    def todas_las_opciones(self):
        """Devuelve opciones en formato 'codigo – nombre'."""
        lista = []

        for codigo, nombre in sorted(self.cuentas.items()):
            lista.append(f"{codigo} – {nombre}")

        return lista

    # ============================================================
    # OBTENER NOMBRE DE CUENTA
    # ============================================================
    def get_nombre(self, codigo):
        codigo = str(codigo).strip()
        return self.cuentas.get(codigo, "Cuenta desconocida")

    # ============================================================
    # VALIDAR CONCEPTO
    # ============================================================
    def es_concepto_valido(self, codigo, concepto):
        codigo = str(codigo).strip()

        if codigo not in self.reglas:
            return True  # no reglas → se permite todo

        reglas = self.reglas[codigo].get("permitidos", [])
        if not reglas:
            return True

        concepto = concepto.lower()

        # Valida si alguna palabra permitida está dentro del concepto
        return any(p.lower() in concepto for p in reglas)

    # ============================================================
    # GUARDAR NUEVO CONCEPTO EN REGLAS
    # ============================================================
    def agregar_concepto_a_reglas(self, codigo, concepto):
        codigo = str(codigo).strip()

        if codigo not in self.reglas:
            self.reglas[codigo] = {"permitidos": []}

        concepto = concepto.lower().strip()

        if concepto not in self.reglas[codigo]["permitidos"]:
            self.reglas[codigo]["permitidos"].append(concepto)

            # Guardar cambios en archivo JSON
            try:
                with open(self.archivo, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Handle BOTH formats
                if "cuentas" in data and isinstance(data.get("cuentas"), list):
                    # Old format with list
                    for c in data.get("cuentas", []):
                        if str(c.get("codigo")) == codigo:
                            if "permitidos" not in c:
                                c["permitidos"] = []
                            if concepto not in c["permitidos"]:
                                c["permitidos"].append(concepto)
                else:
                    # Actual format: dictionary with codes as keys
                    if codigo in data and isinstance(data[codigo], dict):
                        if "permitidos" not in data[codigo]:
                            data[codigo]["permitidos"] = []
                        if concepto not in data[codigo]["permitidos"]:
                            data[codigo]["permitidos"].append(concepto)

                with open(self.archivo, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                print(f"[MotorCuentas] Regla añadida para {codigo}: {concepto}")

            except Exception as e:
                print(f"[MotorCuentas] ERROR guardando regla: {e}")
