#!/usr/bin/env powershell
<#
.SYNOPSIS
Safe validation summary script for PowerShell
Avoids indentation issues with inline Python commands

.DESCRIPTION
This script safely generates a validation summary by calling a dedicated Python script
instead of using inline Python commands that may have indentation issues.
#>

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Set Python path
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)\.."

Write-Host "📊 Generating validation summary..." -ForegroundColor Cyan

try {
    # Run the dedicated validation summary script
    python validation_summary.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Validation summary completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Validation summary failed with error code $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error running validation summary: $($_.Exception.Message)" -ForegroundColor Red
}

# Return to original directory
Set-Location $PSScriptRoot
