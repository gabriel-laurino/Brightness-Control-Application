Set objShell = CreateObject("WScript.Shell")

' Define o diretório do script (pasta raiz do projeto)
scriptDir = Replace(WScript.ScriptFullName, WScript.ScriptName, "")

' Caminho para o interpretador Python embutido
pythonExe = """" & scriptDir & "python\pythonw.exe" & """"

' Caminho para o script Python principal (main/main.py)
pythonScript = """" & scriptDir & "main\main.py" & """"

' Comando a ser executado
pythonCommand = pythonExe & " " & pythonScript

' Executa o comando de maneira completamente silenciosa (estilo da janela 0, sem abrir PowerShell)
objShell.Run pythonCommand, 0, False