# -*- coding: utf-8 -*-
"""
Motor de Cuentas v3.1 PRO — Aprendizaje Automático
==================================================
✔ Compatible con plan_contable_v3.json
✔ Compatible con reglas_conceptos.json
✔ Validación concepto ↔ cuenta contable
✔ Auto–aprendizaje
✔ Devuelve lista de cuentas: "600000 – Compra farmacia"
✔ 100% compatible con PyInstaller (ruta_recurso)
"""

import json
from pathlib import Path
from utils.rutas import ruta_recurso    # 🔥 RUTA UNIVERSAL PRO

class MotorCuentas:

    def __init__(self, archivo_json="data/plan_contable_v3.json"):

        # 🔥 Ruta universal — funciona en Python y en EXE
        self.archivo_json = ruta_recurso(archivo_json)

        self.cuentas = {}
        self.reglas = {}

        self.subcategorias = {
            "Huevos": "Huevos",
            "Leche": "Leche",
            "Pan": "Panadería",
            "Verduras": "Verduras",
            "Carne": "Carne",
            "Pollo": "Pollo",
            "Café": "Café",
        }

        self._cargar()
        self._cargar_reglas()

    # ---------------------------------------------------------
    def _cargar(self):
        """Carga el plan contable completo v3 usando ruta absoluta."""
        if not self.archivo_json.exists():
            raise FileNotFoundError(f"No existe {self.archivo_json}")

        with self.archivo_json.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.cuentas = {codigo: datos for codigo, datos in data.items()}

    # ---------------------------------------------------------
    def _cargar_reglas(self):
        """Carga reglas_conceptos.json con ruta universal."""
        ruta_reglas = ruta_recurso("data/reglas_conceptos.json")

        if not ruta_reglas.exists():
            print("⚠ ADVERTENCIA: No se encontró reglas_conceptos.json. Validación desactivada.")
            self.reglas = {}
            return

        try:
            with ruta_reglas.open("r", encoding="utf-8") as f:
                self.reglas = json.load(f)
        except Exception as e:
            print(f"⚠ ERROR cargando reglas_conceptos.json: {e}")
            self.reglas = {}

    # ---------------------------------------------------------
    def agregar_concepto_a_reglas(self, codigo, concepto):
        """Añade dinámicamente un concepto nuevo a reglas_conceptos.json."""
        ruta_reglas = ruta_recurso("data/reglas_conceptos.json")

        try:
            with ruta_reglas.open("r", encoding="utf-8") as f:
                reglas = json.load(f)
        except Exception as e:
            print(f"⚠ ERROR leyendo reglas_conceptos.json: {e}")
            return False

        concepto = concepto.lower().strip()

        if codigo not in reglas:
            reglas[codigo] = {
                "categoria": self.get_nombre(codigo),
                "permitidos": []
            }

        if concepto not in reglas[codigo]["permitidos"]:
            reglas[codigo]["permitidos"].append(concepto)

        try:
            with ruta_reglas.open("w", encoding="utf-8") as f:
                json.dump(reglas, f, indent=4, ensure_ascii=False)
            self.reglas = reglas
            return True
        except Exception as e:
            print(f"⚠ ERROR guardando reglas_conceptos.json: {e}")
            return False

    # ---------------------------------------------------------
    def listar_codigos(self):
        return sorted(self.cuentas.keys())
    # ---------------------------------------------------------
    # LISTA DE CUENTAS EN FORMATO "codigo – nombre"
    # ---------------------------------------------------------
    def cuentas_lista(self):
        lista = []
        for codigo in self.listar_codigos():
            lista.append(self.get_combo_display(codigo))
        return lista

    # ---------------------------------------------------------
    def get_nombre(self, codigo):
        return self.cuentas.get(codigo, {}).get("nombre", "")

    # ---------------------------------------------------------
    def get_descripcion(self, codigo):
        return self.cuentas.get(codigo, {}).get("descripcion", "")

    # ---------------------------------------------------------
    def get_combo_display(self, codigo):
        nombre = self.get_nombre(codigo)
        return f"{codigo} – {nombre}"

    # ---------------------------------------------------------
    def todas_las_opciones(self):
        lista = [self.get_combo_display(c) for c in self.listar_codigos()]
        lista.extend([f"SUB – {sub}" for sub in self.subcategorias])
        return lista

    # ---------------------------------------------------------
    def filtrar(self, texto):
        texto = texto.lower().strip()
        if texto == "":
            return self.todas_las_opciones()

        return [item for item in self.todas_las_opciones() if texto in item.lower()]

    # ---------------------------------------------------------
    def es_subcategoria(self, valor):
        return valor.startswith("SUB – ")

    # ---------------------------------------------------------
    def extraer_nombre_subcategoria(self, valor):
        return valor.replace("SUB – ", "").strip()

    # ---------------------------------------------------------
    def es_concepto_valido(self, codigo, concepto):
        """Valida que el concepto coincide con palabras clave permitidas."""
        codigo = codigo.strip()

        if codigo not in self.reglas:
            return True

        concepto = concepto.lower()

        for palabra in self.reglas[codigo]["permitidos"]:
            if palabra.lower() in concepto:
                return True

        return False
