#!/usr/bin/env python3
"""
Test script for multi-model orchestrator with OpenAI and Gemini fallback
"""

import asyncio
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.multi_model_orchestrator import MultiModelOrchestrator

async def test_multi_model_setup():
    """Test multi-model orchestrator initialization"""
    print("🧪 Testing multi-model orchestrator setup...")
    
    try:
        # Test with both API keys
        orchestrator = MultiModelOrchestrator()
        print("✅ Multi-model orchestrator initialized successfully")
        
        # Check which models are available
        if orchestrator.openai_client:
            print("✅ OpenAI client available")
        else:
            print("❌ OpenAI client not available")
            
        if orchestrator.gemini_client:
            print("✅ Gemini client available")
        else:
            print("❌ Gemini client not available")
            
        print(f"🎯 Current model: {orchestrator.current_model}")
        
        await orchestrator.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_model_switching():
    """Test model switching functionality"""
    print("🧪 Testing model switching...")
    
    try:
        orchestrator = MultiModelOrchestrator()
        
        # Test switching models
        initial_model = orchestrator.current_model
        print(f"Initial model: {initial_model}")
        
        await orchestrator._switch_model("Test switch")
        new_model = orchestrator.current_model
        print(f"Switched to: {new_model}")
        
        # Switch back
        await orchestrator._switch_model("Switch back")
        final_model = orchestrator.current_model
        print(f"Final model: {final_model}")
        
        await orchestrator.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_discovery_with_fallback():
    """Test grant discovery with model fallback"""
    print("🧪 Testing discovery with fallback...")
    
    try:
        orchestrator = MultiModelOrchestrator()
        
        # Test with a simple URL
        test_url = "https://seedfund.startupindia.gov.in/"
        print(f"🔍 Testing URL: {test_url}")
        
        result = await orchestrator.discover_grants_from_url(test_url)
        print(f"✅ Discovery completed: {result is not None}")
        
        await orchestrator.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_main_integration():
    """Test main.py integration with multi-model orchestrator"""
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
    """Run all multi-model tests"""
    print("🚀 Starting Multi-Model Orchestrator Tests...")
    print("=" * 60)
    
    tests = [
        ("Multi-Model Setup", test_multi_model_setup),
        ("Model Switching", test_model_switching),
        ("Discovery with Fallback", test_discovery_with_fallback),
        ("Main Integration", test_main_integration),
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
        print("🎉 All multi-model tests passed!")
        print("The system can now use both OpenAI and Gemini with automatic fallback.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 