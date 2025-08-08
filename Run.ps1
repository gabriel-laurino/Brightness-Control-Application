$base = Split-Path -Parent $MyInvocation.MyCommand.Definition
Start-Process -FilePath "$base\python\pythonw.exe" -ArgumentList "`"$base\main\main.py`"" -WindowStyle Hidden
