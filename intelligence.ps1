#!/usr/bin/env powershell
<#
.SYNOPSIS
University Application Intelligence System v2.1 - Advanced Master Control Script

.DESCRIPTION
Complete automation pipeline with cutting-edge AI features for intelligent university application management

.PARAMETER Action
The intelligence operation to perform

.PARAMETER Schools
Specific schools to target (space-separated school IDs)

.PARAMETER Verbose
Enable verbose output

.PARAMETER SaveReport
Save detailed execution report

.EXAMPLE
.\intelligence.ps1 full
.\intelligence.ps1 quick
.\intelligence.ps1 scrape
.\intelligence.ps1 validate
.\intelligence.ps1 docs -Schools "taltech aalto"
.\intelligence.ps1 dashboard
.\intelligence.ps1 academic
.\intelligence.ps1 alerts

.NOTES
Author: Pei-Chen Lee
Version: 2.0.0
Requires: Python 3.7+, pip, git
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("full", "quick", "scrape", "validate", "docs", "dashboard", "academic", "alerts", "status", "help", 
                 "advanced-full", "advanced-quick", "gamification", "narrative", "portfolio", "whatif", "analysis")]
    [string]$Action = "help",
    
    [Parameter()]
    [string[]]$Schools = @(),
    
    [Parameter()]
    [switch]$Verbose,
    
    [Parameter()]
    [switch]$SaveReport,
    
    [Parameter()]
    [switch]$SkipScraping
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Colors and formatting
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Highlight = "Magenta"
}

function Write-StatusMessage {
    param(
        [string]$Message,
        [string]$Type = "Info",
        [string]$Icon = ""
    )
    
    $color = $Colors[$Type]
    if ($Icon) {
        Write-Host "$Icon " -NoNewline -ForegroundColor $color
    }
    Write-Host $Message -ForegroundColor $color
}

function Show-Header {
    Write-Host "`n🎓 " -NoNewline -ForegroundColor Magenta
    Write-Host "University Application Intelligence System v2.0" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Gray
    Write-Host "Complete automation for intelligent application management" -ForegroundColor Gray
    Write-Host ""
}

function Test-Dependencies {
    Write-StatusMessage "🔧 Checking system dependencies..." "Info"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-StatusMessage "✅ Python: $pythonVersion" "Success"
        } else {
            throw "Python not found"
        }
    } catch {
        Write-StatusMessage "❌ Python is not installed or not in PATH" "Error"
        Write-StatusMessage "💡 Please install Python 3.7+ from https://python.org" "Warning"
        return $false
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-StatusMessage "✅ Pip: Available" "Success"
        }
    } catch {
        Write-StatusMessage "❌ Pip not available" "Error"
        return $false
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-StatusMessage "✅ Git: Available" "Success"
        }
    } catch {
        Write-StatusMessage "⚠️ Git not available (optional)" "Warning"
    }
    
    # Check core Python packages
    Write-StatusMessage "📦 Checking Python packages..." "Info"
    
    $requiredPackages = @("PyYAML", "requests", "beautifulsoup4")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            python -c "import $($package.ToLower())" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-StatusMessage "  ✅ $package" "Success"
            } else {
                $missingPackages += $package
                Write-StatusMessage "  ❌ $package (missing)" "Warning"
            }
        } catch {
            $missingPackages += $package
            Write-StatusMessage "  ❌ $package (missing)" "Warning"
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-StatusMessage "📦 Installing missing packages..." "Info"
        pip install ($missingPackages -join " ")
        
        if ($LASTEXITCODE -ne 0) {
            Write-StatusMessage "❌ Failed to install packages" "Error"
            return $false
        }
    }
    
    return $true
}

