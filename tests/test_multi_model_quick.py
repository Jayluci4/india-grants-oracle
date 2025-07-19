#!/usr/bin/env python3
"""
Quick test for multi-model orchestrator - no discovery, just setup verification
"""

import asyncio
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_quick_setup():
    """Quick test of multi-model setup without discovery"""
    print("🧪 Quick multi-model setup test...")
    
    try:
        from agents.multi_model_orchestrator import MultiModelOrchestrator
        
        # Initialize orchestrator
        orchestrator = MultiModelOrchestrator()
        print("✅ Multi-model orchestrator initialized")
        
        # Check available models
        print(f"🎯 Current model: {orchestrator.current_model}")
        print(f"OpenAI available: {orchestrator.openai_client is not None}")
        print(f"Gemini available: {orchestrator.gemini_client is not None}")
        
        # Test model switching
        initial_model = orchestrator.current_model
        await orchestrator._switch_model("Quick test")
        new_model = orchestrator.current_model
        print(f"🔄 Model switching: {initial_model} -> {new_model}")
        
        # Test team creation (without discovery)
        print("🧪 Testing team creation...")
        team = await orchestrator._create_fresh_team(['coder'])
        if team:
            print("✅ Team created successfully")
            await orchestrator._cleanup_team(team)
            print("✅ Team cleaned up")
        else:
            print("❌ Team creation failed")
        
        # Clean up
        await orchestrator.close()
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

async def test_gemini_only():
    """Test Gemini client directly"""
    print("🧪 Testing Gemini client directly...")
    
    try:
        from agents.gemini_client import GeminiChatCompletionClient
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not set")
            return False
        
        client = GeminiChatCompletionClient(api_key=api_key)
        print("✅ Gemini client created")
        
        # Quick test without discovery
        messages = [
            {'role': 'user', 'content': 'Say "Gemini is working" in one sentence.'}
        ]
        
        response = await client.create(messages)
        content = response['choices'][0]['message']['content']
        print(f"✅ Gemini response: {content}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

async def main():
    """Run quick tests"""
    print("🚀 Quick Multi-Model Tests...")
    print("=" * 40)
    
    tests = [
        ("Quick Setup", test_quick_setup),
        ("Gemini Direct", test_gemini_only),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 25)
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 Quick Test Results:")
    print("=" * 40)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 Quick tests passed!")
        print("Multi-model system is ready to use.")
    else:
        print("⚠️  Some tests failed.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 