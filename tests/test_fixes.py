#!/usr/bin/env python3
"""
Test script to verify the fixes for the India Grants Oracle
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.models import DatabaseManager
from agents.magentic_one_orchestrator import GrantOracleOrchestrator

async def test_magentic_orchestrator():
    """Test the fixed Magentic-One orchestrator"""
    print("🧪 Testing Magentic-One orchestrator fixes...")
    
    try:
        # Initialize orchestrator
        orchestrator = GrantOracleOrchestrator()
        print("✅ Orchestrator initialized successfully")
        
        # Test with a single URL
        test_url = "https://seedfund.startupindia.gov.in/"
        print(f"🔍 Testing URL: {test_url}")
        
        result = await orchestrator.discover_grants_from_url(test_url)
        print(f"✅ Discovery completed: {result is not None}")
        
        await orchestrator.close()
        print("✅ Orchestrator closed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def test_deadline_check():
    """Test the fixed deadline checking"""
    print("🧪 Testing deadline checking fixes...")
    
    try:
        from main import GrantOracleMain
        
        oracle = GrantOracleMain()
        
        # Test deadline check
        oracle.check_deadlines()
        print("✅ Deadline check completed without errors")
        
    except Exception as e:
        print(f"❌ Deadline check failed: {e}")
        return False
    
    return True

def test_database_operations():
    """Test database operations"""
    print("🧪 Testing database operations...")
    
    try:
        db_manager = DatabaseManager()
        
        # Test getting grants
        grants = db_manager.get_grants(filters={'status': 'live'}, limit=5)
        print(f"✅ Database query successful: {len(grants)} grants found")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting India Grants Oracle Fix Tests...")
    print("=" * 50)
    
    tests = [
        ("Database Operations", test_database_operations),
        ("Deadline Check", test_deadline_check),
        ("Magentic-One Orchestrator", test_magentic_orchestrator),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results.append((test_name, result))
            
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 