#!/usr/bin/env python3
"""
Intelligent Alert and Notification System

Features:
- Deadline monitoring and alerts
- GitHub Issues integration for task management  
- Email notifications
- Slack/Discord integration
- Risk-based alerting
- Automated task creation
"""

import os
import sys
import json
import yaml
import smtplib
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GitHubIntegration:
    """GitHub Issues integration for task management"""
    
    def __init__(self, repo_owner: str, repo_name: str, token: Optional[str] = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        if not self.token:
            print("WARNING: GitHub token not found. Set GITHUB_TOKEN environment variable for issue creation.")
    
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[str]:
        """Create a GitHub issue"""
        if not self.token:
            print(f"[INFO] Would create GitHub issue: {title}")
            return None
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': title,
            'body': body,
            'labels': labels or []
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/issues",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_url = issue_data['html_url']
                print(f"[SUCCESS] Created GitHub issue: {issue_url}")
                return issue_url
            else:
                print(f"[ERROR] Failed to create issue: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[ERROR] GitHub API error: {str(e)}")
            return None
    
    def list_issues(self, state: str = 'open', labels: List[str] = None) -> List[Dict]:
        """List existing issues"""
        if not self.token:
            return []
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        params = {'state': state}
        if labels:
            params['labels'] = ','.join(labels)
        
        try:
            response = requests.get(
                f"{self.base_url}/issues", 
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to list issues: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ GitHub API error: {str(e)}")
            return []

class NotificationCenter:
    """Central notification management system"""
    
    def __init__(self):
        # Get the script directory and navigate to project root
        script_dir = Path(__file__).parent.absolute()
        self.base_dir = script_dir.parent
        
        # Handle different execution environments
        if not (self.base_dir / "source_data").exists():
            # Try alternative path resolution for CI/CD environments
            current_dir = Path.cwd()
            if (current_dir / "source_data").exists():
                self.base_dir = current_dir
            elif (current_dir.parent / "source_data").exists():
                self.base_dir = current_dir.parent
            else:
                # Check if we're in a CI/CD environment like /harness
                if str(current_dir).startswith('/harness'):
                    # In Harness CI/CD, try to find the project root
                    potential_roots = [
                        Path('/harness'),
                        Path('/harness/workspace'),
                        current_dir,
                        current_dir.parent
                    ]
                    for root in potential_roots:
                        if (root / "source_data").exists():
                            self.base_dir = root
                            break
                    else:
                        # Fallback: create directories relative to current location
                        self.base_dir = current_dir
                else:
                    # Fallback to relative path from notifications directory
                    self.base_dir = Path("..").absolute()
        
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        
        # Load configuration
        self.load_config()
        
        # Initialize integrations
        self.github = GitHubIntegration(
            repo_owner="dennislee928", 
            repo_name="personal-publicdata"
        )
        
        # Notification settings
        self.notification_settings = self.load_notification_settings()
    
    def load_config(self):
        """Load school and validation data"""
        # Load schools
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
        
        # Load validation results if available
        validation_file = self.output_dir / "validation_results.json"
        if validation_file.exists():
            with open(validation_file, 'r', encoding='utf-8') as f:
                self.validation_data = json.load(f)
        else:
            self.validation_data = {}
    
    def load_notification_settings(self) -> Dict[str, Any]:
        """Load notification preferences"""
        settings_file = self.base_dir / "notifications" / "settings.yml"
        
        default_settings = {
            'deadline_alerts': {
                'enabled': True,
                'urgent_threshold_days': 7,
                'warning_threshold_days': 30
            },
            'github_integration': {
                'enabled': True,
                'auto_create_issues': True,
                'labels': ['university-application', 'auto-generated']
            },
            'email_notifications': {
                'enabled': False,  # Requires setup
                'smtp_server': '',
                'smtp_port': 587,
                'sender_email': '',
                'recipient_email': 'admin@dennisleehappy.org'
            },
            'risk_alerts': {
                'enabled': True,
                'monitor_ielts_gaps': True,
                'monitor_budget_overruns': True,
                'monitor_missing_documents': True
            }
        }
        
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                user_settings = yaml.safe_load(f)
                # Merge with defaults
                for key, value in user_settings.items():
                    if key in default_settings:
                        default_settings[key].update(value)
                    else:
                        default_settings[key] = value
        
        return default_settings
    
    def check_deadline_alerts(self) -> List[Dict[str, Any]]:
        """Check for approaching deadlines and generate alerts"""
        alerts = []
        today = date.today()
        
        urgent_threshold = self.notification_settings['deadline_alerts']['urgent_threshold_days']
        warning_threshold = self.notification_settings['deadline_alerts']['warning_threshold_days']
        
        for school_id, school in self.schools.items():
            if school.get('status') != 'active':
                continue
            
            deadline_str = school.get('application_deadline', '')
            if not deadline_str:
                continue
            
            # Parse deadline (simplified - use validator's more robust version)
            deadline_date = self.parse_deadline(deadline_str)
            if not deadline_date:
                continue
            
            days_until = (deadline_date - today).days
            
            # Check application status
            app_status = school.get('application_status', 'NOT_STARTED')
            
            if days_until < 0 and app_status not in ['SUBMITTED', 'ACCEPTED', 'REJECTED']:
                alerts.append({
                    'type': 'DEADLINE_PASSED',
                    'severity': 'CRITICAL',
                    'school_id': school_id,
                    'school_name': school['full_name'],
                    'message': f"Application deadline has passed ({deadline_str})",
                    'days_until': days_until,
                    'suggested_action': 'Check if late applications are accepted or remove from active list'
                })
            
            elif 0 <= days_until <= urgent_threshold and app_status not in ['SUBMITTED', 'ACCEPTED', 'REJECTED']:
                alerts.append({
                    'type': 'DEADLINE_URGENT',
                    'severity': 'HIGH',
                    'school_id': school_id,
                    'school_name': school['full_name'],
                    'message': f"URGENT: Application due in {days_until} days",
                    'days_until': days_until,
                    'suggested_action': 'Prioritize completion and submission immediately'
                })
            
            elif urgent_threshold < days_until <= warning_threshold and app_status == 'NOT_STARTED':
                alerts.append({
                    'type': 'DEADLINE_UPCOMING',
                    'severity': 'MEDIUM',
                    'school_id': school_id,
                    'school_name': school['full_name'],
                    'message': f"Application due in {days_until} days, but not yet started",
                    'days_until': days_until,
                    'suggested_action': 'Begin application preparation'
                })
        
        return alerts
    
    def check_validation_alerts(self) -> List[Dict[str, Any]]:
        """Check validation results for issues requiring attention"""
        alerts = []
        
        if not self.validation_data:
            return alerts
        
        results = self.validation_data.get('results', {})
        
        for school_id, validation_result in results.items():
            school = self.schools.get(school_id, {})
            school_name = school.get('full_name', school_id)
            
            overall_status = validation_result.get('overall_status')
            validation_details = validation_result.get('validation_details', {})
            
            # IELTS issues
            if validation_details.get('ielts_status') in ['WARNING', 'INELIGIBLE']:
                severity = 'HIGH' if validation_details.get('ielts_status') == 'INELIGIBLE' else 'MEDIUM'
                alerts.append({
                    'type': 'IELTS_REQUIREMENT',
                    'severity': severity,
                    'school_id': school_id,
                    'school_name': school_name,
                    'message': 'IELTS requirements not met or borderline',
                    'suggested_action': 'Consider IELTS retake focusing on writing skills (target: 6.5)'
                })
            
            # Budget issues
            if validation_details.get('budget_status') in ['WARNING', 'INELIGIBLE']:
                severity = 'HIGH' if validation_details.get('budget_status') == 'INELIGIBLE' else 'MEDIUM'
                alerts.append({
                    'type': 'BUDGET_CONCERN',
                    'severity': severity,
                    'school_id': school_id,
                    'school_name': school_name,
                    'message': 'Tuition exceeds comfortable budget range',
                    'suggested_action': 'Research scholarship opportunities or adjust budget expectations'
                })
            
            # Low confidence in scraped data
            confidence_score = validation_result.get('confidence_score', 1.0)
            if confidence_score < 0.5:
                alerts.append({
                    'type': 'DATA_QUALITY',
                    'severity': 'LOW',
                    'school_id': school_id,
                    'school_name': school_name,
                    'message': f'Low confidence in scraped data ({confidence_score:.1%})',
                    'suggested_action': 'Manually verify requirements on school website'
                })
        
        return alerts
    
    def parse_deadline(self, deadline_str: str) -> Optional[date]:
        """Parse deadline string - simplified version"""
        import re
        
        if not deadline_str:
            return None
        
        # Try common patterns
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, deadline_str)
            if match:
                parts = [int(match.group(i)) for i in range(1, 4)]
                
                # Try different interpretations
                for year, month, day in [parts, [parts[2], parts[0], parts[1]], [parts[2], parts[1], parts[0]]]:
                    try:
                        if year < 100:
                            year += 2000
                        return date(year, month, day)
                    except ValueError:
                        continue
        
        return None
    
    def create_github_issues(self, alerts: List[Dict[str, Any]]) -> List[str]:
        """Create GitHub issues for alerts"""
        if not self.notification_settings['github_integration']['enabled']:
            return []
        
        created_issues = []
        existing_issues = self.github.list_issues(labels=['university-application'])
        
        # Extract titles of existing issues to avoid duplicates
        existing_titles = {issue['title'] for issue in existing_issues}
        
        for alert in alerts:
            # Generate issue title
            severity_prefix = {'CRITICAL': '🚨', 'HIGH': '⚠️', 'MEDIUM': '📋', 'LOW': '💡'}
            prefix = severity_prefix.get(alert['severity'], '📋')
            
            title = f"{prefix} {alert['school_name']}: {alert['message']}"
            
            # Skip if similar issue already exists
            if any(alert['school_name'] in existing_title and alert['type'] in existing_title 
                   for existing_title in existing_titles):
                continue
            
            # Generate issue body
            body_lines = [
                f"**School**: {alert['school_name']} ({alert['school_id']})",
                f"**Alert Type**: {alert['type']}",
                f"**Severity**: {alert['severity']}",
                "",
                f"**Issue**: {alert['message']}",
                "",
                f"**Suggested Action**: {alert['suggested_action']}",
                "",
                "---",
                "",
                "**Additional Information**:",
            ]
            
            # Add context-specific information
            if alert['type'].startswith('DEADLINE'):
                body_lines.extend([
                    f"- Days until deadline: {alert.get('days_until', 'Unknown')}",
                    f"- Current status: {self.schools[alert['school_id']].get('application_status', 'Unknown')}"
                ])
            
            if alert['type'] in ['IELTS_REQUIREMENT', 'BUDGET_CONCERN']:
                validation_result = self.validation_data.get('results', {}).get(alert['school_id'], {})
                validation_details = validation_result.get('validation_details', {})
                
                body_lines.extend([
                    f"- IELTS Status: {validation_details.get('ielts_status', 'Unknown')}",
                    f"- Budget Status: {validation_details.get('budget_status', 'Unknown')}",
                    f"- Overall Status: {validation_result.get('overall_status', 'Unknown')}"
                ])
            
            body_lines.extend([
                "",
                f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Application Alert System*"
            ])
            
            body = "\n".join(body_lines)
            
            # Create issue
            labels = self.notification_settings['github_integration']['labels'] + [
                alert['type'].lower().replace('_', '-'),
                alert['severity'].lower()
            ]
            
            issue_url = self.github.create_issue(title, body, labels)
            if issue_url:
                created_issues.append(issue_url)
        
        return created_issues
    
    def send_email_notification(self, subject: str, body: str) -> bool:
        """Send email notification"""
        email_config = self.notification_settings['email_notifications']
        
        if not email_config['enabled']:
            print(f"📧 Email notification (disabled): {subject}")
            return False
        
        if not all([email_config.get('smtp_server'), email_config.get('sender_email'), 
                   email_config.get('recipient_email')]):
            print("⚠️  Email configuration incomplete")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                if email_config.get('password'):
                    server.login(email_config['sender_email'], email_config['password'])
                
                text = msg.as_string()
                server.sendmail(email_config['sender_email'], email_config['recipient_email'], text)
            
            print(f"✅ Email sent: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Email failed: {str(e)}")
            return False
    
    def process_all_alerts(self) -> Dict[str, Any]:
        """Process all types of alerts and notifications"""
        print("[NOTIFY] Processing alerts and notifications...")
        
        # Collect all alerts
        deadline_alerts = self.check_deadline_alerts()
        validation_alerts = self.check_validation_alerts()
        
        all_alerts = deadline_alerts + validation_alerts
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        all_alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        # Create GitHub issues
        created_issues = []
        if self.notification_settings['github_integration']['auto_create_issues']:
            created_issues = self.create_github_issues(all_alerts)
        
        # Send summary email
        if all_alerts and self.notification_settings['email_notifications']['enabled']:
            subject = f"University Application Alerts - {len(all_alerts)} item(s)"
            body = self.generate_alert_summary(all_alerts)
            self.send_email_notification(subject, body)
        
        # Generate summary report
        summary = {
            'processed_at': datetime.now().isoformat(),
            'total_alerts': len(all_alerts),
            'alerts_by_severity': {},
            'alerts_by_type': {},
            'created_github_issues': len(created_issues),
            'github_issue_urls': created_issues
        }
        
        for alert in all_alerts:
            severity = alert['severity']
            alert_type = alert['type']
            
            summary['alerts_by_severity'][severity] = summary['alerts_by_severity'].get(severity, 0) + 1
            summary['alerts_by_type'][alert_type] = summary['alerts_by_type'].get(alert_type, 0) + 1
        
        # Save summary
        summary_file = self.output_dir / "alert_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"[SUMMARY] Alert summary saved to {summary_file}")
        
        return summary
    
    def generate_alert_summary(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate human-readable alert summary"""
        lines = [
            "University Application Alert Summary",
            "=" * 40,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Alerts: {len(alerts)}",
            ""
        ]
        
        # Group by severity
        by_severity = {}
        for alert in alerts:
            severity = alert['severity']
            by_severity.setdefault(severity, []).append(alert)
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            severity_alerts = by_severity.get(severity, [])
            if severity_alerts:
                lines.extend([
                    f"{severity} PRIORITY ({len(severity_alerts)} items):",
                    "-" * 30
                ])
                
                for alert in severity_alerts:
                    lines.append(f"• {alert['school_name']}: {alert['message']}")
                    lines.append(f"  Action: {alert['suggested_action']}")
                
                lines.append("")
        
        lines.extend([
            "Best regards,",
            "Application Alert System"
        ])
        
        return "\n".join(lines)

def main():
    """Main notification system execution"""
    notification_center = NotificationCenter()
    
    try:
        # Process all alerts
        summary = notification_center.process_all_alerts()
        
        # Print summary
        print(f"\n[SUMMARY] Alert Processing Summary:")
        print(f"   Total alerts: {summary['total_alerts']}")
        print(f"   GitHub issues created: {summary['created_github_issues']}")
        
        for severity, count in summary['alerts_by_severity'].items():
            print(f"   {severity}: {count}")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Alert processing failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