function Show-SystemStatus {
    Write-StatusMessage "📊 System Status Overview" "Highlight"
    Write-Host ""
    
    # Check if output directory exists and show file counts
    if (Test-Path "final_applications") {
        $cvFiles = @(Get-ChildItem "final_applications" -Recurse -Filter "CV_*.md").Count
        $sopFiles = @(Get-ChildItem "final_applications" -Recurse -Filter "SOP_*.md").Count
        $reportFiles = @(Get-ChildItem "final_applications" -Filter "*report*.md").Count
        
        Write-StatusMessage "📁 Generated Documents:" "Info"
        Write-Host "   CV Documents: $cvFiles" -ForegroundColor Gray
        Write-Host "   SOP Documents: $sopFiles" -ForegroundColor Gray
        Write-Host "   Reports: $reportFiles" -ForegroundColor Gray
        
        # Check for recent activity
        $recentFiles = Get-ChildItem "final_applications" -Recurse -Filter "*.md" | Where-Object { 
            $_.LastWriteTime -gt (Get-Date).AddDays(-1) 
        }
        
        if ($recentFiles.Count -gt 0) {
            Write-StatusMessage "   🕐 Files updated in last 24h: $($recentFiles.Count)" "Success"
        } else {
            Write-StatusMessage "   ⏰ No recent updates" "Warning"
        }
    } else {
        Write-StatusMessage "📁 No generated documents found" "Warning"
        Write-StatusMessage "   Run 'intelligence.ps1 docs' to generate documents" "Info"
    }
    
    # Check configuration files
    Write-StatusMessage "`n📋 Configuration Status:" "Info"
    
    if (Test-Path "source_data/schools.yml") {
        try {
            python -c "import yaml; data = yaml.safe_load(open('source_data/schools.yml')); print('Schools configured: ' + str(len(data['schools'])))" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-StatusMessage "   ✅ Schools configuration: Valid" "Success"
            }
        } catch {
            Write-StatusMessage "   ❌ Schools configuration: Invalid" "Error"
        }
    } else {
        Write-StatusMessage "   ❌ Schools configuration: Missing" "Error"
    }
    
    if (Test-Path "source_data/schools_live_data.yml") {
        $liveDataAge = (Get-Date) - (Get-Item "source_data/schools_live_data.yml").LastWriteTime
        if ($liveDataAge.TotalHours -lt 24) {
            Write-StatusMessage "   ✅ Live data: Fresh (updated $([math]::Round($liveDataAge.TotalHours, 1))h ago)" "Success"
        } else {
            Write-StatusMessage "   ⚠️ Live data: Stale (updated $([math]::Round($liveDataAge.TotalDays, 1)) days ago)" "Warning"
        }
    } else {
        Write-StatusMessage "   ❌ Live data: Not available" "Warning"
        Write-StatusMessage "      Run 'intelligence.ps1 scrape' to collect data" "Info"
    }
    
    # Show environment info
    Write-StatusMessage "`n🔧 Environment:" "Info"
    Write-Host "   Working Directory: $(Get-Location)" -ForegroundColor Gray
    Write-Host "   PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
    Write-Host "   System: $env:OS" -ForegroundColor Gray
}

function Show-Help {
    Write-Host @"

🎓 University Application Intelligence System v2.0
═══════════════════════════════════════════════════

USAGE:
  .\intelligence.ps1 action [options]

ACTIONS:
  Basic Intelligence:
  full          Run complete intelligence pipeline (data collection + analysis + documents)
  quick         Run quick update pipeline (skip data collection, faster execution)
  scrape        Run data collection only (web scraping)
  validate      Run validation only (check eligibility and requirements)
  docs          Generate application documents only
  dashboard     Generate monitoring dashboard only
  academic      Run academic intelligence gathering only
  alerts        Process notifications and alerts only

  Advanced Intelligence (NEW!):
  advanced-full   🚀 Complete advanced pipeline (all cutting-edge features)
  advanced-quick  ⚡ Advanced analysis without data collection (recommended)
  gamification    [Gamification system (achievements, progress, motivation)]
  narrative       📖 Narrative consistency analysis (LLM-powered)
  portfolio       📊 Risk portfolio balancing (financial optimization)
  whatif          🔮 Interactive What-If scenario simulator
  analysis        🔬 Advanced analysis suite (narrative + portfolio + whatif)

  System:
  status        Show system status and configuration
  help          Show this help message

OPTIONS:
  -Schools    Target specific schools (e.g., -Schools taltech aalto)
  -Verbose    Enable verbose output and detailed logging
  -SaveReport Save detailed execution report to file
  -SkipScraping  Skip web scraping in full pipeline (use cached data)

EXAMPLES:
  Basic Usage:
  .\intelligence.ps1 full                         # Complete intelligence pipeline
  .\intelligence.ps1 quick                        # Quick update with existing data
  .\intelligence.ps1 docs -Schools "taltech"      # Generate docs for TalTech only
  .\intelligence.ps1 status                       # Check system status

  Advanced Intelligence (RECOMMENDED):
  .\intelligence.ps1 advanced-quick               # 🚀 All advanced features (fast)
  .\intelligence.ps1 advanced-full -SaveReport    # 🌟 Complete advanced pipeline + report
  .\intelligence.ps1 gamification                 # 🎮 Check achievements and progress
  .\intelligence.ps1 narrative                    # 📖 Analyze story consistency
  .\intelligence.ps1 portfolio                    # 📊 Optimize school portfolio
  .\intelligence.ps1 whatif                       # 🔮 Interactive scenario testing
  .\intelligence.ps1 analysis                     # 🔬 Advanced analysis suite

INTELLIGENCE FEATURES:
  Core Intelligence:
  🔍 Automated university data collection and validation
  📊 Real-time application status monitoring and dashboards
  🔔 Smart alerts and GitHub issue creation for deadlines
  🔬 Academic intelligence: professor research and GitHub monitoring
  📝 Dynamic document generation with school-specific content

  Advanced Intelligence (NEW!):
  🎮 Gamification system with 25+ achievements and progress tracking
  📖 AI-powered narrative consistency analysis across documents
  📊 Financial portfolio theory applied to school selection optimization
  🔮 Interactive What-If scenario simulator for strategic decisions
  🎯 Predictive modeling for admission probability and ROI analysis
  💡 Automated strategic recommendations and effort optimization

PIPELINE STAGES:
  1. Data Collection    - Web scraping university requirements
  2. Data Validation    - Eligibility checking and risk assessment  
  3. Academic Intelligence - Professor research and GitHub monitoring
  4. Document Generation - Customized CV and SOP creation
  5. Monitoring Dashboard - Real-time status and metrics
  6. Notifications      - Alerts and task management via GitHub

SYSTEM REQUIREMENTS:
  - Python 3.7 or higher
  - Internet connection for data collection
  - GitHub token (optional, for issue creation)
  - 500MB+ free disk space

For more information, visit: https://github.com/dennislee928/personal-publicdata

"@ -ForegroundColor Gray
}

