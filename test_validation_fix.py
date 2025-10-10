#!/usr/bin/env python3
"""
Test script to verify the validation IndentationError fix
"""

import os
import sys
import json
from pathlib import Path

def test_validation_summary():
    """Test the validation summary functionality"""
    print("🧪 Testing validation summary fix...")
    
    try:
        # Import the validation summary module
        sys.path.append(str(Path(__file__).parent / "data_collection"))
        from validation_summary import print_validation_summary
        
        # Test the function
        result = print_validation_summary()
        
        if result == 0:
            print("✅ Validation summary test passed")
            return True
        else:
            print(f"❌ Validation summary test failed with code {result}")
            return False
            
    except Exception as e:
        print(f"❌ Validation summary test error: {e}")
        return False

def test_validator_import():
    """Test that the validator can be imported without errors"""
    print("🧪 Testing validator import...")
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from data_collection.validator import ApplicationValidator
        
        # Try to create an instance
        validator = ApplicationValidator()
        print("✅ Validator import test passed")
        return True
        
    except Exception as e:
        print(f"❌ Validator import test error: {e}")
        return False

def test_master_controller_import():
    """Test that the master controller can be imported without errors"""
    print("🧪 Testing master controller import...")
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from build_scripts.master_controller import ApplicationIntelligenceSystem
        
        # Try to create an instance
        system = ApplicationIntelligenceSystem()
        print("✅ Master controller import test passed")
        return True
        
    except Exception as e:
        print(f"❌ Master controller import test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Running validation fix tests...")
    print("=" * 50)
    
    tests = [
        test_validation_summary,
        test_validator_import,
        test_master_controller_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The IndentationError fix is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
