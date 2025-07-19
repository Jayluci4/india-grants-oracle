#!/usr/bin/env python3
"""
Test script to verify timeout and error handling fixes
"""

import asyncio
import os
import sys
import time

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.magentic_one_orchestrator import GrantOracleOrchestrator

async def test_timeout_handling():
    """Test timeout handling in the orchestrator"""
    print("🧪 Testing timeout handling...")
    
    try:
        # Initialize orchestrator
        orchestrator = GrantOracleOrchestrator()
        print("✅ Orchestrator initialized successfully")
        
        # Test with a URL that might timeout
        test_url = "https://seedfund.startupindia.gov.in/"
        print(f"🔍 Testing URL with timeout: {test_url}")
        
        # This should complete within the timeout
        result = await orchestrator.discover_grants_from_url(test_url)
        print(f"✅ Discovery completed: {result is not None}")
        
        # Don't close here - let the main test handle cleanup
        print("✅ Timeout handling test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

async def test_error_recovery():
    """Test error recovery mechanisms"""
    print("🧪 Testing error recovery...")
    
    try:
        from main import GrantOracleMain
        
        oracle = GrantOracleMain()
        
        # Test the discovery with error handling
        await oracle.run_magentic_discovery()
        print("✅ Error recovery test completed")
        
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        return False
    
    return True

async def test_resource_cleanup():
    """Test resource cleanup"""
    print("🧪 Testing resource cleanup...")
    
    try:
        orchestrator = GrantOracleOrchestrator()
        
        # Create multiple teams to test cleanup
        for i in range(3):
            team = await orchestrator._create_fresh_team(['coder'])
            if team:
                print(f"✅ Created team {i+1}")
                await orchestrator._cleanup_team(team)
                print(f"✅ Cleaned up team {i+1}")
        
        await orchestrator.close()
        print("✅ Resource cleanup test completed")
        
    except Exception as e:
        print(f"❌ Resource cleanup test failed: {e}")
        return False
    
    return True

async def main():
    """Run all timeout and error handling tests"""
    print("🚀 Starting Timeout and Error Handling Tests...")
    print("=" * 60)
    
    tests = [
        ("Timeout Handling", test_timeout_handling),
        ("Error Recovery", test_error_recovery),
        ("Resource Cleanup", test_resource_cleanup),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All timeout and error handling tests passed!")
        print("The system should now handle timeouts and errors gracefully.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 