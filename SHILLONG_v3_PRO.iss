; ============================================================
; SHILLONG CONTABILIDAD v3.7.7 PRO — INSTALLER PROFESIONAL
; Características:
; - Mensaje de Bienvenida "SHALOM"
; - Selección de carpeta (Local o Red)
; - Permisos de escritura automáticos
; ============================================================

#define MyAppName "SHILLONG CONTABILIDAD v3 PRO"
#define MyAppVersion "3.7.7"
#define MyAppPublisher "Shillong Soft"
#define MyAppURL "https://github.com/TonyBlanco/SHILLONG-CONTABILIDAD"
#define MyAppExeName "SHILLONG_v3_PRO.exe"
#define MyAppIconName "shillong_logov3.ico"

[Setup]
; --- IDENTIFICACIÓN ---
AppId={{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; --- INSTALACIÓN Y RUTAS ---
DefaultDirName={autopf}\{#MyAppName}
; ¡IMPORTANTE! Esto permite al usuario ELEGIR dónde instalar
DisableDirPage=no
; Permite instalar en la raíz del disco (ej: D:\Shillong)
AllowRootDirectory=yes
; Permite instalar en unidades de red (ej: Z:\Contabilidad)
AllowNetworkDrive=yes
; Permite rutas de red directas (ej: \\Servidor\Carpeta)
AllowUNCPath=yes

; --- PERMISOS ---
PrivilegesRequired=admin

; --- SALIDA ---
OutputDir=Output
OutputBaseFilename=Instalador_Shillong_v3.7.7_PRO
SetupIconFile=assets\shillong_logov3.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; --- 1. PROGRAMA PRINCIPAL ---
; Asegúrate de que la ruta 'Source' coincida con donde PyInstaller creó tu carpeta o archivo.
Source: "dist\SHILLONG_v3_PRO\*"; DestDir: "{app}"; Excludes: "\data\*"; Flags: ignoreversion recursesubdirs createallsubdirs

; --- 2. DATOS INICIALES (PROTEGIDOS) ---
; Copia los JSON solo si no existen, para no borrar datos previos.
; Copia configuraciones (bancos, reglas, plan) pero IGNORA el archivo de movimientos del desarrollador
Source: "data\*"; DestDir: "{app}\data"; Excludes: "shillong_*.json"; Flags: onlyifdoesntexist recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\{#MyAppIconName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\{#MyAppIconName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Dirs]
; --- PERMISOS DE ESCRITURA (CRUCIAL PARA WINDOWS) ---
; Permite que la app guarde datos sin ser Administrador
Name: "{app}\backups"; Permissions: users-modify
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify

[Registry]
; --- FORZAR EJECUCIÓN COMO ADMINISTRADOR ---
; Esto marca automáticamente la casilla "Ejecutar como administrador" en el exe instalado.
Root: HKCU; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; \
    ValueType: string; ValueName: "{app}\{#MyAppExeName}"; ValueData: "~ RUNASADMIN"; \
    Flags: uninsdeletevalue

[Code]
// --- LÓGICA DE INICIO ---
function InitializeSetup(): Boolean;
var
  Respuesta: Integer;
begin
  // 1. MENSAJE DE BIENVENIDA "SHALOM"
  MsgBox('🕊️ SHALOM!' + #13#10 + #13#10 +
         'Bienvenido al instalador de Shillong Contabilidad v3.7 PRO.' + #13#10 +
         'Que este software sea de gran bendición y utilidad.', 
         mbInformation, MB_OK);

  // 2. AVISO DE SEGURIDAD (BACKUP)
  Respuesta := MsgBox('⚠️ AVISO DE SEGURIDAD ⚠️' + #13#10 + #13#10 +
                      'Si está actualizando una versión anterior, se recomienda tener una COPIA DE SEGURIDAD de sus datos.' + #13#10 + #13#10 +
                      'El instalador intentará respetar sus datos existentes, pero es mejor prevenir.' + #13#10 + #13#10 +
                      '¿Desea continuar con la instalación?',
                      mbConfirmation, MB_YESNO);

  if Respuesta = IDYES then
    Result := True
  else
    Result := False;
end;

// --- CREACIÓN DE ARCHIVOS POR DEFECTO ---
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Si por alguna razón no hay bancos.json, creamos uno básico
    if not FileExists(ExpandConstant('{app}\data\bancos.json')) then
    begin
      SaveStringToFile(
        ExpandConstant('{app}\data\bancos.json'),
        '{ "banks": ['#13#10 +
        '  { "id": 1, "nombre": "Federal Bank", "saldo": 0.0 },'#13#10 +
        '  { "id": 2, "nombre": "SBI", "saldo": 0.0 },'#13#10 +
        '  { "id": 3, "nombre": "Union Bank", "saldo": 0.0 },'#13#10 +
        '  { "id": 4, "nombre": "Otro", "saldo": 0.0 },'#13#10 +
        '  { "id": 5, "nombre": "Caja", "saldo": 0.0 }'#13#10 +
        '] }',
        False);
    end;
  end;
end;
