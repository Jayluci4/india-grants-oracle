import scrapy
from .base_spider import BaseGrantSpider

class StartupIndiaSpider(BaseGrantSpider):
    name = 'startup_india'
    allowed_domains = ['startupindia.gov.in', 'seedfund.startupindia.gov.in']
    start_urls = [
        'https://seedfund.startupindia.gov.in/',
        'https://www.startupindia.gov.in/content/sih/en/government-schemes.html'
    ]
    
    def parse(self, response):
        """Parse Startup India pages"""
        # Look for scheme cards, sections, and grant information
        scheme_sections = response.css('.scheme-card, .card, .content-section, .main-content')
        
        for section in scheme_sections:
            title = section.css('h1, h2, h3, .title, .card-title::text').get()
            if title:
                title = title.strip()
                
                # Get description
                description_parts = section.css('p, .description, .card-text::text').getall()
                description = ' '.join([part.strip() for part in description_parts if part.strip()])
                
                # Extract key information
                content = f"{title} {description}"
                
                # Check if this is a grant/funding scheme
                if self.is_funding_scheme(content):
                    # Extract amounts
                    min_amount = self.extract_amount_from_text(content)
                    max_amount = self.extract_max_amount(content)
                    
                    # Extract deadline
                    deadline = self.extract_deadline_from_text(content)
                    
                    # Determine characteristics
                    bucket = self.determine_bucket_from_content(content)
                    eligibility = self.extract_eligibility(content)
                    
                    grant_item = self.create_grant_item(
                        title=title,
                        agency="DPIIT, GoI",
                        bucket=bucket,
                        instrument=self.determine_instrument(content),
                        min_ticket_lakh=min_amount,
                        max_ticket_lakh=max_amount or min_amount,
                        typical_ticket_lakh=max_amount or min_amount,
                        deadline_type=self.determine_deadline_type(content),
                        next_deadline_iso=deadline,
                        eligibility_flags=eligibility,
                        sector_tags=["tech_agnostic"],
                        state_scope="national",
                        source_urls=[response.url],
                        confidence=0.9
                    )
                    
                    self.grants_found.append(grant_item)
                    yield grant_item
        
        # Follow links to detailed pages
        detail_links = response.css('a[href*="scheme"], a[href*="fund"], a[href*="grant"]::attr(href)').getall()
        for link in detail_links[:5]:  # Limit to avoid too many requests
            yield response.follow(link, self.parse)
    
    def is_funding_scheme(self, content):
        """Check if content describes a funding scheme"""
        funding_keywords = [
            'seed fund', 'grant', 'funding', 'financial support', 'investment',
            'scheme', 'startup fund', 'venture', 'capital', 'loan', 'subsidy'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in funding_keywords)
    
    def extract_max_amount(self, content):
        """Extract maximum amount, looking for ranges"""
        import re
        
        # Look for range patterns like "20 lakh to 70 lakh"
        range_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)\s*to\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac)',
            r'₹\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac)\s*-\s*₹\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac)',
            r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:lakh|lac)'
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return float(match.group(2))  # Return the higher amount
                
        return None
    
    def determine_bucket_from_content(self, content):
        """Determine bucket based on content analysis"""
        content_lower = content.lower()
        
        if 'seed' in content_lower:
            return "Early Stage"
        elif any(word in content_lower for word in ['prototype', 'mvp', 'pilot']):
            return "MVP Prototype"
        elif any(word in content_lower for word in ['growth', 'scale', 'expansion']):
            return "Growth"
        else:
            return "Early Stage"
    
    def extract_eligibility(self, content):
        """Extract eligibility criteria"""
        eligibility = []
        content_lower = content.lower()
        
        if 'dpiit' in content_lower or 'recognised' in content_lower:
            eligibility.append('dpiit_recognised')
        if 'indian' in content_lower:
            eligibility.append('indian_promoters')
        if '2 year' in content_lower or 'two year' in content_lower:
            eligibility.append('<2_years')
        if 'woman' in content_lower or 'female' in content_lower:
            eligibility.append('women_led')
            
        return eligibility
    
    def determine_instrument(self, content):
        """Determine funding instrument type"""
        content_lower = content.lower()
        
        instruments = []
        if 'grant' in content_lower:
            instruments.append('grant')
        if 'loan' in content_lower:
            instruments.append('soft_loan')
        if 'debenture' in content_lower or 'convertible' in content_lower:
            instruments.append('convertible_debenture')
        if 'equity' in content_lower:
            instruments.append('equity')
            
        return instruments if instruments else ['grant']
    
    def determine_deadline_type(self, content):
        """Determine deadline type"""
        content_lower = content.lower()
        
        if 'rolling' in content_lower or 'continuous' in content_lower:
            return 'rolling'
        elif 'annual' in content_lower or 'yearly' in content_lower:
            return 'annual'
        elif 'batch' in content_lower or 'call' in content_lower:
            return 'batch_call'
        else:
            return 'rolling'

