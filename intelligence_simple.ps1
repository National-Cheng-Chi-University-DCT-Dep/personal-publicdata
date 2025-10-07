#!/usr/bin/env powershell
<#
.SYNOPSIS
Simplified University Application Intelligence System
.DESCRIPTION
A simplified version of the intelligence system without complex syntax
#>

param(
    [Parameter(Position=0)]
    [string]$Action = "help"
)

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

function Show-Help {
    Write-Host ""
    Write-Host "University Application Intelligence System v2.0" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Gray
    Write-Host ""
    Write-Host "USAGE: .\intelligence_simple.ps1 action" -ForegroundColor White
    Write-Host ""
    Write-Host "ACTIONS:" -ForegroundColor White
    Write-Host "  help          Show this help message" -ForegroundColor Gray
    Write-Host "  status        Show system status" -ForegroundColor Gray
    Write-Host "  validate      Run validation only" -ForegroundColor Gray
    Write-Host "  quick         Run quick update pipeline" -ForegroundColor Gray
    Write-Host "  full          Run complete pipeline" -ForegroundColor Gray
    Write-Host "  docs          Generate documents only" -ForegroundColor Gray
    Write-Host "  dashboard     Generate dashboard only" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Advanced Features:" -ForegroundColor White
    Write-Host "  advanced-quick    Run advanced analysis suite" -ForegroundColor Gray
    Write-Host "  gamification     Run gamification system" -ForegroundColor Gray
    Write-Host "  narrative        Run narrative analysis" -ForegroundColor Gray
    Write-Host "  portfolio        Run portfolio analysis" -ForegroundColor Gray
    Write-Host "  whatif           Run what-if simulator" -ForegroundColor Gray
    Write-Host ""
}

function Show-Status {
    Write-Host "System Status:" -ForegroundColor Cyan
    Write-Host ""
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "Python: Not available" -ForegroundColor Red
        }
    } catch {
        Write-Host "Python: Not available" -ForegroundColor Red
    }
    
    # Check directories
    if (Test-Path "final_applications") {
        $files = Get-ChildItem "final_applications" -Recurse -Filter "*.md" | Measure-Object
        Write-Host "Generated files: $($files.Count)" -ForegroundColor Green
    } else {
        Write-Host "Generated files: 0 (directory not found)" -ForegroundColor Yellow
    }
    
    # Check validation results
    if (Test-Path "final_applications/validation_results.json") {
        Write-Host "Validation results: Available" -ForegroundColor Green
    } else {
        Write-Host "Validation results: Not available" -ForegroundColor Yellow
    }
}

function Run-PythonScript {
    param([string]$Script, [string]$Arguments = "")
    
    $env:PYTHONPATH = "$(Get-Location)"
    
    if ($Arguments) {
        python $Script $Arguments
    } else {
        python $Script
    }
    
    return $LASTEXITCODE
}

# Main execution
switch ($Action) {
    "help" {
        Show-Help
    }
    "status" {
        Show-Status
    }
    "validate" {
        Write-Host "Running validation..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/master_controller.py" "--validate-only"
        if ($exitCode -eq 0) {
            Write-Host "Validation completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "Validation failed!" -ForegroundColor Red
        }
    }
    "quick" {
        Write-Host "Running quick update..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/master_controller.py" "--quick"
        if ($exitCode -eq 0) {
            Write-Host "Quick update completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "Quick update failed!" -ForegroundColor Red
        }
    }
    "full" {
        Write-Host "Running full pipeline..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/master_controller.py" "--full"
        if ($exitCode -eq 0) {
            Write-Host "Full pipeline completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "Full pipeline failed!" -ForegroundColor Red
        }
    }
    "docs" {
        Write-Host "Generating documents..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/master_controller.py" "--docs-only"
        if ($exitCode -eq 0) {
            Write-Host "Document generation completed!" -ForegroundColor Green
        } else {
            Write-Host "Document generation failed!" -ForegroundColor Red
        }
    }
    "dashboard" {
        Write-Host "Generating dashboard..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/master_controller.py" "--dashboard-only"
        if ($exitCode -eq 0) {
            Write-Host "Dashboard generation completed!" -ForegroundColor Green
        } else {
            Write-Host "Dashboard generation failed!" -ForegroundColor Red
        }
    }
    "advanced-quick" {
        Write-Host "Running advanced analysis..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/advanced_controller.py" "--advanced-quick"
        if ($exitCode -eq 0) {
            Write-Host "Advanced analysis completed!" -ForegroundColor Green
        } else {
            Write-Host "Advanced analysis failed!" -ForegroundColor Red
        }
    }
    "gamification" {
        Write-Host "Running gamification system..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/advanced_controller.py" "--gamification"
        if ($exitCode -eq 0) {
            Write-Host "Gamification system completed!" -ForegroundColor Green
        } else {
            Write-Host "Gamification system failed!" -ForegroundColor Red
        }
    }
    "narrative" {
        Write-Host "Running narrative analysis..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/advanced_controller.py" "--narrative"
        if ($exitCode -eq 0) {
            Write-Host "Narrative analysis completed!" -ForegroundColor Green
        } else {
            Write-Host "Narrative analysis failed!" -ForegroundColor Red
        }
    }
    "portfolio" {
        Write-Host "Running portfolio analysis..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/advanced_controller.py" "--portfolio"
        if ($exitCode -eq 0) {
            Write-Host "Portfolio analysis completed!" -ForegroundColor Green
        } else {
            Write-Host "Portfolio analysis failed!" -ForegroundColor Red
        }
    }
    "whatif" {
        Write-Host "Running what-if simulator..." -ForegroundColor Cyan
        $exitCode = Run-PythonScript "build_scripts/advanced_controller.py" "--whatif"
        if ($exitCode -eq 0) {
            Write-Host "What-if simulator completed!" -ForegroundColor Green
        } else {
            Write-Host "What-if simulator failed!" -ForegroundColor Red
        }
    }
    default {
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Write-Host "Use 'help' to see available actions" -ForegroundColor Yellow
        Show-Help
    }
}
