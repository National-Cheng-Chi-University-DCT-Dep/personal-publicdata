# 🎓 University Application Document Generator

An automated system for generating customized CV and Statement of Purpose (SOP) documents for European university applications.

## 📁 Repository Structure

```
/personal-publicdata
├── 📁 templates/
│   ├── 📄 cv_template.md              # Main CV template
│   ├── 📄 sop_master_template.md      # Master SOP template with placeholders
│   ├── 📄 sop_bridge_taltech.md       # TalTech-specific bridge content
│   ├── 📄 sop_bridge_aalto.md         # Aalto-specific bridge content
│   └── 📄 sop_bridge_generic.md       # Generic bridge content
│
├── 📁 source_data/
│   ├── 📄 schools.yml                 # School information database
│   └── 📄 recommenders.yml            # Recommender contact information
│
├── 📁 build_scripts/
│   ├── 📄 generate_docs.py            # Main document generation script
│   └── 📄 requirements.txt            # Python dependencies
│
├── 📁 final_applications/             # Generated documents (gitignored)
│   ├── 📁 TalTech/
│   │   ├── 📄 CV_PeiChenLee.md
│   │   └── 📄 SOP_PeiChenLee_TalTech.md
│   └── 📁 Aalto/
│       ├── 📄 CV_PeiChenLee.md
│       └── 📄 SOP_PeiChenLee_Aalto.md
│
├── 📁 .harness/                      # CI/CD pipeline configuration
│   └── 📄 application_pipeline.yml
│
├── 📄 .gitignore                     # Git ignore rules
└── 📄 README_APPLICATION_SYSTEM.md   # This documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip package manager
- Git

### Installation

1. Clone the repository (if not already done):
```bash
git clone https://github.com/dennislee928/personal-publicdata.git
cd personal-publicdata
```

2. Install Python dependencies:
```bash
cd build_scripts
pip install -r requirements.txt
```

### Basic Usage

#### Generate documents for a specific school:
```bash
python build_scripts/generate_docs.py --school taltech
```

#### Generate documents for all active schools:
```bash
python build_scripts/generate_docs.py --all
```

#### List all available schools:
```bash
python build_scripts/generate_docs.py --list
```

## 📊 Managing School Data

### Adding a New School

1. Edit `source_data/schools.yml`
2. Add new school entry following the existing format:

```yaml
- school_id: "new_school"
  school: "New University"
  full_name: "New University Full Name"
  program: "MSc in Computer Science"
  country: "Country"
  location: "City, Country"
  sop_bridge_file: "sop_bridge_generic.md"  # or create specific bridge file
  ielts_requirement:
    overall: 6.5
    minimum_band: 5.5
  tuition_fee: "€X,XXX/year"
  application_deadline: "Month Day, Year"
  website: "https://university.edu"
  key_features:
    - "Feature 1"
    - "Feature 2"
  priority_level: "medium"  # high, medium, low
  status: "active"          # active, inactive, template
```

3. (Optional) Create a school-specific bridge file in `templates/sop_bridge_newschool.md`

### School Status Management

- **active**: Documents will be generated
- **inactive**: Skipped during generation
- **template**: Used as template for future schools

## 🎨 Customizing Templates

### CV Template
Edit `templates/cv_template.md` to modify the CV content. The CV is currently shared across all applications.

### SOP Master Template
Edit `templates/sop_master_template.md` to modify the core SOP structure. Use these placeholders:
- `{{PROGRAM_NAME}}`: Replaced with program name from schools.yml
- `{{UNIVERSITY_NAME}}`: Replaced with school name from schools.yml  
- `{{BRIDGE_CONTENT}}`: Replaced with school-specific bridge content

### School-Specific Bridge Content
Create `templates/sop_bridge_[school_id].md` files for school-specific content. The generic bridge is used as fallback.

## ⚙️ CI/CD Automation with Harness

### Automatic Triggers

The Harness pipeline automatically triggers when:
1. `source_data/schools.yml` is modified
2. Any file in `source_data/` directory changes
3. Manual pipeline execution

### Pipeline Steps

1. **Setup Environment**: Install Python and dependencies
2. **Validate Configuration**: Check YAML file validity
3. **Generate Documents**: Create customized CV and SOP files
4. **Organize Output**: Create manifest and organize files
5. **Cache Results**: Save generated documents to cloud storage

### Manual Pipeline Execution

Access your Harness dashboard and manually trigger the "University Application Document Generator" pipeline.

## 📋 Current School Portfolio

### High Priority (Ready to Apply)
- **🇪🇪 TalTech** - MSc in Cybersecurity (€6,000/year)
- **🇫🇮 Aalto University** - SECCLO Erasmus Mundus (Scholarship available)
- **🇩🇪 Hochschule Darmstadt** - MSc Computer Science (Free tuition)

### Medium Priority (Consider Adding)
- **🇸🇪 Linköping University** - MSc Computer Science (€12,500/year)

See `source_data/schools.yml` for complete list with requirements and deadlines.

## 🔧 Advanced Features

### Environment Variables

Set these environment variables for enhanced functionality:

```bash
export GENERATE_PDF=true          # Enable PDF generation (future)
export TARGET_SCHOOLS=taltech,aalto  # Generate only specific schools
export OUTPUT_FORMAT=both        # Generate both MD and PDF
```

### Batch Operations

Generate documents for specific school categories:
```bash
# High priority schools only
python build_scripts/generate_docs.py --priority high

# EU schools only (future feature)
python build_scripts/generate_docs.py --region eu
```

## 📞 Recommender Management

Edit `source_data/recommenders.yml` to manage recommender contact information. This data can be used for:
- Quick reference during applications
- Generating recommender information sheets
- Tracking recommendation letter status

## 🐛 Troubleshooting

### Common Issues

**1. Missing bridge file error:**
```
Warning: Bridge file sop_bridge_xxx.md not found, using generic content
```
- Solution: Create the specific bridge file or use `sop_bridge_generic.md`

**2. YAML validation error:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
```
- Solution: Check YAML indentation and syntax in `schools.yml`

**3. Permission denied on output directory:**
- Solution: Ensure write permissions on `final_applications/` directory

### Debug Mode

Run with verbose output:
```bash
python build_scripts/generate_docs.py --school taltech --verbose
```

## 🔮 Future Enhancements

### Planned Features
- [ ] PDF generation using WeasyPrint/Pandoc
- [ ] School-specific CV customization
- [ ] Automated deadline tracking
- [ ] Integration with university application portals
- [ ] Multi-language support (中文/English)
- [ ] Email notifications for application deadlines

### Contributing

To add new features:
1. Create feature branch
2. Update relevant templates/scripts
3. Test with existing schools
4. Submit pull request

## 📧 Support

For issues or questions:
- **Email**: admin@dennisleehappy.org
- **GitHub Issues**: Create issue in this repository
- **Documentation**: See inline comments in Python scripts

---

**Last Updated**: October 2025  
**Version**: 1.0.0  
**Maintainer**: Pei-Chen Lee
