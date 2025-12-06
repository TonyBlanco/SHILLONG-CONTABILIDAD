# -*- coding: utf-8 -*-
"""
models/fix_data.py
Script de emergencia para corregir errores en el archivo de datos JSON.
- repara_ids_de_cuenta: Corrige el error de 'cuenta' con nombre en vez de ID.
- repara_errores_debe_haber: Corrige el error DEBE vs HABER en gastos.
"""
import json
from pathlib import Path

def repara_ids_de_cuenta(archivo_entrada="data/shillong_2026.json", archivo_plan_contable="data/plan_contable_v3.json"):
    """
    Lee un archivo JSON de movimientos, corrige los campos 'cuenta' que contienen
    un nombre de cuenta en lugar de un ID, y guarda el resultado en un nuevo
    archivo con el sufijo '.fixed'.
    """
    path_entrada = Path(archivo_entrada)
    path_plan = Path(archivo_plan_contable)
    path_salida = path_entrada.with_suffix(path_entrada.suffix + '.fixed')

    if not path_entrada.exists():
        print(f"❌ No encuentro el archivo de movimientos: {path_entrada}")
        return
    if not path_plan.exists():
        print(f"❌ No encuentro el plan contable: {path_plan}")
        return

    # 1. Cargar plan contable y crear mapa inverso (nombre -> id)
    with open(path_plan, "r", encoding="utf-8") as f:
        plan_contable = json.load(f)

    nombre_a_id = {v['nombre'].strip().lower(): k for k, v in plan_contable.items()}
    # Añadir algunas variaciones comunes encontradas en los datos
    nombre_a_id["teléfonos"] = "629200"
    nombre_a_id["telefonos"] = "629200"


    # 2. Cargar datos de movimientos
    with open(path_entrada, "r", encoding="utf-8") as f:
        data = json.load(f)

    movimientos = data.get("movimientos", [])
    corregidos = 0
    no_encontrados = set()

    print(f"🔍 Analizando {len(movimientos)} movimientos para corregir IDs de cuenta...")

    # 3. Recorrer y arreglar
    for m in movimientos:
        cuenta_val = m.get("cuenta", "")
        
        # Si la cuenta no es un número, es un nombre que hay que corregir
        if isinstance(cuenta_val, str) and not cuenta_val.strip().isdigit():
            cuenta_nombre = cuenta_val.strip().lower().rstrip(',')
            
            if cuenta_nombre in nombre_a_id:
                id_correcto = nombre_a_id[cuenta_nombre]
                if m["cuenta"] != id_correcto:
                    print(f"   🔧 Corregido: '{cuenta_val}' -> '{id_correcto}' (Concepto: {m.get('concepto', '')})")
                    m["cuenta"] = id_correcto
                    corregidos += 1
            else:
                if cuenta_nombre not in no_encontrados:
                    print(f"   ⚠️ No se encontró ID para el nombre de cuenta: '{cuenta_nombre}'")
                    no_encontrados.add(cuenta_nombre)

    # 4. Guardar siempre el archivo de salida
    with open(path_salida, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    if corregidos > 0:
        print(f"\n✅ ¡ÉXITO! Se han corregido {corregidos} IDs de cuenta.")
    else:
        print("\n👍 No se encontraron IDs de cuenta para corregir (se ha creado una copia).")
    
    print(f"El archivo de datos se ha procesado y guardado en: {path_salida}")


def repara_errores_debe_haber(archivo_entrada="data/shillong_2026.json"):
    path = Path(archivo_entrada)
    
    if not path.exists():
        print(f"❌ No encuentro el archivo: {path}")
        return

    # 1. Cargar datos
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    movimientos = data.get("movimientos", [])
    corregidos = 0
    
    print(f"🔍 Analizando {len(movimientos)} movimientos para errores de Debe/Haber...")

    # 2. Recorrer y arreglar
    for m in movimientos:
        cuenta = str(m.get("cuenta", ""))
        debe = float(m.get("debe", 0))
        haber = float(m.get("haber", 0))
        concepto = m.get("concepto", "")

        # CRITERIO: Si es cuenta de Gasto (6...) o Inversión (2...)
        # Y tiene importe en HABER pero no en DEBE... ¡ES UN ERROR!
        if (cuenta.startswith("6") or cuenta.startswith("2")) and haber > 0 and debe == 0:
            
            # --- LA CORRECCIÓN MÁGICA ---
            m["debe"] = haber       # Movemos el importe al DEBE
            m["haber"] = 0.0        # Vaciamos el HABER
            m["saldo"] = -haber     # El saldo ahora resta (dinero sale)
            
            print(f"   🔧 Reparado: {concepto} | {haber} INR movidos a Gasto.")
            corregidos += 1

    # 3. Guardar si hubo cambios
    if corregidos > 0:
        # ATENCIÓN: Este método sobrescribe el archivo que se le pasa.
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n✅ ¡ÉXITO! Se han corregido {corregidos} movimientos erróneos en {path}.")
        print("Ahora tu saldo bancario debería ser real.")
    else:
        print("\n👍 Todo parece correcto. No se encontraron errores de Debe/Haber.")

if __name__ == "__main__":
    print("--- INICIANDO REPARACIÓN DE IDs DE CUENTA ---")
    repara_ids_de_cuenta("data/shillong_2026.json")
    
    print("\n--- INICIANDO REPARACIÓN DE ERRORES DEBE/HABER ---")
    # Se ejecuta sobre el archivo recién corregido para encadenar los arreglos.
    fixed_file = "data/shillong_2026.json.fixed"
    if Path(fixed_file).exists():
        repara_errores_debe_haber(fixed_file)
    else:
        print("No se encontró archivo .fixed para analizar, saltando este paso.")