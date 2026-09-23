$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $PSScriptRoot '..\controller\HdrDisplayTopology.cs')
[HdrDisplayTopology]::GetActiveDisplays() |
    Select-Object DeviceName, FriendlyName, TargetId, HdrSupported, HdrActive, ColorState, SdrWhiteLevel, Handle |
    Format-Table -AutoSize
