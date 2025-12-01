# -*- coding: utf-8 -*-
"""
models/fix_data.py
Script de emergencia para corregir el error DEBE vs HABER en gastos.
"""
import json
from pathlib import Path

def reparar_json(archivo_entrada="data/shillong_2026.json"):
    path = Path(archivo_entrada)
    
    if not path.exists():
        print(f"❌ No encuentro el archivo: {path}")
        return

    # 1. Cargar datos
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    movimientos = data.get("movimientos", [])
    corregidos = 0
    
    print(f"🔍 Analizando {len(movimientos)} movimientos...")

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
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n✅ ¡ÉXITO! Se han corregido {corregidos} movimientos erróneos.")
        print("Ahora tu saldo bancario debería ser real.")
    else:
        print("\n👍 Todo parece correcto. No se encontraron errores de Debe/Haber.")

if __name__ == "__main__":
    # Ajusta el nombre del archivo si es distinto
    reparar_json("data/shillong_2026.json")