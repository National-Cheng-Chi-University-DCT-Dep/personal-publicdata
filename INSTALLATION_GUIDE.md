# 🚀 University Application Intelligence System - Installation Guide

**Quick setup guide for getting the intelligence system running in minutes**

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Prerequisites Check
```powershell
# Check Python version (requires 3.7+)
python --version

# Check pip
pip --version

# Check Git
git --version
```

### Step 2: Download & Setup
```bash
# Clone repository
git clone https://github.com/dennislee928/personal-publicdata.git
cd personal-publicdata

# Install core dependencies
pip install PyYAML requests beautifulsoup4 pandas matplotlib
```

### Step 3: First Run
```powershell
# Check system status
.\intelligence.ps1 status

# Run quick intelligence pipeline
.\intelligence.ps1 quick

# Generate documents
.\intelligence.ps1 docs
```

**That's it!** Check `final_applications/` for generated documents.

---

## 🔧 Full Installation (Complete Features)

### Step 1: System Requirements
- **Windows 10/11** with PowerShell 5.1+
- **Python 3.7+** with pip
- **Git** for version control
- **Internet connection** for data collection
- **2GB+ RAM** and **500MB+ disk space**

### Step 2: Python Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv intelligence-env

# Activate environment
intelligence-env\Scripts\activate  # Windows
# source intelligence-env/bin/activate  # Linux/Mac

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies
```bash
# Navigate to project
cd personal-publicdata

# Install all dependencies
pip install -r build_scripts/requirements.txt

# Verify installation
python -c "import yaml, requests, bs4, pandas; print('✅ Core packages installed')"
```

### Step 4: Configuration
```yaml
# Edit source_data/schools.yml to add your target schools
- school_id: "your_school"
  school: "Your University"
  full_name: "Your University Full Name"
  program: "Your Target Program"
  # ... other configuration
```

### Step 5: Optional - GitHub Integration
```bash
# Set GitHub token for automated issue creation
$env:GITHUB_TOKEN = "your_github_personal_access_token"

# Test GitHub integration
.\intelligence.ps1 alerts
```

---

## 🎯 Verification & Testing

### Basic System Check
```powershell
# Comprehensive system status
.\intelligence.ps1 status

# Should show:
# ✅ Python: Available
# ✅ Core packages installed
# ✅ Configuration files valid
```

### Test Each Component
```powershell
# Test document generation
.\intelligence.ps1 docs -Schools "taltech"

# Test validation system
.\intelligence.ps1 validate

# Test dashboard generation  
.\intelligence.ps1 dashboard

# Test notification system
.\intelligence.ps1 alerts
```

### Expected Results
After successful installation, you should see:
```
final_applications/
├── TalTech/
│   ├── CV_PeiChenLee.md
│   └── SOP_PeiChenLee_TalTech.md
├── application_dashboard.md
├── validation_report.md
└── execution_report.md
```

---

## 🚨 Troubleshooting

### Common Installation Issues

**❌ "Python is not recognized"**
```bash
# Add Python to PATH or reinstall Python with "Add to PATH" option
# Download from: https://python.org/downloads/
```

**❌ "pip install fails with SSL error"**
```bash
# Upgrade certificates
pip install --trusted-host pypi.org --trusted-host pypi.python.org --upgrade pip
```

**❌ "PowerShell execution policy error"**
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**❌ "Missing dependencies error"**
```bash
# Install minimal required packages only
pip install PyYAML requests beautifulsoup4

# Run with basic functionality
python build_scripts/generate_docs.py --list
```

### Performance Issues

**⚠️ "Slow web scraping"**
```bash
# Skip scraping and use existing data
.\intelligence.ps1 full -SkipScraping

# Or run individual components
.\intelligence.ps1 docs  # Documents only
.\intelligence.ps1 dashboard  # Dashboard only
```

**⚠️ "Out of memory errors"**
```bash
# Run components separately
.\intelligence.ps1 validate
.\intelligence.ps1 docs -Schools "taltech"  # One school at a time
```

---

## 🎯 Next Steps After Installation

### 1. Configure Your Profile
Edit the validation system to match your credentials:
- IELTS scores
- GPA information  
- Budget preferences
- Target countries

### 2. Add Your Target Schools
Update `source_data/schools.yml` with:
- School websites
- Program requirements
- Application deadlines
- Priority levels

### 3. Run Full Intelligence Pipeline
```powershell
# Complete intelligence analysis
.\intelligence.ps1 full -SaveReport

# Review generated reports
notepad final_applications/validation_report.md
notepad final_applications/academic_intelligence_report.md
```

### 4. Set Up Automation (Optional)
- Configure GitHub token for issue management
- Set up email notifications  
- Enable Harness CI/CD pipeline

---

## 📞 Need Help?

### Self-Service Resources
```powershell
# Built-in help
.\intelligence.ps1 help

# System diagnostics
.\intelligence.ps1 status

# Verbose output for debugging
.\intelligence.ps1 validate -Verbose
```

### Support Channels
- **📧 Email**: admin@dennisleehappy.org
- **🐛 GitHub Issues**: Report bugs and request features
- **📖 Documentation**: README_INTELLIGENCE_SYSTEM.md

### Quick Fix Commands
```powershell
# Reset and reinstall dependencies
pip uninstall -y -r build_scripts/requirements.txt
pip install -r build_scripts/requirements.txt

# Clear generated files and restart
Remove-Item -Recurse final_applications/*
.\intelligence.ps1 quick
```

---

**🎊 Congratulations!** Your University Application Intelligence System is ready to revolutionize your application process.

Start with: `.\intelligence.ps1 full` and let the AI guide your path to admission success! 🚀
