# Gemini 2.5 Pro Setup Guide

This guide helps you set up Gemini 2.5 Pro as a fallback model to avoid OpenAI rate limits.

## Why Use Gemini?

- **Rate Limit Relief**: When OpenAI hits rate limits, Gemini can take over
- **Cost Optimization**: Gemini can be more cost-effective for certain tasks
- **Redundancy**: Ensures your system keeps working even if one API is down
- **Performance**: Gemini 2.5 Pro is very capable for grant discovery tasks

## Setup Steps

### 1. Get Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key" in the top right
4. Create a new API key or use an existing one
5. Copy the API key

### 2. Install Dependencies

```bash
pip install google-generativeai==0.3.2
```

### 3. Set Environment Variables

Add to your `.env` file:

```env
# OpenAI (primary)
OPENAI_API_KEY=your_openai_key_here

# Google Gemini (fallback)
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Test the Setup

Run the simple test to verify both models work:

```bash
python test_multi_model_simple.py
```

You should see output like:
```
✅ OpenAI client available
✅ Gemini client available
🎯 Using OpenAI as primary model
```

## How It Works

### Automatic Fallback

The system will automatically switch between models:

1. **Primary**: Uses OpenAI GPT-4o-mini for most tasks
2. **Fallback**: Switches to Gemini 2.5 Pro when:
   - OpenAI hits rate limits
   - OpenAI API is down
   - OpenAI returns errors

### Model Switching Logic

```python
# When rate limit is hit
if "rate limit" in error_msg:
    await orchestrator._switch_model("Rate limit hit")
    # Retry with Gemini
```

### Rate Limiting

- **OpenAI**: 3 requests per minute (conservative)
- **Gemini**: 15 requests per minute (more generous)
- **Automatic delays**: 2-5 seconds between requests

## Configuration Options

### Model Preferences

You can set preferred models in the orchestrator:

```python
# Prefer Gemini for certain tasks
result = await orchestrator.discover_grants_from_url(
    url, 
    preferred_model="gemini"
)
```

### Timeout Settings

Adjust timeouts in `src/agents/multi_model_orchestrator.py`:

```python
# Discovery timeout (default: 60 seconds)
async with asyncio.timeout(60):
    result = await orchestrator.discover_grants_from_url(url)

# Team creation timeout (default: 30 seconds)
async with asyncio.timeout(30):
    team = await orchestrator._create_fresh_team(['coder'])
```

## Cost Comparison

| Model | Input Cost | Output Cost | Rate Limit |
|-------|------------|-------------|------------|
| GPT-4o-mini | $0.15/1M tokens | $0.60/1M tokens | 3 req/min |
| Gemini 2.5 Pro | $0.075/1M tokens | $0.30/1M tokens | 15 req/min |

## Troubleshooting

### Gemini Not Available

If you see "⚠️ Gemini not available":

1. Check if `google-generativeai` is installed:
   ```bash
   pip install google-generativeai==0.3.2
   ```

2. Verify your API key:
   ```bash
   echo $GOOGLE_API_KEY
   ```

3. Test the API key manually:
   ```python
   import google.generativeai as genai
   genai.configure(api_key="your_key")
   model = genai.GenerativeModel('gemini-2.0-flash-exp')
   response = model.generate_content("Hello")
   print(response.text)
   ```

### Rate Limit Issues

If you're still hitting rate limits:

1. Increase delays between requests:
   ```python
   self.min_call_interval = 5.0  # 5 seconds between calls
   ```

2. Use more conservative limits:
   ```python
   # In main.py
   await asyncio.sleep(10)  # 10 seconds between URLs
   ```

3. Monitor usage in Google AI Studio dashboard

## Production Deployment

For production, consider:

1. **Environment Variables**: Set both API keys in your deployment environment
2. **Monitoring**: Add logging to track which model is being used
3. **Cost Tracking**: Monitor usage in both OpenAI and Google dashboards
4. **Fallback Strategy**: Test both models regularly

## Example Usage

```python
from agents.multi_model_orchestrator import MultiModelOrchestrator

# Initialize with both models
orchestrator = MultiModelOrchestrator()

# Discover grants (will use best available model)
grants = await orchestrator.discover_grants_from_url(
    "https://seedfund.startupindia.gov.in/"
)

# Clean up
await orchestrator.close()
```

The system will automatically handle model switching and rate limiting for you! 