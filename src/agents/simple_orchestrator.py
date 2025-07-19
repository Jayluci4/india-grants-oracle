#!/usr/bin/env python3
"""
Simplified Orchestrator for Development
"""

import os
import sys
from datetime import datetime
import asyncio

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import DatabaseManager

class SimpleGrantOrchestrator:
    """Simplified orchestrator for development testing"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db_manager.create_tables()
        
    async def discover_grants_from_url(self, url):
        """Mock grant discovery for development"""
        print(f"Mock discovery from {url}")
        
        # Return mock grant data for testing
        mock_grants = [
            {
                'id': f'mock-{url.split("//")[1].split("/")[0].replace(".", "-")}',
                'title': f'Mock Grant from {url}',
                'bucket': 'Early Stage',
                'instrument': ['grant'],
                'min_ticket_lakh': 25.0,
                'max_ticket_lakh': 100.0,
                'typical_ticket_lakh': 50.0,
                'deadline_type': 'rolling',
                'next_deadline_iso': '2024-12-31T23:59:59Z',
                'eligibility_flags': ['tech_startup', 'early_stage'],
                'sector_tags': ['technology', 'innovation'],
                'state_scope': 'national',
                'agency': f'Agency from {url}',
                'source_urls': [url],
                'confidence': 0.75,
                'status': 'live'
            }
        ]
        
        return mock_grants
        
    async def daily_discovery_mission(self, target_urls):
        """Execute daily grant discovery mission"""
        print(f"Starting simplified daily discovery mission at {datetime.now()}")
        
        discovered_grants = []
        
        for url in target_urls:
            print(f"Processing URL: {url}")
            
            try:
                # Discover grants from URL
                grants_data = await self.discover_grants_from_url(url)
                
                if grants_data:
                    discovered_grants.append({
                        'source_url': url,
                        'grants': grants_data,
                        'discovered_at': datetime.now().isoformat()
                    })
                    
                    # Save grants to database
                    for grant in grants_data:
                        success = self.db_manager.upsert_grant(grant)
                        if success:
                            print(f"✅ Saved grant: {grant['title']}")
                        else:
                            print(f"❌ Failed to save grant: {grant['title']}")
                
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
            
            # Add delay between requests
            await asyncio.sleep(1)
        
        print(f"Simplified discovery completed. Found {len(discovered_grants)} grant sources.")
        return discovered_grants
        
    def close(self):
        """Clean up resources"""
        print("Simple orchestrator closed")

# Example usage
async def test_simple_orchestrator():
    """Test the simplified orchestrator"""
    orchestrator = SimpleGrantOrchestrator()
    
    test_urls = [
        "https://seedfund.startupindia.gov.in/",
        "https://birac.nic.in/call_details.aspx",
        "https://tdb.gov.in/"
    ]
    
    try:
        results = await orchestrator.daily_discovery_mission(test_urls)
        print("Discovery results:", results)
    finally:
        orchestrator.close()

if __name__ == "__main__":
    asyncio.run(test_simple_orchestrator()) 