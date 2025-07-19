"""
Application Complexity Indicator Enhancement
Calculates how complex the application process is for each grant
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class ApplicationComplexityAnalyzer:
    """Analyze and score application complexity for grants"""
    
    def __init__(self):
        # Complexity scoring factors
        self.complexity_factors = {
            'document_requirements': {
                'weight': 0.25,
                'simple': ['basic_info', 'pitch_deck', 'business_plan'],
                'medium': ['financial_statements', 'legal_documents', 'references'],
                'complex': ['detailed_projections', 'technical_specifications', 'compliance_certificates'],
                'very_complex': ['audited_financials', 'regulatory_approvals', 'patent_documents']
            },
            'application_stages': {
                'weight': 0.20,
                'simple': 1,      # Single stage
                'medium': 2,      # Two stages
                'complex': 3,     # Three stages
                'very_complex': 4 # Four or more stages
            },
            'evaluation_process': {
                'weight': 0.20,
                'simple': ['online_form', 'automated_screening'],
                'medium': ['document_review', 'basic_interview'],
                'complex': ['presentation', 'site_visit', 'panel_interview'],
                'very_complex': ['multiple_rounds', 'due_diligence', 'board_approval']
            },
            'timeline_duration': {
                'weight': 0.15,
                'simple': 30,     # Days - quick turnaround
                'medium': 90,     # Days - standard process
                'complex': 180,   # Days - lengthy process
                'very_complex': 365 # Days - very long process
            },
            'eligibility_criteria': {
                'weight': 0.10,
                'simple': 3,      # Few criteria
                'medium': 6,      # Moderate criteria
                'complex': 10,    # Many criteria
                'very_complex': 15 # Extensive criteria
            },
            'funding_amount': {
                'weight': 0.10,
                'simple': 10,     # Lakh - smaller amounts
                'medium': 50,     # Lakh - medium amounts
                'complex': 200,   # Lakh - large amounts
                'very_complex': 500 # Lakh - very large amounts
            }
        }
        
        # Keywords for different complexity levels
        self.complexity_keywords = {
            'simple': [
                'online application', 'simple form', 'basic requirements',
                'quick process', 'fast track', 'streamlined'
            ],
            'medium': [
                'standard process', 'document submission', 'review process',
                'evaluation committee', 'shortlisting'
            ],
            'complex': [
                'detailed application', 'multiple stages', 'presentation required',
                'site visit', 'panel interview', 'technical evaluation'
            ],
            'very_complex': [
                'comprehensive review', 'due diligence', 'multiple rounds',
                'board approval', 'regulatory compliance', 'audit required'
            ]
        }
    
    def calculate_complexity_score(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate application complexity score for a grant
        
        Args:
            grant: Grant dictionary with application information
            
        Returns:
            Dictionary with complexity score and analysis
        """
        complexity_analysis = {
            'overall_complexity': 'medium',
            'complexity_score': 0.5,  # 0-1 scale
            'factor_scores': {},
            'complexity_reasons': [],
            'estimated_effort_hours': 0,
            'calculated_at': datetime.now().isoformat()
        }
        
        # Analyze each complexity factor
        total_weighted_score = 0.0
        
        # Document requirements
        doc_score = self._analyze_document_requirements(grant)
        complexity_analysis['factor_scores']['document_requirements'] = doc_score
        total_weighted_score += doc_score['score'] * self.complexity_factors['document_requirements']['weight']
        
        # Application stages
        stages_score = self._analyze_application_stages(grant)
        complexity_analysis['factor_scores']['application_stages'] = stages_score
        total_weighted_score += stages_score['score'] * self.complexity_factors['application_stages']['weight']
        
        # Evaluation process
        eval_score = self._analyze_evaluation_process(grant)
        complexity_analysis['factor_scores']['evaluation_process'] = eval_score
        total_weighted_score += eval_score['score'] * self.complexity_factors['evaluation_process']['weight']
        
        # Timeline duration
        timeline_score = self._analyze_timeline_duration(grant)
        complexity_analysis['factor_scores']['timeline_duration'] = timeline_score
        total_weighted_score += timeline_score['score'] * self.complexity_factors['timeline_duration']['weight']
        
        # Eligibility criteria
        eligibility_score = self._analyze_eligibility_criteria(grant)
        complexity_analysis['factor_scores']['eligibility_criteria'] = eligibility_score
        total_weighted_score += eligibility_score['score'] * self.complexity_factors['eligibility_criteria']['weight']
        
        # Funding amount
        funding_score = self._analyze_funding_amount(grant)
        complexity_analysis['factor_scores']['funding_amount'] = funding_score
        total_weighted_score += funding_score['score'] * self.complexity_factors['funding_amount']['weight']
        
        # Calculate overall complexity
        complexity_analysis['complexity_score'] = round(total_weighted_score, 2)
        complexity_analysis['overall_complexity'] = self._score_to_complexity_level(total_weighted_score)
        
        # Estimate effort hours
        complexity_analysis['estimated_effort_hours'] = self._estimate_effort_hours(total_weighted_score)
        
        # Generate complexity reasons
        complexity_analysis['complexity_reasons'] = self._generate_complexity_reasons(complexity_analysis['factor_scores'])
        
        return complexity_analysis
    
    def _analyze_document_requirements(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document requirements complexity"""
        eligibility_flags = grant.get('eligibility_flags', [])
        
        # Count document-related requirements
        doc_keywords = {
            'simple': ['application form', 'basic info', 'pitch deck'],
            'medium': ['business plan', 'financial statements', 'references'],
            'complex': ['detailed projections', 'technical specs', 'certificates'],
            'very_complex': ['audited financials', 'regulatory approvals', 'patents']
        }
        
        complexity_level = 'simple'
        doc_count = 0
        
        for flag in eligibility_flags:
            flag_lower = str(flag).lower()
            for level, keywords in doc_keywords.items():
                if any(keyword in flag_lower for keyword in keywords):
                    complexity_level = level
                    doc_count += 1
        
        # Convert to score
        level_scores = {'simple': 0.2, 'medium': 0.4, 'complex': 0.7, 'very_complex': 1.0}
        score = level_scores.get(complexity_level, 0.4)
        
        return {
            'score': score,
            'level': complexity_level,
            'document_count': doc_count,
            'details': f"Estimated {doc_count} document types required"
        }
    
    def _analyze_application_stages(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze number of application stages"""
        # Estimate stages based on grant type and funding amount
        funding_amount = grant.get('typical_ticket_lakh', 0) or grant.get('max_ticket_lakh', 0)
        
        if funding_amount < 10:
            stages = 1
        elif funding_amount < 50:
            stages = 2
        elif funding_amount < 200:
            stages = 3
        else:
            stages = 4
        
        # Convert to score
        if stages == 1:
            score = 0.2
            level = 'simple'
        elif stages == 2:
            score = 0.4
            level = 'medium'
        elif stages == 3:
            score = 0.7
            level = 'complex'
        else:
            score = 1.0
            level = 'very_complex'
        
        return {
            'score': score,
            'level': level,
            'estimated_stages': stages,
            'details': f"Estimated {stages} application stages"
        }
    
    def _analyze_evaluation_process(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze evaluation process complexity"""
        agency = grant.get('agency', '').lower()
        funding_amount = grant.get('typical_ticket_lakh', 0) or grant.get('max_ticket_lakh', 0)
        
        # Government agencies typically have more complex processes
        if 'government' in agency or 'ministry' in agency:
            if funding_amount > 100:
                level = 'very_complex'
                score = 1.0
            else:
                level = 'complex'
                score = 0.7
        else:
            if funding_amount > 50:
                level = 'medium'
                score = 0.4
            else:
                level = 'simple'
                score = 0.2
        
        return {
            'score': score,
            'level': level,
            'details': f"Evaluation complexity based on agency type and funding amount"
        }
    
    def _analyze_timeline_duration(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze application timeline duration"""
        deadline_type = grant.get('deadline_type', 'unknown')
        
        # Estimate timeline based on deadline type
        if deadline_type == 'rolling':
            estimated_days = 45
            level = 'medium'
        elif deadline_type == 'batch_call':
            estimated_days = 120
            level = 'complex'
        elif deadline_type == 'annual':
            estimated_days = 180
            level = 'complex'
        else:
            estimated_days = 90
            level = 'medium'
        
        # Convert to score
        if estimated_days <= 30:
            score = 0.2
        elif estimated_days <= 90:
            score = 0.4
        elif estimated_days <= 180:
            score = 0.7
        else:
            score = 1.0
        
        return {
            'score': score,
            'level': level,
            'estimated_days': estimated_days,
            'details': f"Estimated {estimated_days} days process duration"
        }
    
    def _analyze_eligibility_criteria(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze eligibility criteria complexity"""
        eligibility_flags = grant.get('eligibility_flags', [])
        criteria_count = len(eligibility_flags)
        
        if criteria_count <= 3:
            score = 0.2
            level = 'simple'
        elif criteria_count <= 6:
            score = 0.4
            level = 'medium'
        elif criteria_count <= 10:
            score = 0.7
            level = 'complex'
        else:
            score = 1.0
            level = 'very_complex'
        
        return {
            'score': score,
            'level': level,
            'criteria_count': criteria_count,
            'details': f"{criteria_count} eligibility criteria"
        }
    
    def _analyze_funding_amount(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze funding amount impact on complexity"""
        funding_amount = grant.get('typical_ticket_lakh', 0) or grant.get('max_ticket_lakh', 0)
        
        if funding_amount <= 10:
            score = 0.2
            level = 'simple'
        elif funding_amount <= 50:
            score = 0.4
            level = 'medium'
        elif funding_amount <= 200:
            score = 0.7
            level = 'complex'
        else:
            score = 1.0
            level = 'very_complex'
        
        return {
            'score': score,
            'level': level,
            'funding_amount': funding_amount,
            'details': f"₹{funding_amount}L funding amount"
        }
    
    def _score_to_complexity_level(self, score: float) -> str:
        """Convert numerical score to complexity level"""
        if score <= 0.3:
            return 'simple'
        elif score <= 0.5:
            return 'medium'
        elif score <= 0.8:
            return 'complex'
        else:
            return 'very_complex'
    
    def _estimate_effort_hours(self, score: float) -> int:
        """Estimate effort hours based on complexity score"""
        base_hours = {
            'simple': 8,      # 1 day
            'medium': 24,     # 3 days
            'complex': 56,    # 1 week
            'very_complex': 120 # 2-3 weeks
        }
        
        level = self._score_to_complexity_level(score)
        return base_hours[level]
    
    def _generate_complexity_reasons(self, factor_scores: Dict[str, Any]) -> List[str]:
        """Generate reasons for complexity rating"""
        reasons = []
        
        for factor, score_info in factor_scores.items():
            if score_info['score'] >= 0.7:
                reasons.append(f"High {factor.replace('_', ' ')}: {score_info['details']}")
        
        if not reasons:
            reasons.append("Standard application process with moderate requirements")
        
        return reasons


def calculate_application_complexity(grant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate application complexity for a grant
    
    Args:
        grant: Grant dictionary
        
    Returns:
        Complexity analysis results
    """
    analyzer = ApplicationComplexityAnalyzer()
    return analyzer.calculate_complexity_score(grant)


if __name__ == "__main__":
    # Test the complexity analysis
    test_grant = {
        'typical_ticket_lakh': 100,
        'agency': 'Government of India, Ministry of Science',
        'deadline_type': 'batch_call',
        'eligibility_flags': [
            'DPIIT recognized startup',
            'Audited financial statements required',
            'Technical specifications needed',
            'Business plan mandatory',
            'References from industry experts'
        ]
    }
    
    result = calculate_application_complexity(test_grant)
    print(f"Overall Complexity: {result['overall_complexity']}")
    print(f"Complexity Score: {result['complexity_score']}")
    print(f"Estimated Effort: {result['estimated_effort_hours']} hours")
    print(f"Complexity Reasons: {result['complexity_reasons']}")

