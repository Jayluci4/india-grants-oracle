#!/usr/bin/env python3
"""
Direct test for Gemini client
"""

import asyncio
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_gemini_import():
    """Test if Gemini can be imported"""
    print("🧪 Testing Gemini import...")
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
        return True
    except ImportError as e:
        print(f"❌ google.generativeai import failed: {e}")
        return False

async def test_gemini_client():
    """Test our custom Gemini client"""
    print("🧪 Testing custom Gemini client...")
    
    try:
        from agents.gemini_client import GeminiChatCompletionClient
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not set")
            return False
        
        client = GeminiChatCompletionClient(api_key=api_key)
        print("✅ Gemini client created")
        
        # Test simple completion
        messages = [
            {'role': 'user', 'content': 'Say hello in one sentence.'}
        ]
        
        response = await client.create(messages)
        content = response['choices'][0]['message']['content']
        print(f"✅ Gemini response: {content}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Gemini client test failed: {e}")
        return False

async def test_multi_model_gemini():
    """Test multi-model orchestrator with Gemini"""
    print("🧪 Testing multi-model orchestrator with Gemini...")
    
    try:
        from agents.multi_model_orchestrator import MultiModelOrchestrator
        
        orchestrator = MultiModelOrchestrator()
        
        # Check if Gemini is available
        if orchestrator.gemini_client:
            print("✅ Gemini client available in orchestrator")
            print(f"🎯 Current model: {orchestrator.current_model}")
            
            # Test model switching
            await orchestrator._switch_model("Test")
            print(f"🔄 Switched to: {orchestrator.current_model}")
            
        else:
            print("❌ Gemini client not available in orchestrator")
            return False
        
        await orchestrator.close()
        return True
        
    except Exception as e:
        print(f"❌ Multi-model test failed: {e}")
        return False

async def main():
    """Run all Gemini tests"""
    print("🚀 Starting Gemini Tests...")
    print("=" * 50)
    
    tests = [
        ("Gemini Import", test_gemini_import),
        ("Gemini Client", test_gemini_client),
        ("Multi-Model Integration", test_multi_model_gemini),
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
        print("🎉 All Gemini tests passed!")
        print("Gemini is now working with the multi-model system.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        print("\n💡 To fix Gemini issues:")
        print("1. Install: pip install google-generativeai==0.3.2")
        print("2. Set GOOGLE_API_KEY in your environment")
        print("3. Get API key from: https://aistudio.google.com/")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 