# Advanced intelligence execution logic
function Invoke-AdvancedIntelligenceAction {
    param([string]$ActionType)
    
    # Build command arguments for advanced controller
    $pythonScript = "build_scripts/advanced_controller.py"
    $arguments = @()
    
    switch ($ActionType) {
        "advanced-full" {
            $arguments += "--advanced-full"
            Write-StatusMessage "🚀 Running complete advanced intelligence pipeline..." "Highlight"
        }
        "advanced-quick" {
            $arguments += "--advanced-quick"
            Write-StatusMessage "⚡ Running advanced analysis suite..." "Highlight"
        }
        "gamification" {
            $arguments += "--gamification"
            Write-StatusMessage "🎮 Updating gamification system..." "Highlight"
        }
        "narrative" {
            $arguments += "--narrative" 
            Write-StatusMessage "📖 Analyzing narrative consistency..." "Highlight"
        }
        "portfolio" {
            $arguments += "--portfolio"
            Write-StatusMessage "📊 Running risk portfolio analysis..." "Highlight"
        }
        "whatif" {
            $arguments += "--whatif"
            Write-StatusMessage "🔮 Launching What-If simulator..." "Highlight"
        }
        "analysis" {
            $arguments += "--analysis-only"
            Write-StatusMessage "🔬 Running advanced analysis suite..." "Highlight"
        }
    }
    
    if ($Verbose) { $arguments += "--verbose" }
    if ($SaveReport) { $arguments += "--save-report" }
    
    # Execute the advanced intelligence system
    Write-Host ""
    
    if ($Verbose) {
        Write-StatusMessage "Command: python $pythonScript $($arguments -join ' ')" "Info"
        Write-Host ""
    }
    
    $env:PYTHONPATH = "$(Get-Location)"
    python $pythonScript @arguments
    
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-StatusMessage "✅ Advanced intelligence completed successfully!" "Success"
        
        # Show specific results based on action
        switch ($ActionType) {
            "gamification" {
                Write-StatusMessage "🎮 Check final_applications/gamification_dashboard.md for your progress!" "Success"
            }
            "narrative" {
                Write-StatusMessage "📖 Check final_applications/narrative_consistency_report.md for analysis!" "Success"
            }
            "portfolio" {
                Write-StatusMessage "📊 Check final_applications/risk_portfolio_analysis.md for recommendations!" "Success"
            }
            "whatif" {
                Write-StatusMessage "🔮 Interactive simulator completed!" "Success"
            }
            default {
                Write-StatusMessage "📁 Check final_applications/ for all generated reports!" "Success"
            }
        }
        
        # Advanced feature suggestions
        Write-StatusMessage "`n💡 Advanced features available:" "Info"
        switch ($ActionType) {
            "gamification" {
                Write-Host "   • Run 'intelligence.ps1 narrative' to check story consistency" -ForegroundColor Gray
                Write-Host "   • Run 'intelligence.ps1 portfolio' to optimize school selection" -ForegroundColor Gray
            }
            "narrative" {
                Write-Host "   • Run 'intelligence.ps1 gamification' to see your achievements" -ForegroundColor Gray
                Write-Host "   • Run 'intelligence.ps1 whatif' to test improvement scenarios" -ForegroundColor Gray
            }
            "portfolio" {
                Write-Host "   • Run 'intelligence.ps1 whatif' to simulate portfolio changes" -ForegroundColor Gray
                Write-Host "   • Run 'intelligence.ps1 gamification' to track optimization progress" -ForegroundColor Gray
            }
            default {
                Write-Host "   • All advanced analysis completed! Review reports for strategic insights" -ForegroundColor Gray
            }
        }
    } else {
        Write-StatusMessage "❌ Advanced intelligence failed with exit code: $exitCode" "Error"
        Write-StatusMessage "💡 Try running with -Verbose for detailed error information" "Warning"
        return $exitCode
    }
    
    return $exitCode
}

