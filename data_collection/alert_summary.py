#!/usr/bin/env python3
"""
Alert Summary Script
Safe script to parse and display alert results without indentation issues
"""

import json
import sys
from pathlib import Path

def print_alert_summary():
    """Print alert results summary safely"""
    try:
        # Find alert summary file
        base_dir = Path(__file__).parent.parent
        alert_file = base_dir / "final_applications" / "alert_summary.json"
        
        if not alert_file.exists():
            print("❌ Alert summary file not found")
            print(f"Expected location: {alert_file}")
            return 1
        
        # Load and parse JSON
        with open(alert_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Print summary
        print("📊 Alert Summary:")
        print(f"   Total alerts: {data.get('total_alerts', 0)}")
        print(f"   GitHub issues created: {data.get('created_github_issues', 0)}")
        
        # Show alerts by severity
        alerts_by_severity = data.get('alerts_by_severity', {})
        if alerts_by_severity:
            print("   Alerts by severity:")
            for severity, count in alerts_by_severity.items():
                icon = {
                    'high': '🔴',
                    'medium': '🟡', 
                    'low': '🟢',
                    'critical': '🚨'
                }.get(severity.lower(), '📌')
                print(f"     {icon} {severity.title()}: {count}")
        
        # Show recent alerts if available
        recent_alerts = data.get('recent_alerts', [])
        if recent_alerts:
            print(f"\n📋 Recent Alerts ({len(recent_alerts)}):")
            for i, alert in enumerate(recent_alerts[:3], 1):  # Show first 3
                print(f"   {i}. {alert.get('title', 'Unknown alert')}")
            if len(recent_alerts) > 3:
                print(f"   ... and {len(recent_alerts) - 3} more")
        
        print(f"\n🕐 Generated: {data.get('generated_at', 'N/A')}")
        
        return 0
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(print_alert_summary())
