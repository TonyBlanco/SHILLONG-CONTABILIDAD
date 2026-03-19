; ================================================================
; SHILLONG CONTABILIDAD v3 PRO — PARCHE DE DATOS 3.8.2
; ----------------------------------------------------------------
; Entrega SOLO los archivos de datos actualizados:
;   - shillong_2026.json  (con campo cuenta_banco migrado)
;   - saldos_mensuales.json (saldos iniciales 2026 cargados)
;
; SEGURIDAD: hace copia de seguridad de los archivos existentes
;            antes de sobreescribirlos.
;
; Busca la instalación en el registro (clave guardada por el
; instalador principal). Si no la encuentra, deja elegir la ruta.
; ================================================================

#define PatchName "SHILLONG CONTABILIDAD v3 PRO — Parche de Datos"
#define PatchVersion "3.8.2"
#define AppId "{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}"

[Setup]
AppName={#PatchName}
AppVersion={#PatchVersion}
; No registra en agregar/quitar programas (es solo un parche)
CreateUninstallRegKey=no
DefaultDirName={code:GetAppInstallPath|{localappdata}\SHILLONG CONTABILIDAD v3 PRO}
DisableDirPage=no
DisableProgramGroupPage=yes
OutputDir=..\Output
OutputBaseFilename=SHILLONG_PATCH_DATOS_3.8.2
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Los dos archivos de datos actualizados — sobreescriben los existentes
; (el [Code] hace backup antes de que Inno los instale)
Source: "..\data\shillong_2026.json"; DestDir: "{app}\data"; Flags: ignoreversion
Source: "..\data\saldos_mensuales.json"; DestDir: "{app}\data"; Flags: ignoreversion

[Code]

{ ── Leer la ruta de instalación desde el registro ── }
function GetAppInstallPath(Default: string): string;
var
  Path: string;
  RegKey: string;
begin
  RegKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppId}_is1';
  if RegQueryStringValue(HKEY_CURRENT_USER, RegKey, 'InstallLocation', Path) then
  begin
    { Quitar barra final si la tiene }
    if (Length(Path) > 0) and (Path[Length(Path)] = '\') then
      Path := Copy(Path, 1, Length(Path) - 1);
    Result := Path;
  end else
    Result := Default;
end;

{ ── Backup antes de instalar ── }
procedure BackupDataFile(DataDir, FileName: string);
var
  Src, Dst: string;
  Timestamp: string;
begin
  Src := DataDir + '\' + FileName;
  if FileExists(Src) then
  begin
    Timestamp := GetDateTimeString('yyyymmdd_hhnnss', #0, #0);
    Dst := DataDir + '\' + FileName + '.bak_' + Timestamp;
    if FileCopy(Src, Dst, False) then
      Log('Backup creado: ' + Dst)
    else
      Log('ADVERTENCIA: No se pudo crear backup de ' + Src);
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox(
    'PARCHE DE DATOS SHILLONG 3.8.2' + #13#10 + #13#10 +
    'Este parche actualiza únicamente:' + #13#10 +
    '  • shillong_2026.json  (campo cuenta_banco añadido)' + #13#10 +
    '  • saldos_mensuales.json  (saldos iniciales enero 2026)' + #13#10 + #13#10 +
    'Se creará una copia de seguridad automática de los archivos' + #13#10 +
    'existentes antes de sobreescribirlos.' + #13#10 + #13#10 +
    'IMPORTANTE: Asegúrese de que la app esté cerrada.',
    mbInformation, MB_OK
  );
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DataDir: string;
begin
  if CurStep = ssInstall then
  begin
    DataDir := ExpandConstant('{app}\data');
    BackupDataFile(DataDir, 'shillong_2026.json');
    BackupDataFile(DataDir, 'saldos_mensuales.json');
  end;
end;

procedure CurStepChangedPost(CurStep: TSetupStep);
begin
  if CurStep = ssDone then
  begin
    MsgBox(
      '¡Parche aplicado correctamente!' + #13#10 + #13#10 +
      'Los archivos de datos han sido actualizados.' + #13#10 +
      'Las copias de seguridad están en la carpeta data\ ' +
      'con extensión .bak_FECHA.',
      mbInformation, MB_OK
    );
  end;
end;
