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

class GrantOracleOrchestrator:
    """Magentic-One orchestrator for India Startup Grant Oracle"""
    
    def __init__(self, openai_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
            
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",  # Use mini to reduce token usage
            api_key=self.openai_api_key,
            timeout=60.0  # Add timeout to prevent hanging
        )
        
        # Track active teams for cleanup
        self.active_teams = []
        self._closed = False
        
        # Rate limiting
        self.last_api_call = 0
        self.min_call_interval = 2.0  # Minimum 2 seconds between calls
        
    async def _rate_limit_delay(self):
        """Add delay to respect rate limits"""
        now = time.time()
        time_since_last = now - self.last_api_call
        if time_since_last < self.min_call_interval:
            delay = self.min_call_interval - time_since_last
            await asyncio.sleep(delay)
        self.last_api_call = time.time()
        
    async def _ensure_client_available(self):
        """Ensure the model client is available and not closed"""
        if self._closed:
            # Recreate the client if it was closed
            if not self.openai_api_key:
                raise ValueError("OpenAI API key is required")
            self.model_client = OpenAIChatCompletionClient(
                model="gpt-4o-mini",  # Use mini to reduce token usage
                api_key=self.openai_api_key,
                timeout=60.0
            )
            self._closed = False
            print("✅ Recreated model client")
        
    def setup_agents(self):
        """Setup Magentic-One agents for grant discovery"""
        
        # Web Surfer for browsing government portals
        self.web_surfer = MultimodalWebSurfer(
            "GovPortalAgent",
            model_client=self.model_client,
            description="Specialized agent for browsing government portals and extracting grant information"
        )
        
        # File Surfer for processing PDFs and documents
        self.file_surfer = FileSurfer(
            "PDFExtractorAgent", 
            model_client=self.model_client,
            description="Agent for reading and extracting information from PDF documents and files"
        )
        
        # Coder for data processing and validation
        self.coder = MagenticOneCoderAgent(
            "SchemaCoder",
            model_client=self.model_client,
            description="Agent for validating data schemas and processing grant information"
        )
        
        # Terminal for executing commands
        self.terminal = CodeExecutorAgent(
            "ComputerTerminal",
            code_executor=LocalCommandLineCodeExecutor(),
            description="Agent for executing system commands and scripts"
        )
        
        # Create the Magentic-One team
        self.team = MagenticOneGroupChat(
            [self.web_surfer, self.file_surfer, self.coder, self.terminal],
            model_client=self.model_client
        )
        
    async def _create_fresh_team(self, agents_needed=None):
        """Create a fresh team with proper error handling"""
        try:
            # Ensure client is available
            await self._ensure_client_available()
            
            # Add rate limiting delay
            await self._rate_limit_delay()
            
            if agents_needed is None:
                agents_needed = ['web_surfer', 'file_surfer', 'coder', 'terminal']
            
            agents = []
            if 'web_surfer' in agents_needed:
                agents.append(MultimodalWebSurfer(
                    "GovPortalAgent",
                    model_client=self.model_client,
                    description="Specialized agent for browsing government portals and extracting grant information"
                ))
            
            if 'file_surfer' in agents_needed:
                agents.append(FileSurfer(
                    "PDFExtractorAgent", 
                    model_client=self.model_client,
                    description="Agent for reading and extracting information from PDF documents and files"
                ))
            
            if 'coder' in agents_needed:
                agents.append(MagenticOneCoderAgent(
                    "SchemaCoder",
                    model_client=self.model_client,
                    description="Agent for validating data schemas and processing grant information"
                ))
            
            if 'terminal' in agents_needed:
                agents.append(CodeExecutorAgent(
                    "ComputerTerminal",
                    code_executor=LocalCommandLineCodeExecutor(),
                    description="Agent for executing system commands and scripts"
                ))
            
            fresh_team = MagenticOneGroupChat(agents, model_client=self.model_client)
            self.active_teams.append(fresh_team)
            return fresh_team
            
        except Exception as e:
            print(f"Error creating fresh team: {e}")
            return None
        
    async def _cleanup_team(self, team):
        """Clean up a team instance"""
        try:
            if team in self.active_teams:
                self.active_teams.remove(team)
            # Add any additional cleanup needed
        except Exception as e:
            print(f"Error cleaning up team: {e}")
        
    async def discover_grants_from_url(self, url, focus_area=None):
        """Discover grants from a specific URL with proper error handling"""
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
                # Create a fresh team instance for each URL to avoid state conflicts
                team = await self._create_fresh_team(['web_surfer', 'coder'])
                if not team:
                    print(f"Failed to create team for {url}")
                    return None
                
                # Add timeout to prevent hanging
                async with asyncio.timeout(120):  # 2 minute timeout
                    async for result in team.run_stream(task=task):
                        # Return the first result from the stream
                        return result
                        
            except asyncio.TimeoutError:
                print(f"Timeout while processing {url}")
                return None
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10  # Exponential backoff
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"Rate limit exceeded after {max_retries} attempts for {url}")
                        return None
                else:
                    print(f"Error discovering grants from {url}: {e}")
                    return None
            finally:
                if team:
                    await self._cleanup_team(team)
        
        return None
        
    async def process_pdf_document(self, pdf_path):
        """Process a PDF document to extract grant information"""
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
        try:
            # Create a fresh team instance for PDF processing
            team = await self._create_fresh_team(['file_surfer', 'coder'])
            if not team:
                print(f"Failed to create team for PDF processing")
                return None
            
            # Add timeout to prevent hanging
            async with asyncio.timeout(180):  # 3 minute timeout for PDF processing
                async for result in team.run_stream(task=task):
                    # Return the first result from the stream
                    return result
                    
        except asyncio.TimeoutError:
            print(f"Timeout while processing PDF {pdf_path}")
            return None
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {e}")
            return None
        finally:
            if team:
                await self._cleanup_team(team)
            
    async def validate_and_normalize_grant_data(self, raw_grant_data):
        """Validate and normalize grant data using the coder agent"""
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
        try:
            # Create a fresh team instance for data validation
            team = await self._create_fresh_team(['coder'])
            if not team:
                print(f"Failed to create team for data validation")
                return None
            
            # Add timeout to prevent hanging
            async with asyncio.timeout(60):  # 1 minute timeout for validation
                async for result in team.run_stream(task=task):
                    # Return the first result from the stream
                    return result
                    
        except asyncio.TimeoutError:
            print(f"Timeout while validating grant data")
            return None
        except Exception as e:
            print(f"Error validating grant data: {e}")
            return None
        finally:
            if team:
                await self._cleanup_team(team)
            
    async def daily_discovery_mission(self, target_urls):
        """Execute daily grant discovery mission"""
        print(f"Starting daily grant discovery mission at {datetime.now()}")
        
        discovered_grants = []
        
        for url in target_urls:
            print(f"Processing URL: {url}")
            
            try:
                # Discover grants from URL using fresh team
                grants_data = await self.discover_grants_from_url(url)
                
                if grants_data:
                    # Validate and normalize the data using fresh team
                    normalized_data = await self.validate_and_normalize_grant_data(grants_data)
                    
                    if normalized_data:
                        discovered_grants.append({
                            'source_url': url,
                            'grants': normalized_data,
                            'discovered_at': datetime.now().isoformat()
                        })
                
                # Add delay between requests to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                continue
        
        print(f"Discovery mission completed. Found {len(discovered_grants)} grant sources.")
        return discovered_grants
        
    async def close(self):
        """Clean up resources"""
        try:
            # Clean up active teams
            for team in self.active_teams:
                await self._cleanup_team(team)
            
            # Close the model client
            if not self._closed:
                await self.model_client.close()
                self._closed = True
                print("✅ Model client closed successfully")
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")

# Example usage and testing
async def test_orchestrator():
    """Test the orchestrator with sample URLs"""
    orchestrator = GrantOracleOrchestrator()
    
    test_urls = [
        "https://seedfund.startupindia.gov.in/",
        "https://birac.nic.in/call_details.aspx"
    ]
    
    try:
        results = await orchestrator.daily_discovery_mission(test_urls)
        print("Discovery results:", results)
    finally:
        await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(test_orchestrator())

