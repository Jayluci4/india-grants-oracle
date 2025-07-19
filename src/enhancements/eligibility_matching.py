"""
Eligibility Matching Score Enhancement
Calculates how well a startup profile matches grant eligibility criteria
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timedelta


class EligibilityMatcher:
    """Calculate eligibility matching scores for startups against grants"""
    
    def __init__(self):
        # Scoring weights for different criteria
        self.weights = {
            'stage_match': 0.25,        # Startup stage alignment
            'sector_match': 0.20,       # Sector/industry alignment  
            'location_match': 0.15,     # Geographic eligibility
            'funding_match': 0.15,      # Funding amount alignment
            'age_match': 0.10,          # Company age requirements
            'size_match': 0.10,         # Company size requirements
            'special_criteria': 0.05    # Special eligibility criteria
        }
        
        # Stage mappings
        self.stage_mappings = {
            'ideation': ['idea', 'concept', 'ideation', 'pre-seed'],
            'mvp_prototype': ['mvp', 'prototype', 'poc', 'proof of concept', 'pilot'],
            'early_stage': ['early', 'seed', 'pre-series', 'validation'],
            'growth_stage': ['growth', 'series', 'scale', 'expansion', 'mature']
        }
        
        # Common sector mappings
        self.sector_mappings = {
            'technology': ['tech', 'software', 'it', 'digital', 'ai', 'ml', 'iot'],
            'healthcare': ['health', 'medical', 'pharma', 'biotech', 'life sciences'],
            'fintech': ['finance', 'banking', 'payments', 'insurance'],
            'agritech': ['agriculture', 'farming', 'food', 'agri'],
            'cleantech': ['clean', 'green', 'renewable', 'sustainability', 'climate'],
            'edtech': ['education', 'learning', 'training'],
            'mobility': ['transport', 'automotive', 'logistics', 'mobility']
        }
    
    def calculate_eligibility_score(self, startup_profile: Dict[str, Any], 
                                  grant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate eligibility matching score between startup and grant
        
        Args:
            startup_profile: Dictionary containing startup information
            grant: Dictionary containing grant information
            
        Returns:
            Dictionary with eligibility score and breakdown
        """
        scores = {}
        
        # Stage matching
        scores['stage_match'] = self._calculate_stage_match(
            startup_profile.get('stage'), 
            grant.get('bucket')
        )
        
        # Sector matching
        scores['sector_match'] = self._calculate_sector_match(
            startup_profile.get('sectors', []), 
            grant.get('sector_tags', [])
        )
        
        # Location matching
        scores['location_match'] = self._calculate_location_match(
            startup_profile.get('location'), 
            grant.get('state_scope')
        )
        
        # Funding amount matching
        scores['funding_match'] = self._calculate_funding_match(
            startup_profile.get('funding_needed'), 
            grant.get('typical_ticket_lakh'),
            grant.get('min_ticket_lakh'),
            grant.get('max_ticket_lakh')
        )
        
        # Company age matching
        scores['age_match'] = self._calculate_age_match(
            startup_profile.get('company_age_years'), 
            grant.get('eligibility_criteria', {})
        )
        
        # Company size matching
        scores['size_match'] = self._calculate_size_match(
            startup_profile.get('team_size'), 
            startup_profile.get('revenue_lakh'),
            grant.get('target_audience', {})
        )
        
        # Special criteria matching
        scores['special_criteria'] = self._calculate_special_criteria_match(
            startup_profile, 
            grant.get('eligibility_flags', [])
        )
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[criterion] * self.weights[criterion] 
            for criterion in scores
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, startup_profile, grant)
        
        return {
            'overall_score': round(overall_score, 2),
            'score_breakdown': scores,
            'recommendations': recommendations,
            'calculated_at': datetime.now().isoformat()
        }
    
    def _calculate_stage_match(self, startup_stage: Optional[str], 
                              grant_bucket: Optional[str]) -> float:
        """Calculate stage alignment score"""
        if not startup_stage or not grant_bucket:
            return 0.5  # Neutral score if information missing
        
        startup_stage_clean = startup_stage.lower().replace(' ', '_')
        grant_bucket_clean = grant_bucket.lower().replace(' ', '_')
        
        # Direct match
        if startup_stage_clean == grant_bucket_clean:
            return 1.0
        
        # Check stage mappings
        for stage_category, stage_keywords in self.stage_mappings.items():
            startup_in_category = any(keyword in startup_stage_clean for keyword in stage_keywords)
            grant_in_category = any(keyword in grant_bucket_clean for keyword in stage_keywords)
            
            if startup_in_category and grant_in_category:
                return 0.8
        
        # Adjacent stages get partial credit
        stage_order = ['ideation', 'mvp_prototype', 'early_stage', 'growth_stage']
        startup_idx = self._get_stage_index(startup_stage_clean, stage_order)
        grant_idx = self._get_stage_index(grant_bucket_clean, stage_order)
        
        if startup_idx is not None and grant_idx is not None:
            distance = abs(startup_idx - grant_idx)
            if distance == 1:
                return 0.6
            elif distance == 2:
                return 0.3
        
        return 0.1
    
    def _calculate_sector_match(self, startup_sectors: List[str], 
                               grant_sectors: List[str]) -> float:
        """Calculate sector alignment score"""
        if not startup_sectors or not grant_sectors:
            return 0.5
        
        # Check for direct matches
        startup_sectors_clean = [s.lower() for s in startup_sectors]
        grant_sectors_clean = [s.lower() for s in grant_sectors]
        
        direct_matches = len(set(startup_sectors_clean) & set(grant_sectors_clean))
        if direct_matches > 0:
            return min(1.0, direct_matches / len(startup_sectors_clean))
        
        # Check for category matches
        match_score = 0.0
        for startup_sector in startup_sectors_clean:
            for grant_sector in grant_sectors_clean:
                category_match = self._check_sector_category_match(startup_sector, grant_sector)
                match_score = max(match_score, category_match)
        
        return match_score
    
    def _calculate_location_match(self, startup_location: Optional[str], 
                                 grant_scope: Optional[str]) -> float:
        """Calculate location eligibility score"""
        if not startup_location or not grant_scope:
            return 0.5
        
        startup_location_clean = startup_location.lower()
        grant_scope_clean = grant_scope.lower()
        
        # National grants match everyone
        if 'national' in grant_scope_clean or 'india' in grant_scope_clean:
            return 1.0
        
        # State-specific grants
        if startup_location_clean in grant_scope_clean or grant_scope_clean in startup_location_clean:
            return 1.0
        
        # Partial matches for regions
        if any(region in grant_scope_clean for region in ['north', 'south', 'east', 'west']):
            return 0.3  # Would need more sophisticated region mapping
        
        return 0.1
    
    def _calculate_funding_match(self, funding_needed: Optional[float],
                                typical_amount: Optional[float],
                                min_amount: Optional[float], 
                                max_amount: Optional[float]) -> float:
        """Calculate funding amount alignment score"""
        if not funding_needed:
            return 0.5
        
        # Use typical amount if available, otherwise use range
        if typical_amount:
            target_amount = typical_amount
        elif min_amount and max_amount:
            target_amount = (min_amount + max_amount) / 2
        elif max_amount:
            target_amount = max_amount
        else:
            return 0.5
        
        # Calculate how well the amounts align
        ratio = min(funding_needed, target_amount) / max(funding_needed, target_amount)
        
        if ratio >= 0.8:
            return 1.0
        elif ratio >= 0.6:
            return 0.8
        elif ratio >= 0.4:
            return 0.6
        elif ratio >= 0.2:
            return 0.4
        else:
            return 0.2
    
    def _calculate_age_match(self, company_age: Optional[float], 
                            eligibility_criteria: Dict[str, Any]) -> float:
        """Calculate company age requirement match"""
        if not company_age:
            return 0.5
        
        max_age = eligibility_criteria.get('company_age_max')
        min_age = eligibility_criteria.get('company_age_min', 0)
        
        if max_age is None:
            return 0.8  # No age restriction
        
        if min_age <= company_age <= max_age:
            return 1.0
        elif company_age < min_age:
            return 0.3  # Too young
        else:
            # Too old - score decreases with age
            excess_years = company_age - max_age
            return max(0.1, 0.8 - (excess_years * 0.1))
    
    def _calculate_size_match(self, team_size: Optional[int], 
                             revenue: Optional[float],
                             target_audience: Dict[str, Any]) -> float:
        """Calculate company size requirement match"""
        scores = []
        
        # Team size check
        max_team_size = target_audience.get('team_size_max')
        if team_size and max_team_size:
            if team_size <= max_team_size:
                scores.append(1.0)
            else:
                excess_ratio = team_size / max_team_size
                scores.append(max(0.1, 1.0 - (excess_ratio - 1.0) * 0.5))
        
        # Revenue check
        max_revenue = target_audience.get('revenue_max')
        if revenue and max_revenue:
            if revenue <= max_revenue:
                scores.append(1.0)
            else:
                excess_ratio = revenue / max_revenue
                scores.append(max(0.1, 1.0 - (excess_ratio - 1.0) * 0.3))
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_special_criteria_match(self, startup_profile: Dict[str, Any], 
                                        eligibility_flags: List[str]) -> float:
        """Calculate special eligibility criteria match"""
        if not eligibility_flags:
            return 1.0
        
        matches = 0
        total_criteria = len(eligibility_flags)
        
        for flag in eligibility_flags:
            flag_lower = flag.lower()
            
            # Check various startup attributes
            if 'dpiit' in flag_lower and startup_profile.get('dpiit_recognized'):
                matches += 1
            elif 'women' in flag_lower and startup_profile.get('women_led'):
                matches += 1
            elif 'sc' in flag_lower or 'st' in flag_lower:
                if startup_profile.get('founder_category') in ['sc', 'st']:
                    matches += 1
            elif 'first_time' in flag_lower and startup_profile.get('first_time_entrepreneur'):
                matches += 1
            # Add more criteria as needed
        
        return matches / total_criteria if total_criteria > 0 else 1.0
    
    def _check_sector_category_match(self, startup_sector: str, grant_sector: str) -> float:
        """Check if sectors belong to the same category"""
        for category, keywords in self.sector_mappings.items():
            startup_in_category = any(keyword in startup_sector for keyword in keywords)
            grant_in_category = any(keyword in grant_sector for keyword in keywords)
            
            if startup_in_category and grant_in_category:
                return 0.7
        
        return 0.0
    
    def _get_stage_index(self, stage: str, stage_order: List[str]) -> Optional[int]:
        """Get the index of a stage in the stage order"""
        for i, stage_name in enumerate(stage_order):
            if stage_name in stage or any(keyword in stage for keyword in self.stage_mappings.get(stage_name, [])):
                return i
        return None
    
    def _generate_recommendations(self, scores: Dict[str, float], 
                                startup_profile: Dict[str, Any], 
                                grant: Dict[str, Any]) -> List[str]:
        """Generate recommendations to improve eligibility"""
        recommendations = []
        
        if scores['stage_match'] < 0.5:
            recommendations.append(f"Consider applying when your startup reaches {grant.get('bucket', 'appropriate')} stage")
        
        if scores['sector_match'] < 0.5:
            recommendations.append(f"This grant focuses on {', '.join(grant.get('sector_tags', []))} sectors")
        
        if scores['location_match'] < 0.5:
            recommendations.append(f"This grant is limited to {grant.get('state_scope', 'specific regions')}")
        
        if scores['funding_match'] < 0.5:
            funding_range = f"₹{grant.get('min_ticket_lakh', 'N/A')}L - ₹{grant.get('max_ticket_lakh', 'N/A')}L"
            recommendations.append(f"Grant funding range is {funding_range}")
        
        if scores['special_criteria'] < 0.8:
            recommendations.append("Review special eligibility criteria carefully")
        
        return recommendations


