#!/usr/bin/env python3
"""
Enhanced India Startup Grant Oracle - Main Application
Integrates Intelligent Source Discovery Module with Enhanced Magentic-One Orchestrator
"""

import asyncio
import os
import sys
import schedule
import time
import json
import logging
from datetime import datetime, timedelta
import threading
from typing import List, Dict, Optional

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.models import DatabaseManager
from scrapers.scrapy_runner import ScrapyRunner
from agents.intelligent_source_discovery import IntelligentSourceDiscoveryModule
from agents.enhanced_magentic_orchestrator import EnhancedGrantOracleOrchestrator
from notifications.slack_notifier import NotificationManager
from api.flask_app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_oracle.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedGrantOracleMain:
    """Enhanced main orchestrator with intelligent source discovery"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.scrapy_runner = ScrapyRunner()
        self.notification_manager = NotificationManager()
        
        # Initialize enhanced components
        self.source_discovery = None
        self.enhanced_orchestrator = None
        
        # Initialize database
        self.db_manager.create_tables()
        
        # Configuration
        self.config = {
            'max_new_sources_per_day': 20,
            'source_discovery_frequency_hours': 24,
            'grant_extraction_frequency_hours': 6,
            'min_source_score_threshold': 0.3,
            'max_concurrent_extractions': 5
        }
        
        # State tracking
        self.last_source_discovery = None
        self.discovered_sources_cache = []
        
        logger.info("Enhanced Grant Oracle initialized")
        
    async def initialize_ai_components(self):
        """Initialize AI-powered components"""
        try:
            # Initialize Intelligent Source Discovery Module
            self.source_discovery = IntelligentSourceDiscoveryModule()
            logger.info("Intelligent Source Discovery Module initialized")
            
            # Initialize Enhanced Orchestrator
            self.enhanced_orchestrator = EnhancedGrantOracleOrchestrator()
            logger.info("Enhanced Magentic-One Orchestrator initialized")
            
            # Add initial seed URLs to orchestrator
            initial_urls = [
                "https://seedfund.startupindia.gov.in/",
                "https://birac.nic.in/call_details.aspx",
                "https://tdb.gov.in/",
                "https://startup.karnataka.gov.in/",
                "https://startup.goa.gov.in/",
                "https://villgro.org/",
                "https://gailebank.gail.co.in/"
            ]
            self.enhanced_orchestrator.add_target_urls(initial_urls)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI components: {e}")
            self.notification_manager.notify_error(f"AI initialization failed: {e}", "Initialization")
            return False
    
    async def run_intelligent_source_discovery(self) -> List[Dict]:
        """Run intelligent source discovery to find new grant sources"""
        logger.info("Starting intelligent source discovery")
        
        if not self.source_discovery:
            await self.initialize_ai_components()
        
        if not self.source_discovery:
            logger.error("Source discovery module not available")
            return []
        
        try:
            # Run discovery mission
            discovered_sources = await self.source_discovery.run_discovery_mission(
                max_new_sources=self.config['max_new_sources_per_day']
            )
            
            # Filter sources by quality threshold
            high_quality_sources = [
                source for source in discovered_sources 
                if source['overall_score'] >= self.config['min_source_score_threshold']
            ]
            
            logger.info(f"Discovered {len(high_quality_sources)} high-quality sources")
            
            # Add to orchestrator for grant extraction
            if high_quality_sources:
                new_urls = [source['url'] for source in high_quality_sources]
                self.enhanced_orchestrator.add_target_urls(new_urls)
                
                # Cache for reporting
                self.discovered_sources_cache = high_quality_sources
                self.last_source_discovery = datetime.now()
                
                # Notify about new sources
                self.notification_manager.notify_new_sources_discovered(len(high_quality_sources))
            
            return high_quality_sources
            
        except Exception as e:
            logger.error(f"Intelligent source discovery failed: {e}")
            self.notification_manager.notify_error(f"Source discovery failed: {e}", "Source Discovery")
            return []
    
    async def run_enhanced_grant_extraction(self) -> List[Dict]:
        """Run enhanced grant extraction from all target sources"""
        logger.info("Starting enhanced grant extraction")
        
        if not self.enhanced_orchestrator:
            await self.initialize_ai_components()
        
        if not self.enhanced_orchestrator:
            logger.error("Enhanced orchestrator not available")
            return []
        
        try:
            # Run discovery mission on all target URLs
            discovered_grants = await self.enhanced_orchestrator.daily_discovery_mission()
            
            grants_processed = 0
            new_grants = []
            
            for result in discovered_grants:
                if 'grant' in result:
                    grant_data = result['grant']
                    
                    # Add metadata
                    grant_data.update({
                        'discovered_at': result['discovered_at'],
                        'source_url': result['source_url'],
                        'discovery_method': 'enhanced_ai'
                    })
                    
                    # Save to database
                    success = self.db_manager.upsert_grant(grant_data)
                    if success:
                        grants_processed += 1
                        new_grants.append(grant_data)
                        
                        # Send notification for high-value grants
                        if grant_data.get('typical_ticket_lakh', 0) > 10:  # > 10 lakhs
                            self.notification_manager.notify_new_grant(grant_data)
            
            logger.info(f"Enhanced extraction completed. Processed {grants_processed} grants")
            
            # Get processing statistics
            stats = self.enhanced_orchestrator.get_processing_stats()
            logger.info(f"Processing statistics: {stats}")
            
            return new_grants
            
        except Exception as e:
            logger.error(f"Enhanced grant extraction failed: {e}")
            self.notification_manager.notify_error(f"Grant extraction failed: {e}", "Grant Extraction")
            return []
    
    def run_traditional_scrapy_discovery(self):
        """Run traditional Scrapy-based discovery for known sources"""
        logger.info("Starting traditional Scrapy discovery")
        
        try:
            # Run spiders
            self.scrapy_runner.run_spiders(['birac', 'startup_india'])
            
            # Get recent grants count
            recent_grants = self.db_manager.get_grants(
                filters={'status': 'live'}, 
                limit=None
            )
            
            logger.info(f"Scrapy discovery completed. Total live grants: {len(recent_grants)}")
            
            return len(recent_grants)
            
        except Exception as e:
            logger.error(f"Scrapy discovery failed: {e}")
            self.notification_manager.notify_error(f"Scrapy discovery failed: {e}", "Scrapy")
            return 0
    
    def check_deadlines(self):
        """Check for upcoming grant deadlines"""
        try:
            # Get grants with deadlines in next 7 days
            week_from_now = datetime.now() + timedelta(days=7)
            
            grants = self.db_manager.get_grants(filters={'status': 'live'})
            expiring_soon = []
            
            for grant in grants:
                if grant.next_deadline_iso:
                    try:
                        deadline = datetime.fromisoformat(grant.next_deadline_iso.replace('Z', '+00:00'))
                        if deadline <= week_from_now:
                            expiring_soon.append({
                                'title': grant.title,
                                'agency': grant.agency,
                                'next_deadline_iso': grant.next_deadline_iso,
                                'typical_ticket_lakh': grant.typical_ticket_lakh
                            })
                    except:
                        continue
            
            if expiring_soon:
                self.notification_manager.slack.notify_deadline_reminder(expiring_soon)
                logger.info(f"Sent deadline reminders for {len(expiring_soon)} grants")
            
        except Exception as e:
            logger.error(f"Deadline check failed: {e}")
            self.notification_manager.notify_error(f"Deadline check failed: {e}", "Deadline Checker")
    
    async def run_comprehensive_discovery_cycle(self):
        """Run a comprehensive discovery cycle combining all methods"""
        logger.info("=== Starting Comprehensive Grant Discovery Cycle ===")
        
        cycle_start = datetime.now()
        
        # Step 1: Intelligent Source Discovery (if due)
        new_sources = []
        if (not self.last_source_discovery or 
            (datetime.now() - self.last_source_discovery).total_seconds() > 
            self.config['source_discovery_frequency_hours'] * 3600):
            
            new_sources = await self.run_intelligent_source_discovery()
        
        # Step 2: Enhanced Grant Extraction
        ai_grants = await self.run_enhanced_grant_extraction()
        
        # Step 3: Traditional Scrapy Discovery
        scrapy_grants_count = self.run_traditional_scrapy_discovery()
        
        # Step 4: Check Deadlines
        self.check_deadlines()
        
        # Generate comprehensive report
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        
        report = {
            'cycle_start': cycle_start.isoformat(),
            'cycle_duration_seconds': cycle_duration,
            'new_sources_discovered': len(new_sources),
            'ai_grants_extracted': len(ai_grants),
            'scrapy_grants_total': scrapy_grants_count,
            'orchestrator_stats': self.enhanced_orchestrator.get_processing_stats() if self.enhanced_orchestrator else {},
            'top_new_sources': new_sources[:5] if new_sources else []
        }
        
        logger.info(f"Discovery cycle completed in {cycle_duration:.1f} seconds")
        logger.info(f"Cycle report: {json.dumps(report, indent=2)}")
        
        # Send daily summary
        total_grants = len(ai_grants) + scrapy_grants_count
        self.notification_manager.notify_daily_summary(
            grants_found=total_grants,
            total_grants=total_grants,
            new_sources=len(new_sources)
        )
        
        logger.info("=== Comprehensive Discovery Cycle Completed ===")
        
        return report
    
    def schedule_tasks(self):
        """Schedule recurring tasks"""
        # Comprehensive discovery every 6 hours
        schedule.every(6).hours.do(lambda: asyncio.run(self.run_comprehensive_discovery_cycle()))
        
        # Source discovery daily at 2:00 AM IST
        schedule.every().day.at("02:00").do(lambda: asyncio.run(self.run_intelligent_source_discovery()))
        
        # Grant extraction every 6 hours
        schedule.every(6).hours.do(lambda: asyncio.run(self.run_enhanced_grant_extraction()))
        
        # Deadline check every Monday at 9:00 AM
        schedule.every().monday.at("09:00").do(self.check_deadlines)
        
        logger.info("Enhanced tasks scheduled:")
        logger.info("- Comprehensive discovery: Every 6 hours")
        logger.info("- Source discovery: Daily at 02:00 IST")
        logger.info("- Grant extraction: Every 6 hours")
        logger.info("- Deadline check: Monday 09:00 IST")
    
    def run_scheduler(self):
        """Run the task scheduler"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start_api_server(self):
        """Start the Flask API server"""
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting API server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    
    async def cleanup(self):
        """Clean up resources"""
        if self.source_discovery:
            await self.source_discovery.close()
        if self.enhanced_orchestrator:
            await self.enhanced_orchestrator.close()
    
    def run(self, mode='full'):
        """Run the enhanced application"""
        logger.info("🚀 Enhanced India Startup Grant Oracle Starting...")
        logger.info(f"Mode: {mode}")
        logger.info(f"Database URL: {os.getenv('DATABASE_URL', 'Not configured')}")
        logger.info(f"OpenAI API Key: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured'}")
        
        try:
            if mode == 'api':
                # Run only API server
                self.start_api_server()
                
            elif mode == 'scheduler':
                # Run only scheduler
                self.schedule_tasks()
                self.run_scheduler()
                
            elif mode == 'discovery':
                # Run discovery once
                asyncio.run(self.run_comprehensive_discovery_cycle())
                
            elif mode == 'source_discovery':
                # Run source discovery only
                asyncio.run(self.run_intelligent_source_discovery())
                
            elif mode == 'grant_extraction':
                # Run grant extraction only
                asyncio.run(self.run_enhanced_grant_extraction())
                
            elif mode == 'full':
                # Run everything
                self.schedule_tasks()
                
                # Start API server in a separate thread
                api_thread = threading.Thread(target=self.start_api_server)
                api_thread.daemon = True
                api_thread.start()
                
                logger.info("✅ Enhanced Grant Oracle fully operational!")
                logger.info("🔍 Intelligent source discovery enabled")
                logger.info("🤖 Enhanced AI-powered grant extraction active")
                logger.info("🌐 API server running in background")
                logger.info("⏰ Scheduler running in foreground")
                
                # Run scheduler in main thread
                self.run_scheduler()
            
            else:
                logger.error(f"Unknown mode: {mode}")
                print("Available modes: full, api, scheduler, discovery, source_discovery, grant_extraction")
                
        except KeyboardInterrupt:
            logger.info("Shutting down Enhanced Grant Oracle...")
            asyncio.run(self.cleanup())
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            asyncio.run(self.cleanup())
            raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced India Startup Grant Oracle')
    parser.add_argument('--mode', 
                       choices=['full', 'api', 'scheduler', 'discovery', 'source_discovery', 'grant_extraction'], 
                       default='full', 
                       help='Run mode')
    
    args = parser.parse_args()
    
    oracle = EnhancedGrantOracleMain()
    oracle.run(mode=args.mode)

if __name__ == "__main__":
    main()

