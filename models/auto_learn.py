# -*- coding: utf-8 -*-
"""
models/auto_learn.py
Script de AUTO-APRENDIZAJE.
Lee el historial de movimientos y enriquece las reglas automáticamente.
"""
import json
from pathlib import Path

def ejecutar_aprendizaje(ruta_movimientos="data/shillong_2026.json", ruta_reglas="data/reglas_conceptos.json"):
    path_mov = Path(ruta_movimientos)
    path_reg = Path(ruta_reglas)

    if not path_mov.exists() or not path_reg.exists():
        return 0, "Faltan archivos de datos."

    # 1. Cargar Movimientos y Reglas
    try:
        with open(path_mov, "r", encoding="utf-8") as f:
            data_mov = json.load(f)
            movimientos = data_mov.get("movimientos", [])

        with open(path_reg, "r", encoding="utf-8") as f:
            reglas = json.load(f)
    except Exception as e:
        return 0, f"Error leyendo archivos: {str(e)}"

    aprendidos = 0
    
    # 2. Analizar historial
    for m in movimientos:
        cuenta = str(m.get("cuenta", "")).strip()
        # Limpiamos el concepto: minúsculas y sin espacios extra
        concepto_raw = m.get("concepto", "").lower().strip()
        
        # Filtros de seguridad: ignorar conceptos muy cortos o vacíos
        if len(concepto_raw) < 3 or not cuenta:
            continue
            
        # Solo aprendemos de cuentas que ya existen en las reglas (ej: 603000, 600000)
        if cuenta in reglas:
            lista_actual = reglas[cuenta].get("permitidos", [])
            
            # ¿El concepto ya está en la lista?
            # Buscamos coincidencia exacta o parcial
            ya_existe = any(x in concepto_raw for x in lista_actual)
            
            if not ya_existe:
                # ¡NUEVO CONOCIMIENTO!
                # Añadimos el concepto a la lista de permitidos de esa cuenta
                reglas[cuenta]["permitidos"].append(concepto_raw)
                aprendidos += 1
                print(f"🧠 Aprendido: '{concepto_raw}' pertenece a {cuenta}")

    # 3. Guardar cambios si aprendió algo
    if aprendidos > 0:
        try:
            with open(path_reg, "w", encoding="utf-8") as f:
                json.dump(reglas, f, indent=4, ensure_ascii=False)
            return aprendidos, f"El sistema ha aprendido {aprendidos} nuevos conceptos."
        except Exception as e:
            return 0, f"Error guardando reglas: {str(e)}"
    
    return 0, "El sistema ya conocía todos los conceptos. Nada nuevo."