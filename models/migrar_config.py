# -*- coding: utf-8 -*-
"""
models/migrar_config.py — Migración automática de configuración base
====================================================================
El instalador copia bancos.json y plan_contable_v3.json con
`onlyifdoesntexist` (para no pisar los datos/personalizaciones de la usuaria).
Eso significa que, cuando una versión nueva añade entradas (p. ej. las cuentas
556/557 o los apartados "Cambio Euros"/"Contrapartida"), las instalaciones
existentes se quedan SIN ellas y antes había que mandar los JSON a mano.

Este módulo resuelve eso al arrancar la app:
  1. Compara la copia del usuario (data/ junto al exe) con la versión
     empaquetada (ruta_recurso → _MEIPASS en el exe, data/ en desarrollo).
  2. Si al usuario le faltan entradas, hace un BACKUP de su archivo actual
     en backups/ y FUSIONA solo lo que falta (añade lo nuevo, conserva todo
     lo que la usuaria ya tenga: nombres personalizados, saldos, cuentas).
  3. Si el archivo del usuario no existe, copia la versión empaquetada.

La operación es idempotente: tras la primera fusión no queda nada que añadir,
así que las siguientes ejecuciones no escriben nada ni crean más backups.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

try:
    from utils.rutas import ruta_recurso, ruta_datos_usuario
except ImportError:
    def ruta_recurso(p):
        return Path(p)

    def ruta_datos_usuario(p):
        return Path("data") / p

# Archivos de configuración base que se migran (añadir aquí futuros configs).
ARCHIVOS_CONFIG = [
    "bancos.json",
    "plan_contable_v3.json",
]


# ============================================================
# FUSIÓN POR TIPO DE ARCHIVO
# ============================================================
def _fusionar_bancos(usuario, empaquetado):
    """Añade bancos del paquete que no existan por nombre (case-insensitive).

    Conserva los bancos existentes y sus saldos; los nuevos reciben el
    siguiente id libre. Devuelve la lista de nombres añadidos.
    """
    banks_u = usuario.get("banks", [])
    nombres = {str(b.get("nombre", "")).strip().lower() for b in banks_u}
    max_id = max((int(b.get("id", 0)) for b in banks_u), default=0)

    añadidos = []
    for b in empaquetado.get("banks", []):
        nombre = str(b.get("nombre", "")).strip()
        if nombre.lower() not in nombres:
            nuevo = dict(b)
            max_id += 1
            nuevo["id"] = max_id
            banks_u.append(nuevo)
            nombres.add(nombre.lower())
            añadidos.append(nombre)
    usuario["banks"] = banks_u
    return añadidos


def _fusionar_plan_contable(usuario, empaquetado):
    """Añade códigos de cuenta del paquete que no existan en la copia del usuario.

    No toca las cuentas existentes (aunque el paquete las haya renombrado).
    Devuelve la lista de códigos añadidos.
    """
    añadidos = []
    for codigo, info in empaquetado.items():
        if codigo not in usuario:
            usuario[codigo] = info
            añadidos.append(codigo)
    return añadidos


def _fusionar(archivo, usuario, empaquetado):
    if archivo == "bancos.json":
        return _fusionar_bancos(usuario, empaquetado)
    return _fusionar_plan_contable(usuario, empaquetado)


# ============================================================
# I/O
# ============================================================
def _leer_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None


def _escribir_json(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def _backup(ruta_origen, backups_dir):
    backups_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = backups_dir / f"{ruta_origen.name}.{ts}.bak"
    shutil.copy2(ruta_origen, destino)
    return destino


# ============================================================
# MIGRACIÓN PRINCIPAL
# ============================================================
def migrar_configuracion():
    """Fusiona las configs empaquetadas en la copia del usuario (con backup).

    Returns:
        list[(archivo, [entradas añadidas])] — vacío si no hubo cambios.
    """
    cambios = []

    for archivo in ARCHIVOS_CONFIG:
        try:
            ruta_empaquetado = ruta_recurso("data/" + archivo)
            ruta_usuario = ruta_datos_usuario(archivo)
            cambios += _migrar_un_archivo(archivo, ruta_empaquetado, ruta_usuario)
        except Exception as e:  # nunca debe impedir el arranque
            print(f"[Migracion] WARN {archivo}: {e}")

    return cambios


def _migrar_un_archivo(archivo, ruta_empaquetado, ruta_usuario):
    """Migra un único archivo; devuelve [(archivo, añadidos)] o []."""
    if not Path(ruta_empaquetado).exists():
        return []

    # En desarrollo empaquetado y usuario son el MISMO archivo (repo data/) → no-op
    try:
        if Path(ruta_empaquetado).resolve() == Path(ruta_usuario).resolve():
            return []
    except OSError:
        pass

    empaquetado = _leer_json(ruta_empaquetado)
    if empaquetado is None:
        return []

    # 1) No existe copia del usuario → instalar la versión empaquetada
    if not Path(ruta_usuario).exists():
        Path(ruta_usuario).parent.mkdir(parents=True, exist_ok=True)
        _escribir_json(ruta_usuario, empaquetado)
        print(f"[Migracion] OK {archivo}: copia inicial instalada")
        return [(archivo, ["(copia inicial)"])]

    usuario = _leer_json(ruta_usuario)
    if usuario is None:
        # Archivo del usuario corrupto → respaldo y restauración limpia
        backups_dir = Path(ruta_usuario).parent.parent / "backups"
        _backup(ruta_usuario, backups_dir)
        _escribir_json(ruta_usuario, empaquetado)
        print(f"[Migracion] WARN {archivo}: corrupto, restaurado (backup en backups/)")
        return [(archivo, ["(restaurado desde backup corrupto)"])]

    # 2) Fusión: añadir solo lo que falta
    añadidos = _fusionar(archivo, usuario, empaquetado)
    if not añadidos:
        return []  # ya está al día → no escribe nada

    backups_dir = Path(ruta_usuario).parent.parent / "backups"
    _backup(ruta_usuario, backups_dir)
    _escribir_json(ruta_usuario, usuario)
    print(f"[Migracion] OK {archivo}: anadidas {len(añadidos)} entradas -> {', '.join(map(str, añadidos))}")
    return [(archivo, añadidos)]


if __name__ == "__main__":
    for archivo, añadidos in migrar_configuracion():
        print(f"  {archivo}: {añadidos}")
