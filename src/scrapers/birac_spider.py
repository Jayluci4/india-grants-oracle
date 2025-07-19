import scrapy
from .base_spider import BaseGrantSpider

class BiracSpider(BaseGrantSpider):
    name = 'birac'
    allowed_domains = ['birac.nic.in']
    start_urls = [
        'https://birac.nic.in/call_details.aspx',
        'https://birac.nic.in/webcontent/1610_1_AboutBIRAC.aspx'
    ]
    
    def parse(self, response):
        """Parse BIRAC main page"""
        # Extract grant information from tables and lists
        grant_sections = response.css('.content-area, .main-content, table')
        
        for section in grant_sections:
            # Look for grant titles and details
            titles = section.css('h3, h4, .title, strong::text').getall()
            descriptions = section.css('p, td, .description::text').getall()
            
            for i, title in enumerate(titles):
                title = title.strip()
                if self.is_grant_title(title):
                    # Extract associated description
                    description = ""
                    if i < len(descriptions):
                        description = descriptions[i].strip()
                    
                    # Extract amount information
                    amount_text = f"{title} {description}"
                    min_amount = self.extract_amount_from_text(amount_text)
                    max_amount = min_amount  # Often same for BIRAC grants
                    
                    # Extract deadline
                    deadline = self.extract_deadline_from_text(description)
                    
                    # Determine grant bucket based on title/description
                    bucket = self.determine_bucket(title, description)
                    
                    grant_item = self.create_grant_item(
                        title=title,
                        agency="BIRAC, DBT, GoI",
                        bucket=bucket,
                        instrument=["grant"],
                        min_ticket_lakh=min_amount,
                        max_ticket_lakh=max_amount,
                        typical_ticket_lakh=min_amount,
                        deadline_type="batch_call",
                        next_deadline_iso=deadline,
                        eligibility_flags=["biotech_startup", "innovation_focus"],
                        sector_tags=["biotechnology", "healthcare", "life_sciences"],
                        state_scope="national",
                        source_urls=[response.url],
                        confidence=0.85
                    )
                    
                    self.grants_found.append(grant_item)
                    yield grant_item
        
        # Follow pagination links
        next_page = response.css('a[href*="page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def is_grant_title(self, title):
        """Check if text looks like a grant title"""
        grant_keywords = [
            'grant', 'fund', 'scheme', 'support', 'award', 'fellowship',
            'seed', 'startup', 'innovation', 'research', 'development',
            'biotechnology', 'biotech', 'life sciences', 'healthcare'
        ]
        
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in grant_keywords) and len(title) > 10
    
    def determine_bucket(self, title, description):
        """Determine grant bucket based on content"""
        content = f"{title} {description}".lower()
        
        if any(word in content for word in ['seed', 'early', 'startup', 'ideation']):
            return "Early Stage"
        elif any(word in content for word in ['prototype', 'mvp', 'proof']):
            return "MVP Prototype"
        elif any(word in content for word in ['growth', 'scale', 'expansion']):
            return "Growth"
        elif any(word in content for word in ['infrastructure', 'facility', 'equipment']):
            return "Infra"
        else:
            return "Early Stage"  # Default for BIRAC

