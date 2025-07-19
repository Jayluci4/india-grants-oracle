"""
Intelligent Source Discovery Module (ISDM)
Autonomously discovers new grant sources using Magentic-One agents
"""

import asyncio
import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging

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

class SourceEvaluator:
    """Evaluates and scores potential grant sources"""
    
    def __init__(self):
        self.grant_keywords = [
            'grant', 'grants', 'funding', 'scheme', 'schemes', 'subsidy', 'subsidies',
            'startup', 'startups', 'innovation', 'entrepreneur', 'entrepreneurship',
            'incubator', 'accelerator', 'venture', 'investment', 'seed fund',
            'government', 'ministry', 'department', 'agency', 'corporation',
            'CSR', 'corporate social responsibility', 'foundation', 'trust'
        ]
        
        self.credibility_indicators = [
            'about us', 'contact', 'address', 'phone', 'email',
            'registration', 'license', 'certificate', 'accreditation',
            'annual report', 'financial statement', 'transparency'
        ]
        
        self.negative_indicators = [
            'scam', 'fraud', 'fake', 'spam', 'advertisement', 'ad',
            'casino', 'gambling', 'loan shark', 'quick money'
        ]
    
    def calculate_relevance_score(self, content: str, url: str) -> float:
        """Calculate relevance score based on content analysis"""
        content_lower = content.lower()
        url_lower = url.lower()
        
        # Count grant-related keywords
        grant_score = sum(1 for keyword in self.grant_keywords if keyword in content_lower)
        
        # Bonus for government domains
        gov_bonus = 2 if any(domain in url_lower for domain in ['.gov.', '.nic.', '.org']) else 0
        
        # Penalty for negative indicators
        negative_penalty = sum(1 for indicator in self.negative_indicators if indicator in content_lower)
        
        # Calculate final score (0-1 range)
        raw_score = (grant_score + gov_bonus - negative_penalty) / 10
        return max(0, min(1, raw_score))
    
    def calculate_credibility_score(self, content: str, url: str) -> float:
        """Calculate credibility score based on website structure and content"""
        content_lower = content.lower()
        
        # Check for credibility indicators
        credibility_score = sum(1 for indicator in self.credibility_indicators if indicator in content_lower)
        
        # Check for professional domain
        domain = urlparse(url).netloc
        professional_bonus = 1 if any(ext in domain for ext in ['.gov', '.org', '.edu', '.in']) else 0
        
        # Calculate final score (0-1 range)
        raw_score = (credibility_score + professional_bonus) / 8
        return max(0, min(1, raw_score))
    
    def calculate_timeliness_score(self, content: str) -> float:
        """Calculate timeliness score based on recent updates"""
        current_year = datetime.now().year
        content_lower = content.lower()
        
        # Look for recent years in content
        recent_years = [str(year) for year in range(current_year - 1, current_year + 2)]
        year_mentions = sum(1 for year in recent_years if year in content)
        
        # Look for recent date patterns
        recent_patterns = ['2024', '2025', 'latest', 'new', 'recent', 'updated']
        pattern_score = sum(1 for pattern in recent_patterns if pattern in content_lower)
        
        # Calculate final score (0-1 range)
        raw_score = (year_mentions + pattern_score) / 6
        return max(0, min(1, raw_score))

