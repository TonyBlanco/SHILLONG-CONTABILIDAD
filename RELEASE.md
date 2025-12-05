# Shillong Contabilidad – Release Notes (v3.8.x)

## Novedades
- Hub único “Cierres & BI” con Libro Mensual, Cierre Mensual, Cierre Anual e Informes BI en pestañas.
- Libro Mensual ahora incluye:
  - Gestor de saldos protegido (menni1234): cargar/editar/eliminar saldos por mes/banco y arrastrar cierre previo.
  - Al pedir saldo inicial propone usar el saldo final del mes anterior y permite abrir el gestor.
  - Exportar Excel pregunta si desea abrir el archivo generado y guarda en `reportes/<YYYY-MM>/<modo>/`.
- Auditoría rápida en Herramientas para detectar faltantes/duplicados y validar totales Debe/Haber.
- Sidebar con logo inferior para identificación de la app.

## Notas operativas
- Contraseña de acciones sensibles: `menni1234`.
- Exportes y reportes se organizan en la carpeta `reportes/` por mes y categoría.
- El cierre de mes en Libro Mensual solicita firma y valida totales antes de guardar saldos finales.

## Archivos clave tocados
- `ui/LibroMensualView.py`, `models/SaldosMensuales.py`, `ui/ToolsView.py`, `ui/Sidebar.py`, `ui/CierresHub.py`, `ui/MainWindow.py`, `ui/CierreMensualView.py`.
