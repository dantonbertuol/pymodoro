$user = $env:USERNAME
$PATH_UTILS = "C:\Users\$user\AppData\Local\Pymodoro\pymodoro_utils"
$PATH_BIN = "C:\Users\$user\AppData\Local\Pymodoro"
$PATH_DESKTOP = "C:\Users\$user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
$PATH_ICON = "C:\Users\$user\AppData\Local\Pymodoro\pymodoro_utils"

New-Item -ItemType Directory -Force -Path $PATH_UTILS
New-Item -ItemType Directory -Force -Path $PATH_BIN
New-Item -ItemType Directory -Force -Path $PATH_DESKTOP
New-Item -ItemType Directory -Force -Path $PATH_ICON

Copy-Item -Path "../utils/pymodoro_darkmode.qss" -Destination $PATH_UTILS
Copy-Item -Path "../utils/pymodoro_icon.ico" -Destination $PATH_UTILS
Copy-Item -Path "../utils/notification.wav" -Destination $PATH_UTILS
Copy-Item -Path "bin/pymodoro.exe" -Destination $PATH_BIN
Copy-Item -Path "../utils/pymodoro_icon.ico" -Destination $PATH_ICON

# Create a shortcut on the desktop
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("$PATH_DESKTOP\Pymodoro.lnk")
$Shortcut.TargetPath = "$PATH_BIN\pymodoro.exe"
$Shortcut.IconLocation = "$PATH_ICON\pymodoro_icon.ico"
$Shortcut.Save()