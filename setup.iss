[Setup]
AppName=AI Image Classifier
AppVersion=1.0
DefaultDirName={pf}\AI Image Classifier
OutputBaseFilename=AIImageClassifier
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
OutputDir=output

[Files]
Source: "dist\AIImageClassifier\AIImageClassifier.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\AIImageClassifier\*"; DestDir: "{app}\AIImageClassifier"; Flags: ignoreversion recursesubdirs createallsubdirs


