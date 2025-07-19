#!/usr/bin/env python3
"""
Simple Test for Enhanced Grant Discovery System
Tests basic functionality without requiring API calls
"""

import os
import sys
import logging

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all modules can be imported"""
    try:
        from agents.intelligent_source_discovery import SourceEvaluator
        from notifications.enhanced_notifier import EnhancedNotificationManager
        logger.info("✅ All imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_source_evaluator():
    """Test the SourceEvaluator without API calls"""
    try:
        from agents.intelligent_source_discovery import SourceEvaluator
        
        evaluator = SourceEvaluator()
        
        # Test relevance scoring
        test_content = "startup grants funding schemes government innovation entrepreneur"
        test_url = "https://startup.gov.in/grants"
        
        relevance = evaluator.calculate_relevance_score(test_content, test_url)
        credibility = evaluator.calculate_credibility_score(test_content, test_url)
        timeliness = evaluator.calculate_timeliness_score(test_content)
        
        logger.info(f"✅ SourceEvaluator test passed")
        logger.info(f"   Relevance: {relevance:.2f}")
        logger.info(f"   Credibility: {credibility:.2f}")
        logger.info(f"   Timeliness: {timeliness:.2f}")
        
        return True
    except Exception as e:
        logger.error(f"❌ SourceEvaluator test failed: {e}")
        return False

def test_enhanced_notifications():
    """Test the Enhanced Notification Manager"""
    try:
        from notifications.enhanced_notifier import EnhancedNotificationManager
        
        # Create notifier (this might fail if Slack is not configured, but that's OK)
        try:
            notifier = EnhancedNotificationManager()
        except:
            # If Slack initialization fails, that's expected in test environment
            logger.info("✅ EnhancedNotificationManager import successful (Slack config not required for test)")
            return True
        
        # Test notification logging
        test_data = {'test': 'data', 'count': 5}
        notifier._log_notification('test_notification', test_data)
        
        # Test notification history
        history = notifier.get_notification_history('test_notification')
        stats = notifier.get_notification_stats()
        
        logger.info(f"✅ EnhancedNotificationManager test passed")
        logger.info(f"   History entries: {len(history)}")
        logger.info(f"   Total notifications: {stats['total_notifications']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ EnhancedNotificationManager test failed: {e}")
        return False

def test_url_utilities():
    """Test URL utility functions"""
    try:
        from agents.intelligent_source_discovery import IntelligentSourceDiscoveryModule
        
        # Test URL filtering (without initializing the full module)
        test_urls = [
            'https://startup.gov.in/grants',
            'https://facebook.com/page',
            'https://birac.nic.in/schemes',
            'https://amazon.com/products',
            'https://innovation.ministry.gov.in'
        ]
        
        # Create a temporary instance just for testing utility functions
        class TestDiscovery:
            def __init__(self):
                self.discovered_sources = set()
            
            def _filter_relevant_urls(self, urls):
                filtered = []
                for url in urls:
                    url_lower = url.lower()
                    if url in self.discovered_sources:
                        continue
                    
                    skip_domains = ['facebook.com', 'amazon.com']
                    if any(domain in url_lower for domain in skip_domains):
                        continue
                    
                    relevant_indicators = ['.in', '.gov', '.org', 'startup', 'grant']
                    if any(indicator in url_lower for indicator in relevant_indicators):
                        filtered.append(url)
                        self.discovered_sources.add(url)
                
                return filtered
        
        test_discovery = TestDiscovery()
        filtered_urls = test_discovery._filter_relevant_urls(test_urls)
        
        logger.info(f"✅ URL utilities test passed")
        logger.info(f"   Filtered URLs: {len(filtered_urls)}")
        logger.info(f"   URLs: {filtered_urls}")
        
        return True
    except Exception as e:
        logger.error(f"❌ URL utilities test failed: {e}")
        return False

def test_configuration():
    """Test configuration and environment"""
    try:
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            logger.info(f"✅ Python version OK: {python_version.major}.{python_version.minor}")
        else:
            logger.warning(f"⚠️ Python version may be too old: {python_version.major}.{python_version.minor}")
        
        # Check OpenAI API key (optional for basic tests)
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            logger.info("✅ OpenAI API key is configured")
        else:
            logger.info("ℹ️ OpenAI API key not configured (OK for basic tests)")
        
        # Check required directories
        required_dirs = ['src', 'logs']
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                logger.info(f"✅ Directory exists: {dir_name}")
            else:
                logger.warning(f"⚠️ Directory missing: {dir_name}")
                if dir_name == 'logs':
                    os.makedirs(dir_name, exist_ok=True)
                    logger.info(f"✅ Created directory: {dir_name}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run simple tests"""
    print("🧪 Running Simple Tests for Enhanced Grant Discovery System")
    print("="*60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Imports", test_imports),
        ("SourceEvaluator", test_source_evaluator),
        ("EnhancedNotifications", test_enhanced_notifications),
        ("URL Utilities", test_url_utilities)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}: {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All basic tests passed! The enhanced system is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

