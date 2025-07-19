"""
Enhanced Magentic-One Orchestrator for Grant Discovery
Supports dynamic URL lists and improved error handling
"""

import asyncio
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.teams.magentic_one import MagenticOne
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_ext.agents.file_surfer import FileSurfer
from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.teams import MagenticOneGroupChat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedGrantOracleOrchestrator:
    """Enhanced Magentic-One orchestrator with dynamic URL support"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
            
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            api_key=self.openai_api_key
        )
        
        # Dynamic URL management
        self.target_urls: Set[str] = set()
        self.processed_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.url_feedback: Dict[str, Dict] = {}
        
        # Performance tracking
        self.processing_stats = {
            'total_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'grants_found': 0
        }
        
        self.setup_agents()
        
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
    
    def add_target_urls(self, urls: List[str]) -> None:
        """Add new target URLs to the processing queue"""
        for url in urls:
            if self._is_valid_url(url) and url not in self.processed_urls:
                self.target_urls.add(url)
                logger.info(f"Added target URL: {url}")
    
    def remove_target_url(self, url: str) -> None:
        """Remove a URL from the target list"""
        self.target_urls.discard(url)
        logger.info(f"Removed target URL: {url}")
    
    def get_pending_urls(self) -> List[str]:
        """Get list of URLs pending processing"""
        return list(self.target_urls - self.processed_urls)
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        return {
            **self.processing_stats,
            'pending_urls': len(self.target_urls - self.processed_urls),
            'total_target_urls': len(self.target_urls),
            'failed_urls': len(self.failed_urls)
        }
    
    async def discover_grants_from_url(self, url: str, focus_area: Optional[str] = None) -> Optional[Dict]:
        """Discover grants from a specific URL with enhanced error handling"""
        if url in self.processed_urls:
            logger.info(f"URL already processed: {url}")
            return self.url_feedback.get(url)
        
        logger.info(f"Processing URL: {url}")
        self.processing_stats['total_processed'] += 1
        
        task = f"""
        Visit the URL: {url}
        
        Extract all grant, funding, and scheme information available on this page and any linked pages.
        For each grant found, extract:
        1. Title/Name of the grant
        2. Funding amount (minimum, maximum, typical) - convert to lakhs
        3. Deadline information (dates, rolling, batch calls)
        4. Eligibility criteria
        5. Application process and requirements
        6. Contact information
        7. Sector/domain focus
        8. Geographic scope (national, state-specific)
        9. Stage focus (ideation, MVP, growth, etc.)
        
        Focus area: {focus_area or 'All startup grants and funding schemes for Indian entrepreneurs'}
        
        Important instructions:
        - Look for PDF documents, application forms, and detailed program pages
        - Follow relevant links to get complete information
        - If the page has navigation menus, explore grant/funding sections
        - Extract exact dates and convert relative dates to absolute dates
        - Identify the funding agency/organization clearly
        - Note if applications are currently open or closed
        
        Format the results as structured JSON data matching this schema:
        {{
            "grants": [
                {{
                    "title": "Grant Name",
                    "agency": "Funding Agency",
                    "min_ticket_lakh": 0.0,
                    "max_ticket_lakh": 0.0,
                    "typical_ticket_lakh": 0.0,
                    "deadline_type": "rolling|batch_call|annual|closed_waitlist",
                    "next_deadline_iso": "ISO date string or null",
                    "eligibility_flags": ["criteria1", "criteria2"],
                    "sector_tags": ["sector1", "sector2"],
                    "state_scope": "national|state_name",
                    "bucket": "Ideation|MVP Prototype|Early Stage|Growth|Infra",
                    "instrument": ["grant", "loan", "subsidy"],
                    "source_urls": ["{url}"],
                    "status": "live|expired|draft",
                    "confidence": 0.0-1.0
                }}
            ],
            "source_quality": {{
                "relevance": 0.0-1.0,
                "data_completeness": 0.0-1.0,
                "update_frequency": 0.0-1.0
            }}
        }}
        
        If no grants are found, return an empty grants array but still assess source quality.
        """
        
        try:
            result = await self.team.run_stream(task=task)
            
            # Process the result
            grants_data = self._extract_grants_from_result(result)
            
            if grants_data:
                self.processing_stats['successful_extractions'] += 1
                grants_count = len(grants_data.get('grants', []))
                self.processing_stats['grants_found'] += grants_count
                
                # Store feedback for this URL
                feedback = {
                    'url': url,
                    'processed_at': datetime.now().isoformat(),
                    'grants_found': grants_count,
                    'success': True,
                    'data': grants_data
                }
                self.url_feedback[url] = feedback
                
                logger.info(f"Successfully extracted {grants_count} grants from {url}")
                
            else:
                self.processing_stats['failed_extractions'] += 1
                self.failed_urls.add(url)
                
                feedback = {
                    'url': url,
                    'processed_at': datetime.now().isoformat(),
                    'grants_found': 0,
                    'success': False,
                    'error': 'No valid grants extracted'
                }
                self.url_feedback[url] = feedback
                
                logger.warning(f"No grants extracted from {url}")
            
            self.processed_urls.add(url)
            return grants_data
            
        except Exception as e:
            self.processing_stats['failed_extractions'] += 1
            self.failed_urls.add(url)
            
            feedback = {
                'url': url,
                'processed_at': datetime.now().isoformat(),
                'grants_found': 0,
                'success': False,
                'error': str(e)
            }
            self.url_feedback[url] = feedback
            
            logger.error(f"Error discovering grants from {url}: {e}")
            self.processed_urls.add(url)
            return None
    
    async def process_pdf_document(self, pdf_path: str) -> Optional[Dict]:
        """Process a PDF document to extract grant information"""
        task = f"""
        Read and analyze the PDF document at: {pdf_path}
        
        Extract all grant, funding, scheme, and subsidy information from this document.
        Look for:
        1. Grant names and titles
        2. Funding amounts (in lakhs/crores) - convert to lakhs
        3. Application deadlines and timelines
        4. Eligibility criteria and requirements
        5. Application procedures and forms
        6. Contact details and addresses
        7. Sector specifications and focus areas
        8. Geographic scope and limitations
        
        Pay special attention to:
        - Tables with grant details
        - Application forms and guidelines
        - Deadline calendars
        - Eligibility matrices
        - Contact directories
        
        Convert all amounts to lakhs for consistency.
        Format the extracted information as structured JSON matching our grant schema.
        Include confidence scores based on data completeness and clarity.
        """
        
        try:
            result = await self.team.run_stream(task=task)
            grants_data = self._extract_grants_from_result(result)
            
            if grants_data:
                logger.info(f"Successfully processed PDF: {pdf_path}")
                return grants_data
            else:
                logger.warning(f"No grants extracted from PDF: {pdf_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return None
    
    async def validate_and_normalize_grant_data(self, raw_grant_data: Dict) -> Optional[Dict]:
        """Validate and normalize grant data using the coder agent"""
        task = f"""
        Validate and normalize the following grant data to match our schema:
        
        Raw data: {json.dumps(raw_grant_data, indent=2)}
        
        Required schema validation and normalization:
        1. Ensure all required fields are present
        2. Validate data types and formats
        3. Normalize funding amounts to lakhs
        4. Standardize date formats to ISO
        5. Clean and categorize eligibility criteria
        6. Standardize sector tags and bucket classifications
        7. Generate unique IDs based on title and agency
        8. Calculate confidence scores based on data completeness
        9. Validate URLs and contact information
        10. Ensure status is correctly set based on deadlines
        
        Schema requirements:
        {{
            "id": "unique_identifier",
            "title": "Grant Title",
            "bucket": "Ideation|MVP Prototype|Early Stage|Growth|Infra",
            "instrument": ["grant", "loan", "subsidy", "equity", "debt"],
            "min_ticket_lakh": float,
            "max_ticket_lakh": float,
            "typical_ticket_lakh": float,
            "deadline_type": "rolling|batch_call|annual|closed_waitlist",
            "next_deadline_iso": "ISO date string or null",
            "eligibility_flags": ["criteria1", "criteria2"],
            "sector_tags": ["sector1", "sector2"],
            "state_scope": "national|state_name",
            "agency": "Agency Name",
            "source_urls": ["url1", "url2"],
            "confidence": 0.0-1.0,
            "status": "live|expired|draft"
        }}
        
        Return the cleaned and validated data as JSON.
        If data is insufficient or invalid, return null with explanation.
        """
        
        try:
            result = await self.team.run_stream(task=task)
            validated_data = self._extract_grants_from_result(result)
            
            if validated_data:
                logger.info("Successfully validated and normalized grant data")
                return validated_data
            else:
                logger.warning("Grant data validation failed")
                return None
                
        except Exception as e:
            logger.error(f"Error validating grant data: {e}")
            return None
    
    async def daily_discovery_mission(self, target_urls: Optional[List[str]] = None) -> List[Dict]:
        """Execute daily grant discovery mission with dynamic URL support"""
        logger.info(f"Starting daily grant discovery mission at {datetime.now()}")
        
        # Add new target URLs if provided
        if target_urls:
            self.add_target_urls(target_urls)
        
        # Get pending URLs to process
        pending_urls = self.get_pending_urls()
        
        if not pending_urls:
            logger.info("No pending URLs to process")
            return []
        
        logger.info(f"Processing {len(pending_urls)} URLs")
        
        discovered_grants = []
        
        for url in pending_urls:
            logger.info(f"Processing URL: {url}")
            
            # Discover grants from URL
            grants_data = await self.discover_grants_from_url(url)
            
            if grants_data and grants_data.get('grants'):
                # Validate and normalize the data
                for grant in grants_data['grants']:
                    normalized_data = await self.validate_and_normalize_grant_data(grant)
                    
                    if normalized_data:
                        discovered_grants.append({
                            'source_url': url,
                            'grant': normalized_data,
                            'discovered_at': datetime.now().isoformat(),
                            'source_quality': grants_data.get('source_quality', {})
                        })
            
            # Add delay between requests to be respectful
            await asyncio.sleep(2)
        
        logger.info(f"Discovery mission completed. Found {len(discovered_grants)} grants from {len(pending_urls)} sources.")
        
        # Log statistics
        stats = self.get_processing_stats()
        logger.info(f"Processing stats: {stats}")
        
        return discovered_grants
    
    def get_url_feedback(self, url: str) -> Optional[Dict]:
        """Get feedback for a specific URL"""
        return self.url_feedback.get(url)
    
    def get_failed_urls(self) -> List[str]:
        """Get list of URLs that failed processing"""
        return list(self.failed_urls)
    
    def reset_url_status(self, url: str) -> None:
        """Reset the processing status of a URL"""
        self.processed_urls.discard(url)
        self.failed_urls.discard(url)
        if url in self.url_feedback:
            del self.url_feedback[url]
        logger.info(f"Reset status for URL: {url}")
    
    def _extract_grants_from_result(self, result) -> Optional[Dict]:
        """Extract grant data from agent result"""
        if not result:
            return None
        
        try:
            # Try to extract JSON from the result
            content = ""
            if hasattr(result, 'messages'):
                for message in result.messages:
                    if hasattr(message, 'content'):
                        content += message.content + " "
            elif hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            # Look for JSON in the content
            import re
            json_pattern = r'\{.*\}'
            json_matches = re.findall(json_pattern, content, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    if 'grants' in data or 'grant' in data:
                        return data
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting grants from result: {e}")
            return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except:
            return False
    
    async def close(self):
        """Clean up resources"""
        await self.model_client.close()

# Example usage and testing
async def test_enhanced_orchestrator():
    """Test the enhanced orchestrator"""
    orchestrator = EnhancedGrantOracleOrchestrator()
    
    test_urls = [
        "https://seedfund.startupindia.gov.in/",
        "https://birac.nic.in/call_details.aspx",
        "https://tdb.gov.in/"
    ]
    
    try:
        # Add URLs and run discovery
        orchestrator.add_target_urls(test_urls)
        results = await orchestrator.daily_discovery_mission()
        
        print("Discovery results:")
        for result in results:
            print(f"- Found grant from {result['source_url']}")
        
        # Print statistics
        stats = orchestrator.get_processing_stats()
        print(f"Processing statistics: {stats}")
        
        return results
    finally:
        await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(test_enhanced_orchestrator())

