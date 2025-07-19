#!/usr/bin/env python3
"""
Multi-Model Orchestrator for India Grants Oracle
Supports both OpenAI and Gemini models with automatic fallback
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.teams.magentic_one import MagenticOne
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_ext.agents.file_surfer import FileSurfer
from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.teams import MagenticOneGroupChat

# Try to import Gemini client
try:
    import google.generativeai as genai
    from agents.gemini_client import GeminiChatCompletionClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini not available - install google-generativeai")

class MultiModelOrchestrator:
    """Multi-model orchestrator with OpenAI and Gemini fallback"""
    
    def __init__(self, openai_api_key=None, gemini_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = gemini_api_key or os.getenv('GOOGLE_API_KEY')
        
        # Initialize model clients
        self.openai_client = None
        self.gemini_client = None
        self.current_model = None
        
        # Track active teams for cleanup
        self.active_teams = []
        self._closed = False
        
        # Rate limiting
        self.last_api_call = 0
        self.min_call_interval = 2.0
        
        # Initialize available models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize available model clients"""
        # Initialize OpenAI
        if self.openai_api_key:
            try:
                self.openai_client = OpenAIChatCompletionClient(
                    model="gpt-4o-mini",
                    api_key=self.openai_api_key,
                    timeout=60.0
                )
                print("✅ OpenAI client initialized")
            except Exception as e:
                print(f"❌ OpenAI client failed: {e}")
                self.openai_client = None
        
        # Initialize Gemini
        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                self.gemini_client = GeminiChatCompletionClient(
                    model="gemini-2.0-flash-exp",
                    api_key=self.gemini_api_key,
                    timeout=60.0
                )
                print("✅ Gemini client initialized")
            except Exception as e:
                print(f"❌ Gemini client failed: {e}")
                self.gemini_client = None
        
        # Set default model
        if self.openai_client:
            self.current_model = "openai"
            print("🎯 Using OpenAI as primary model")
        elif self.gemini_client:
            self.current_model = "gemini"
            print("🎯 Using Gemini as primary model")
        else:
            raise ValueError("No model clients available. Check API keys.")
    
    def _get_model_client(self, preferred_model=None):
        """Get the best available model client"""
        if preferred_model == "openai" and self.openai_client:
            return self.openai_client, "openai"
        elif preferred_model == "gemini" and self.gemini_client:
            return self.gemini_client, "gemini"
        
        # Fallback logic
        if self.openai_client:
            return self.openai_client, "openai"
        elif self.gemini_client:
            return self.gemini_client, "gemini"
        else:
            return None, None
    
    async def _switch_model(self, reason=""):
        """Switch to the other available model"""
        if self.current_model == "openai" and self.gemini_client:
            self.current_model = "gemini"
            print(f"🔄 Switched to Gemini: {reason}")
        elif self.current_model == "gemini" and self.openai_client:
            self.current_model = "openai"
            print(f"🔄 Switched to OpenAI: {reason}")
        else:
            print(f"⚠️  No alternative model available: {reason}")
    
    async def _rate_limit_delay(self):
        """Add delay to respect rate limits"""
        now = time.time()
        time_since_last = now - self.last_api_call
        if time_since_last < self.min_call_interval:
            delay = self.min_call_interval - time_since_last
            await asyncio.sleep(delay)
        self.last_api_call = time.time()
        
    async def _create_fresh_team(self, agents_needed=None, preferred_model=None):
        """Create a fresh team with the best available model"""
        try:
            # Get the best available model client
            model_client, model_name = self._get_model_client(preferred_model)
            if not model_client:
                print("❌ No model client available")
                return None
            
            # Update current model
            self.current_model = model_name
            
            # Add rate limiting delay
            await self._rate_limit_delay()
            
            if agents_needed is None:
                agents_needed = ['web_surfer', 'file_surfer', 'coder', 'terminal']
            
            agents = []
            if 'web_surfer' in agents_needed:
                agents.append(MultimodalWebSurfer(
                    "GovPortalAgent",
                    model_client=model_client,
                    description="Specialized agent for browsing government portals and extracting grant information"
                ))
            
            if 'file_surfer' in agents_needed:
                agents.append(FileSurfer(
                    "PDFExtractorAgent", 
                    model_client=model_client,
                    description="Agent for reading and extracting information from PDF documents and files"
                ))
            
            if 'coder' in agents_needed:
                agents.append(MagenticOneCoderAgent(
                    "SchemaCoder",
                    model_client=model_client,
                    description="Agent for validating data schemas and processing grant information"
                ))
            
            if 'terminal' in agents_needed:
                agents.append(CodeExecutorAgent(
                    "ComputerTerminal",
                    code_executor=LocalCommandLineCodeExecutor(),
                    description="Agent for executing system commands and scripts"
                ))
            
            fresh_team = MagenticOneGroupChat(agents, model_client=model_client)
            self.active_teams.append(fresh_team)
            print(f"✅ Created team with {model_name}")
            return fresh_team
            
        except Exception as e:
            print(f"Error creating fresh team: {e}")
            return None
        
    async def _cleanup_team(self, team):
        """Clean up a team instance"""
        try:
            if team in self.active_teams:
                self.active_teams.remove(team)
        except Exception as e:
            print(f"Error cleaning up team: {e}")
        
    async def discover_grants_from_url(self, url, focus_area=None):
        """Discover grants from a specific URL with multi-model fallback"""
        task = f"""
        Visit the URL: {url}
        
        Extract all grant, funding, and scheme information available on this page.
        For each grant found, extract:
        1. Title/Name of the grant
        2. Funding amount (minimum, maximum, typical)
        3. Deadline information
        4. Eligibility criteria
        5. Application process
        6. Contact information
        7. Sector/domain focus
        
        Focus area: {focus_area or 'All startup grants and funding schemes'}
        
        Format the results as structured JSON data that matches our grant schema.
        """
        
        team = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Try with current model first
                preferred_model = self.current_model
                team = await self._create_fresh_team(['web_surfer', 'coder'], preferred_model)
                
                if not team:
                    # Try with alternative model
                    await self._switch_model("Primary model failed")
                    team = await self._create_fresh_team(['web_surfer', 'coder'])
                    
                if not team:
                    print(f"Failed to create team for {url}")
                    return None
                
                # Add timeout to prevent hanging - shorter timeout for testing
                async with asyncio.timeout(60):  # 1 minute timeout
                    result_count = 0
                    async for result in team.run_stream(task=task):
                        result_count += 1
                        # Return the first result from the stream
                        print(f"✅ Got result #{result_count} from {url}")
                        return result
                    
                    # If we get here without any results, return None
                    if result_count == 0:
                        print(f"No results from {url}")
                        return None
                        
            except asyncio.TimeoutError:
                print(f"⏰ Timeout while processing {url}")
                return None
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        # Switch model on rate limit
                        await self._switch_model("Rate limit hit")
                        wait_time = (attempt + 1) * 10
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"Rate limit exceeded after {max_retries} attempts for {url}")
                        return None
                else:
                    print(f"Error discovering grants from {url}: {e}")
                    # Try switching model on other errors too
                    if attempt < max_retries - 1:
                        await self._switch_model("Error occurred")
                        continue
                    return None
            finally:
                if team:
                    await self._cleanup_team(team)
        
        return None
        
    async def process_pdf_document(self, pdf_path):
        """Process a PDF document with multi-model fallback"""
        task = f"""
        Read and analyze the PDF document at: {pdf_path}
        
        Extract all grant, funding, scheme, and subsidy information from this document.
        Look for:
        1. Grant names and titles
        2. Funding amounts (in lakhs/crores)
        3. Application deadlines
        4. Eligibility criteria
        5. Application procedures
        6. Contact details
        7. Sector specifications
        
        Convert all amounts to lakhs for consistency.
        Format the extracted information as structured JSON matching our grant schema.
        """
        
        team = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                team = await self._create_fresh_team(['file_surfer', 'coder'])
                if not team:
                    print(f"Failed to create team for PDF processing")
                    return None
                
                async with asyncio.timeout(180):  # 3 minute timeout
                    async for result in team.run_stream(task=task):
                        return result
                        
            except asyncio.TimeoutError:
                print(f"Timeout while processing PDF {pdf_path}")
                return None
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        await self._switch_model("Rate limit hit")
                        wait_time = (attempt + 1) * 10
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"Rate limit exceeded after {max_retries} attempts for PDF")
                        return None
                else:
                    print(f"Error processing PDF {pdf_path}: {e}")
                    if attempt < max_retries - 1:
                        await self._switch_model("Error occurred")
                        continue
                    return None
            finally:
                if team:
                    await self._cleanup_team(team)
        
        return None
        
    async def validate_and_normalize_grant_data(self, raw_grant_data):
        """Validate and normalize grant data with multi-model fallback"""
        task = f"""
        Validate and normalize the following grant data to match our schema:
        
        Raw data: {raw_grant_data}
        
        Required schema:
        {{
            "id": "unique_identifier",
            "title": "Grant Title",
            "bucket": "Ideation|MVP Prototype|Early Stage|Growth|Infra",
            "instrument": ["grant", "loan", "subsidy", etc.],
            "min_ticket_lakh": float,
            "max_ticket_lakh": float,
            "typical_ticket_lakh": float,
            "deadline_type": "rolling|batch_call|annual|closed_waitlist",
            "next_deadline_iso": "ISO date string",
            "eligibility_flags": ["criteria1", "criteria2"],
            "sector_tags": ["sector1", "sector2"],
            "state_scope": "national|state_name",
            "agency": "Agency Name",
            "source_urls": ["url1", "url2"],
            "confidence": 0.0-1.0,
            "status": "live|expired|draft"
        }}
        
        Clean the data, standardize formats, and ensure all required fields are present.
        Generate a unique ID based on title and agency.
        Set appropriate confidence scores based on data completeness.
        """
        
        team = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                team = await self._create_fresh_team(['coder'])
                if not team:
                    print(f"Failed to create team for data validation")
                    return None
                
                async with asyncio.timeout(60):  # 1 minute timeout
                    async for result in team.run_stream(task=task):
                        return result
                        
            except asyncio.TimeoutError:
                print(f"Timeout while validating grant data")
                return None
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        await self._switch_model("Rate limit hit")
                        wait_time = (attempt + 1) * 10
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"Rate limit exceeded after {max_retries} attempts for validation")
                        return None
                else:
                    print(f"Error validating grant data: {e}")
                    if attempt < max_retries - 1:
                        await self._switch_model("Error occurred")
                        continue
                    return None
            finally:
                if team:
                    await self._cleanup_team(team)
        
        return None
        
    async def close(self):
        """Clean up resources"""
        try:
            # Clean up active teams
            for team in self.active_teams:
                await self._cleanup_team(team)
            
            # Close model clients
            if self.openai_client and not self._closed:
                await self.openai_client.close()
            if self.gemini_client and not self._closed:
                await self.gemini_client.close()
            
            self._closed = True
            print("✅ Multi-model orchestrator closed successfully")
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")

# Example usage
async def test_multi_model():
    """Test the multi-model orchestrator"""
    try:
        orchestrator = MultiModelOrchestrator()
        print("✅ Multi-model orchestrator initialized")
        
        # Test with a URL
        result = await orchestrator.discover_grants_from_url("https://seedfund.startupindia.gov.in/")
        print(f"✅ Discovery completed: {result is not None}")
        
        await orchestrator.close()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_multi_model()) 