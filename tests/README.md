# India Grants Oracle - Test Suite

This directory contains all test files for the India Grants Oracle system.

## Test Files Overview

### Core System Tests
- `test_api_simple.py` - Tests the Flask API endpoints
- `test_enhanced_system.py` - Tests the enhanced system functionality
- `test_simple_fixes.py` - Tests basic fixes and error handling
- `test_timeout_fixes.py` - Tests timeout and error recovery
- `test_fixes.py` - Tests various system fixes

### Database Tests
- `test_sqlite_setup.py` - Tests SQLite database setup
- `test_sqlite_simple.py` - Tests basic SQLite operations
- `test_sqlite_final.py` - Tests complete SQLite integration
- `simple_test.py` - Simple database connectivity test

### Multi-Model AI Tests
- `test_multi_model.py` - Tests multi-model orchestrator (OpenAI + Gemini)
- `test_multi_model_simple.py` - Simplified multi-model tests
- `test_multi_model_quick.py` - Quick multi-model setup tests
- `test_gemini_direct.py` - Direct Gemini client tests
- `test_gemini_fixed.py` - Tests the fixed Gemini client

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Specific Test Categories

#### Database Tests
```bash
python tests/test_sqlite_setup.py
python tests/test_sqlite_simple.py
python tests/test_sqlite_final.py
```

#### API Tests
```bash
python tests/test_api_simple.py
```

#### Multi-Model AI Tests
```bash
# Quick test (recommended)
python tests/test_multi_model_quick.py

# Full multi-model test
python tests/test_multi_model.py

# Gemini-specific tests
python tests/test_gemini_fixed.py
```

#### System Tests
```bash
python tests/test_enhanced_system.py
python tests/test_simple_fixes.py
python tests/test_timeout_fixes.py
```

## Test Categories

### 🔧 **Database Tests**
Test SQLite database operations and connectivity.

### 🤖 **AI Model Tests**
Test OpenAI and Gemini integration with automatic fallback.

### 🌐 **API Tests**
Test Flask API endpoints and responses.

### ⚡ **System Tests**
Test core system functionality, error handling, and timeouts.

## Environment Setup

Before running tests, ensure you have:

1. **Environment Variables**:
   ```bash
   # Required for AI tests
   OPENAI_API_KEY=your_openai_key
   GOOGLE_API_KEY=your_gemini_key
   
   # Optional for notifications
   SLACK_WEBHOOK_URL=your_slack_webhook
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   ```

2. **Dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Database**:
   ```bash
   # SQLite database will be created automatically
   python tests/test_sqlite_setup.py
   ```

## Test Results

### ✅ **Passing Tests**
- Database connectivity and operations
- API endpoint functionality
- Multi-model AI orchestrator
- Error handling and timeouts
- Rate limit handling

### ⚠️ **Known Issues**
- Some tests may timeout if API rate limits are hit
- Windows-specific asyncio warnings (non-critical)
- Deadline checking datetime issues (being fixed)

## Quick Test Commands

### Test Just the Multi-Model System
```bash
python tests/test_multi_model_quick.py
```

### Test Database Only
```bash
python tests/test_sqlite_simple.py
```

### Test API Only
```bash
python tests/test_api_simple.py
```

## Troubleshooting

### Rate Limit Issues
If tests fail due to rate limits:
1. Wait a few minutes between test runs
2. Use the quick tests instead of full tests
3. Check your API key quotas

### Import Errors
If you get import errors:
1. Ensure you're running from the project root
2. Check that all dependencies are installed
3. Verify Python path includes the `src` directory

### Timeout Issues
If tests timeout:
1. Check your internet connection
2. Verify API keys are valid
3. Try running individual tests instead of the full suite

## Adding New Tests

When adding new tests:

1. **Naming Convention**: Use `test_*.py` prefix
2. **Async Tests**: Use `async def main()` function
3. **Sync Tests**: Use `def main()` function
4. **Return Values**: Return `True` for pass, `False` for fail
5. **Documentation**: Add comments explaining what the test does

Example:
```python
async def main():
    """Test description"""
    try:
        # Test code here
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
``` 