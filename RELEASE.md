# Shillong Contabilidad - Release Notes

## v3.8.3 (2026-03-29)

### Gestion dinamica de bancos
- bancos.json es la unica fuente de verdad para el mapeo banco -> cuenta contable (57xx).
- **Nueva GUI Gestionar Bancos** en Herramientas -> Gestion de Datos.
  Tabla de bancos con acciones Agregar / Editar / Eliminar, sin editar JSON.
- Al registrar un movimiento, cuenta_banco se asigna automaticamente desde bancos.json.
- Ano dinamico: carga shillong_{ano}.json segun el ano real. Funciona en 2027+ sin cambios.
- migrar_banco_57xx.py lee el mapa de bancos desde bancos.json (no mas hardcode).

### Archivos modificados en esta version
data/bancos.json, models/BankManager.py, models/ContabilidadData.py,
models/auto_learn.py, models/fix_data.py, tools/migrar_banco_57xx.py,
ui/DashboardView.py, ui/LibroMensualView.py, ui/RegistrarView.py,
ui/ToolsView.py, ui/Dialogs/GestorBancosDialog.py (NUEVO)

---

## v3.8.2 (2026-03-19)
- Hub Cierres and BI con Libro Mensual, Cierre Mensual, Cierre Anual e Informes BI.
- Gestor de saldos protegido (menni1234) en Libro Mensual.
- Exportar Excel con apertura opcional, en reportes/YYYY-MM/modo/.
- Auditoria rapida en Herramientas.
- Sidebar con logo inferior.

### Notas operativas
- Contrasena acciones sensibles: menni1234
- Archivos: ui/LibroMensualView.py, models/SaldosMensuales.py, ui/ToolsView.py,
  ui/Sidebar.py, ui/CierresHub.py, ui/MainWindow.py, ui/CierreMensualView.py
