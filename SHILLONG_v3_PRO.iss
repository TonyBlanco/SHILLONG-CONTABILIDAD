#define MyAppName "SHILLONG CONTABILIDAD v3 PRO"
#define MyAppVersion "3.8.4"
#define MyAppPublisher "Shillong Soft"
#define MyAppURL "https://github.com/TonyBlanco/SHILLONG-CONTABILIDAD"
#define MyAppExeName "SHILLONG_v3_PRO.exe"

[Setup]
AppId={{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DisableDirPage=no
AllowRootDirectory=yes
AllowNetworkDrive=yes
AllowUNCPath=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=Instalador_Shillong_v3.8.4_PRO
SetupIconFile=assets\shillong_logov3.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; ← LOGO (solo pequeño, sin ñ y en sección correcta)
WizardSmallImageFile=assets\shillong_logo_pequeno.bmp

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"

[Files]
; Archivos de la aplicación (EXE, DLLs, etc.) - Se actualizan siempre
Source: "dist\SHILLONG_v3_PRO\*"; DestDir: "{app}"; Excludes: "data\shillong_*.json,data\*.backup,data\update_cache.json,data\cierres\*"; Flags: ignoreversion recursesubdirs createallsubdirs

; Archivos de configuración BASE - Solo si NO existen (no sobrescribe datos del cliente)
Source: "data\plan_contable_v3.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\bancos.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\reglas_conceptos.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\presupuesto_2025.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\presupuesto_2026.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\kabbalah_72.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\saldos_mensuales.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "data\manual_shillong.pdf"; DestDir: "{app}\data"; Flags: ignoreversion

; NUNCA incluir: shillong_*.json, *.backup, update_cache.json, cierres/*, archivos de test

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\shillong_logov3.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\shillong_logov3.ico"; Tasks: desktopicon

[Run]
; Abrir la app al finalizar (opcional, el usuario puede desmarcar)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{app}\backups"
Name: "{app}\data"
Name: "{app}\logs"
Name: "{app}\reportes"

; [Registry]
; REMOVIDO: Ya no forzamos RUNASADMIN - la app no necesita privilegios de admin
; Root: HKCU; Subkey: "Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"; ValueType: string; ValueName: "{app}\{#MyAppExeName}"; ValueData: "~ RUNASADMIN"; Flags: uninsdeletevalue

[Code]
function InitializeSetup(): Boolean;
var
  Respuesta: Integer;
begin
  // En instalacion silenciosa no se muestran MsgBox (bloquearian /VERYSILENT);
  // el flujo interactivo conserva el saludo y la confirmacion.
  if WizardSilent then
  begin
    Result := True;
    Exit;
  end;

  MsgBox('SHALOM' + #13#10 + #13#10 +
         'Bienvenido al instalador de Shillong Contabilidad v{#MyAppVersion} PRO.' + #13#10 +
         'Que este software sea de gran bendición y utilidad.', mbInformation, MB_OK);

  Respuesta := MsgBox('AVISO IMPORTANTE' + #13#10 + #13#10 +
                      'Si está actualizando, asegúrese de tener copia de seguridad de sus datos.' + #13#10#13#10 +
                      '¿Desea continuar?', mbConfirmation, MB_YESNO);

  Result := (Respuesta = IDYES);
end;

// On uninstall: backup important user JSONs and inform the user where they were saved.
procedure DeinitializeUninstall();
var
  DataPath: string;
  BackupRoot: string;
  BackFile: string;
begin
  DataPath := ExpandConstant('{app}\data');
  BackupRoot := ExpandConstant('{userdocs}\Shillong_Contabilidad_backups');
  if not DirExists(BackupRoot) then
    CreateDir(BackupRoot);

  // Backup commonly-used JSONs if they exist
  if FileExists(DataPath + '\shillong_2026.json') then
  begin
    BackFile := BackupRoot + '\shillong_2026.json.' + GetDateTimeString('yyyymmdd_hhnnss', #0, #0) + '.bak';
    if not CopyFile(DataPath + '\shillong_2026.json', BackFile, False) then
      // best-effort: ignore copy failures
    ;
  end;

  if FileExists(DataPath + '\bancos.json') then
  begin
    BackFile := BackupRoot + '\bancos.json.' + GetDateTimeString('yyyymmdd_hhnnss', #0, #0) + '.bak';
    if not CopyFile(DataPath + '\bancos.json', BackFile, False) then
    ;
  end;

  if FileExists(DataPath + '\shillong_2026.json.backup') then
  begin
    BackFile := BackupRoot + '\shillong_2026.json.backup.' + GetDateTimeString('yyyymmdd_hhnnss', #0, #0) + '.bak';
    if not CopyFile(DataPath + '\shillong_2026.json.backup', BackFile, False) then
    ;
  end;

  // Inform the user where backups were stored (solo en desinstalación interactiva;
  // en silenciosa un MsgBox bloquearía /VERYSILENT)
  if not WizardSilent then
    MsgBox('Se han guardado copias de seguridad de sus archivos de datos (JSON) en:'#13#10 + BackupRoot + #13#10#13#10 +
           'IMPORTANTE: Los datos del usuario no serán borrados automáticamente. Revise ' + BackupRoot + ' si necesita recuperar archivos.', mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DataPath: string;
  BackupPath: string;
begin
  if CurStep = ssPostInstall then
  begin
    DataPath := ExpandConstant('{app}\data');
    BackupPath := ExpandConstant('{app}\backups');
    
    if not DirExists(DataPath) then
      CreateDir(DataPath);
    if not DirExists(BackupPath) then
      CreateDir(BackupPath);

    // Backup existing user JSONs using FileCopy
    if FileExists(DataPath + '\shillong_2026.json') then
      FileCopy(DataPath + '\shillong_2026.json', BackupPath + '\shillong_2026.json.bak', False);

    if FileExists(DataPath + '\bancos.json') then
      FileCopy(DataPath + '\bancos.json', BackupPath + '\bancos.json.bak', False)
    else
    begin
      if not DirExists(ExpandConstant('{app}\backups')) then
        CreateDir(ExpandConstant('{app}\backups'));

      // List of common user JSON files to protect
      if FileExists(DataPath + '\shillong_2026.json') then
      begin
        // Copia byte a byte (evita problemas de codificacion UTF-8 en los JSON)
        CopyFile(DataPath + '\shillong_2026.json', ExpandConstant('{app}\backups\shillong_2026.json.' + GetDateTimeString('yyyymmdd_hhnnss', #0, #0) + '.bak'), False);
      end;

      if FileExists(DataPath + '\bancos.json') then
      begin
        // if user already has bancos.json, keep a backup copy and do not overwrite
        CopyFile(DataPath + '\bancos.json', ExpandConstant('{app}\backups\bancos.json.' + GetDateTimeString('yyyymmdd_hhnnss', #0, #0) + '.bak'), False);
      end else
      begin
        // Install a default bancos.json only if none exists
        SaveStringToFile(DataPath + '\bancos.json',
          '{ "banks": ['#13#10 +
          '  { "id": 1, "nombre": "Federal Bank", "saldo": 0.0 },'#13#10 +
          '  { "id": 2, "nombre": "SBI", "saldo": 0.0 },'#13#10 +
          '  { "id": 3, "nombre": "Union Bank", "saldo": 0.0 },'#13#10 +
          '  { "id": 4, "nombre": "Otro", "saldo": 0.0 },'#13#10 +
          '  { "id": 5, "nombre": "Caja", "saldo": 0.0 },'#13#10 +
          '  { "id": 6, "nombre": "Cambio Euros", "saldo": 0.0 },'#13#10 +
          '  { "id": 7, "nombre": "Contrapartida", "saldo": 0.0 }'#13#10 +
          '] }', False);
      end;

    end;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\assets\shillong_logov3.ico"
Type: files; Name: "{app}\assets\shillong_logo_pequeno.bmp"
