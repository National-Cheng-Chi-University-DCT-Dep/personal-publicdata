#!/usr/bin/env python3
"""
Academic Intelligence Summary Script
Safe script to parse and display academic intelligence results without indentation issues
"""

import json
import sys
from pathlib import Path

def print_academic_summary():
    """Print academic intelligence results summary safely"""
    try:
        # Find academic intelligence results file
        base_dir = Path(__file__).parent.parent
        academic_file = base_dir / "final_applications" / "academic_intelligence.json"
        
        if not academic_file.exists():
            print("❌ Academic intelligence results file not found")
            print(f"Expected location: {academic_file}")
            return 1
        
        # Load and parse JSON
        with open(academic_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract summary information
        summary = data.get('summary', {})
        
        # Print summary
        print("📊 Academic Intelligence Summary:")
        print(f"   Schools: {summary.get('total_schools', 0)}")
        print(f"   Professors: {summary.get('total_professors', 0)}")
        print(f"   Publications: {summary.get('total_publications', 0)}")
        print(f"   GitHub Repos: {summary.get('total_repositories', 0)}")
        
        # Show action items if available
        action_items = data.get('action_items', [])
        if action_items:
            print(f"\n📋 Action Items: {len(action_items)}")
            for i, item in enumerate(action_items[:3], 1):  # Show first 3
                print(f"   {i}. {item}")
            if len(action_items) > 3:
                print(f"   ... and {len(action_items) - 3} more")
        
        print(f"\n🕐 Generated: {data.get('generated_at', 'N/A')}")
        
        return 0
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(print_academic_summary())
