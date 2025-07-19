"""
Smart Deduplication with Fuzzy Matching Enhancement
Detects and handles duplicate grants across multiple sources
"""

from fuzzywuzzy import fuzz
from typing import Dict, Any, List, Tuple, Optional
import re
import logging


class GrantDeduplicator:
    """Smart deduplication system for grants using fuzzy matching"""
    
    def __init__(self, 
                 title_threshold: int = 85,
                 agency_threshold: int = 80,
                 amount_tolerance: float = 0.2):
        """
        Initialize the deduplicator
        
        Args:
            title_threshold: Minimum similarity score for titles (0-100)
            agency_threshold: Minimum similarity score for agencies (0-100)
            amount_tolerance: Maximum relative difference in funding amounts (0-1)
        """
        self.title_threshold = title_threshold
        self.agency_threshold = agency_threshold
        self.amount_tolerance = amount_tolerance
        
        # Common words to ignore in title comparison
        self.stop_words = {
            'scheme', 'fund', 'grant', 'startup', 'innovation', 'support',
            'programme', 'program', 'initiative', 'challenge', 'competition'
        }
    
    def find_duplicates(self, grants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find duplicate grants in a list
        
        Args:
            grants: List of grant dictionaries
            
        Returns:
            List of grants with duplicate information added
        """
        processed_grants = []
        duplicate_groups = []
        
        for i, grant in enumerate(grants):
            grant_copy = grant.copy()
            grant_copy['is_duplicate'] = False
            grant_copy['original_id'] = None
            
            # Check against all previously processed grants
            duplicate_found = False
            for j, processed_grant in enumerate(processed_grants):
                if self._are_duplicates(grant, processed_grant):
                    # Mark current grant as duplicate
                    grant_copy['is_duplicate'] = True
                    grant_copy['original_id'] = processed_grant['id']
                    
                    # Update duplicate group
                    self._update_duplicate_group(duplicate_groups, grant_copy, processed_grant)
                    duplicate_found = True
                    break
            
            if not duplicate_found:
                # This is an original grant
                processed_grants.append(grant_copy)
            else:
                # This is a duplicate, but we still add it to track the relationship
                processed_grants.append(grant_copy)
        
        return processed_grants
    
    def _are_duplicates(self, grant1: Dict[str, Any], grant2: Dict[str, Any]) -> bool:
        """
        Check if two grants are duplicates using fuzzy matching
        
        Args:
            grant1: First grant dictionary
            grant2: Second grant dictionary
            
        Returns:
            True if grants are likely duplicates
        """
        # Skip if one is already marked as duplicate of the other
        if (grant1.get('original_id') == grant2.get('id') or 
            grant2.get('original_id') == grant1.get('id')):
            return False
        
        # Compare titles
        title_similarity = self._compare_titles(
            grant1.get('title', ''), 
            grant2.get('title', '')
        )
        
        # Compare agencies
        agency_similarity = self._compare_agencies(
            grant1.get('agency', ''), 
            grant2.get('agency', '')
        )
        
        # Compare funding amounts
        amount_similarity = self._compare_amounts(
            grant1.get('typical_ticket_lakh'),
            grant2.get('typical_ticket_lakh'),
            grant1.get('max_ticket_lakh'),
            grant2.get('max_ticket_lakh')
        )
        
        # Determine if duplicates based on combined criteria
        is_duplicate = (
            title_similarity >= self.title_threshold and
            agency_similarity >= self.agency_threshold and
            amount_similarity
        )
        
        return is_duplicate
    
    def _compare_titles(self, title1: str, title2: str) -> int:
        """Compare grant titles using fuzzy matching"""
        if not title1 or not title2:
            return 0
        
        # Clean titles
        clean_title1 = self._clean_title(title1)
        clean_title2 = self._clean_title(title2)
        
        # Use token sort ratio for better matching of reordered words
        return fuzz.token_sort_ratio(clean_title1, clean_title2)
    
    def _compare_agencies(self, agency1: str, agency2: str) -> int:
        """Compare agency names using fuzzy matching"""
        if not agency1 or not agency2:
            return 0
        
        # Clean agency names
        clean_agency1 = self._clean_agency(agency1)
        clean_agency2 = self._clean_agency(agency2)
        
        return fuzz.ratio(clean_agency1, clean_agency2)
    
    def _compare_amounts(self, amount1: Optional[float], amount2: Optional[float],
                        max1: Optional[float], max2: Optional[float]) -> bool:
        """Compare funding amounts with tolerance"""
        # Use typical amounts first, fall back to max amounts
        amt1 = amount1 or max1
        amt2 = amount2 or max2
        
        if not amt1 or not amt2:
            return True  # If amounts are missing, don't use as discriminator
        
        # Calculate relative difference
        avg_amount = (amt1 + amt2) / 2
        difference = abs(amt1 - amt2)
        relative_diff = difference / avg_amount if avg_amount > 0 else 0
        
        return relative_diff <= self.amount_tolerance
    
    def _clean_title(self, title: str) -> str:
        """Clean and normalize title for comparison"""
        # Convert to lowercase
        clean = title.lower()
        
        # Remove common punctuation and extra spaces
        clean = re.sub(r'[^\w\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Remove stop words
        words = clean.split()
        filtered_words = [word for word in words if word not in self.stop_words]
        
        return ' '.join(filtered_words)
    
    def _clean_agency(self, agency: str) -> str:
        """Clean and normalize agency name for comparison"""
        # Convert to lowercase and remove extra spaces
        clean = agency.lower()
        clean = re.sub(r'[^\w\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Remove common agency suffixes/prefixes
        agency_words = ['ministry', 'department', 'government', 'govt', 'of', 'india']
        words = clean.split()
        filtered_words = [word for word in words if word not in agency_words]
        
        return ' '.join(filtered_words)
    
    def _update_duplicate_group(self, duplicate_groups: List[List[str]], 
                               duplicate_grant: Dict[str, Any], 
                               original_grant: Dict[str, Any]):
        """Update duplicate groups tracking"""
        duplicate_id = duplicate_grant['id']
        original_id = original_grant['id']
        
        # Find existing group or create new one
        group_found = False
        for group in duplicate_groups:
            if original_id in group:
                group.append(duplicate_id)
                group_found = True
                break
        
        if not group_found:
            duplicate_groups.append([original_id, duplicate_id])
    
    def get_best_grant_from_duplicates(self, grants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best grant from a group of duplicates
        
        Args:
            grants: List of duplicate grants
            
        Returns:
            The grant with highest confidence score
        """
        if not grants:
            return None
        
        if len(grants) == 1:
            return grants[0]
        
        # Sort by confidence score (highest first)
        sorted_grants = sorted(grants, 
                             key=lambda g: g.get('confidence', 0), 
                             reverse=True)
        
        best_grant = sorted_grants[0].copy()
        
        # Merge source URLs from all duplicates
        all_sources = []
        for grant in grants:
            sources = grant.get('source_urls', [])
            if isinstance(sources, list):
                all_sources.extend(sources)
            else:
                all_sources.append(str(sources))
        
        # Remove duplicates and update
        best_grant['source_urls'] = list(set(all_sources))
        
        # Add metadata about deduplication
        best_grant['duplicate_count'] = len(grants)
        best_grant['merged_from'] = [g['id'] for g in grants[1:]]
        
        return best_grant


def deduplicate_grants(grants: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Deduplicate a list of grants
    
    Args:
        grants: List of grant dictionaries
        
    Returns:
        Tuple of (deduplicated_grants, deduplication_stats)
    """
    deduplicator = GrantDeduplicator()
    
    # Find duplicates
    processed_grants = deduplicator.find_duplicates(grants)
    
    # Separate originals and duplicates
    original_grants = [g for g in processed_grants if not g.get('is_duplicate', False)]
    duplicate_grants = [g for g in processed_grants if g.get('is_duplicate', False)]
    
    # Generate statistics
    stats = {
        'total_input_grants': len(grants),
        'original_grants': len(original_grants),
        'duplicate_grants': len(duplicate_grants),
        'deduplication_rate': len(duplicate_grants) / len(grants) if grants else 0,
        'duplicate_pairs': []
    }
    
    # Track duplicate relationships
    for dup in duplicate_grants:
        stats['duplicate_pairs'].append({
            'duplicate_id': dup['id'],
            'original_id': dup['original_id'],
            'duplicate_title': dup.get('title', ''),
            'original_title': next((g['title'] for g in original_grants 
                                  if g['id'] == dup['original_id']), '')
        })
    
    return processed_grants, stats


if __name__ == "__main__":
    # Test the deduplication
    test_grants = [
        {
            'id': 'grant1',
            'title': 'Startup India Seed Fund Scheme',
            'agency': 'DPIIT, Government of India',
            'typical_ticket_lakh': 50,
            'confidence': 0.9
        },
        {
            'id': 'grant2', 
            'title': 'Startup India Seed Fund Scheme (SISFS)',
            'agency': 'DPIIT, GoI',
            'typical_ticket_lakh': 45,
            'confidence': 0.85
        },
        {
            'id': 'grant3',
            'title': 'BIRAC Innovation Grant',
            'agency': 'BIRAC',
            'typical_ticket_lakh': 75,
            'confidence': 0.8
        }
    ]
    
    deduplicated, stats = deduplicate_grants(test_grants)
    print(f"Deduplication Stats: {stats}")
    print(f"Processed Grants: {len(deduplicated)}")
    for grant in deduplicated:
        print(f"- {grant['id']}: {grant['title']} (duplicate: {grant.get('is_duplicate', False)})")

