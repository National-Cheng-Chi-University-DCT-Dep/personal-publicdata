#!/usr/bin/env python3
"""
Advanced Data Validator and Application Eligibility Checker

Features:
- Schema validation for scraped data
- Rule-based eligibility checking  
- Personal profile matching
- Risk assessment and flagging
- Automated issue creation for GitHub
- Validation reporting
"""

import os
import sys
import yaml
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class ValidationResult:
    school_id: str
    overall_status: str  # ELIGIBLE, WARNING, INELIGIBLE, NEEDS_REVIEW
    confidence_score: float
    validation_details: Dict[str, Any]
    action_items: List[str]
    risk_factors: List[str]
    advantages: List[str]

class PersonalProfile:
    """User's personal academic and professional profile"""
    def __init__(self, profile_file: Optional[Path] = None):
        self.bachelor_gpa = 2.92
        self.master_gpa = 3.96
        self.ielts_overall = 7.0
        self.ielts_writing = 5.5
        self.ielts_reading = 9.0
        self.ielts_listening = 7.5
        self.ielts_speaking = 6.5
        self.work_experience_years = 5
        self.has_cybersecurity_background = True
        self.has_awards = True
        self.target_budget_eur = 12500  # per year
        self.risk_tolerance = "medium"  # low, medium, high
        
        if profile_file and profile_file.exists():
            self.load_from_file(profile_file)
    
    def load_from_file(self, profile_file: Path):
        """Load profile from YAML file"""
        with open(profile_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

class ApplicationValidator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        
        # Load configurations
        self.profile = PersonalProfile()
        self.load_schools_config()
        self.load_live_data()
        
        # Validation rules
        self.validation_rules = self.setup_validation_rules()
    
    def load_schools_config(self):
        """Load school configuration"""
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
    
    def load_live_data(self):
        """Load scraped live data"""
        live_data_file = self.source_data_dir / "schools_live_data.yml"
        
        if live_data_file.exists():
            with open(live_data_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.live_data = {item['school_id']: item for item in data.get('schools_live_data', [])}
                self.scrape_metadata = data.get('metadata', {})
        else:
            print("WARNING: No live data found. Run scraper first.")
            self.live_data = {}
            self.scrape_metadata = {}
    
    def setup_validation_rules(self) -> Dict[str, Any]:
        """Setup validation rules based on personal profile"""
        return {
            'ielts_thresholds': {
                'critical': {  # Must meet or high risk
                    'overall_gap': 0.5,  # If required score - actual > 0.5
                    'writing_gap': 0.0   # Must meet writing requirement exactly
                },
                'warning': {    # Should meet for better chances
                    'overall_gap': 0.0,
                    'writing_gap': -0.5
                }
            },
            'budget_thresholds': {
                'acceptable': self.profile.target_budget_eur,
                'stretch': self.profile.target_budget_eur * 1.5,
                'unaffordable': self.profile.target_budget_eur * 2
            },
            'deadline_thresholds': {
                'urgent': 30,     # days
                'upcoming': 60,   # days
                'planning': 120   # days
            }
        }
    
    def validate_schema(self, school_id: str) -> Tuple[bool, List[str]]:
        """Validate data schema completeness"""
        issues = []
        
        # Check if school exists in config
        if school_id not in self.schools:
            issues.append(f"School {school_id} not found in configuration")
            return False, issues
        
        school_config = self.schools[school_id]
        
        # Check required fields in config
        required_fields = ['school', 'program', 'country', 'ielts_requirement']
        for field in required_fields:
            if field not in school_config:
                issues.append(f"Missing required field: {field}")
        
        # Check live data availability if scraped
        if school_id in self.live_data:
            live_data = self.live_data[school_id]
            confidence = live_data.get('confidence_score', 0)
            
            if confidence < 0.3:
                issues.append(f"Low confidence scraped data ({confidence:.1%})")
            
            # Check for contradictions between config and scraped data
            scraped_ielts = live_data.get('data', {}).get('ielts_requirements_scraped')
            if scraped_ielts and 'ielts_requirement' in school_config:
                config_ielts = school_config['ielts_requirement']
                
                # Compare overall scores if both available
                if 'overall' in scraped_ielts and 'overall' in config_ielts:
                    scraped_overall = scraped_ielts['overall']
                    config_overall = config_ielts['overall']
                    
                    if abs(scraped_overall - config_overall) > 0.5:
                        issues.append(f"IELTS requirement mismatch: config={config_overall}, scraped={scraped_overall}")
        
        return len(issues) == 0, issues
    
    def check_ielts_eligibility(self, school_id: str) -> Tuple[str, List[str], List[str]]:
        """Check IELTS eligibility against requirements"""
        school_config = self.schools[school_id]
        requirements = school_config.get('ielts_requirement', {})
        
        # Use scraped data if available and reliable
        if school_id in self.live_data:
            scraped_ielts = self.live_data[school_id].get('data', {}).get('ielts_requirements_scraped')
            if scraped_ielts:
                requirements.update(scraped_ielts)  # Scraped data takes priority
        
        issues = []
        advantages = []
        
        # Check overall score
        required_overall = requirements.get('overall', 6.5)
        overall_gap = required_overall - self.profile.ielts_overall
        
        if overall_gap > self.validation_rules['ielts_thresholds']['critical']['overall_gap']:
            issues.append(f"IELTS overall score gap: need {required_overall}, have {self.profile.ielts_overall}")
            status = "INELIGIBLE"
        elif overall_gap > 0:
            issues.append(f"IELTS overall score below requirement: need {required_overall}, have {self.profile.ielts_overall}")
            status = "WARNING"
        else:
            advantages.append(f"IELTS overall score exceeds requirement: have {self.profile.ielts_overall}, need {required_overall}")
            status = "ELIGIBLE"
        
        # Check writing score (critical for many programs)
        required_writing = requirements.get('writing_minimum', requirements.get('minimum_band', 5.5))
        writing_gap = required_writing - self.profile.ielts_writing
        
        if writing_gap > self.validation_rules['ielts_thresholds']['critical']['writing_gap']:
            issues.append(f"IELTS writing score insufficient: need {required_writing}, have {self.profile.ielts_writing}")
            if status != "INELIGIBLE":
                status = "WARNING"
        elif writing_gap > self.validation_rules['ielts_thresholds']['warning']['writing_gap']:
            issues.append(f"IELTS writing score at minimum: need {required_writing}, have {self.profile.ielts_writing}")
        else:
            advantages.append(f"IELTS writing score sufficient: have {self.profile.ielts_writing}, need {required_writing}")
        
        # Check minimum band requirements
        required_band = requirements.get('minimum_band', 5.5)
        min_score = min([self.profile.ielts_reading, self.profile.ielts_listening, 
                        self.profile.ielts_speaking, self.profile.ielts_writing])
        
        if min_score < required_band:
            issues.append(f"Minimum band requirement not met: need {required_band}, minimum band is {min_score}")
            if status == "ELIGIBLE":
                status = "WARNING"
        
        return status, issues, advantages
    
    def check_budget_feasibility(self, school_id: str) -> Tuple[str, List[str], List[str]]:
        """Check budget feasibility"""
        school_config = self.schools[school_id]
        tuition_fee_str = school_config.get('tuition_fee', '')
        
        # Use scraped tuition if available
        if school_id in self.live_data:
            scraped_fee = self.live_data[school_id].get('data', {}).get('tuition_fee_scraped')
            if scraped_fee:
                tuition_fee_str = scraped_fee
        
        issues = []
        advantages = []
        
        # Extract numeric value from tuition fee string
        fee_amount = self.extract_fee_amount(tuition_fee_str)
        
        if fee_amount is None:
            issues.append("Tuition fee information unclear or missing")
            return "NEEDS_REVIEW", issues, advantages
        
        thresholds = self.validation_rules['budget_thresholds']
        
        if fee_amount <= thresholds['acceptable']:
            advantages.append(f"Tuition within budget: €{fee_amount:,} ≤ €{thresholds['acceptable']:,}")
            status = "ELIGIBLE"
        elif fee_amount <= thresholds['stretch']:
            issues.append(f"Tuition requires budget stretch: €{fee_amount:,} vs budget €{thresholds['acceptable']:,}")
            status = "WARNING"
        elif fee_amount <= thresholds['unaffordable']:
            issues.append(f"Tuition significantly over budget: €{fee_amount:,} vs budget €{thresholds['acceptable']:,}")
            status = "WARNING"
        else:
            issues.append(f"Tuition unaffordable: €{fee_amount:,} vs budget €{thresholds['acceptable']:,}")
            status = "INELIGIBLE"
        
        return status, issues, advantages
    
    def extract_fee_amount(self, fee_string: str) -> Optional[float]:
        """Extract numeric fee amount from string"""
        if not fee_string or fee_string.lower() in ['free', 'no tuition']:
            return 0.0
        
        # Remove common words and normalize
        fee_string = re.sub(r'per year|annual|yearly|semester|/year|/semester', '', fee_string.lower())
        
        # Extract numeric values with currency symbols
        patterns = [
            r'€\s*(\d+[,.]?\d*)',  # €6,000 or €6.000
            r'(\d+[,.]?\d*)\s*€',  # 6000€
            r'(\d+[,.]?\d*)\s*eur',  # 6000 EUR
            r'sek\s*(\d+[,.]?\d*)',  # SEK 140,000
            r'(\d+[,.]?\d*)\s*sek',  # 140000 SEK
        ]
        
        for pattern in patterns:
            match = re.search(pattern, fee_string)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    
                    # Convert SEK to EUR (rough conversion)
                    if 'sek' in fee_string:
                        amount = amount / 11.0  # Approximate SEK to EUR
                    
                    # Handle semester vs annual fees
                    if 'semester' in fee_string and amount < 10000:
                        amount *= 2  # Convert semester to annual
                    
                    return amount
                except ValueError:
                    continue
        
        return None
    
    def check_deadline_urgency(self, school_id: str) -> Tuple[str, List[str], List[str]]:
        """Check application deadline urgency"""
        school_config = self.schools[school_id]
        deadline_str = school_config.get('application_deadline', '')
        
        # Use scraped deadline if available
        if school_id in self.live_data:
            scraped_deadline = self.live_data[school_id].get('data', {}).get('application_deadline_scraped')
            if scraped_deadline:
                deadline_str = scraped_deadline
        
        issues = []
        advantages = []
        
        # Parse deadline
        deadline_date = self.parse_deadline(deadline_str)
        
        if deadline_date is None:
            issues.append("Application deadline unclear or missing")
            return "NEEDS_REVIEW", issues, advantages
        
        # Calculate days until deadline
        today = date.today()
        days_until = (deadline_date - today).days
        
        thresholds = self.validation_rules['deadline_thresholds']
        
        if days_until < 0:
            issues.append(f"Application deadline has passed: {deadline_str}")
            status = "INELIGIBLE"
        elif days_until < thresholds['urgent']:
            issues.append(f"URGENT: Application due in {days_until} days")
            status = "WARNING"
        elif days_until < thresholds['upcoming']:
            issues.append(f"Application due soon: {days_until} days remaining")
            status = "WARNING"
        else:
            advantages.append(f"Plenty of time to apply: {days_until} days remaining")
            status = "ELIGIBLE"
        
        return status, issues, advantages
    
    def parse_deadline(self, deadline_str: str) -> Optional[date]:
        """Parse deadline string to date object"""
        if not deadline_str:
            return None
        
        # Common deadline formats
        patterns = [
            r'(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{4})[./\-](\d{1,2})[./\-](\d{1,2})',  # YYYY/MM/DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, deadline_str)
            if match:
                try:
                    parts = [int(match.group(i)) for i in range(1, 4)]
                    
                    # Try different date formats
                    for year, month, day in [parts, [parts[2], parts[1], parts[0]], [parts[0], parts[1], parts[2]]]:
                        try:
                            if year < 100:  # Two-digit year
                                year += 2000
                            return date(year, month, day)
                        except ValueError:
                            continue
                except (ValueError, IndexError):
                    continue
        
        # Try month names
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        for month_name, month_num in month_names.items():
            if month_name in deadline_str.lower():
                # Look for day and year
                day_match = re.search(r'(\d{1,2})', deadline_str)
                year_match = re.search(r'(20\d{2})', deadline_str)
                
                if day_match and year_match:
                    try:
                        day = int(day_match.group(1))
                        year = int(year_match.group(1))
                        return date(year, month_num, day)
                    except ValueError:
                        continue
        
        return None
    
    def validate_school(self, school_id: str) -> ValidationResult:
        """Perform comprehensive validation for a school"""
        print(f"[VALIDATING] Validating {school_id}...")
        
        # Schema validation
        schema_valid, schema_issues = self.validate_schema(school_id)
        
        # Initialize result
        result = ValidationResult(
            school_id=school_id,
            overall_status="NEEDS_REVIEW",
            confidence_score=0.0,
            validation_details={},
            action_items=[],
            risk_factors=[],
            advantages=[]
        )
        
        if not schema_valid:
            result.risk_factors.extend(schema_issues)
            result.action_items.append("Review and fix data quality issues")
        
        # IELTS eligibility
        ielts_status, ielts_issues, ielts_advantages = self.check_ielts_eligibility(school_id)
        result.validation_details['ielts_status'] = ielts_status
        result.risk_factors.extend(ielts_issues)
        result.advantages.extend(ielts_advantages)
        
        # Budget feasibility
        budget_status, budget_issues, budget_advantages = self.check_budget_feasibility(school_id)
        result.validation_details['budget_status'] = budget_status
        result.risk_factors.extend(budget_issues)
        result.advantages.extend(budget_advantages)
        
        # Deadline urgency
        deadline_status, deadline_issues, deadline_advantages = self.check_deadline_urgency(school_id)
        result.validation_details['deadline_status'] = deadline_status
        result.risk_factors.extend(deadline_issues)
        result.advantages.extend(deadline_advantages)
        
        # Determine overall status
        statuses = [ielts_status, budget_status, deadline_status]
        
        if "INELIGIBLE" in statuses:
            result.overall_status = "INELIGIBLE"
        elif "WARNING" in statuses or not schema_valid:
            result.overall_status = "WARNING"
        elif "NEEDS_REVIEW" in statuses:
            result.overall_status = "NEEDS_REVIEW"
        else:
            result.overall_status = "ELIGIBLE"
        
        # Calculate confidence score
        confidence_factors = []
        if schema_valid:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.3)
        
        # Add live data confidence if available
        if school_id in self.live_data:
            confidence_factors.append(self.live_data[school_id].get('confidence_score', 0.5))
        
        result.confidence_score = sum(confidence_factors) / len(confidence_factors)
        
        # Generate action items
        if result.overall_status == "INELIGIBLE":
            result.action_items.append("Consider alternative schools or address eligibility issues")
        elif result.overall_status == "WARNING":
            result.action_items.append("Review risk factors and consider mitigation strategies")
        elif result.overall_status == "ELIGIBLE":
            result.action_items.append("Proceed with application preparation")
        
        return result
    
    def validate_all_schools(self) -> Dict[str, ValidationResult]:
        """Validate all active schools"""
        results = {}
        
        active_schools = [school_id for school_id, school in self.schools.items() 
                         if school.get('status') == 'active']
        
        print(f"[VALIDATING] Validating {len(active_schools)} active schools...")
        
        for school_id in active_schools:
            results[school_id] = self.validate_school(school_id)
        
        return results
    
    def generate_validation_report(self, results: Dict[str, ValidationResult]) -> str:
        """Generate comprehensive validation report"""
        report_lines = [
            "# 🎓 University Application Validation Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Profile**: IELTS {self.profile.ielts_overall} (W:{self.profile.ielts_writing}), Budget: €{self.profile.target_budget_eur:,}",
            "",
            "## [SUMMARY] Executive Summary",
            ""
        ]
        
        # Summary statistics
        status_counts = {}
        for result in results.values():
            status = result.overall_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_schools = len(results)
        report_lines.extend([
            f"| Status | Count | Percentage |",
            f"|--------|-------|------------|",
        ])
        
        status_icons = {
            "ELIGIBLE": "[ELIGIBLE]",
            "WARNING": "[WARNING]",
            "NEEDS_REVIEW": "[REVIEW]", 
            "INELIGIBLE": "[INELIGIBLE]"
        }
        
        for status, count in status_counts.items():
            icon = status_icons.get(status, "❓")
            percentage = count / total_schools * 100
            report_lines.append(f"| {icon} {status} | {count} | {percentage:.1f}% |")
        
        report_lines.extend([
            "",
            "## [ANALYSIS] School-by-School Analysis",
            ""
        ])
        
        # Sort schools by overall status and confidence
        sorted_schools = sorted(results.items(), 
                              key=lambda x: (
                                  x[1].overall_status != "ELIGIBLE",
                                  x[1].overall_status != "WARNING", 
                                  -x[1].confidence_score
                              ))
        
        for school_id, result in sorted_schools:
            school_name = self.schools[school_id]['full_name']
            status_icon = status_icons.get(result.overall_status, "❓")
            
            report_lines.extend([
                f"### {status_icon} {school_name} ({school_id})",
                "",
                f"**Overall Status**: {result.overall_status}",
                f"**Confidence Score**: {result.confidence_score:.1%}",
                ""
            ])
            
            if result.advantages:
                report_lines.extend([
                    "**[ADVANTAGES] Advantages:**",
                    ""
                ])
                for advantage in result.advantages:
                    report_lines.append(f"- {advantage}")
                report_lines.append("")
            
            if result.risk_factors:
                report_lines.extend([
                    "**[RISKS] Risk Factors:**",
                    ""
                ])
                for risk in result.risk_factors:
                    report_lines.append(f"- {risk}")
                report_lines.append("")
            
            if result.action_items:
                report_lines.extend([
                    "**[ACTIONS] Action Items:**",
                    ""
                ])
                for action in result.action_items:
                    report_lines.append(f"- {action}")
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
        
        # Recommendations
        eligible_schools = [school_id for school_id, result in results.items() 
                          if result.overall_status == "ELIGIBLE"]
        warning_schools = [school_id for school_id, result in results.items() 
                         if result.overall_status == "WARNING"]
        
        report_lines.extend([
            "## [STRATEGY] Strategic Recommendations",
            "",
        ])
        
        if eligible_schools:
            report_lines.extend([
                f"### [PRIORITY] Priority Applications ({len(eligible_schools)} schools)",
                "These schools meet all basic requirements and should be your primary focus:",
                ""
            ])
            for school_id in eligible_schools:
                school_name = self.schools[school_id]['full_name']
                report_lines.append(f"- **{school_name}** ({school_id})")
            report_lines.append("")
        
        if warning_schools:
            report_lines.extend([
                f"### [CONDITIONAL] Conditional Applications ({len(warning_schools)} schools)", 
                "These schools have some risk factors but may still be viable:",
                ""
            ])
            for school_id in warning_schools:
                school_name = self.schools[school_id]['full_name']
                issues = len(results[school_id].risk_factors)
                report_lines.append(f"- **{school_name}** ({school_id}) - {issues} issue(s)")
            report_lines.append("")
        
        # Action plan
        urgent_deadlines = []
        ielts_issues = []
        budget_concerns = []
        
        for school_id, result in results.items():
            for risk in result.risk_factors:
                if "urgent" in risk.lower() or "due in" in risk.lower():
                    urgent_deadlines.append((school_id, risk))
                elif "ielts" in risk.lower():
                    ielts_issues.append((school_id, risk))
                elif any(term in risk.lower() for term in ["budget", "tuition", "fee"]):
                    budget_concerns.append((school_id, risk))
        
        if urgent_deadlines or ielts_issues or budget_concerns:
            report_lines.extend([
                "## [URGENT] Immediate Action Required",
                ""
            ])
            
            if urgent_deadlines:
                report_lines.extend([
                    "### ⏰ Urgent Deadlines",
                    ""
                ])
                for school_id, issue in urgent_deadlines:
                    school_name = self.schools[school_id]['school']
                    report_lines.append(f"- **{school_name}**: {issue}")
                report_lines.append("")
            
            if ielts_issues:
                report_lines.extend([
                    "### [IELTS] IELTS Retake Needed",
                    ""
                ])
                for school_id, issue in ielts_issues:
                    school_name = self.schools[school_id]['school']  
                    report_lines.append(f"- **{school_name}**: {issue}")
                report_lines.extend([
                    "",
                    "**Recommendation**: Schedule IELTS retake focusing on writing skills (target: 6.5)",
                    ""
                ])
            
            if budget_concerns:
                report_lines.extend([
                    "### 💰 Budget Considerations",
                    ""
                ])
                for school_id, issue in budget_concerns:
                    school_name = self.schools[school_id]['school']
                    report_lines.append(f"- **{school_name}**: {issue}")
                report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            f"*Report generated by University Application Validator v2.0*",
            f"*Data sources: Static config + Live scraped data (last updated: {self.scrape_metadata.get('scraped_at', 'N/A')})*"
        ])
        
        return "\n".join(report_lines)
    
    def save_validation_report(self, results: Dict[str, ValidationResult]):
        """Save validation report to file"""
        report_content = self.generate_validation_report(results)
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Save report
        report_file = self.output_dir / "validation_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"[REPORT] Validation report saved to {report_file}")
        
        # Also save structured data for programmatic use
        structured_data = {
            'generated_at': datetime.now().isoformat(),
            'profile_summary': {
                'ielts_overall': self.profile.ielts_overall,
                'ielts_writing': self.profile.ielts_writing,
                'budget_eur': self.profile.target_budget_eur
            },
            'results': {}
        }
        
        for school_id, result in results.items():
            structured_data['results'][school_id] = {
                'overall_status': result.overall_status,
                'confidence_score': result.confidence_score,
                'validation_details': result.validation_details,
                'risk_count': len(result.risk_factors),
                'advantage_count': len(result.advantages)
            }
        
        json_file = self.output_dir / "validation_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2)
        
        print(f"[DATA] Structured results saved to {json_file}")
        
        # Print validation summary
        self.print_validation_summary(results)

    def print_validation_summary(self, results: Dict[str, ValidationResult]):
        """Print validation summary to console"""
        try:
            # Count statuses
            status_counts = {}
            for result in results.values():
                status = result.overall_status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"\n[SUMMARY] Validation Summary:")
            print(f"   IELTS Overall: {self.profile.ielts_overall}")
            print(f"   IELTS Writing: {self.profile.ielts_writing}")
            print(f"   Budget: €{self.profile.target_budget_eur:,}")
            print()
            
            print("📈 School Status Distribution:")
            status_icons = {
                "ELIGIBLE": "[ELIGIBLE]",
                "WARNING": "[WARNING]",
                "INELIGIBLE": "[INELIGIBLE]",
                "NEEDS_REVIEW": "🔍"
            }
            
            for status, count in status_counts.items():
                icon = status_icons.get(status, "❓")
                print(f"   {icon} {status}: {count}")
            
            print(f"\n[TOTAL] Total Schools: {len(results)}")
            
            # Show top recommendations
            eligible_schools = [school_id for school_id, result in results.items() 
                              if result.overall_status == "ELIGIBLE"]
            
            if eligible_schools:
                print(f"\n[RECOMMENDED] Recommended Schools ({len(eligible_schools)}):")
                for school_id in eligible_schools[:3]:  # Show top 3
                    school_name = self.schools[school_id]['school']
                    print(f"   • {school_name} ({school_id})")
                if len(eligible_schools) > 3:
                    print(f"   • ... and {len(eligible_schools) - 3} more")
            
        except Exception as e:
            print(f"[ERROR] Summary generation failed: {e}")

def main():
    """Main validator execution"""
    validator = ApplicationValidator()
    
    try:
        # Validate all schools
        results = validator.validate_all_schools()
        
        # Generate and save report
        validator.save_validation_report(results)
        
        # Summary
        eligible_count = sum(1 for r in results.values() if r.overall_status == "ELIGIBLE")
        warning_count = sum(1 for r in results.values() if r.overall_status == "WARNING")
        ineligible_count = sum(1 for r in results.values() if r.overall_status == "INELIGIBLE")
        
        print(f"\n[SUMMARY] Validation Summary:")
        print(f"   [ELIGIBLE] Eligible: {eligible_count}")
        print(f"   [WARNING] Warning: {warning_count}")
        print(f"   [INELIGIBLE] Ineligible: {ineligible_count}")
        print(f"   [TOTAL] Total: {len(results)}")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Validation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
