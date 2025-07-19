#!/usr/bin/env python3
"""
India Startup Grant Oracle - Main Application
Orchestrates the multi-agent system for grant discovery and notification
"""

import asyncio
import os
import sys
import schedule
import time
from datetime import datetime, timedelta
import threading

# Set Windows event loop policy for better async support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.models import DatabaseManager
from scrapers.scrapy_runner import ScrapyRunner
from agents.multi_model_orchestrator import MultiModelOrchestrator
from agents.simple_orchestrator import SimpleGrantOrchestrator
from notifications.slack_notifier import NotificationManager
from api.flask_app import app

class GrantOracleMain:
    """Main orchestrator for the India Startup Grant Oracle"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.scrapy_runner = ScrapyRunner()
        self.notification_manager = NotificationManager()
        self.magentic_orchestrator = None
        
        # Initialize database
        self.db_manager.create_tables()
        
        # Target URLs for discovery
        self.target_urls = [
            "https://seedfund.startupindia.gov.in/",
            "https://birac.nic.in/call_details.aspx",
            "https://tdb.gov.in/",
            "https://startup.karnataka.gov.in/",
            "https://startup.goa.gov.in/",
            "https://villgro.org/"
        ]
        
    async def initialize_magentic_one(self):
        """Initialize Magentic-One orchestrator"""
        try:
            self.magentic_orchestrator = MultiModelOrchestrator()
            print("Magentic-One orchestrator initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Magentic-One: {e}")
            print("Falling back to simplified orchestrator...")
            try:
                self.magentic_orchestrator = SimpleGrantOrchestrator()
                print("Simplified orchestrator initialized successfully")
            except Exception as e2:
                print(f"Failed to initialize simplified orchestrator: {e2}")
                self.notification_manager.notify_error(f"All orchestrator initialization failed: {e}", "Orchestrator")
    
    def run_scrapy_discovery(self):
        """Run Scrapy-based discovery"""
        print(f"Starting Scrapy discovery at {datetime.now()}")
        
        try:
            # Run spiders
            self.scrapy_runner.run_spiders(['birac', 'startup_india'])
            
            # Get recent grants count
            recent_grants = self.db_manager.get_grants(
                filters={'status': 'live'}, 
                limit=None
            )
            
            print(f"Scrapy discovery completed. Total grants: {len(recent_grants)}")
            
            # Send daily summary
            self.notification_manager.notify_daily_summary(
                grants_found=len(recent_grants), 
                total_grants=len(recent_grants)
            )
            
        except Exception as e:
            print(f"Scrapy discovery failed: {e}")
            self.notification_manager.notify_error(f"Scrapy discovery failed: {e}", "Scrapy")
    
    async def run_magentic_discovery(self):
        """Run Magentic-One based discovery"""
        if not self.magentic_orchestrator:
            await self.initialize_magentic_one()
            
        if not self.magentic_orchestrator:
            print("Magentic-One not available, skipping AI discovery")
            return
            
        print(f"Starting Magentic-One discovery at {datetime.now()}")
        
        try:
            # Process URLs one by one to avoid team state issues
            grants_processed = 0
            successful_urls = 0
            
            for url in self.target_urls:
                try:
                    print(f"Processing URL: {url}")
                    
                    # Add timeout for each URL processing - shorter timeout
                    async with asyncio.timeout(120):  # 2 minute timeout per URL
                        # Discover grants from single URL
                        grants_data = await self.magentic_orchestrator.discover_grants_from_url(url)
                        
                        if grants_data and isinstance(grants_data, list):
                            for grant in grants_data:
                                success = self.db_manager.upsert_grant(grant)
                                if success:
                                    grants_processed += 1
                                    # Send notification for new grant
                                    self.notification_manager.notify_new_grant(grant)
                        
                        successful_urls += 1
                        print(f"✅ Successfully processed {url}")
                    
                    # Add delay between URLs to avoid overwhelming
                    await asyncio.sleep(10)  # Increased to 10 seconds for rate limiting
                    
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout processing {url}")
                    continue
                except Exception as e:
                    print(f"❌ Error processing {url}: {e}")
                    continue
            
            print(f"Magentic-One discovery completed. Processed {grants_processed} grants from {successful_urls}/{len(self.target_urls)} URLs")
            
        except Exception as e:
            print(f"Magentic-One discovery failed: {e}")
            self.notification_manager.notify_error(f"Magentic-One discovery failed: {e}", "Magentic-One")
    
    def check_deadlines(self):
        """Check for upcoming grant deadlines"""
        try:
            # Get grants with deadlines in next 7 days
            week_from_now = datetime.now() + timedelta(days=7)
            # Ensure week_from_now is naive datetime for comparison
            if week_from_now.tzinfo:
                week_from_now = week_from_now.replace(tzinfo=None)
            
            grants = self.db_manager.get_grants(filters={'status': 'live'})
            expiring_soon = []
            
            for grant in grants:
                deadline_str = grant.next_deadline_iso
                if deadline_str is not None:
                    try:
                        # Convert SQLAlchemy column to string
                        deadline_str = str(deadline_str)
                        
                        # Handle both UTC and local time formats
                        if deadline_str.endswith('Z'):
                            deadline_str = deadline_str.replace('Z', '+00:00')
                        elif '+' not in deadline_str and 'T' in deadline_str:
                            # Assume UTC if no timezone info
                            deadline_str = deadline_str + '+00:00'
                        
                        deadline = datetime.fromisoformat(deadline_str)
                        # Convert to naive datetime for comparison
                        if deadline.tzinfo:
                            deadline = deadline.replace(tzinfo=None)
                        
                        if deadline <= week_from_now:
                            expiring_soon.append({
                                'title': grant.title,
                                'agency': grant.agency,
                                'next_deadline_iso': grant.next_deadline_iso,
                                'typical_ticket_lakh': grant.typical_ticket_lakh
                            })
                    except Exception as e:
                        print(f"Warning: Could not parse deadline for grant {grant.id}: {e}")
                        continue
            
            if expiring_soon:
                self.notification_manager.slack.notify_deadline_reminder(expiring_soon)
                print(f"Sent deadline reminders for {len(expiring_soon)} grants")
            
        except Exception as e:
            print(f"Deadline check failed: {e}")
            self.notification_manager.notify_error(f"Deadline check failed: {e}", "Deadline Checker")
    
    def run_daily_tasks(self):
        """Run all daily discovery tasks"""
        print("=== Starting Daily Grant Discovery Tasks ===")
        
        # Run Scrapy discovery
        self.run_scrapy_discovery()
        
        # Run Magentic-One discovery (async)
        try:
            asyncio.run(self.run_magentic_discovery())
        except Exception as e:
            print(f"Failed to run Magentic-One discovery: {e}")
        
        # Check deadlines
        self.check_deadlines()
        
        print("=== Daily Discovery Tasks Completed ===")
    
    def schedule_tasks(self):
        """Schedule recurring tasks"""
        # Daily discovery at 6:00 AM IST
        schedule.every().day.at("06:00").do(self.run_daily_tasks)
        
        # Deadline check every Monday at 9:00 AM
        schedule.every().monday.at("09:00").do(self.check_deadlines)
        
        print("Tasks scheduled:")
        print("- Daily discovery: 06:00 IST")
        print("- Deadline check: Monday 09:00 IST")
    
    def run_scheduler(self):
        """Run the task scheduler"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start_api_server(self):
        """Start the Flask API server"""
        port = int(os.environ.get('PORT', 5000))
        print(f"Starting API server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    
    def run(self, mode='full'):
        """Run the application"""
        print("🏗️ India Startup Grant Oracle Starting...")
        print(f"Mode: {mode}")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'Not configured')}")
        print(f"OpenAI API Key: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured'}")
        
        if mode == 'api':
            # Run only API server
            self.start_api_server()
            
        elif mode == 'scheduler':
            # Run only scheduler
            self.schedule_tasks()
            self.run_scheduler()
            
        elif mode == 'discovery':
            # Run discovery once
            self.run_daily_tasks()
            
        elif mode == 'full':
            # Run everything
            self.schedule_tasks()
            
            # Start API server in a separate thread
            api_thread = threading.Thread(target=self.start_api_server)
            api_thread.daemon = True
            api_thread.start()
            
            print("✅ Grant Oracle fully operational!")
            print("API server running in background")
            print("Scheduler running in foreground")
            
            # Run scheduler in main thread
            self.run_scheduler()
        
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: full, api, scheduler, discovery")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='India Startup Grant Oracle')
    parser.add_argument('--mode', choices=['full', 'api', 'scheduler', 'discovery'], 
                       default='full', help='Run mode')
    
    args = parser.parse_args()
    
    oracle = GrantOracleMain()
    oracle.run(mode=args.mode)

if __name__ == "__main__":
    main()

