#!/usr/bin/env python3
"""
Validation Results Summary Script
Safe script to parse and display validation results without indentation issues
"""

import json
import sys
from pathlib import Path

def print_validation_summary():
    """Print validation results summary safely"""
    try:
        # Find validation results file
        base_dir = Path(__file__).parent.parent
        validation_file = base_dir / "final_applications" / "validation_results.json"
        
        if not validation_file.exists():
            print("❌ Validation results file not found")
            print(f"Expected location: {validation_file}")
            return 1
        
        # Load and parse JSON
        with open(validation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract summary information
        results = data.get('results', {})
        profile = data.get('profile_summary', {})
        
        # Print summary
        print("📊 Validation Summary:")
        print(f"   IELTS Overall: {profile.get('ielts_overall', 'N/A')}")
        print(f"   IELTS Writing: {profile.get('ielts_writing', 'N/A')}")
        print(f"   Budget: €{profile.get('budget_eur', 'N/A'):,}")
        print()
        
        # Count statuses
        status_counts = {}
        for school_id, result in results.items():
            status = result.get('overall_status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("📈 School Status Distribution:")
        for status, count in status_counts.items():
            icon = {
                'ELIGIBLE': '✅',
                'WARNING': '⚠️',
                'INELIGIBLE': '❌',
                'NEEDS_REVIEW': '🔍'
            }.get(status, '❓')
            print(f"   {icon} {status}: {count}")
        
        print(f"\n📊 Total Schools: {len(results)}")
        print(f"🕐 Generated: {data.get('generated_at', 'N/A')}")
        
        return 0
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(print_validation_summary())
