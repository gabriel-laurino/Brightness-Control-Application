$ErrorActionPreference = 'Stop'
$base = Split-Path -Parent $MyInvocation.MyCommand.Definition
$python = Join-Path $base '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw "Brightness Control Application v2.0.1 runtime not found: $python"
}
Start-Process -FilePath $python -ArgumentList @('-m', 'app.main') -WorkingDirectory $base -WindowStyle Hidden
