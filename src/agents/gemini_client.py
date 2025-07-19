#!/usr/bin/env python3
"""
Direct Gemini client for autogen framework
"""

import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, Optional
import google.generativeai as genai
class GeminiChatCompletionClient:
    """Direct Gemini client for autogen framework"""
    
    def __init__(self, model="gemini-2.0-flash-exp", api_key=None, timeout=60.0):
        self.model_name = model
        self.api_key = api_key
        self.timeout = timeout
        self._configured = False
        
        # Add model_info attribute that autogen expects
        self.model_info = {
            "model": model,
            "max_tokens": 4096,
            "temperature": 0.1,
            "top_p": 1.0,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        if api_key:
            self._configure()
    
    def _configure(self):
        """Configure Gemini client"""
        try:
            genai.configure(api_key=self.api_key)
            self._configured = True
            print(f"✅ Gemini client configured with model: {self.model_name}")
        except Exception as e:
            print(f"❌ Gemini configuration failed: {e}")
            self._configured = False
    
    async def create(self, messages, **kwargs):
        """Create a chat completion with Gemini"""
        if not self._configured:
            raise ValueError("Gemini client not configured. Check API key.")
        
        try:
            # Convert autogen messages to Gemini format
            gemini_messages = self._convert_messages(messages)
            
            # Create Gemini model
            model = genai.GenerativeModel(self.model_name)
            
            # Generate content
            response = await asyncio.to_thread(
                model.generate_content,
                gemini_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 4096),
                )
            )
            
            # Convert response to autogen format
            return self._convert_response(response)
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            raise
    
    def _convert_messages(self, messages):
        """Convert autogen messages to Gemini format"""
        gemini_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                # Gemini doesn't have system messages, prepend to user message
                if gemini_messages and gemini_messages[-1]['role'] == 'user':
                    gemini_messages[-1]['parts'] = [content + '\n\n' + gemini_messages[-1]['parts'][0]]
                else:
                    gemini_messages.append({
                        'role': 'user',
                        'parts': [content]
                    })
            elif role in ['user', 'assistant']:
                gemini_messages.append({
                    'role': role,
                    'parts': [content]
                })
        
        return gemini_messages
    
    def _convert_response(self, response):
        """Convert Gemini response to autogen format"""
        try:
            content = response.text
        except AttributeError:
            content = str(response)
        
        return {
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': content
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': 0,  # Gemini doesn't provide token counts
                'completion_tokens': 0,
                'total_tokens': 0
            }
        }
    
    async def close(self):
        """Close the client"""
        # Gemini client doesn't need explicit closing
        pass
    
    def get_model_info(self):
        """Get model information"""
        return self.model_info
    
    def get_model_name(self):
        """Get the model name"""
        return self.model_name

# Test function
async def test_gemini_client():
    """Test the Gemini client"""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not set")
            return False
        
        client = GeminiChatCompletionClient(api_key=api_key)
        
        # Test simple completion
        messages = [
            {'role': 'user', 'content': 'Hello, how are you?'}
        ]
        
        response = await client.create(messages)
        print(f"✅ Gemini test successful: {response['choices'][0]['message']['content'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

if __name__ == "__main__":
    import os
    asyncio.run(test_gemini_client()) 