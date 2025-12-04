#define MyAppName "SHILLONG CONTABILIDAD v3 PRO"
#define MyAppVersion "3.7.8"
#define MyAppPublisher "Shillong Soft"
#define MyAppURL "https://github.com/TonyBlanco/SHILLONG-CONTABILIDAD"
#define MyAppExeName "SHILLONG_v3_PRO.exe"

[Setup]
AppId={{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=no
AllowRootDirectory=yes
AllowNetworkDrive=yes
AllowUNCPath=yes
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=Instalador_Shillong_v3.7.8_PRO
SetupIconFile=assets\shillong_logov3.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; ← LOGO (solo pequeño, sin ñ y en sección correcta)
WizardSmallImageFile=assets\shillong_logo_pequeno.bmp

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked

[Files]
; Archivos de la aplicación (EXE, DLLs, etc.) - Se actualizan siempre
Source: "dist\SHILLONG_v3_PRO\*"; DestDir: "{app}"; Excludes: "data\shillong_*.json,data\*.backup,data\update_cache.json,data\cierres\*"; Flags: ignoreversion recursesubdirs createallsubdirs

; Archivos de configuración BASE - Solo si NO existen (no sobrescribe datos del cliente)
Source: "data\plan_contable_v3.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\bancos.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\reglas_conceptos.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\presupuesto_2025.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\kabbalah_72.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\manual_shillong.pdf"; DestDir: "{app}\data"; Flags: ignoreversion

; NUNCA incluir: shillong_*.json, *.backup, update_cache.json, cierres/*, archivos de test

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\shillong_logov3.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\shillong_logov3.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{app}\backups"; Permissions: users-modify
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: string; ValueName: "{app}\{#MyAppExeName}"; ValueData: "~ RUNASADMIN"; Flags: uninsdeletevalue

[Code]
function InitializeSetup(): Boolean;
var
  Respuesta: Integer;
begin
  MsgBox('SHALOM' + #13#10 + #13#10 +
         'Bienvenido al instalador de Shillong Contabilidad v3.7.8 PRO.' + #13#10 +
         'Que este software sea de gran bendición y utilidad.', mbInformation, MB_OK);

  Respuesta := MsgBox('AVISO IMPORTANTE' + #13#10 + #13#10 +
                      'Si está actualizando, asegúrese de tener copia de seguridad de sus datos.' + #13#10#13#10 +
                      '¿Desea continuar?', mbConfirmation, MB_YESNO);

  Result := (Respuesta = IDYES);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DataPath: string;
begin
  if CurStep = ssPostInstall then
  begin
    DataPath := ExpandConstant('{app}\data');
    if not DirExists(DataPath) then
      CreateDir(DataPath);

    if not FileExists(DataPath + '\bancos.json') then
    begin
      SaveStringToFile(DataPath + '\bancos.json',
        '{ "banks": ['#13#10 +
        '  { "id": 1, "nombre": "Federal Bank", "saldo": 0.0 },'#13#10 +
        '  { "id": 2, "nombre": "SBI", "saldo": 0.0 },'#13#10 +
        '  { "id": 3, "nombre": "Union Bank", "saldo": 0.0 },'#13#10 +
        '  { "id": 4, "nombre": "Otro", "saldo": 0.0 },'#13#10 +
        '  { "id": 5, "nombre": "Caja", "saldo": 0.0 }'#13#10 +
        '] }', False);
    end;
  end;
end;