#!/usr/bin/env python3
"""
Simple test to verify the basic fixes work without client closure issues
"""

import asyncio
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.magentic_one_orchestrator import GrantOracleOrchestrator

async def test_basic_orchestrator():
    """Test basic orchestrator functionality"""
    print("🧪 Testing basic orchestrator...")
    
    try:
        # Initialize orchestrator
        orchestrator = GrantOracleOrchestrator()
        print("✅ Orchestrator initialized successfully")
        
        # Test team creation
        team = await orchestrator._create_fresh_team(['coder'])
        if team:
            print("✅ Team creation successful")
            await orchestrator._cleanup_team(team)
            print("✅ Team cleanup successful")
        else:
            print("❌ Team creation failed")
            return False
        
        # Test client recreation
        await orchestrator._ensure_client_available()
        print("✅ Client availability check successful")
        
        await orchestrator.close()
        print("✅ Orchestrator closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_main_integration():
    """Test main.py integration without full discovery"""
    print("🧪 Testing main integration...")
    
    try:
        from main import GrantOracleMain
        
        oracle = GrantOracleMain()
        print("✅ GrantOracleMain initialized successfully")
        
        # Test database connection
        grants = oracle.db_manager.get_grants(filters={'status': 'live'}, limit=5)
        print(f"✅ Database connection working - {len(grants)} grants found")
        
        # Test deadline checking
        oracle.check_deadlines()
        print("✅ Deadline checking completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run simple tests"""
    print("🚀 Starting Simple Fix Tests...")
    print("=" * 50)
    
    tests = [
        ("Basic Orchestrator", test_basic_orchestrator),
        ("Main Integration", test_main_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = await test_func()
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
        print("🎉 All simple tests passed!")
        print("The basic fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 