# Main execution logic  
function Invoke-IntelligenceAction {
    param([string]$ActionType)
    
    # Build command arguments
    $pythonScript = "build_scripts/master_controller.py"
    $arguments = @()
    
    switch ($ActionType) {
        "full" {
            $arguments += "--full"
            if ($SkipScraping) { $arguments += "--skip-scraping" }
        }
        "quick" { $arguments += "--quick" }
        "scrape" { $arguments += "--scrape-only" }
        "validate" { $arguments += "--validate-only" }
        "docs" { $arguments += "--docs-only" }
        "dashboard" { $arguments += "--dashboard-only" }
        "academic" { $arguments += "--academic-only" }
        "alerts" { $arguments += "--alerts-only" }
    }
    
    if ($Schools.Count -gt 0) {
        $arguments += "--schools"
        $arguments += $Schools
    }
    
    if ($Verbose) { $arguments += "--verbose" }
    if ($SaveReport) { $arguments += "--save-report" }
    
    # Execute the intelligence system
    Write-StatusMessage "🚀 Executing: $ActionType" "Highlight"
    Write-Host ""
    
    if ($Verbose) {
        Write-StatusMessage "Command: python $pythonScript $($arguments -join ' ')" "Info"
        Write-Host ""
    }
    
    $env:PYTHONPATH = "$(Get-Location)"
    python $pythonScript @arguments
    
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-StatusMessage "✅ Operation completed successfully!" "Success"
        
        # Show quick results summary
        if (Test-Path "final_applications") {
            $newFiles = Get-ChildItem "final_applications" -Recurse -Filter "*.md" | Where-Object { 
                $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) 
            }
            
            if ($newFiles.Count -gt 0) {
                Write-StatusMessage "📁 Generated $($newFiles.Count) new files in final_applications/" "Success"
            }
        }
        
        # Suggest next actions based on what was run
        Write-StatusMessage "`n💡 Suggested next steps:" "Info"
        switch ($ActionType) {
            "scrape" {
                Write-Host "   • Run 'intelligence.ps1 validate' to check updated requirements" -ForegroundColor Gray
                Write-Host "   • Run 'intelligence.ps1 docs' to regenerate documents with new data" -ForegroundColor Gray
            }
            "validate" {
                Write-Host "   • Check final_applications/validation_report.md for eligibility details" -ForegroundColor Gray
                Write-Host "   • Run 'intelligence.ps1 alerts' to process any warnings" -ForegroundColor Gray
            }
            "docs" {
                Write-Host "   • Review generated documents in final_applications/" -ForegroundColor Gray
                Write-Host "   • Run 'intelligence.ps1 dashboard' to update application status" -ForegroundColor Gray
            }
            default {
                Write-Host "   • Check final_applications/ for all generated reports and documents" -ForegroundColor Gray
                Write-Host "   • Review GitHub Issues for any action items created" -ForegroundColor Gray
            }
        }
    } else {
        Write-StatusMessage "❌ Operation failed with exit code: $exitCode" "Error"
        Write-StatusMessage "💡 Try running with -Verbose for detailed error information" "Warning"
        return $exitCode
    }
    
    return $exitCode
}

# Main execution
try {
    Show-Header
    
    switch ($Action) {
        "help" {
            Show-Help
            return 0
        }
        "status" {
            if (!(Test-Dependencies)) {
                return 1
            }
            Show-SystemStatus
            return 0
        }
        default {
            # Check dependencies for all other actions
            if (!(Test-Dependencies)) {
                Write-StatusMessage "❌ Dependency check failed" "Error"
                Write-StatusMessage "💡 Please resolve the above issues and try again" "Warning"
                return 1
            }
            
            # Execute the requested action
            if ($Action -in @("advanced-full", "advanced-quick", "gamification", "narrative", "portfolio", "whatif", "analysis")) {
                $result = Invoke-AdvancedIntelligenceAction -ActionType $Action
            } else {
                $result = Invoke-IntelligenceAction -ActionType $Action
            }
            return $result
        }
    }
    
} catch {
    Write-StatusMessage "❌ Unexpected error: $($_.Exception.Message)" "Error"
    Write-StatusMessage "💡 Please check the error details and try again" "Warning"
    return 1
}
