import scrapy
import hashlib
import json
from datetime import datetime
from urllib.parse import urljoin

class BaseGrantSpider(scrapy.Spider):
    """Base spider class for grant scraping"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grants_found = []
        
    def generate_grant_id(self, title, agency):
        """Generate unique ID for grant based on title and agency"""
        combined = f"{title}_{agency}".lower().replace(" ", "_")
        return hashlib.md5(combined.encode()).hexdigest()[:12]
        
    def create_grant_item(self, **kwargs):
        """Create standardized grant item"""
        required_fields = ['title', 'agency']
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"Required field '{field}' missing")
                
        grant_id = self.generate_grant_id(kwargs['title'], kwargs['agency'])
        
        item = {
            'id': grant_id,
            'title': kwargs.get('title'),
            'bucket': kwargs.get('bucket', 'Unknown'),
            'instrument': kwargs.get('instrument', ['grant']),
            'min_ticket_lakh': kwargs.get('min_ticket_lakh'),
            'max_ticket_lakh': kwargs.get('max_ticket_lakh'),
            'typical_ticket_lakh': kwargs.get('typical_ticket_lakh'),
            'deadline_type': kwargs.get('deadline_type', 'rolling'),
            'next_deadline_iso': kwargs.get('next_deadline_iso'),
            'eligibility_flags': kwargs.get('eligibility_flags', []),
            'sector_tags': kwargs.get('sector_tags', ['tech_agnostic']),
            'state_scope': kwargs.get('state_scope', 'national'),
            'agency': kwargs.get('agency'),
            'source_urls': kwargs.get('source_urls', []),
            'confidence': kwargs.get('confidence', 0.8),
            'last_seen_iso': datetime.utcnow().isoformat(),
            'created_iso': datetime.utcnow().isoformat(),
            'status': kwargs.get('status', 'live')
        }
        
        return item
        
    def extract_amount_from_text(self, text):
        """Extract amount in lakhs from text"""
        import re
        
        # Common patterns for amounts
        patterns = [
            r'₹\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac)',
            r'Rs\.?\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac)',
            r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)',
            r'₹\s*(\d+(?:\.\d+)?)\s*(?:crore|cr)',
            r'Rs\.?\s*(\d+(?:\.\d+)?)\s*(?:crore|cr)',
            r'(\d+(?:\.\d+)?)\s*(?:crore|cr)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                if 'crore' in pattern or 'cr' in pattern:
                    amount *= 100  # Convert crores to lakhs
                return amount
                
        return None
        
    def extract_deadline_from_text(self, text):
        """Extract deadline from text"""
        import re
        from dateutil import parser
        
        # Common date patterns
        date_patterns = [
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
            r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{2,4})\b',
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{2,4})\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    parsed_date = parser.parse(match)
                    return parsed_date.isoformat()
                except:
                    continue
                    
        return None

