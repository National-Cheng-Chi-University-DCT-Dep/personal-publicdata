#!/usr/bin/env python3
"""
Robust path resolver for different execution environments
"""

import os
from pathlib import Path

def resolve_project_paths():
    """
    Resolve project paths in different execution environments
    Returns: (base_dir, source_data_dir, output_dir)
    """
    
    # Get current script location
    script_file = Path(__file__).absolute()
    script_dir = script_file.parent
    current_dir = Path.cwd()
    
    print(f"[PATH_RESOLVER] Script: {script_file}")
    print(f"[PATH_RESOLVER] Script dir: {script_dir}")
    print(f"[PATH_RESOLVER] Current dir: {current_dir}")
    
    # Strategy 1: Standard project structure (script in notifications/)
    base_dir = script_dir.parent
    if (base_dir / "source_data").exists():
        print(f"[PATH_RESOLVER] Found standard structure at: {base_dir}")
        return base_dir, base_dir / "source_data", base_dir / "final_applications"
    
    # Strategy 2: Check current working directory
    if (current_dir / "source_data").exists():
        print(f"[PATH_RESOLVER] Found project in current dir: {current_dir}")
        return current_dir, current_dir / "source_data", current_dir / "final_applications"
    
    # Strategy 3: Check parent of current directory
    if (current_dir.parent / "source_data").exists():
        print(f"[PATH_RESOLVER] Found project in parent dir: {current_dir.parent}")
        return current_dir.parent, current_dir.parent / "source_data", current_dir.parent / "final_applications"
    
    # Strategy 4: CI/CD environment handling
    if str(current_dir).startswith('/harness') or os.environ.get('HARNESS_BUILD_ID'):
        print(f"[PATH_RESOLVER] Detected CI/CD environment")
        
        # In CI/CD, files might be in various locations
        potential_bases = [
            current_dir,
            Path('/harness'),
            Path('/harness/workspace'),
            script_dir.parent,
            current_dir.parent
        ]
        
        for base in potential_bases:
            print(f"[PATH_RESOLVER] Checking CI/CD base: {base}")
            if base.exists() and (base / "source_data").exists():
                print(f"[PATH_RESOLVER] Found CI/CD project at: {base}")
                return base, base / "source_data", base / "final_applications"
        
        # If no source_data found in CI/CD, use current directory as base
        # and create necessary structure
        print(f"[PATH_RESOLVER] Using CI/CD fallback: {current_dir}")
        output_dir = current_dir / "final_applications"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a minimal source_data structure if needed
        source_dir = current_dir / "source_data"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        return current_dir, source_dir, output_dir
    
    # Strategy 5: Final fallback
    print(f"[PATH_RESOLVER] Using final fallback: {script_dir.parent}")
    base_dir = script_dir.parent
    output_dir = base_dir / "final_applications"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return base_dir, base_dir / "source_data", output_dir

if __name__ == "__main__":
    base, source, output = resolve_project_paths()
    print(f"Base directory: {base}")
    print(f"Source data directory: {source}")
    print(f"Output directory: {output}")
    print(f"Output directory exists: {output.exists()}")
