; DonTouchMe 安装脚本 - Inno Setup 6.x
; 用于创建专业的 Windows 安装程序

#define MyAppName "DonTouchMe"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "WoodMe"
#define MyAppURL "https://github.com/woodmeone/DonTouchMe"
#define MyAppExeName "DonTouchMe.exe"

[Setup]
; 应用基本信息
AppId={{A8B9C1D2-E3F4-5678-9ABC-DEF012345678}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 默认安装路径
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; 输出设置
OutputDir=installer_output
OutputBaseFilename=DonTouchMe_Setup_v{#MyAppVersion}

; 安装程序图标（可选，如果有图标文件）
; SetupIconFile=icon.ico

; 压缩设置
Compression=lzma2/max
SolidCompression=yes

; Windows 版本要求
MinVersion=10.0
PrivilegesRequired=admin

; 界面设置
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no

; 许可证和说明文档（可选）
; LicenseFile=LICENSE.txt
; InfoBeforeFile=README.txt

[Languages]
; 使用英文（默认，所有版本都支持）
Name: "english"; MessagesFile: "compiler:Default.isl"

; 如果需要中文界面，取消下面一行的注释
; 注意：不同版本的 Inno Setup 中文语言文件名可能不同
; Inno Setup 6.x: ChineseSimplified.isl
; Inno Setup 5.x: ChineseSimp.isl
; Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: unchecked
Name: "startupicon"; Description: "开机自动启动"; GroupDescription: "其他选项:"; Flags: unchecked

[Files]
; 复制所有程序文件
Source: "dist\DonTouchMe\DonTouchMe.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\DonTouchMe\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; 复制默认配置文件（如果不存在）
Source: "data\config.json"; DestDir: "{app}\data"; Flags: onlyifdoesntexist uninsneveruninstall

; 复制文档
Source: "使用说明-可执行文件.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Dirs]
; 创建必要的目录
Name: "{app}\data"
Name: "{app}\data\captures"
Name: "{app}\data\captures\camera"
Name: "{app}\data\captures\screen"
Name: "{app}\logs"

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\配置文件"; Filename: "{app}\data\config.json"
Name: "{group}\查看日志"; Filename: "{app}\logs"
Name: "{group}\使用说明"; Filename: "{app}\使用说明-可执行文件.md"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"

; 桌面快捷方式（可选）
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; 开机自动启动（可选）
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
; 安装完成后的操作
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除的文件和文件夹
Type: filesandordirs; Name: "{app}\data\captures"
Type: filesandordirs; Name: "{app}\logs"
Type: files; Name: "{app}\data\history.db"

[Code]
// 安装前检查
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // 检查 Windows 版本
  if not IsWindows10OrLater then
  begin
    MsgBox('DonTouchMe 需要 Windows 10 或更高版本。', mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // 检查是否已经运行
  if CheckForMutexes('DonTouchMe_SingleInstance') then
  begin
    if MsgBox('DonTouchMe 正在运行。是否关闭后继续安装？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // 尝试关闭程序
      Exec('taskkill', '/F /IM DonTouchMe.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end
    else
    begin
      Result := False;
      Exit;
    end;
  end;
end;

// 安装后配置
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  Lines: TArrayOfString;
begin
  if CurStep = ssPostInstall then
  begin
    // 创建默认配置文件（如果不存在）
    ConfigFile := ExpandConstant('{app}\data\config.json');
    if not FileExists(ConfigFile) then
    begin
      // 配置文件已经通过 [Files] 部分复制
      MsgBox('首次安装完成！请在启动程序后配置 PushPlus Token。', mbInformation, MB_OK);
    end;
  end;
end;

// 卸载前确认
function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // 提示用户保存配置
  if MsgBox('卸载将删除程序文件，但会保留配置文件。' + #13#10 + #13#10 +
            '是否继续卸载？', mbConfirmation, MB_YESNO) = IDNO then
  begin
    Result := False;
    Exit;
  end;

  // 关闭正在运行的程序
  Exec('taskkill', '/F /IM DonTouchMe.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

// 卸载完成
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('是否删除所有配置文件和历史记录？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\data'), True, True, True);
      DelTree(ExpandConstant('{app}\logs'), True, True, True);
    end;
  end;
end;
