Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class ScreenBrightnessSetter
{
    [DllImport("user32.dll")]
    public static extern IntPtr MonitorFromWindow(IntPtr hwnd, uint dwFlags);
    [DllImport("kernel32", CharSet = CharSet.Unicode)]
    public static extern IntPtr LoadLibrary(string lpFileName);
    [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true)]
    public static extern IntPtr GetProcAddress(IntPtr hModule, int address);

    public delegate void DwmpSDRToHDRBoostPtr(IntPtr monitor, double brightness);
}
"@

function Load-LanguageStrings {
    param ($language)

    $languageFile = Join-Path -Path $PSScriptRoot -ChildPath "..\data\lang.json"
    if (Test-Path $languageFile) {
        $langData = Get-Content -Raw -Path $languageFile | ConvertFrom-Json

        if ($langData.$language) {
            return $langData.$language
        }
        else {
            throw "Language '$language' not supported."
        }
    }
    else {
        throw "Language file 'lang.json' not found at path $languageFile."
    }
}

function Load-Config {
    $configPath = Join-Path -Path $PSScriptRoot -ChildPath "..\data\config.json"

    if (Test-Path $configPath) {
        $configContent = Get-Content -Raw -Path $configPath | ConvertFrom-Json
        return $configContent
    }
    else {
        throw "Configuration file 'config.json' not found at path $configPath."
    }
}

function Set-Brightness {
    param ([int]$brightness)

    $mappedBrightness = [math]::Round(1.0 + ($brightness * 5.0 / 100), 1)
    
    $primaryMonitor = [ScreenBrightnessSetter]::MonitorFromWindow([IntPtr]::Zero, 1)
    $hmodule_dwmapi = [ScreenBrightnessSetter]::LoadLibrary("dwmapi.dll")
    $procAddress = [ScreenBrightnessSetter]::GetProcAddress($hmodule_dwmapi, 171)

    $changeBrightness = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer(
        $procAddress,
        [ScreenBrightnessSetter+DwmpSDRToHDRBoostPtr]
    )
    $changeBrightness.Invoke($primaryMonitor, $mappedBrightness)

    $message = "$($script:strings.MSG_01): $brightness ($($script:strings.MSG_02) $mappedBrightness)"
    Write-Output $message
}

function Adjust-BrightnessBasedOnTime {
    $config = Load-Config
    $currentHour = (Get-Date).Hour

    $schedule = $config.Schedule

    $morningStart = [int]$schedule.MorningStart
    $morningEnd = [int]$schedule.MorningEnd
    $afternoonStart = [int]$schedule.AfternoonStart
    $afternoonEnd = [int]$schedule.AfternoonEnd
    $eveningStart = [int]$schedule.EveningStart
    $eveningEnd = [int]$schedule.EveningEnd
    $nightStart = [int]$schedule.NightStart
    $nightEnd = [int]$schedule.NightEnd

    if ($currentHour -ge $morningStart -and $currentHour -lt $morningEnd) {
        Set-Brightness -brightness $config.BrightnessLevels.B1
    }
    elseif ($currentHour -ge $afternoonStart -and $currentHour -lt $afternoonEnd) {
        Set-Brightness -brightness $config.BrightnessLevels.B2
    }
    elseif ($currentHour -ge $eveningStart -and $currentHour -lt $eveningEnd) {
        Set-Brightness -brightness $config.BrightnessLevels.B3
    }
    elseif (
        ($currentHour -ge $nightStart -and $currentHour -lt 24) -or
        ($currentHour -ge 0 -and $currentHour -lt $nightEnd)
    ) {
        Set-Brightness -brightness $config.BrightnessLevels.B4
    }
    else {
        Write-Output "Horário atual ($currentHour h) não está definido em nenhum período de brilho."
    }
}

$config = Load-Config
$script:strings = Load-LanguageStrings $config.Language

Write-Host "Configuração carregada: $config"
Write-Host "Strings carregadas: $script:strings"

Write-Host "Brightness Levels carregados: $($config.BrightnessLevels)"
Write-Host "B1: $($config.BrightnessLevels.B1)"
Write-Host "B2: $($config.BrightnessLevels.B2)"
Write-Host "B3: $($config.BrightnessLevels.B3)"
Write-Host "B4: $($config.BrightnessLevels.B4)"

while ($true) {
    Adjust-BrightnessBasedOnTime
    Start-Sleep -Seconds 1
}