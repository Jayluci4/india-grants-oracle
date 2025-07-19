import os
import json
import requests
from datetime import datetime
from typing import List, Dict

class SlackNotifier:
    """Slack notification system for grant updates"""
    
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK')
        if not self.webhook_url or self.webhook_url == 'https://hooks.slack.com/services/placeholder':
            print("Warning: Slack webhook URL not configured")
            self.enabled = False
        else:
            self.enabled = True
    
    def send_message(self, text, channel="#grants-feed", username="Grant Oracle Bot"):
        """Send a message to Slack"""
        if not self.enabled:
            print(f"Slack disabled - would send: {text}")
            return False
            
        payload = {
            "channel": channel,
            "username": username,
            "text": text,
            "icon_emoji": ":money_with_wings:"
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send Slack message: {e}")
            return False
    
    def notify_new_grant(self, grant_data):
        """Send notification for a new grant"""
        amount_text = ""
        if grant_data.get('min_ticket_lakh') and grant_data.get('max_ticket_lakh'):
            if grant_data['min_ticket_lakh'] == grant_data['max_ticket_lakh']:
                amount_text = f"₹{grant_data['min_ticket_lakh']} Lakh"
            else:
                amount_text = f"₹{grant_data['min_ticket_lakh']}-{grant_data['max_ticket_lakh']} Lakh"
        elif grant_data.get('typical_ticket_lakh'):
            amount_text = f"₹{grant_data['typical_ticket_lakh']} Lakh"
        
        deadline_text = ""
        if grant_data.get('next_deadline_iso'):
            try:
                deadline_date = datetime.fromisoformat(grant_data['next_deadline_iso'].replace('Z', '+00:00'))
                deadline_text = f" - Deadline: {deadline_date.strftime('%d %b %Y')}"
            except:
                deadline_text = f" - Deadline: {grant_data['next_deadline_iso']}"
        
        message = f"""🆕 *New Grant Alert!*
        
*{grant_data['title']}*
Agency: {grant_data['agency']}
Amount: {amount_text}
Bucket: {grant_data.get('bucket', 'Unknown')}
{deadline_text}

Eligibility: {', '.join(grant_data.get('eligibility_flags', []))}
Sectors: {', '.join(grant_data.get('sector_tags', []))}
"""
        
        return self.send_message(message)
    
    def notify_daily_summary(self, grants_found, total_grants):
        """Send daily summary notification"""
        message = f"""📊 *Daily Grant Discovery Summary*
        
🔍 New grants found today: {grants_found}
📈 Total grants in database: {total_grants}
🕐 Last updated: {datetime.now().strftime('%d %b %Y, %H:%M IST')}

Visit the dashboard for full details!
"""
        
        return self.send_message(message)
    
    def notify_deadline_reminder(self, grants_expiring_soon):
        """Send deadline reminder notifications"""
        if not grants_expiring_soon:
            return True
            
        message = "⏰ *Grant Deadline Reminders*\n\n"
        
        for grant in grants_expiring_soon:
            deadline_date = datetime.fromisoformat(grant['next_deadline_iso'].replace('Z', '+00:00'))
            days_left = (deadline_date - datetime.now()).days
            
            message += f"• *{grant['title']}* - {days_left} days left\n"
            message += f"  Agency: {grant['agency']}\n"
            message += f"  Amount: ₹{grant.get('typical_ticket_lakh', 'TBD')} Lakh\n\n"
        
        return self.send_message(message)
    
    def notify_error(self, error_message, component="System"):
        """Send error notification"""
        message = f"""🚨 *Error Alert*
        
Component: {component}
Error: {error_message}
Time: {datetime.now().strftime('%d %b %Y, %H:%M IST')}
"""
        
        return self.send_message(message, channel="#alerts")

# WhatsApp notifier using Twilio
class WhatsAppNotifier:
    """WhatsApp notification system using Twilio"""
    
    def __init__(self, account_sid=None, auth_token=None):
        self.account_sid = account_sid or os.getenv('TWILIO_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_TOKEN')
        
        if not self.account_sid or self.account_sid == 'placeholder':
            print("Warning: Twilio credentials not configured")
            self.enabled = False
        else:
            self.enabled = True
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
            except ImportError:
                print("Twilio library not installed")
                self.enabled = False
    
    def send_whatsapp_message(self, to_number, message):
        """Send WhatsApp message via Twilio"""
        if not self.enabled:
            print(f"WhatsApp disabled - would send to {to_number}: {message}")
            return False
            
        try:
            message = self.client.messages.create(
                body=message,
                from_='whatsapp:+14155238886',  # Twilio Sandbox number
                to=f'whatsapp:{to_number}'
            )
            return True
        except Exception as e:
            print(f"Failed to send WhatsApp message: {e}")
            return False
    
    def notify_new_grant_whatsapp(self, grant_data, phone_numbers):
        """Send new grant notification via WhatsApp"""
        amount_text = f"₹{grant_data.get('typical_ticket_lakh', 'TBD')} Lakh"
        
        message = f"""🆕 New Grant Alert!

{grant_data['title']}
Agency: {grant_data['agency']}
Amount: {amount_text}

Check the dashboard for full details!"""
        
        success_count = 0
        for phone in phone_numbers:
            if self.send_whatsapp_message(phone, message):
                success_count += 1
        
        return success_count

# Combined notification manager
class NotificationManager:
    """Manages all notification channels"""
    
    def __init__(self):
        self.slack = SlackNotifier()
        self.whatsapp = WhatsAppNotifier()
        
    def notify_new_grant(self, grant_data, whatsapp_numbers=None):
        """Send new grant notification to all channels"""
        results = {}
        
        # Slack notification
        results['slack'] = self.slack.notify_new_grant(grant_data)
        
        # WhatsApp notification
        if whatsapp_numbers:
            results['whatsapp'] = self.whatsapp.notify_new_grant_whatsapp(grant_data, whatsapp_numbers)
        
        return results
    
    def notify_daily_summary(self, grants_found, total_grants):
        """Send daily summary to Slack"""
        return self.slack.notify_daily_summary(grants_found, total_grants)
    
    def notify_error(self, error_message, component="System"):
        """Send error notification"""
        return self.slack.notify_error(error_message, component)

# Test the notification system
if __name__ == "__main__":
    notifier = NotificationManager()
    
    # Test grant data
    test_grant = {
        'title': 'Test Startup Grant',
        'agency': 'Test Agency',
        'min_ticket_lakh': 10,
        'max_ticket_lakh': 50,
        'typical_ticket_lakh': 30,
        'bucket': 'Early Stage',
        'next_deadline_iso': '2025-08-31T23:59:59Z',
        'eligibility_flags': ['dpiit_recognised', 'indian_promoters'],
        'sector_tags': ['technology', 'innovation']
    }
    
    # Test notifications
    print("Testing Slack notification...")
    result = notifier.notify_new_grant(test_grant)
    print(f"Notification result: {result}")
    
    print("Testing daily summary...")
    summary_result = notifier.notify_daily_summary(5, 150)
    print(f"Summary result: {summary_result}")

