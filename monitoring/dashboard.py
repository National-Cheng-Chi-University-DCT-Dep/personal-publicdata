#!/usr/bin/env python3
"""
Application Status Dashboard Generator

Features:
- Real-time application status tracking
- Visual progress indicators
- Deadline monitoring
- Risk assessment visualization
- Performance metrics
"""

import os
import sys
import yaml
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

@dataclass 
class SchoolStatus:
    school_id: str
    school_name: str
    program: str
    country: str
    application_status: str  # NOT_STARTED, DRAFTING, SUBMITTED, DECISION_PENDING, ACCEPTED, REJECTED
    deadline: Optional[date]
    days_until_deadline: Optional[int]
    ielts_status: str  # MEETS, WARNING, INSUFFICIENT
    budget_status: str  # AFFORDABLE, STRETCH, EXPENSIVE
    confidence_score: float
    priority_level: str
    last_updated: datetime

class ApplicationDashboard:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        
        # Load data
        self.load_configuration()
        self.load_validation_results()
    
    def load_configuration(self):
        """Load school configuration"""
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
    
    def load_validation_results(self):
        """Load validation results if available"""
        validation_file = self.output_dir / "validation_results.json"
        
        if validation_file.exists():
            with open(validation_file, 'r', encoding='utf-8') as f:
                self.validation_data = json.load(f)
        else:
            print("[WARNING] No validation results found. Run validator first.")
            self.validation_data = {}
    
    def get_school_status(self, school_id: str) -> SchoolStatus:
        """Get comprehensive status for a school"""
        school = self.schools[school_id]
        
        # Application status (would be updated manually or through integrations)
        app_status = school.get('application_status', 'NOT_STARTED')
        
        # Deadline calculation
        deadline_str = school.get('application_deadline', '')
        deadline_date = self.parse_deadline(deadline_str)
        days_until = None
        
        if deadline_date:
            days_until = (deadline_date - date.today()).days
        
        # Get validation results
        validation_result = self.validation_data.get('results', {}).get(school_id, {})
        
        # Map validation statuses to simpler categories
        overall_status = validation_result.get('overall_status', 'NEEDS_REVIEW')
        
        ielts_status = "MEETS"
        budget_status = "AFFORDABLE"
        confidence_score = validation_result.get('confidence_score', 0.5)
        
        # Extract specific statuses from validation details
        validation_details = validation_result.get('validation_details', {})
        
        if validation_details.get('ielts_status') in ['WARNING', 'INELIGIBLE']:
            ielts_status = "WARNING" if validation_details.get('ielts_status') == 'WARNING' else "INSUFFICIENT"
        
        if validation_details.get('budget_status') in ['WARNING', 'INELIGIBLE']:
            budget_status = "STRETCH" if validation_details.get('budget_status') == 'WARNING' else "EXPENSIVE"
        
        return SchoolStatus(
            school_id=school_id,
            school_name=school['full_name'],
            program=school['program'],
            country=school['country'],
            application_status=app_status,
            deadline=deadline_date,
            days_until_deadline=days_until,
            ielts_status=ielts_status,
            budget_status=budget_status,
            confidence_score=confidence_score,
            priority_level=school.get('priority_level', 'medium'),
            last_updated=datetime.now()
        )
    
    def parse_deadline(self, deadline_str: str) -> Optional[date]:
        """Parse deadline string to date object"""
        # This is a simplified version - the validator has a more robust implementation
        import re
        
        if not deadline_str:
            return None
        
        # Try to find a date pattern
        date_match = re.search(r'(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})', deadline_str)
        if date_match:
            try:
                # Assume MM/DD/YYYY format first
                month, day, year = map(int, date_match.groups())
                return date(year, month, day)
            except ValueError:
                try:
                    # Try DD/MM/YYYY format
                    day, month, year = map(int, date_match.groups())
                    return date(year, month, day)
                except ValueError:
                    pass
        
        # Try month names
        month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        
        for i, month_name in enumerate(month_names, 1):
            if month_name in deadline_str.lower():
                # Look for day and year
                day_match = re.search(r'(\d{1,2})', deadline_str)
                year_match = re.search(r'(20\d{2})', deadline_str)
                
                if day_match and year_match:
                    try:
                        day = int(day_match.group(1))
                        year = int(year_match.group(1))
                        return date(year, i, day)
                    except ValueError:
                        pass
        
        return None
    
    def generate_dashboard(self) -> str:
        """Generate the main dashboard HTML/Markdown"""
        dashboard_lines = [
            "# 🎓 University Application Dashboard",
            "",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## [OVERVIEW] Quick Overview",
            ""
        ]
        
        # Get status for all active schools
        statuses = []
        for school_id, school in self.schools.items():
            if school.get('status') == 'active':
                statuses.append(self.get_school_status(school_id))
        
        # Summary statistics
        total_schools = len(statuses)
        
        # Application status counts
        app_status_counts = {}
        for status in statuses:
            app_status = status.application_status
            app_status_counts[app_status] = app_status_counts.get(app_status, 0) + 1
        
        # Create overview table
        dashboard_lines.extend([
            "### 📈 Application Progress",
            "",
            "| Status | Count | Percentage | Progress Bar |",
            "|--------|-------|------------|--------------|"
        ])
        
        status_order = ['NOT_STARTED', 'DRAFTING', 'SUBMITTED', 'DECISION_PENDING', 'ACCEPTED', 'REJECTED']
        status_icons = {
            'NOT_STARTED': '⚪',
            'DRAFTING': '🟡', 
            'SUBMITTED': '🟢',
            'DECISION_PENDING': '🔵',
            'ACCEPTED': '[ACCEPTED]',
            'REJECTED': '[REJECTED]'
        }
        
        for app_status in status_order:
            count = app_status_counts.get(app_status, 0)
            if count > 0:
                percentage = count / total_schools * 100
                progress_bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
                icon = status_icons.get(app_status, '❓')
                dashboard_lines.append(f"| {icon} {app_status} | {count} | {percentage:.1f}% | {progress_bar} |")
        
        # Deadline urgency
        urgent_deadlines = []
        upcoming_deadlines = []
        
        for status in statuses:
            if status.days_until_deadline is not None:
                if 0 <= status.days_until_deadline <= 7:
                    urgent_deadlines.append(status)
                elif 8 <= status.days_until_deadline <= 30:
                    upcoming_deadlines.append(status)
        
        if urgent_deadlines:
            dashboard_lines.extend([
                "",
                "## [URGENT] URGENT DEADLINES (≤7 days)",
                ""
            ])
            
            for status in sorted(urgent_deadlines, key=lambda x: x.days_until_deadline):
                urgency_icon = "[CRITICAL]" if status.days_until_deadline <= 3 else "[URGENT]"
                dashboard_lines.append(f"- {urgency_icon} **{status.school_name}**: {status.days_until_deadline} days remaining")
        
        if upcoming_deadlines:
            dashboard_lines.extend([
                "",
                "## ⏰ Upcoming Deadlines (8-30 days)",
                ""
            ])
            
            for status in sorted(upcoming_deadlines, key=lambda x: x.days_until_deadline):
                dashboard_lines.append(f"- 📅 **{status.school_name}**: {status.days_until_deadline} days remaining")
        
        # Detailed school table
        dashboard_lines.extend([
            "",
            "## [STATUS] Detailed School Status",
            "",
            "| School | Country | Status | Deadline | IELTS | Budget | Priority | Confidence |",
            "|--------|---------|--------|----------|-------|--------|----------|------------|"
        ])
        
        # Sort by priority and deadline urgency
        sorted_statuses = sorted(statuses, key=lambda x: (
            x.priority_level != 'high',
            x.priority_level != 'medium',
            x.days_until_deadline if x.days_until_deadline is not None else 999,
            -x.confidence_score
        ))
        
        for status in sorted_statuses:
            # Status icon
            status_icon = status_icons.get(status.application_status, '❓')
            
            # Deadline display
            if status.days_until_deadline is not None:
                if status.days_until_deadline < 0:
                    deadline_display = f"[PASSED] Passed"
                elif status.days_until_deadline <= 7:
                    deadline_display = f"[URGENT] {status.days_until_deadline}d"
                elif status.days_until_deadline <= 30:
                    deadline_display = f"[WARNING] {status.days_until_deadline}d"
                else:
                    deadline_display = f"[OK] {status.days_until_deadline}d"
            else:
                deadline_display = "❓ Unknown"
            
            # IELTS status
            ielts_icons = {'MEETS': '[MEETS]', 'WARNING': '[WARNING]', 'INSUFFICIENT': '[INSUFFICIENT]'}
            ielts_display = f"{ielts_icons.get(status.ielts_status, '❓')} {status.ielts_status}"
            
            # Budget status  
            budget_icons = {'AFFORDABLE': '[AFFORDABLE]', 'STRETCH': '[STRETCH]', 'EXPENSIVE': '[EXPENSIVE]'}
            budget_display = f"{budget_icons.get(status.budget_status, '❓')} {status.budget_status}"
            
            # Priority
            priority_icons = {'high': '🔥', 'medium': '⚡', 'low': '💫'}
            priority_display = f"{priority_icons.get(status.priority_level, '❓')} {status.priority_level.upper()}"
            
            # Confidence score
            confidence_display = f"{status.confidence_score:.0%}"
            
            # Country flag (simple text for now)
            country_flag = {'Estonia': '🇪🇪', 'Finland': '🇫🇮', 'Sweden': '🇸🇪', 'Germany': '🇩🇪'}.get(status.country, '🏳️')
            
            dashboard_lines.append(
                f"| {status_icon} **{status.school_name}** | {country_flag} {status.country} | "
                f"{status.application_status} | {deadline_display} | {ielts_display} | "
                f"{budget_display} | {priority_display} | {confidence_display} |"
            )
        
        # Key metrics
        dashboard_lines.extend([
            "",
            "## 📈 Key Metrics",
            ""
        ])
        
        # Calculate metrics
        high_priority_count = sum(1 for s in statuses if s.priority_level == 'high')
        meets_ielts_count = sum(1 for s in statuses if s.ielts_status == 'MEETS')
        affordable_count = sum(1 for s in statuses if s.budget_status == 'AFFORDABLE')
        avg_confidence = sum(s.confidence_score for s in statuses) / len(statuses) if statuses else 0
        
        submitted_count = sum(1 for s in statuses if s.application_status == 'SUBMITTED')
        pending_count = sum(1 for s in statuses if s.application_status == 'DECISION_PENDING')
        
        dashboard_lines.extend([
            f"- **High Priority Schools**: {high_priority_count}/{total_schools} ({high_priority_count/total_schools:.1%})",
            f"- **IELTS Requirements Met**: {meets_ielts_count}/{total_schools} ({meets_ielts_count/total_schools:.1%})",
            f"- **Budget Friendly**: {affordable_count}/{total_schools} ({affordable_count/total_schools:.1%})",
            f"- **Average Confidence**: {avg_confidence:.1%}",
            f"- **Applications Submitted**: {submitted_count}",
            f"- **Decisions Pending**: {pending_count}",
            ""
        ])
        
        # Action items
        action_items = []
        
        # Check for urgent actions
        if urgent_deadlines:
            action_items.append("[URGENT] **URGENT**: Complete applications with deadlines ≤7 days")
        
        not_started_count = app_status_counts.get('NOT_STARTED', 0)
        if not_started_count > 0:
            action_items.append(f"[TODO] Start work on {not_started_count} applications not yet begun")
        
        drafting_count = app_status_counts.get('DRAFTING', 0)
        if drafting_count > 0:
            action_items.append(f"✍️ Complete {drafting_count} applications currently in draft")
        
        ielts_issues_count = sum(1 for s in statuses if s.ielts_status != 'MEETS')
        if ielts_issues_count > 0:
            action_items.append(f"📚 Consider IELTS retake for {ielts_issues_count} schools with language issues")
        
        if action_items:
            dashboard_lines.extend([
                "## [ACTIONS] Recommended Actions",
                ""
            ])
            for item in action_items:
                dashboard_lines.append(f"- {item}")
            dashboard_lines.append("")
        
        # Footer
        dashboard_lines.extend([
            "---",
            "",
            "### [UPDATE] How to Update This Dashboard",
            "",
            "To update application status, modify the `application_status` field in `source_data/schools.yml`:",
            "",
            "```yaml",
            "- school_id: \"taltech\"",
            "  # ... other fields ...", 
            "  application_status: \"SUBMITTED\"  # NOT_STARTED, DRAFTING, SUBMITTED, DECISION_PENDING, ACCEPTED, REJECTED",
            "```",
            "",
            "Then regenerate the dashboard by running:",
            "```bash",
            "python monitoring/dashboard.py",
            "```",
            "",
            f"*Dashboard generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Application Intelligence System v2.0*"
        ])
        
        return "\n".join(dashboard_lines)
    
    def save_dashboard(self):
        """Save dashboard to file"""
        dashboard_content = self.generate_dashboard()
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Save dashboard
        dashboard_file = self.output_dir / "application_dashboard.md"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        print(f"[DASHBOARD] Dashboard saved to {dashboard_file}")
        
        # Also save as HTML for better visualization (optional)
        try:
            html_content = self.generate_html_dashboard(dashboard_content)
            html_file = self.output_dir / "application_dashboard.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"[HTML] HTML dashboard saved to {html_file}")
        except Exception as e:
            print(f"[WARNING] HTML generation skipped: {e}")
    
    def generate_html_dashboard(self, markdown_content: str) -> str:
        """Generate HTML version of dashboard (basic conversion)"""
        try:
            import markdown
            
            # Convert markdown to HTML
            html_body = markdown.markdown(markdown_content, extensions=['tables'])
            
            # Wrap in HTML template
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>University Application Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .urgent {{ background-color: #ffebee; }}
        .warning {{ background-color: #fff3e0; }}
        .success {{ background-color: #e8f5e8; }}
        h1 {{ color: #1976d2; }}
        h2 {{ color: #424242; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }}
    </style>
    <meta http-equiv="refresh" content="300">  <!-- Auto refresh every 5 minutes -->
</head>
<body>
{html_body}
<script>
    // Add some basic interactivity
    document.addEventListener('DOMContentLoaded', function() {{
        // Highlight urgent deadlines
        const rows = document.querySelectorAll('tr');
        rows.forEach(row => {{
            const text = row.textContent.toLowerCase();
            if (text.includes('[urgent]') || text.includes('urgent')) {{
                row.classList.add('urgent');
            }} else if (text.includes('[warning]') || text.includes('warning')) {{
                row.classList.add('warning');
            }} else if (text.includes('[ok]') || text.includes('[meets]') || text.includes('[affordable]')) {{
                row.classList.add('success');
            }}
        }});
    }});
</script>
</body>
</html>
            """
            return html_template
            
        except ImportError:
            print("[WARNING] Install 'markdown' package for HTML generation: pip install markdown")
            return ""

def main():
    """Main dashboard execution"""
    dashboard = ApplicationDashboard()
    
    try:
        # Generate and save dashboard
        dashboard.save_dashboard()
        
        print("[SUCCESS] Dashboard generation completed successfully!")
        return 0
        
    except Exception as e:
        print(f"[ERROR] Dashboard generation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