class IntelligentSourceDiscoveryModule:
    """Main class for intelligent source discovery using Magentic-One"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            api_key=self.openai_api_key
        )
        
        self.evaluator = SourceEvaluator()
        self.discovered_sources: Set[str] = set()
        self.evaluated_sources: Dict[str, Dict] = {}
        
        # Initialize seed URLs
        self.seed_urls = [
            "https://www.startupindia.gov.in/",
            "https://www.investindia.gov.in/",
            "https://msme.gov.in/",
            "https://dst.gov.in/",
            "https://www.birac.nic.in/",
            "https://tdb.gov.in/",
            "https://www.nasscom.in/",
            "https://www.cii.in/",
            "https://ficci.in/",
            "https://www.assocham.org/"
        ]
        
        self.setup_agents()
    
    def setup_agents(self):
        """Setup Magentic-One agents for source discovery"""
        
        # Web Surfer for browsing and discovery
        self.web_surfer = MultimodalWebSurfer(
            "SourceDiscoveryAgent",
            model_client=self.model_client,
            description="Specialized agent for discovering and evaluating potential grant sources"
        )
        
        # File Surfer for document analysis
        self.file_surfer = FileSurfer(
            "DocumentAnalyzer", 
            model_client=self.model_client,
            description="Agent for analyzing documents and extracting source information"
        )
        
        # Coder for data processing and scoring
        self.coder = MagenticOneCoderAgent(
            "SourceEvaluator",
            model_client=self.model_client,
            description="Agent for evaluating and scoring potential grant sources"
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
    
    async def discover_from_seed_expansion(self, max_depth: int = 2) -> List[str]:
        """Discover new sources by expanding from seed URLs"""
        logger.info(f"Starting seed URL expansion with max depth {max_depth}")
        
        discovered_urls = []
        
        for seed_url in self.seed_urls:
            try:
                task = f"""
                Visit the URL: {seed_url}
                
                Your task is to find links to other websites that might contain grant or funding information for Indian startups.
                
                Look for:
                1. Links to government departments and ministries
                2. Links to startup ecosystem organizations
                3. Links to funding agencies and corporations
                4. Links to state government startup portals
                5. Links to incubators and accelerators
                
                Extract all relevant URLs and categorize them by type.
                Focus on Indian organizations and government entities.
                
                Return the results as a JSON list of URLs with their categories.
                """
                
                result = await self.team.run_stream(task=task)
                
                # Parse the result to extract URLs
                if result and hasattr(result, 'messages'):
                    for message in result.messages:
                        if hasattr(message, 'content'):
                            urls = self._extract_urls_from_content(message.content)
                            discovered_urls.extend(urls)
                
                # Add delay between requests
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing seed URL {seed_url}: {e}")
                continue
        
        # Remove duplicates and filter
        unique_urls = list(set(discovered_urls))
        filtered_urls = self._filter_relevant_urls(unique_urls)
        
        logger.info(f"Discovered {len(filtered_urls)} potential sources from seed expansion")
        return filtered_urls
    
    async def discover_from_search(self) -> List[str]:
        """Discover new sources through targeted web searches"""
        logger.info("Starting search-based discovery")
        
        search_queries = [
            "new startup grants India 2024",
            "government funding schemes for startups India",
            "state government startup policy India",
            "corporate CSR grants for startups India",
            "technology startup grants India",
            "women entrepreneur grants India",
            "rural startup funding schemes India",
            "fintech startup grants India",
            "healthtech startup funding India",
            "agritech startup grants India"
        ]
        
        discovered_urls = []
        
        for query in search_queries:
            try:
                task = f"""
                Perform a web search for: "{query}"
                
                Analyze the search results and identify websites that might contain grant or funding information.
                
                Look for:
                1. Government websites (.gov.in, .nic.in)
                2. Official startup portals
                3. Corporate websites with CSR sections
                4. NGO and foundation websites
                5. News articles about new grant announcements
                
                Visit the top 5-10 most promising results and extract their URLs.
                Evaluate each website briefly for relevance to startup grants.
                
                Return a JSON list of URLs with brief descriptions of why they might be relevant.
                """
                
                result = await self.team.run_stream(task=task)
                
                # Parse the result to extract URLs
                if result and hasattr(result, 'messages'):
                    for message in result.messages:
                        if hasattr(message, 'content'):
                            urls = self._extract_urls_from_content(message.content)
                            discovered_urls.extend(urls)
                
                # Add delay between searches
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error processing search query '{query}': {e}")
                continue
        
        # Remove duplicates and filter
        unique_urls = list(set(discovered_urls))
        filtered_urls = self._filter_relevant_urls(unique_urls)
        
        logger.info(f"Discovered {len(filtered_urls)} potential sources from search")
        return filtered_urls
    
    async def evaluate_source(self, url: str) -> Optional[Dict]:
        """Evaluate a potential source and calculate its score"""
        if url in self.evaluated_sources:
            return self.evaluated_sources[url]
        
        try:
            task = f"""
            Visit and thoroughly analyze the website: {url}
            
            Your task is to evaluate this website as a potential source of grant information for Indian startups.
            
            Analyze:
            1. Content relevance - Does it contain grant/funding information?
            2. Credibility - Is it a legitimate organization?
            3. Timeliness - Is the information current and updated?
            4. Accessibility - Is grant information easy to find?
            
            Look for:
            - Grant announcements and programs
            - Application processes and deadlines
            - Eligibility criteria
            - Contact information
            - About us / organization details
            - Recent updates or news
            
            Provide a detailed analysis including:
            - Summary of the organization
            - Types of grants/funding available (if any)
            - Target beneficiaries
            - Application process
            - Overall assessment of usefulness
            
            Rate the source on a scale of 1-10 for grant discovery potential.
            """
            
            result = await self.team.run_stream(task=task)
            
            # Extract content for scoring
            content = ""
            if result and hasattr(result, 'messages'):
                for message in result.messages:
                    if hasattr(message, 'content'):
                        content += message.content + " "
            
            # Calculate scores
            relevance_score = self.evaluator.calculate_relevance_score(content, url)
            credibility_score = self.evaluator.calculate_credibility_score(content, url)
            timeliness_score = self.evaluator.calculate_timeliness_score(content)
            
            # Calculate overall score
            overall_score = (relevance_score * 0.4 + credibility_score * 0.4 + timeliness_score * 0.2)
            
            evaluation = {
                'url': url,
                'relevance_score': relevance_score,
                'credibility_score': credibility_score,
                'timeliness_score': timeliness_score,
                'overall_score': overall_score,
                'content_summary': content[:500],  # First 500 chars
                'evaluated_at': datetime.now().isoformat(),
                'agent_analysis': content
            }
            
            self.evaluated_sources[url] = evaluation
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating source {url}: {e}")
            return None
    
    async def run_discovery_mission(self, max_new_sources: int = 20) -> List[Dict]:
        """Run a complete discovery mission"""
        logger.info("Starting intelligent source discovery mission")
        
        # Step 1: Discover from seed expansion
        seed_urls = await self.discover_from_seed_expansion()
        
        # Step 2: Discover from search
        search_urls = await self.discover_from_search()
        
        # Combine and deduplicate
        all_discovered = list(set(seed_urls + search_urls))
        logger.info(f"Total discovered URLs: {len(all_discovered)}")
        
        # Step 3: Evaluate sources
        evaluated_sources = []
        for url in all_discovered[:max_new_sources]:  # Limit to prevent overload
            evaluation = await self.evaluate_source(url)
            if evaluation and evaluation['overall_score'] > 0.3:  # Minimum threshold
                evaluated_sources.append(evaluation)
            
            # Add delay between evaluations
            await asyncio.sleep(1)
        
        # Sort by overall score
        evaluated_sources.sort(key=lambda x: x['overall_score'], reverse=True)
        
        logger.info(f"Evaluated {len(evaluated_sources)} high-quality sources")
        return evaluated_sources
    
    def _extract_urls_from_content(self, content: str) -> List[str]:
        """Extract URLs from text content"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        # Clean and validate URLs
        cleaned_urls = []
        for url in urls:
            # Remove trailing punctuation
            url = url.rstrip('.,;:!?')
            
            # Basic validation
            if self._is_valid_url(url):
                cleaned_urls.append(url)
        
        return cleaned_urls
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except:
            return False
    
    def _filter_relevant_urls(self, urls: List[str]) -> List[str]:
        """Filter URLs to keep only potentially relevant ones"""
        filtered = []
        
        for url in urls:
            url_lower = url.lower()
            
            # Skip if already discovered
            if url in self.discovered_sources:
                continue
            
            # Skip common irrelevant domains
            skip_domains = [
                'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
                'youtube.com', 'google.com', 'wikipedia.org', 'amazon.com'
            ]
            
            if any(domain in url_lower for domain in skip_domains):
                continue
            
            # Prefer Indian domains and relevant keywords
            relevant_indicators = [
                '.in', '.gov', '.org', 'startup', 'grant', 'funding',
                'scheme', 'ministry', 'department', 'innovation'
            ]
            
            if any(indicator in url_lower for indicator in relevant_indicators):
                filtered.append(url)
                self.discovered_sources.add(url)
        
        return filtered
    
    async def close(self):
        """Clean up resources"""
        await self.model_client.close()

# Example usage and testing
async def test_discovery():
    """Test the discovery module"""
    discovery = IntelligentSourceDiscoveryModule()
    
    try:
        results = await discovery.run_discovery_mission(max_new_sources=10)
        
        print(f"Discovery completed. Found {len(results)} high-quality sources:")
        for result in results[:5]:  # Show top 5
            print(f"- {result['url']} (Score: {result['overall_score']:.2f})")
        
        return results
    finally:
        await discovery.close()

if __name__ == "__main__":
    asyncio.run(test_discovery())

