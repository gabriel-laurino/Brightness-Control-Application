param(
    [switch]$ListMonitors,
    [switch]$RunOnce,
    [switch]$Json,
    [string]$ConfigPath
)

$ErrorActionPreference = 'Stop'

# Keep the known-good 0..100 -> 1.0..6.0 mapping and DWM ordinal 171. The
# topology class only selects HDR-active HMONITORs; it never changes a display.
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class ScreenBrightnessSetter
{
    [DllImport("kernel32", CharSet = CharSet.Unicode)]
    public static extern IntPtr LoadLibrary(string lpFileName);
    [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true)]
    public static extern IntPtr GetProcAddress(IntPtr hModule, int address);
    public delegate int DwmpSDRToHDRBoostPtr(IntPtr monitor, double brightness);
}
"@
Add-Type -Path (Join-Path $PSScriptRoot 'HdrDisplayTopology.cs')

if ($ListMonitors) {
    $monitors = @([HdrDisplayTopology]::GetActiveDisplays())
    if ($Json) {
        $monitors |
            Select-Object DeviceName, FriendlyName, TargetId, HdrSupported, HdrActive, ColorState |
            ConvertTo-Json -Compress
    } else {
        $monitors |
            Select-Object DeviceName, FriendlyName, TargetId, HdrSupported, HdrActive, ColorState, Handle |
            Format-Table -AutoSize
    }
    return
}

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $configPath = Join-Path $PSScriptRoot '..\data\config.json'
} else {
    $configPath = $ConfigPath
}
if (-not (Test-Path -LiteralPath $configPath)) {
    throw "Configuration file not found: $configPath"
}

$module = [ScreenBrightnessSetter]::LoadLibrary('dwmapi.dll')
if ($module -eq [IntPtr]::Zero) { throw 'Could not load dwmapi.dll.' }
$procAddress = [ScreenBrightnessSetter]::GetProcAddress($module, 171)
if ($procAddress -eq [IntPtr]::Zero) { throw 'DWM SDR boost ordinal 171 is unavailable.' }
$changeBrightness = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
    $procAddress, [ScreenBrightnessSetter+DwmpSDRToHDRBoostPtr]
)

function Get-ScheduledBrightness {
    param([object]$Config, [int]$Hour)

    $schedule = $Config.Schedule
    if ($Hour -ge [int]$schedule.MorningStart -and $Hour -lt [int]$schedule.MorningEnd) {
        return [int]$Config.BrightnessLevels.B1
    }
    if ($Hour -ge [int]$schedule.AfternoonStart -and $Hour -lt [int]$schedule.AfternoonEnd) {
        return [int]$Config.BrightnessLevels.B2
    }
    if ($Hour -ge [int]$schedule.EveningStart -and $Hour -lt [int]$schedule.EveningEnd) {
        return [int]$Config.BrightnessLevels.B3
    }
    if (($Hour -ge [int]$schedule.NightStart -and $Hour -lt 24) -or
        ($Hour -ge 0 -and $Hour -lt [int]$schedule.NightEnd)) {
        return [int]$Config.BrightnessLevels.B4
    }
    throw "No brightness period covers hour $Hour."
}

function Set-Brightness {
    param([int]$Brightness)
    if ($Brightness -lt 0 -or $Brightness -gt 100) {
        throw "Brightness $Brightness is outside 0..100."
    }

    $mappedBrightness = [math]::Round(1.0 + ($Brightness * 5.0 / 100), 1)
    $displays = [HdrDisplayTopology]::GetActiveDisplays()
    $targets = @($displays | Where-Object {
        $_.HdrSupported -and $_.HdrActive -and $_.Handle -ne [IntPtr]::Zero
    })
    if ($targets.Count -eq 0) {
        throw 'No active HDR monitor was verified; no brightness was changed.'
    }

    $seen = New-Object 'System.Collections.Generic.HashSet[IntPtr]'
    $adjusted = 0
    foreach ($target in $targets) {
        if (-not $seen.Add($target.Handle)) { continue }
        $result = $changeBrightness.Invoke($target.Handle, $mappedBrightness)
        if ($result -ne 0) {
            Write-Error "DWM rejected $($target.DeviceName) (HRESULT 0x$('{0:X8}' -f [uint32]$result))." -ErrorAction Continue
            continue
        }
        $adjusted++
    }
    if ($adjusted -eq 0) { throw 'DWM did not adjust any HDR monitor.' }
    Write-Output "Applied $Brightness ($mappedBrightness) to $adjusted active HDR monitor(s)."
}

function Invoke-ScheduledBrightness {
    $config = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
    $brightness = Get-ScheduledBrightness -Config $config -Hour (Get-Date).Hour
    Set-Brightness -Brightness $brightness
}

if ($RunOnce) {
    Invoke-ScheduledBrightness
    return
}

while ($true) {
    try { Invoke-ScheduledBrightness | Out-Null }
    catch { Write-Error $_ -ErrorAction Continue }
    Start-Sleep -Seconds 1
}
