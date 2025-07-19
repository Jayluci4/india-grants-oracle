import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import sys
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.birac_spider import BiracSpider
from scrapers.startup_india_spider import StartupIndiaSpider
from database.models import DatabaseManager

class ScrapyRunner:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.db_manager.create_tables()
        
    def run_spiders(self, spider_names=None):
        """Run specified spiders or all spiders"""
        if spider_names is None:
            spider_names = ['birac', 'startup_india']
            
        # Configure Scrapy settings
        settings = {
            'USER_AGENT': 'India Grants Oracle Bot 1.0',
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 2,
            'RANDOMIZE_DOWNLOAD_DELAY': True,
            'CONCURRENT_REQUESTS': 1,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 1,
            'AUTOTHROTTLE_MAX_DELAY': 10,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
            'LOG_LEVEL': 'INFO',
            'TWISTED_REACTOR': 'twisted.internet.selectreactor.SelectReactor'
        }
        
        process = CrawlerProcess(settings)
        
        # Add spiders to process
        spider_classes = {
            'birac': BiracSpider,
            'startup_india': StartupIndiaSpider
        }
        
        for spider_name in spider_names:
            if spider_name in spider_classes:
                process.crawl(spider_classes[spider_name])
        
        # Start the crawling process
        process.start()
        
    def process_spider_results(self, spider_results):
        """Process results from spiders and save to database"""
        grants_saved = 0
        
        for grant_data in spider_results:
            try:
                success = self.db_manager.upsert_grant(grant_data)
                if success:
                    grants_saved += 1
                    print(f"Saved grant: {grant_data['title']}")
                else:
                    print(f"Failed to save grant: {grant_data['title']}")
            except Exception as e:
                print(f"Error processing grant {grant_data.get('title', 'Unknown')}: {e}")
        
        print(f"Total grants saved: {grants_saved}")
        return grants_saved

if __name__ == "__main__":
    runner = ScrapyRunner()
    runner.run_spiders()