def calculate_startup_grant_match(startup_profile: Dict[str, Any], 
                                grant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate eligibility match between a startup and grant
    
    Args:
        startup_profile: Startup information
        grant: Grant information
        
    Returns:
        Eligibility matching results
    """
    matcher = EligibilityMatcher()
    return matcher.calculate_eligibility_score(startup_profile, grant)


if __name__ == "__main__":
    # Test the eligibility matching
    test_startup = {
        'stage': 'early_stage',
        'sectors': ['technology', 'fintech'],
        'location': 'Karnataka',
        'funding_needed': 50,
        'company_age_years': 2,
        'team_size': 8,
        'revenue_lakh': 10,
        'dpiit_recognized': True,
        'women_led': False
    }
    
    test_grant = {
        'bucket': 'Early Stage',
        'sector_tags': ['technology', 'financial'],
        'state_scope': 'national',
        'typical_ticket_lakh': 60,
        'min_ticket_lakh': 25,
        'max_ticket_lakh': 100,
        'eligibility_criteria': {'company_age_max': 5},
        'target_audience': {'team_size_max': 15, 'revenue_max': 50},
        'eligibility_flags': ['dpiit_recognized']
    }
    
    result = calculate_startup_grant_match(test_startup, test_grant)
    print(f"Overall Score: {result['overall_score']}")
    print(f"Score Breakdown: {result['score_breakdown']}")
    print(f"Recommendations: {result['recommendations']}")

