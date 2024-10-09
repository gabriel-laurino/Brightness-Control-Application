Set objShell = CreateObject("WScript.Shell")

' Define the script folder (root folder of the project)
scriptDir = Replace(WScript.ScriptFullName, WScript.ScriptName, "")

' Path to the Python script (main/main.py)
pythonCommand = "python """ & scriptDir & "main\main.py"""
objShell.Run pythonCommand, 0, False
