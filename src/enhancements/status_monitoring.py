"""
Grant Status Monitoring Enhancement
Monitors grant status and detects when grants close or deadlines pass
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import re
from urllib.parse import urlparse
import logging


class GrantStatusMonitor:
    """Monitor grant status and detect changes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Keywords that indicate a grant is closed or expired
        self.closed_keywords = [
            'closed', 'expired', 'deadline passed', 'applications closed',
            'no longer accepting', 'ended', 'concluded', 'completed',
            'submissions closed', 'registration closed'
        ]
        
        # Keywords that indicate a grant is still open
        self.open_keywords = [
            'apply now', 'applications open', 'accepting applications',
            'submit application', 'register now', 'deadline', 'last date'
        ]
    
    def check_grant_status(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the current status of a grant
        
        Args:
            grant: Grant dictionary with source URLs and deadline info
            
        Returns:
            Dictionary with status information
        """
        status_info = {
            'status': grant.get('status', 'live'),
            'status_reason': None,
            'last_checked_iso': datetime.now().isoformat(),
            'deadline_status': 'unknown',
            'website_accessible': True,
            'status_confidence': 0.5
        }
        
        # Check deadline status first
        deadline_status = self._check_deadline_status(grant)
        status_info.update(deadline_status)
        
        # If deadline has passed, mark as expired
        if status_info['deadline_status'] == 'expired':
            status_info['status'] = 'expired'
            status_info['status_reason'] = 'deadline_passed'
            status_info['status_confidence'] = 1.0
            return status_info
        
        # Check website status
        website_status = self._check_website_status(grant)
        status_info.update(website_status)
        
        return status_info
    
    def _check_deadline_status(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Check if grant deadline has passed"""
        deadline_info = {
            'deadline_status': 'unknown',
            'days_until_deadline': None
        }
        
        deadline_str = grant.get('next_deadline_iso')
        deadline_type = grant.get('deadline_type', 'unknown')
        
        if not deadline_str or deadline_type == 'rolling':
            deadline_info['deadline_status'] = 'rolling'
            return deadline_info
        
        try:
            # Parse deadline
            if 'T' in deadline_str:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            else:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            
            now = datetime.now()
            if deadline.tzinfo:
                now = now.replace(tzinfo=deadline.tzinfo)
            
            days_diff = (deadline - now).days
            deadline_info['days_until_deadline'] = days_diff
            
            if days_diff < 0:
                deadline_info['deadline_status'] = 'expired'
            elif days_diff <= 7:
                deadline_info['deadline_status'] = 'closing_soon'
            elif days_diff <= 30:
                deadline_info['deadline_status'] = 'open_near_deadline'
            else:
                deadline_info['deadline_status'] = 'open'
                
        except (ValueError, TypeError) as e:
            logging.warning(f"Could not parse deadline {deadline_str}: {e}")
            deadline_info['deadline_status'] = 'unknown'
        
        return deadline_info
    
    def _check_website_status(self, grant: Dict[str, Any]) -> Dict[str, Any]:
        """Check if grant website is accessible and shows current status"""
        website_info = {
            'website_accessible': True,
            'website_status_indicators': [],
            'status_confidence': 0.5
        }
        
        source_urls = grant.get('source_urls', [])
        if not source_urls:
            return website_info
        
        # Check the primary source URL
        primary_url = source_urls[0] if isinstance(source_urls, list) else str(source_urls)
        
        try:
            response = self.session.get(primary_url, timeout=10, allow_redirects=True)
            
            if response.status_code == 404:
                website_info['website_accessible'] = False
                website_info['status_confidence'] = 0.9
                return website_info
            
            if response.status_code != 200:
                website_info['website_accessible'] = False
                website_info['status_confidence'] = 0.7
                return website_info
            
            # Analyze page content
            content = response.text.lower()
            content_analysis = self._analyze_page_content(content)
            website_info.update(content_analysis)
            
        except requests.RequestException as e:
            logging.warning(f"Could not access {primary_url}: {e}")
            website_info['website_accessible'] = False
            website_info['status_confidence'] = 0.6
        
        return website_info
    
    def _analyze_page_content(self, content: str) -> Dict[str, Any]:
        """Analyze page content for status indicators"""
        analysis = {
            'website_status_indicators': [],
            'status_confidence': 0.5
        }
        
        # Count closed indicators
        closed_count = sum(1 for keyword in self.closed_keywords if keyword in content)
        
        # Count open indicators  
        open_count = sum(1 for keyword in self.open_keywords if keyword in content)
        
        analysis['website_status_indicators'] = {
            'closed_indicators': closed_count,
            'open_indicators': open_count
        }
        
        # Determine confidence based on indicators
        if closed_count > open_count and closed_count > 0:
            analysis['status_confidence'] = min(0.9, 0.5 + (closed_count * 0.1))
            analysis['likely_status'] = 'closed'
        elif open_count > closed_count and open_count > 0:
            analysis['status_confidence'] = min(0.9, 0.5 + (open_count * 0.1))
            analysis['likely_status'] = 'open'
        else:
            analysis['likely_status'] = 'unknown'
        
        return analysis
    
    def monitor_grants_batch(self, grants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Monitor status for a batch of grants
        
        Args:
            grants: List of grant dictionaries
            
        Returns:
            List of grants with updated status information
        """
        updated_grants = []
        
        for grant in grants:
            try:
                status_info = self.check_grant_status(grant)
                
                # Update grant with new status information
                updated_grant = grant.copy()
                updated_grant.update(status_info)
                
                updated_grants.append(updated_grant)
                
            except Exception as e:
                logging.error(f"Error monitoring grant {grant.get('id', 'unknown')}: {e}")
                # Keep original grant if monitoring fails
                updated_grants.append(grant)
        
        return updated_grants
    
    def get_grants_needing_monitoring(self, grants: List[Dict[str, Any]], 
                                    hours_since_last_check: int = 24) -> List[Dict[str, Any]]:
        """
        Get grants that need status monitoring
        
        Args:
            grants: List of all grants
            hours_since_last_check: Hours since last check to trigger monitoring
            
        Returns:
            List of grants that need monitoring
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_since_last_check)
        
        grants_to_monitor = []
        
        for grant in grants:
            # Skip if already marked as expired
            if grant.get('status') == 'expired':
                continue
            
            # Check last monitoring time
            last_checked_str = grant.get('last_checked_iso')
            if last_checked_str:
                try:
                    last_checked = datetime.fromisoformat(last_checked_str.replace('Z', '+00:00'))
                    if last_checked.tzinfo is None:
                        last_checked = last_checked.replace(tzinfo=cutoff_time.tzinfo)
                    
                    if last_checked > cutoff_time:
                        continue  # Recently checked
                except (ValueError, TypeError):
                    pass  # Invalid date, include in monitoring
            
            grants_to_monitor.append(grant)
        
        return grants_to_monitor
    
    def generate_status_report(self, grants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a status monitoring report
        
        Args:
            grants: List of grants with status information
            
        Returns:
            Status report dictionary
        """
        report = {
            'total_grants': len(grants),
            'status_breakdown': {},
            'deadline_breakdown': {},
            'monitoring_summary': {
                'last_updated': datetime.now().isoformat(),
                'grants_monitored': 0,
                'website_issues': 0,
                'expired_grants': 0
            }
        }
        
        # Count status breakdown
        for grant in grants:
            status = grant.get('status', 'unknown')
            report['status_breakdown'][status] = report['status_breakdown'].get(status, 0) + 1
            
            deadline_status = grant.get('deadline_status', 'unknown')
            report['deadline_breakdown'][deadline_status] = report['deadline_breakdown'].get(deadline_status, 0) + 1
            
            # Count monitoring metrics
            if grant.get('last_checked_iso'):
                report['monitoring_summary']['grants_monitored'] += 1
            
            if not grant.get('website_accessible', True):
                report['monitoring_summary']['website_issues'] += 1
            
            if status == 'expired':
                report['monitoring_summary']['expired_grants'] += 1
        
        return report


def monitor_grant_status(grant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Monitor status of a single grant
    
    Args:
        grant: Grant dictionary
        
    Returns:
        Updated grant with status information
    """
    monitor = GrantStatusMonitor()
    status_info = monitor.check_grant_status(grant)
    
    updated_grant = grant.copy()
    updated_grant.update(status_info)
    
    return updated_grant


if __name__ == "__main__":
    # Test the status monitoring
    test_grant = {
        'id': 'test_grant',
        'title': 'Test Grant',
        'next_deadline_iso': '2025-12-31T23:59:59Z',
        'deadline_type': 'batch_call',
        'source_urls': ['https://example.com/grant'],
        'status': 'live'
    }
    
    result = monitor_grant_status(test_grant)
    print(f"Grant Status: {result['status']}")
    print(f"Deadline Status: {result.get('deadline_status', 'unknown')}")
    print(f"Days Until Deadline: {result.get('days_until_deadline', 'unknown')}")
    print(f"Website Accessible: {result.get('website_accessible', 'unknown')}")

