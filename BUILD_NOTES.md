# BUILD NOTES — SHILLONG CONTABILIDAD v3.8.3
> Para agentes de build, CI y despliegue. Última actualización: 2026-03-29

---

## Versión objetivo: 3.8.3
- **Base:** v3.8.2 (build 2026-03-19)
- **Comit de referencia:** `e2d0d09`
- **Rama:** `main`

---

## Cambios de esta iteración (2026-03-29)

### 1. `data/bancos.json` — campo `cuenta_contable` nuevo
- Todos los bancos ahora tienen el campo `"cuenta_contable": "57xx"`.
- Este archivo es la **única fuente de verdad** para el mapeo banco → Plan Contable.
- Al agregar un banco nuevo desde la GUI, el campo se escribe aquí automáticamente.
- **Impacto build:** copiar al instalador en `data/bancos.json` — el archivo de instalación `C:\SHILLONG CONTABILIDAD v3 PRO\data\bancos.json` ya fue actualizado manualmente; el próximo build lo incluirá directo desde source.

### 2. `models/BankManager.py` — nuevos métodos
| Método | Propósito |
|--------|-----------|
| `get_cuenta_contable(nombre_banco)` | Devuelve el código 57xx de un banco por nombre |
| `agregar_banco(nombre, cuenta_contable)` | Agrega banco a `bancos.json`, auto-genera ID |

### 3. `models/ContabilidadData.py` — año dinámico
- **Antes:** `archivo_json = "shillong_2026.json"` (hardcodeado)
- **Ahora:** `_archivo_datos_por_defecto()` usa `datetime.now().year`  
- Efecto: el 1 de enero de 2027 cargará `shillong_2027.json` automáticamente.
- **Impacto build:** ninguno. No requiere cambio en el `.spec` ni en los recursos empaquetados.

### 4. `models/auto_learn.py` + `models/fix_data.py` — año dinámico
- Parámetros por defecto y bloques `__main__` usan `datetime.now().year`.

### 5. `ui/DashboardView.py` + `ui/LibroMensualView.py` — año dinámico
- Nombres de archivos de backup ya no llevan `2026` fijo.

### 6. `ui/RegistrarView.py` — auto-asignación de `cuenta_banco`
- Al guardar un movimiento nuevo, llama a `BankManager.get_cuenta_contable(banco)`.
- Campo `cuenta_banco` se almacena en el JSON del movimiento.
- Retrocompatible: si el banco no tiene `cuenta_contable` en `bancos.json`, queda `""`.

### 7. `tools/migrar_banco_57xx.py` — lee mapa desde `bancos.json`
- Eliminado el diccionario `BANCO_A_CUENTA` hardcodeado.
- Nueva función `_cargar_mapa_bancos()` lee `data/bancos.json`.
- **Impacto operativo:** para migrar datos existentes en instalaciones nuevas, ejecutar este script una vez sobre la instalación.

### 8. `ui/Dialogs/GestorBancosDialog.py` — **ARCHIVO NUEVO**
- Diálogo GUI completo para gestionar bancos sin tocar JSON.
- Tabla con columnas: ID | Nombre | Cuenta Contable | Saldo Inicial
- Acciones: Agregar, Editar, Eliminar
- Combo de cuentas 57xx poblado desde `plan_contable_v3.json` (editable para códigos nuevos)
- Guarda cambios en tiempo real en `bancos.json` vía `BankManager._guardar()`
- **Impacto build:** agregar al `.spec` en la sección `Analysis` — el archivo vive en `ui/Dialogs/` que ya está incluido por wildcard. Verificar que `ui/Dialogs/` esté en el `pathex` o `datas` del `.spec`.

### 9. `ui/ToolsView.py` — botón Gestionar Bancos
- Nueva tarjeta **"🏦 Gestionar Bancos"** en sección *Gestión de Datos* (fila 2, col 1).
- Lanza `GestorBancosDialog`.
- Import con `try/except` — si el módulo falla, muestra mensaje de error en lugar de crashear.

---

## Checklist antes del build

- [ ] Verificar `data/bancos.json` tiene `cuenta_contable` en todos los bancos
- [ ] Verificar `data/plan_contable_v3.json` tiene todas las cuentas 57xx necesarias
- [ ] Confirmar que `ui/Dialogs/GestorBancosDialog.py` está incluido en el `.spec`
- [ ] Correr `python tools/migrar_banco_57xx.py` en instalaciones que tengan movimientos sin `cuenta_banco`
- [ ] Bump de versión: `core/version.json` → `3.8.3`, `core/version.py` → `3.8.3`

---

## Archivos fuente modificados (commit `e2d0d09`)

