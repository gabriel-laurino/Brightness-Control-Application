Set objShell = CreateObject("WScript.Shell")

' Definir a pasta do script (pasta raiz do projeto)
scriptDir = Replace(WScript.ScriptFullName, WScript.ScriptName, "")

' Caminho do script Python (main/main.py)
pythonCommand = "python """ & scriptDir & "main\main.py"""
objShell.Run pythonCommand, 0, False

' Caminho do script PowerShell para ajuste automático de brilho (control/adjust_brightness.ps1)
psCommand = "powershell -ExecutionPolicy Bypass -File """ & scriptDir & "control\adjust_brightness.ps1"""
objShell.Run psCommand, 0, False