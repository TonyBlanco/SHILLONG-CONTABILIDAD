; ============================================================
; SHILLONG CONTABILIDAD v3 PRO — INSTALLER PROFESIONAL (CORREGIDO)
; Adaptado para estructura "One-File" (Un solo ejecutable)
; ============================================================

#define MyAppName "SHILLONG CONTABILIDAD v3 PRO"
#define MyAppVersion "3.6"
#define MyAppPublisher "Shillong Soft" 
#define MyAppURL "https://www.tuweb.com"
#define MyAppExeName "SHILLONG CONTABILIDAD v3 PRO.exe"
#define MyAppIconName "shillong_logov3.ico"

[Setup]
; --- Identidad ---
AppId={{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}

; --- Directorios ---
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=SHILLONG_v3_PRO_Setup_Final

; --- Estética y Iconos ---
; Usamos ruta absoluta para evitar errores de "file not found"
SetupIconFile=D:\ShillongV3\shillong_logov3.ico
WizardStyle=modern
EnableDirDoesntExistWarning=yes

; --- Compresión PRO ---
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64

; --- Sistema ---
CreateUninstallRegKey=yes
ChangesAssociations=yes
PrivilegesRequired=admin

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
; Solo dejamos el icono de escritorio aquí
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked

[Run]
; Aquí es donde ocurre la magia. 
; "postinstall" crea automáticamente la casilla de "Iniciar aplicación" en la pantalla final.
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Files]
; === 1. EL EJECUTABLE PRINCIPAL (CORREGIDO) ===
; Apunta directamente al archivo único que tienes en D:\ShillongV3\dist
Source: "D:\ShillongV3\dist\SHILLONG CONTABILIDAD v3 PRO.exe"; DestDir: "{app}"; Flags: ignoreversion

; === 2. EL ÍCONO NUEVO ===
Source: "D:\ShillongV3\shillong_logov3.ico"; DestDir: "{app}"; Flags: ignoreversion

; NOTA: Si tu EXE ya incluye dentro los reportes y templates (modo One-File), 
; NO hace falta copiarlos aquí. Si necesitas archivos externos obligatorios,
; descomenta las siguientes líneas, pero verifica que las rutas existan:
; Source: "D:\ShillongV3\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs

[Icons]
; Aquí usamos las variables para que no falle el nombre del ícono
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIconName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIconName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar Aplicación"; Flags: nowait postinstall skipifsilent

[Code]
// Este código es vital para crear las carpetas vacías que necesita tu app para guardar datos
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Creamos carpetas de datos vacías para que el usuario pueda guardar cosas
    CreateDir(ExpandConstant('{app}\data'));
    CreateDir(ExpandConstant('{app}\data\cierres'));
    CreateDir(ExpandConstant('{app}\logs'));
    CreateDir(ExpandConstant('{app}\reports'));
    CreateDir(ExpandConstant('{app}\templates'));

    // Creamos el JSON base si no existe
    if not FileExists(ExpandConstant('{app}\data\shillong_2026.json')) then
      SaveStringToFile(ExpandConstant('{app}\data\shillong_2026.json'), '[]', False);
  end;
end;