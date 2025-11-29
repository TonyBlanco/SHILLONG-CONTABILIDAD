; ============================================================
; SHILLONG CONTABILIDAD v3 PRO — INSTALLER PROFESIONAL FINAL
; Estructura para PyInstaller ONEFOLDER (dist/SHILLONG_v3_PRO)
; ============================================================

#define MyAppName "SHILLONG CONTABILIDAD v3 PRO"
#define MyAppVersion "3.6.0"
#define MyAppPublisher "Shillong Soft"
#define MyAppURL "https://www.shillong-contabilidad.com"
#define MyAppExeName "SHILLONG_v3_PRO.exe"
#define MyAppIconName "shillong_logov3.ico"

[Setup]
AppId={{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Importante: Pide permisos de admin para escribir en Program Files
PrivilegesRequired=admin

OutputDir=Output
OutputBaseFilename=SHILLONG_v3_PRO_Setup
SetupIconFile=assets\shillong_logov3.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copiar todo el contenido de la carpeta generada por PyInstaller
Source: "dist\SHILLONG_v3_PRO\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\{#MyAppIconName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\{#MyAppIconName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Dirs]
; Crear carpeta de backups y logs por si acaso
Name: "{app}\backups"; Permissions: users-modify
Name: "{app}\data"; Permissions: users-modify

[Code]
// Sección para inicializar datos si es necesario (Opcional)
// Ten cuidado con sobrescribir datos si el usuario ya tiene la app instalada.
// El código original que tenías reiniciaba bancos.json. Si eso es lo que quieres, mantenlo.
// Si prefieres NO borrar los datos del usuario al actualizar, elimina o comenta esta parte.

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Ejemplo: Solo crear si no existe (para no borrar saldo de usuario)
    if not FileExists(ExpandConstant('{app}\data\bancos.json')) then
    begin
      SaveStringToFile(
        ExpandConstant('{app}\data\bancos.json'),
        '{ "banks": ['#13#10 +
        '  { "id": 1, "nombre": "Federal Bank", "saldo": 0.0 },'#13#10 +
        '  { "id": 2, "nombre": "SBI", "saldo": 0.0 },'#13#10 +
        '  { "id": 3, "nombre": "Union Bank", \"saldo\": 50000.0 },'#13#10 +
        '  { "id": 4, "nombre": "Otro", "saldo": 0.0 },'#13#10 +
        '  { "id": 5, "nombre": "Caja", "saldo": -20000.0 }'#13#10 +
        '] }',
        False);
    end;
  end;
end;