[Setup]
AppName=CORE_SYNC
AppVersion=1.0
DefaultDirName={pf}\CORE_SYNC
DefaultGroupName=CORE_SYNC
OutputDir=output
OutputBaseFilename=CORE_SYNC_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "{#SourcePath}\dist\CORE_SYNC.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CORE_SYNC"; Filename: "{app}\CORE_SYNC.exe"
Name: "{commondesktop}\CORE_SYNC"; Filename: "{app}\CORE_SYNC.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Accesos directos:"
