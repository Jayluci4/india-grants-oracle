"""
Enhanced Notification Manager
Provides comprehensive notifications for the enhanced grant discovery system
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from .slack_notifier import SlackNotifier

class BaseNotificationManager:
    """Base notification manager"""
    def __init__(self):
        self.slack = SlackNotifier()

logger = logging.getLogger(__name__)

class EnhancedNotificationManager(BaseNotificationManager):
    """Enhanced notification manager with additional capabilities"""
    
    def __init__(self):
        super().__init__()
        self.notification_history = []
        
    def notify_new_sources_discovered(self, count: int, sources: Optional[List[Dict]] = None):
        """Notify about newly discovered grant sources"""
        try:
            message = f"🔍 **Source Discovery Update**\n\n"
            message += f"Discovered **{count}** new potential grant sources!\n\n"
            
            if sources:
                message += "**Top Sources:**\n"
                for i, source in enumerate(sources[:3], 1):
                    score = source.get('overall_score', 0)
                    url = source.get('url', 'Unknown')
                    message += f"{i}. {url} (Score: {score:.2f})\n"
            
            message += f"\n📅 Discovery Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.slack.send_message(message)
            
            # Log notification
            self._log_notification('source_discovery', {
                'count': count,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to send source discovery notification: {e}")
    
    def notify_enhanced_daily_summary(self, report: Dict):
        """Send enhanced daily summary with comprehensive statistics"""
        try:
            message = f"📊 **Enhanced Daily Grant Discovery Report**\n\n"
            
            # Discovery cycle information
            cycle_duration = report.get('cycle_duration_seconds', 0)
            message += f"⏱️ **Cycle Duration:** {cycle_duration:.1f} seconds\n\n"
            
            # Source discovery
            new_sources = report.get('new_sources_discovered', 0)
            message += f"🔍 **New Sources Discovered:** {new_sources}\n"
            
            # Grant extraction
            ai_grants = report.get('ai_grants_extracted', 0)
            scrapy_grants = report.get('scrapy_grants_total', 0)
            total_grants = ai_grants + scrapy_grants
            message += f"🤖 **AI-Extracted Grants:** {ai_grants}\n"
            message += f"🕷️ **Scrapy-Extracted Grants:** {scrapy_grants}\n"
            message += f"📈 **Total Grants Found:** {total_grants}\n\n"
            
            # Processing statistics
            stats = report.get('orchestrator_stats', {})
            if stats:
                message += f"📊 **Processing Statistics:**\n"
                message += f"• Total URLs Processed: {stats.get('total_processed', 0)}\n"
                message += f"• Successful Extractions: {stats.get('successful_extractions', 0)}\n"
                message += f"• Failed Extractions: {stats.get('failed_extractions', 0)}\n"
                message += f"• Pending URLs: {stats.get('pending_urls', 0)}\n\n"
            
            # Top new sources
            top_sources = report.get('top_new_sources', [])
            if top_sources:
                message += f"🌟 **Top New Sources:**\n"
                for i, source in enumerate(top_sources[:3], 1):
                    url = source.get('url', 'Unknown')
                    score = source.get('overall_score', 0)
                    message += f"{i}. {url} (Score: {score:.2f})\n"
            
            message += f"\n📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.slack.send_message(message)
            
            # Log notification
            self._log_notification('enhanced_daily_summary', report)
            
        except Exception as e:
            logger.error(f"Failed to send enhanced daily summary: {e}")
    
    def notify_high_value_grant(self, grant: Dict):
        """Notify about high-value grants (>50 lakhs)"""
        try:
            ticket_size = grant.get('typical_ticket_lakh', 0)
            
            if ticket_size > 50:  # High-value threshold
                message = f"💰 **High-Value Grant Alert!**\n\n"
                message += f"**Grant:** {grant.get('title', 'Unknown')}\n"
                message += f"**Agency:** {grant.get('agency', 'Unknown')}\n"
                message += f"**Funding:** ₹{ticket_size} Lakhs\n"
                
                deadline = grant.get('next_deadline_iso')
                if deadline:
                    message += f"**Deadline:** {deadline}\n"
                
                sectors = grant.get('sector_tags', [])
                if sectors:
                    message += f"**Sectors:** {', '.join(sectors)}\n"
                
                source_url = grant.get('source_url')
                if source_url:
                    message += f"**Source:** {source_url}\n"
                
                message += f"\n🚨 **Action Required:** Review and apply immediately!"
                
                self.slack.send_message(message)
                
                # Log notification
                self._log_notification('high_value_grant', grant)
        
        except Exception as e:
            logger.error(f"Failed to send high-value grant notification: {e}")
    
    def notify_source_evaluation_complete(self, url: str, evaluation: Dict):
        """Notify about completed source evaluation"""
        try:
            score = evaluation.get('overall_score', 0)
            
            if score > 0.7:  # High-quality source
                message = f"✅ **High-Quality Source Identified**\n\n"
                message += f"**URL:** {url}\n"
                message += f"**Overall Score:** {score:.2f}\n"
                message += f"**Relevance:** {evaluation.get('relevance_score', 0):.2f}\n"
                message += f"**Credibility:** {evaluation.get('credibility_score', 0):.2f}\n"
                message += f"**Timeliness:** {evaluation.get('timeliness_score', 0):.2f}\n"
                
                message += f"\n🎯 **Recommendation:** Add to priority extraction list"
                
                self.slack.send_message(message)
                
                # Log notification
                self._log_notification('source_evaluation', {
                    'url': url,
                    'evaluation': evaluation
                })
        
        except Exception as e:
            logger.error(f"Failed to send source evaluation notification: {e}")
    
    def notify_extraction_errors(self, failed_urls: List[str], error_summary: Dict):
        """Notify about extraction errors and failed URLs"""
        try:
            if len(failed_urls) > 5:  # Only notify if significant failures
                message = f"⚠️ **Extraction Errors Detected**\n\n"
                message += f"**Failed URLs:** {len(failed_urls)}\n"
                message += f"**Success Rate:** {error_summary.get('success_rate', 0):.1f}%\n\n"
                
                message += f"**Sample Failed URLs:**\n"
                for url in failed_urls[:3]:
                    message += f"• {url}\n"
                
                if len(failed_urls) > 3:
                    message += f"• ... and {len(failed_urls) - 3} more\n"
                
                message += f"\n🔧 **Action Required:** Review and fix extraction issues"
                
                self.slack.send_message(message)
                
                # Log notification
                self._log_notification('extraction_errors', {
                    'failed_urls': failed_urls,
                    'error_summary': error_summary
                })
        
        except Exception as e:
            logger.error(f"Failed to send extraction error notification: {e}")
    
    def notify_system_performance(self, performance_metrics: Dict):
        """Notify about system performance metrics"""
        try:
            # Only notify if performance is concerning
            success_rate = performance_metrics.get('success_rate', 100)
            avg_processing_time = performance_metrics.get('avg_processing_time', 0)
            
            if success_rate < 80 or avg_processing_time > 300:  # 5 minutes
                message = f"📊 **System Performance Alert**\n\n"
                message += f"**Success Rate:** {success_rate:.1f}%\n"
                message += f"**Avg Processing Time:** {avg_processing_time:.1f}s\n"
                message += f"**Total Sources Processed:** {performance_metrics.get('total_processed', 0)}\n"
                message += f"**Active Sources:** {performance_metrics.get('active_sources', 0)}\n"
                
                if success_rate < 80:
                    message += f"\n⚠️ **Low Success Rate Detected**"
                
                if avg_processing_time > 300:
                    message += f"\n🐌 **Slow Processing Detected**"
                
                message += f"\n🔧 **Recommendation:** Review system performance"
                
                self.slack.send_message(message)
                
                # Log notification
                self._log_notification('system_performance', performance_metrics)
        
        except Exception as e:
            logger.error(f"Failed to send performance notification: {e}")
    
    def notify_weekly_insights(self, insights: Dict):
        """Send weekly insights and trends"""
        try:
            message = f"📈 **Weekly Grant Discovery Insights**\n\n"
            
            # Discovery trends
            total_sources = insights.get('total_sources_discovered', 0)
            total_grants = insights.get('total_grants_found', 0)
            message += f"🔍 **Sources Discovered This Week:** {total_sources}\n"
            message += f"📋 **Grants Found This Week:** {total_grants}\n\n"
            
            # Top performing sources
            top_sources = insights.get('top_performing_sources', [])
            if top_sources:
                message += f"🌟 **Top Performing Sources:**\n"
                for i, source in enumerate(top_sources[:3], 1):
                    grants_count = source.get('grants_found', 0)
                    url = source.get('url', 'Unknown')
                    message += f"{i}. {url} ({grants_count} grants)\n"
                message += "\n"
            
            # Sector trends
            sector_trends = insights.get('sector_trends', {})
            if sector_trends:
                message += f"📊 **Trending Sectors:**\n"
                for sector, count in list(sector_trends.items())[:3]:
                    message += f"• {sector}: {count} grants\n"
                message += "\n"
            
            # Funding trends
            avg_funding = insights.get('avg_funding_lakh', 0)
            max_funding = insights.get('max_funding_lakh', 0)
            message += f"💰 **Funding Insights:**\n"
            message += f"• Average Grant Size: ₹{avg_funding:.1f} Lakhs\n"
            message += f"• Largest Grant: ₹{max_funding:.1f} Lakhs\n\n"
            
            message += f"📅 Week Ending: {datetime.now().strftime('%Y-%m-%d')}"
            
            self.slack.send_message(message)
            
            # Log notification
            self._log_notification('weekly_insights', insights)
            
        except Exception as e:
            logger.error(f"Failed to send weekly insights: {e}")
    
    def _log_notification(self, notification_type: str, data: Dict):
        """Log notification for tracking and analytics"""
        log_entry = {
            'type': notification_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.notification_history.append(log_entry)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        logger.info(f"Logged notification: {notification_type}")
    
    def get_notification_history(self, notification_type: Optional[str] = None, 
                               limit: int = 100) -> List[Dict]:
        """Get notification history"""
        history = self.notification_history
        
        if notification_type:
            history = [n for n in history if n['type'] == notification_type]
        
        return history[-limit:]
    
    def get_notification_stats(self) -> Dict:
        """Get notification statistics"""
        total_notifications = len(self.notification_history)
        
        type_counts = {}
        for notification in self.notification_history:
            notification_type = notification['type']
            type_counts[notification_type] = type_counts.get(notification_type, 0) + 1
        
        return {
            'total_notifications': total_notifications,
            'type_breakdown': type_counts,
            'last_notification': self.notification_history[-1] if self.notification_history else None
        }

# Example usage
if __name__ == "__main__":
    notifier = EnhancedNotificationManager()
    
    # Test notifications
    notifier.notify_new_sources_discovered(5)
    
    sample_report = {
        'cycle_duration_seconds': 120.5,
        'new_sources_discovered': 3,
        'ai_grants_extracted': 15,
        'scrapy_grants_total': 8,
        'orchestrator_stats': {
            'total_processed': 25,
            'successful_extractions': 20,
            'failed_extractions': 5
        }
    }
    
    notifier.notify_enhanced_daily_summary(sample_report)

