# Makefile.ps1 - PowerShell version of your Makefile

param(
    [string]$Target = "all"
)

function Fetch-Data {
    Write-Output "--- Fetching data ---"
    .\fetch_data.ps1
}

function Process-Data {
    Fetch-Data
    Write-Output "--- Processing data ---"
    .\process_data.ps1
    Write-Output "--- Pipeline complete ---"
}

function Clean {
    Write-Output "--- Cleaning up ---"
    Remove-Item -Path "breeds.json" -ErrorAction SilentlyContinue
}

switch ($Target) {
    "all"          { Process-Data }
    "fetch_data"   { Fetch-Data }
    "process_data" { Process-Data }
    "clean"        { Clean }
    default        { Write-Error "Unknown target: $Target" }
}
