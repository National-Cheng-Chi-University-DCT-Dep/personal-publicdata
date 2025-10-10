#!/usr/bin/env python3
"""
Extract priority schools from validation results
"""

import json
import sys
from pathlib import Path

def extract_priority_schools():
    """Extract schools with ELIGIBLE or WARNING status"""
    try:
        results_file = Path('../final_applications/validation_results.json')
        
        if not results_file.exists():
            print("[INFO] Validation results not found, using all active schools")
            with open('priority_schools.txt', 'w') as f:
                f.write('all')
            return
        
        # Load validation results
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results = data.get('results', {})
        
        # Extract priority schools
        priority_schools = [
            school_id for school_id, result in results.items()
            if result.get('overall_status') in ['ELIGIBLE', 'WARNING']
        ]
        
        if priority_schools:
            print('[INFO] Priority schools for document generation:')
            for school in priority_schools:
                print(f'  - {school}')
            
            # Save to file
            with open('priority_schools.txt', 'w') as f:
                f.write(' '.join(priority_schools))
            
            print(f'[SUCCESS] Found {len(priority_schools)} priority schools')
        else:
            print('[INFO] No priority schools found, using all active schools')
            with open('priority_schools.txt', 'w') as f:
                f.write('all')
        
    except Exception as e:
        print(f'[ERROR] Failed to extract priority schools: {e}')
        print('[INFO] Falling back to all active schools')
        with open('priority_schools.txt', 'w') as f:
            f.write('all')

if __name__ == "__main__":
    extract_priority_schools()