```
data/bancos.json                        ← campo cuenta_contable añadido
models/BankManager.py                   ← 2 métodos nuevos
models/ContabilidadData.py              ← año dinámico
models/auto_learn.py                    ← año dinámico
models/fix_data.py                      ← año dinámico
tools/migrar_banco_57xx.py              ← lee mapa de bancos.json
ui/DashboardView.py                     ← backup con año dinámico
ui/LibroMensualView.py                  ← backup con año dinámico
ui/RegistrarView.py                     ← auto-asigna cuenta_banco
ui/ToolsView.py                         ← botón Gestionar Bancos
ui/Dialogs/GestorBancosDialog.py        ← NUEVO
```

---

## Notas de migración para instalaciones existentes

1. **`shillong_2026.json` sin `cuenta_banco`**: ejecutar `tools/migrar_banco_57xx.py` apuntando a la instalación.
2. **`bancos.json` antiguo sin `cuenta_contable`**: copiar el nuevo `data/bancos.json` o agregar el campo manualmente.
3. **No se requiere cambiar `plan_contable_v3.json`** — las cuentas 57xx ya existen.

---

## Trabajo actual: Exportador programático para "Modelo evolutivo presupuestario"

### Contexto
- El export de "Modelo evolutivo presupuestario" usaba datos embebidos en templates XLSX en lugar de calcular desde `data/shillong_2026.json`.
- Solución: Generar el reporte programáticamente usando las funciones de cálculo existentes.

### Cambios implementados (commit `a68ff7e`)
- `models/ExportadorModeloEvolutivo.py`: Nuevo módulo para generar XLSX con layout del reporte (secciones 6=Gastos, 7=Ingresos, 2=Inversiones), headers, datos y totales.
- `ui/InformesView.py`: Actualizado `_exportar_excel_modelo_sisters()` para usar el exportador programático primero, fallback a template.
- `tests/test_modelo_evolutivo.py`: Test standalone para verificar generación.
- `tools/check_dist_template.py` y `tools/force_clean_dist_template.py`: Scripts para inspeccionar y limpiar templates empaquetados.

### Tareas pendientes
1. **Patch print regeneration**: Modificar `ui/InformesView.py` en `_imprimir()` y `_exportar_excel_vista()` para llamar a `_mostrar_reporte_modelo_sisters()` antes de imprimir/exportar, evitando datos stale en print.
2. **Rebuild installer**: Ejecutar `.\build_full.ps1` para incluir el nuevo exportador en el EXE.
3. **Manual GUI verification**: Instalar el EXE, generar el reporte desde la GUI, exportar XLSX y verificar que use datos actuales (comparar con `tools/compare_export_json.py`).

### Checklist antes del build
- [ ] Confirmar que `models/ExportadorModeloEvolutivo.py` esté incluido en `SHILLONG_v3_PRO.spec` (debería estar por wildcard en `models/`).
- [ ] Verificar que openpyxl esté en las dependencias del `.spec`.
- [ ] Bump de versión si aplica: `core/version.json` y `core/version.py` → `3.8.3` (si se considera nueva feature).

### Archivos fuente modificados (commit `a68ff7e`)
```
models/ExportadorModeloEvolutivo.py    ← NUEVO
tests/test_modelo_evolutivo.py         ← NUEVO
tools/check_dist_template.py          ← NUEVO
tools/force_clean_dist_template.py    ← NUEVO
ui/InformesView.py                    ← modificado
```

---

## Updates and Issues

### Updates (2026-05-06)
- **Commit `a68ff7e`**: Implemented programmatic exporter for "Modelo evolutivo presupuestario" report. Fixes issue where exports used embedded sample data instead of real JSON calculations.
- **Commit `584f4e2`**: Documented pending tasks and current work in BUILD_NOTES.md.
- **Remote push**: All commits pushed to `origin/main` on GitHub.

### Issues
1. **Print regeneration not patched**: The `_imprimir()` and `_exportar_excel_vista()` methods in `ui/InformesView.py` do not force regenerate the UI view before printing/exporting, which could lead to stale data in printed reports.
   - **Status**: Pending implementation.
   - **Impact**: Low - affects print only, not export XLSX.
   - **Fix**: Add call to `_mostrar_reporte_modelo_sisters()` before print/export.

2. **Installer not rebuilt**: The packaged EXE in `dist/` does not include the new exporter module.
   - **Status**: Pending rebuild.
   - **Impact**: High - users won't have the fix until installer is updated.
   - **Fix**: Run `.\build_full.ps1` to rebuild with PyInstaller.

3. **Manual verification not done**: No GUI testing of the export in the installed app.
   - **Status**: Pending.
   - **Impact**: Medium - code tested standalone, but not in packaged environment.
   - **Fix**: Install EXE, generate report, export XLSX, compare with `tools/compare_export_json.py`.

4. **Version bump not applied**: Version remains 3.8.2, but new feature added.
   - **Status**: Pending decision.
   - **Impact**: Low - versioning for tracking.
   - **Fix**: Update `core/version.json` and `core/version.py` to 3.8.3 if considering this a minor release.

### Next Steps
- Patch print regeneration.
- Rebuild installer.
- Manual GUI verification.
- Decide on version bump.
