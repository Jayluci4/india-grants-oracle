#!/usr/bin/env python3
"""
Test the fixed Gemini client
"""

import asyncio
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_gemini_client():
    """Test the fixed Gemini client"""
    print("🧪 Testing fixed Gemini client...")
    
    try:
        from agents.gemini_client import GeminiChatCompletionClient
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not set")
            return False
        
        client = GeminiChatCompletionClient(api_key=api_key)
        print("✅ Gemini client created")
        
        # Check model info
        print(f"Model name: {client.get_model_name()}")
        print(f"Model info: {client.get_model_info()}")
        
        # Test simple completion
        messages = [
            {'role': 'user', 'content': 'Say "Gemini is working" in one sentence.'}
        ]
        
        response = await client.create(messages)
        content = response['choices'][0]['message']['content']
        print(f"✅ Gemini response: {content}")
        
        await client.close()
        print("✅ Gemini client closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multi_model_with_fixed_gemini():
    """Test multi-model orchestrator with fixed Gemini"""
    print("🧪 Testing multi-model with fixed Gemini...")
    
    try:
        from agents.multi_model_orchestrator import MultiModelOrchestrator
        
        orchestrator = MultiModelOrchestrator()
        print("✅ Multi-model orchestrator initialized")
        
        # Check models
        print(f"OpenAI available: {orchestrator.openai_client is not None}")
        print(f"Gemini available: {orchestrator.gemini_client is not None}")
        print(f"Current model: {orchestrator.current_model}")
        
        # Test team creation
        team = await orchestrator._create_fresh_team(['coder'])
        if team:
            print("✅ Team created successfully")
            await orchestrator._cleanup_team(team)
            print("✅ Team cleaned up")
        else:
            print("❌ Team creation failed")
        
        await orchestrator.close()
        return True
        
    except Exception as e:
        print(f"❌ Multi-model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run tests"""
    print("🚀 Testing Fixed Gemini Client...")
    print("=" * 50)
    
    tests = [
        ("Gemini Client", test_gemini_client),
        ("Multi-Model Integration", test_multi_model_with_fixed_gemini),
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
        print("🎉 All tests passed!")
        print("Gemini client is now working correctly.")
    else:
        print("⚠️  Some tests failed.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 