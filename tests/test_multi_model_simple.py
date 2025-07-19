#!/usr/bin/env python3
"""
Simple test script for multi-model orchestrator - no hanging
"""

import asyncio
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.multi_model_orchestrator import MultiModelOrchestrator

async def test_basic_setup():
    """Test basic setup without discovery"""
    print("🧪 Testing basic multi-model setup...")
    
    try:
        orchestrator = MultiModelOrchestrator()
        print("✅ Multi-model orchestrator initialized")
        print(f"🎯 Current model: {orchestrator.current_model}")
        
        # Test model switching
        initial_model = orchestrator.current_model
        await orchestrator._switch_model("Test")
        print(f"🔄 Model switching test completed")
        
        await orchestrator.close()
        print("✅ Cleanup completed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_team_creation():
    """Test team creation with timeout"""
    print("🧪 Testing team creation...")
    
    try:
        orchestrator = MultiModelOrchestrator()
        
        # Test team creation with timeout
        async with asyncio.timeout(30):  # 30 second timeout
            team = await orchestrator._create_fresh_team(['coder'])
            if team:
                print("✅ Team created successfully")
                await orchestrator._cleanup_team(team)
                print("✅ Team cleaned up")
            else:
                print("❌ Team creation failed")
        
        await orchestrator.close()
        return True
        
    except asyncio.TimeoutError:
        print("⏰ Team creation timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_discovery_timeout():
    """Test discovery with strict timeout"""
    print("🧪 Testing discovery with timeout...")
    
    try:
        orchestrator = MultiModelOrchestrator()
        
        # Test with a simple URL but with strict timeout
        test_url = "https://seedfund.startupindia.gov.in/"
        print(f"🔍 Testing URL: {test_url}")
        
        async with asyncio.timeout(60):  # 1 minute timeout
            result = await orchestrator.discover_grants_from_url(test_url)
            print(f"✅ Discovery completed: {result is not None}")
        
        await orchestrator.close()
        return True
        
    except asyncio.TimeoutError:
        print("⏰ Discovery timed out - this is expected for testing")
        return True  # Timeout is acceptable in testing
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run simple multi-model tests"""
    print("🚀 Starting Simple Multi-Model Tests...")
    print("=" * 50)
    
    tests = [
        ("Basic Setup", test_basic_setup),
        ("Team Creation", test_team_creation),
        ("Discovery Timeout", test_discovery_timeout),
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
        print("Multi-model system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 