; ================================================================
; SHILLONG CONTABILIDAD v3 — MINI UPDATER 3.7.8
; Actualiza RegistrarView.py de forma segura
; Compatible con:
;   - C:\Program Files\SHILLONGv3PRO\
;   - C:\SHILLONGV3\
; ---------------------------------------------------------------
; Autor: Tony Blanco + ChatGPT
; Fecha: 2025
; ================================================================

#define AppName "SHILLONG CONTABILIDAD v3 PRO"
#define AppVersion "3.7.8"
#define AppExe "SHILLONG_v3_PRO.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={auto}
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=SHILLONG_UPDATE_3_7_8
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "RegistrarView.py"; DestDir: "{code:GetInstallPath}\ui"; Flags: ignoreversion restartreplace;

[Code]

function GetInstallPath(Value: string): string;
begin
  if DirExists('C:\Program Files\SHILLONGv3PRO') then
    begin
      Result := 'C:\Program Files\SHILLONGv3PRO';
      exit;
    end;

  if DirExists('C:\SHILLONGV3') then
    begin
      Result := 'C:\SHILLONGV3';
      exit;
    end;

  MsgBox('No se encontró una instalación válida de SHILLONG v3 PRO.', mbCriticalError, MB_OK);
  Result := '';
end;

procedure BackupFile(FilePath: string);
var
  BackupDir: string;
begin
  BackupDir := ExpandConstant('{pf}\SHILLONG_BACKUPS\3.7.8');
  if not DirExists(BackupDir) then
    ForceDirectories(BackupDir);

  if FileExists(FilePath) then
    FileCopy(FilePath, BackupDir + '\' + ExtractFileName(FilePath), False);
end;

procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := 
    'Bienvenido al actualizador SHILLONG v3.7.8' + #13#10 +
    'Este asistente actualizará los módulos sin borrar datos.';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  exePath: string;
  installPath: string;
begin
  if CurStep = ssInstall then
    begin
      installPath := GetInstallPath('');

      if installPath = '' then
        Abort();

      exePath := installPath + '\' + '{#AppExe}';

      ; Cerrar automáticamente la app si está abierta
      ShellExec('', 'taskkill.exe', '/IM {#AppExe} /F', '', SW_HIDE, ewWaitUntilTerminated);

      ; Crear backup del archivo original
      BackupFile(installPath + '\ui\RegistrarView.py');

    end;
end;

[Run]
Filename: "{code:GetInstallPath}\{#AppExe}"; Description: "Iniciar SHILLONG"; Flags: postinstall nowait runasoriginaluser;
