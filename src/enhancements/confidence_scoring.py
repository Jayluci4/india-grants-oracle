"""
Confidence Scoring and Data Lineage Enhancement
Calculates confidence scores based on data source quality and completeness
"""

import re
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, Any, List


class ConfidenceScorer:
    """Calculate confidence scores and track data lineage for grants"""
    
    def __init__(self):
        # Base confidence scores for different source types
        self.source_type_scores = {
            'official_portal': 0.9,      # .gov.in domains
            'government_website': 0.85,   # Other government sites
            'news_article': 0.6,          # News sources
            'blog_post': 0.4,            # Blog posts
            'social_media': 0.3,         # Social media posts
            'unknown': 0.5               # Unknown source type
        }
        
        # Confidence modifiers
        self.modifiers = {
            'has_deadline': 0.1,         # Clear deadline found
            'has_amount': 0.1,           # Funding amount specified
            'has_eligibility': 0.05,     # Eligibility criteria found
            'has_contact': 0.05,         # Contact information available
            'recent_update': 0.05,       # Recently updated (within 6 months)
            'multiple_sources': 0.1,     # Confirmed by multiple sources
            'structured_data': 0.1,      # Extracted from structured data (API/JSON)
            'pdf_extraction': -0.1,      # Extracted from PDF (less reliable)
            'manual_entry': -0.05        # Manually entered data
        }
    
    def calculate_confidence_score(self, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate confidence score and data lineage for a grant
        
        Args:
            grant_data: Dictionary containing grant information
            
        Returns:
            Dictionary with confidence score and data lineage
        """
        lineage = {
            'source_type': self._determine_source_type(grant_data.get('source_urls', [])),
            'extraction_method': grant_data.get('extraction_method', 'unknown'),
            'data_completeness': {},
            'quality_indicators': [],
            'confidence_factors': []
        }
        
        # Start with base score from source type
        base_score = self.source_type_scores.get(lineage['source_type'], 0.5)
        confidence_score = base_score
        
        # Check data completeness
        completeness = self._assess_data_completeness(grant_data)
        lineage['data_completeness'] = completeness
        
        # Apply modifiers based on data quality
        modifiers_applied = []
        
        # Has clear deadline
        if grant_data.get('next_deadline_iso') and grant_data.get('deadline_type') != 'unknown':
            confidence_score += self.modifiers['has_deadline']
            modifiers_applied.append('has_deadline')
            lineage['quality_indicators'].append('clear_deadline_found')
        
        # Has funding amount
        if grant_data.get('typical_ticket_lakh') or grant_data.get('max_ticket_lakh'):
            confidence_score += self.modifiers['has_amount']
            modifiers_applied.append('has_amount')
            lineage['quality_indicators'].append('funding_amount_specified')
        
        # Has eligibility criteria
        if grant_data.get('eligibility_flags') and len(grant_data['eligibility_flags']) > 0:
            confidence_score += self.modifiers['has_eligibility']
            modifiers_applied.append('has_eligibility')
            lineage['quality_indicators'].append('eligibility_criteria_found')
        
        # Multiple sources
        source_urls = grant_data.get('source_urls', [])
        if isinstance(source_urls, list) and len(source_urls) > 1:
            confidence_score += self.modifiers['multiple_sources']
            modifiers_applied.append('multiple_sources')
            lineage['quality_indicators'].append('multiple_sources_confirmed')
        
        # Extraction method modifiers
        extraction_method = grant_data.get('extraction_method', 'unknown')
        if extraction_method == 'api' or extraction_method == 'structured':
            confidence_score += self.modifiers['structured_data']
            modifiers_applied.append('structured_data')
            lineage['quality_indicators'].append('structured_data_source')
        elif extraction_method == 'pdf':
            confidence_score += self.modifiers['pdf_extraction']
            modifiers_applied.append('pdf_extraction')
            lineage['quality_indicators'].append('pdf_extraction_used')
        
        # Ensure score is between 0 and 1
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        lineage['confidence_factors'] = modifiers_applied
        lineage['calculated_at'] = datetime.now().isoformat()
        lineage['base_score'] = base_score
        lineage['final_score'] = confidence_score
        
        return {
            'confidence': round(confidence_score, 2),
            'data_lineage': lineage
        }
    
    def _determine_source_type(self, source_urls: List[str]) -> str:
        """Determine the type of source based on URLs"""
        if not source_urls:
            return 'unknown'
        
        # Check the primary source URL
        primary_url = source_urls[0] if isinstance(source_urls, list) else str(source_urls)
        
        try:
            domain = urlparse(primary_url).netloc.lower()
            
            # Government domains
            if '.gov.in' in domain or '.nic.in' in domain:
                return 'official_portal'
            elif any(gov_indicator in domain for gov_indicator in ['.gov.', 'government', 'ministry']):
                return 'government_website'
            elif any(news_indicator in domain for news_indicator in ['times', 'hindu', 'economic', 'business', 'news']):
                return 'news_article'
            elif any(blog_indicator in domain for blog_indicator in ['blog', 'medium', 'wordpress']):
                return 'blog_post'
            elif any(social_indicator in domain for social_indicator in ['facebook', 'twitter', 'linkedin', 'instagram']):
                return 'social_media'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _assess_data_completeness(self, grant_data: Dict[str, Any]) -> Dict[str, bool]:
        """Assess completeness of grant data"""
        return {
            'has_title': bool(grant_data.get('title')),
            'has_agency': bool(grant_data.get('agency')),
            'has_funding_amount': bool(grant_data.get('typical_ticket_lakh') or grant_data.get('max_ticket_lakh')),
            'has_deadline': bool(grant_data.get('next_deadline_iso')),
            'has_eligibility': bool(grant_data.get('eligibility_flags')),
            'has_sector_tags': bool(grant_data.get('sector_tags')),
            'has_source_url': bool(grant_data.get('source_urls')),
            'has_bucket': bool(grant_data.get('bucket'))
        }


def enhance_grant_with_confidence(grant_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance grant data with confidence scoring and data lineage
    
    Args:
        grant_data: Original grant data dictionary
        
    Returns:
        Enhanced grant data with confidence and lineage information
    """
    scorer = ConfidenceScorer()
    confidence_data = scorer.calculate_confidence_score(grant_data)
    
    # Update the grant data
    enhanced_data = grant_data.copy()
    enhanced_data['confidence'] = confidence_data['confidence']
    enhanced_data['data_lineage'] = confidence_data['data_lineage']
    
    return enhanced_data


if __name__ == "__main__":
    # Test the confidence scoring
    test_grant = {
        'title': 'Test Grant',
        'agency': 'Test Agency',
        'typical_ticket_lakh': 50,
        'next_deadline_iso': '2025-12-31T23:59:59Z',
        'eligibility_flags': ['startup', 'tech'],
        'sector_tags': ['technology'],
        'source_urls': ['https://example.gov.in/grant'],
        'extraction_method': 'api'
    }
    
    enhanced = enhance_grant_with_confidence(test_grant)
    print(f"Confidence Score: {enhanced['confidence']}")
    print(f"Data Lineage: {enhanced['data_lineage']}")

