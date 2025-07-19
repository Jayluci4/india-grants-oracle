#!/usr/bin/env python3
"""
Test runner for all India Grants Oracle tests
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n🧪 Running: {test_file}")
    print("-" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ PASS")
            return True
        else:
            print("❌ FAIL")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def run_async_test_file(test_file):
    """Run an async test file"""
    print(f"\n🧪 Running: {test_file}")
    print("-" * 50)
    
    try:
        # Import and run the test
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'main'):
            result = await module.main()
            if result:
                print("✅ PASS")
                return True
            else:
                print("❌ FAIL")
                return False
        else:
            print("❌ No main() function found")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 India Grants Oracle - Test Suite")
    print("=" * 60)
    
    # Get all test files
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob("test_*.py"))
    test_files.sort()
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    
    print("\n" + "=" * 60)
    
    results = []
    
    for test_file in test_files:
        # Skip this runner script
        if test_file.name == "run_all_tests.py":
            continue
            
        try:
            # Check if it's an async test
            with open(test_file, 'r') as f:
                content = f.read()
                is_async = 'async def main()' in content or 'asyncio.run(' in content
            
            if is_async:
                # For async tests, we'll run them with subprocess for now
                result = run_test_file(str(test_file))
            else:
                result = run_test_file(str(test_file))
                
            results.append((test_file.name, result))
            
        except Exception as e:
            print(f"❌ Failed to run {test_file.name}: {e}")
            results.append((test_file.name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 