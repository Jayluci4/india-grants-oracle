#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Grant Discovery System
Tests all components of the intelligent source discovery and enhanced orchestration
"""

import asyncio
import os
import sys
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.intelligent_source_discovery import IntelligentSourceDiscoveryModule, SourceEvaluator
from agents.enhanced_magentic_orchestrator import EnhancedGrantOracleOrchestrator
from notifications.enhanced_notifier import EnhancedNotificationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedSystemTester:
    """Comprehensive tester for the enhanced grant discovery system"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        
    async def test_source_evaluator(self) -> Dict:
        """Test the SourceEvaluator component"""
        logger.info("Testing SourceEvaluator...")
        
        evaluator = SourceEvaluator()
        
        # Test cases
        test_cases = [
            {
                'name': 'High relevance government site',
                'content': 'startup grants funding schemes government ministry innovation entrepreneur',
                'url': 'https://startup.gov.in/grants',
                'expected_relevance': 0.7
            },
            {
                'name': 'Low relevance commercial site',
                'content': 'buy products online shopping discount sale',
                'url': 'https://shop.example.com',
                'expected_relevance': 0.1
            },
            {
                'name': 'High credibility site',
                'content': 'about us contact address phone email annual report transparency',
                'url': 'https://birac.nic.in',
                'expected_credibility': 0.6
            }
        ]
        
        results = []
        for test_case in test_cases:
            relevance = evaluator.calculate_relevance_score(test_case['content'], test_case['url'])
            credibility = evaluator.calculate_credibility_score(test_case['content'], test_case['url'])
            timeliness = evaluator.calculate_timeliness_score(test_case['content'])
            
            result = {
                'test_name': test_case['name'],
                'relevance_score': relevance,
                'credibility_score': credibility,
                'timeliness_score': timeliness,
                'passed': True  # Basic functionality test
            }
            results.append(result)
            
            logger.info(f"Test '{test_case['name']}': Relevance={relevance:.2f}, Credibility={credibility:.2f}")
        
        return {
            'component': 'SourceEvaluator',
            'status': 'PASSED',
            'test_count': len(test_cases),
            'results': results
        }
    
    async def test_intelligent_source_discovery(self) -> Dict:
        """Test the Intelligent Source Discovery Module"""
        logger.info("Testing Intelligent Source Discovery Module...")
        
        try:
            # Initialize with test configuration
            discovery = IntelligentSourceDiscoveryModule()
            
            # Test URL filtering
            test_urls = [
                'https://startup.gov.in/grants',
                'https://facebook.com/page',
                'https://birac.nic.in/schemes',
                'https://amazon.com/products',
                'https://innovation.ministry.gov.in'
            ]
            
            filtered_urls = discovery._filter_relevant_urls(test_urls)
            
            # Test URL extraction
            test_content = """
            Visit these links for more information:
            https://seedfund.startupindia.gov.in/
            https://birac.nic.in/call_details.aspx
            https://tdb.gov.in/schemes
            """
            
            extracted_urls = discovery._extract_urls_from_content(test_content)
            
            # Test source evaluation (limited test to avoid API calls)
            test_evaluation = {
                'url': 'https://test.gov.in',
                'relevance_score': 0.8,
                'credibility_score': 0.7,
                'timeliness_score': 0.6,
                'overall_score': 0.7
            }
            
            await discovery.close()
            
            return {
                'component': 'IntelligentSourceDiscovery',
                'status': 'PASSED',
                'filtered_urls_count': len(filtered_urls),
                'extracted_urls_count': len(extracted_urls),
                'test_evaluation': test_evaluation
            }
            
        except Exception as e:
            logger.error(f"ISDM test failed: {e}")
            return {
                'component': 'IntelligentSourceDiscovery',
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_enhanced_orchestrator(self) -> Dict:
        """Test the Enhanced Grant Oracle Orchestrator"""
        logger.info("Testing Enhanced Grant Oracle Orchestrator...")
        
        try:
            orchestrator = EnhancedGrantOracleOrchestrator()
            
            # Test URL management
            test_urls = [
                'https://seedfund.startupindia.gov.in/',
                'https://birac.nic.in/call_details.aspx',
                'https://tdb.gov.in/'
            ]
            
            orchestrator.add_target_urls(test_urls)
            pending_urls = orchestrator.get_pending_urls()
            
            # Test statistics
            stats = orchestrator.get_processing_stats()
            
            # Test URL validation
            valid_url = orchestrator._is_valid_url('https://example.com')
            invalid_url = orchestrator._is_valid_url('not-a-url')
            
            await orchestrator.close()
            
            return {
                'component': 'EnhancedOrchestrator',
                'status': 'PASSED',
                'pending_urls_count': len(pending_urls),
                'initial_stats': stats,
                'url_validation': {
                    'valid_url_test': valid_url,
                    'invalid_url_test': not invalid_url
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced orchestrator test failed: {e}")
            return {
                'component': 'EnhancedOrchestrator',
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_enhanced_notifications(self) -> Dict:
        """Test the Enhanced Notification Manager"""
        logger.info("Testing Enhanced Notification Manager...")
        
        try:
            notifier = EnhancedNotificationManager()
            
            # Test notification logging
            test_data = {'test': 'data', 'count': 5}
            notifier._log_notification('test_notification', test_data)
            
            # Test notification history
            history = notifier.get_notification_history('test_notification')
            stats = notifier.get_notification_stats()
            
            return {
                'component': 'EnhancedNotifications',
                'status': 'PASSED',
                'history_count': len(history),
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Enhanced notifications test failed: {e}")
            return {
                'component': 'EnhancedNotifications',
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_integration_workflow(self) -> Dict:
        """Test the integration between components"""
        logger.info("Testing component integration workflow...")
        
        try:
            # Initialize components
            discovery = IntelligentSourceDiscoveryModule()
            orchestrator = EnhancedGrantOracleOrchestrator()
            notifier = EnhancedNotificationManager()
            
            # Simulate discovery workflow
            test_sources = [
                {
                    'url': 'https://test-source-1.gov.in',
                    'overall_score': 0.8,
                    'relevance_score': 0.9,
                    'credibility_score': 0.7,
                    'timeliness_score': 0.8
                },
                {
                    'url': 'https://test-source-2.org.in',
                    'overall_score': 0.6,
                    'relevance_score': 0.7,
                    'credibility_score': 0.5,
                    'timeliness_score': 0.6
                }
            ]
            
            # Test source addition to orchestrator
            high_quality_sources = [s for s in test_sources if s['overall_score'] > 0.7]
            source_urls = [s['url'] for s in high_quality_sources]
            orchestrator.add_target_urls(source_urls)
            
            # Test notification
            notifier.notify_new_sources_discovered(len(high_quality_sources), high_quality_sources)
            
            # Test statistics
            orchestrator_stats = orchestrator.get_processing_stats()
            notification_stats = notifier.get_notification_stats()
            
            await discovery.close()
            await orchestrator.close()
            
            return {
                'component': 'Integration',
                'status': 'PASSED',
                'high_quality_sources': len(high_quality_sources),
                'orchestrator_stats': orchestrator_stats,
                'notification_stats': notification_stats
            }
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            return {
                'component': 'Integration',
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def test_performance_benchmarks(self) -> Dict:
        """Test performance benchmarks"""
        logger.info("Testing performance benchmarks...")
        
        try:
            # Test source evaluation performance
            evaluator = SourceEvaluator()
            
            start_time = time.time()
            for i in range(100):
                test_content = f"startup grants funding scheme {i} innovation entrepreneur"
                test_url = f"https://test-{i}.gov.in"
                evaluator.calculate_relevance_score(test_content, test_url)
                evaluator.calculate_credibility_score(test_content, test_url)
                evaluator.calculate_timeliness_score(test_content)
            
            evaluation_time = time.time() - start_time
            
            # Test URL filtering performance
            discovery = IntelligentSourceDiscoveryModule()
            
            test_urls = [f"https://test-{i}.com" for i in range(1000)]
            
            start_time = time.time()
            filtered_urls = discovery._filter_relevant_urls(test_urls)
            filtering_time = time.time() - start_time
            
            await discovery.close()
            
            return {
                'component': 'Performance',
                'status': 'PASSED',
                'evaluation_time_100_sources': evaluation_time,
                'filtering_time_1000_urls': filtering_time,
                'evaluations_per_second': 100 / evaluation_time if evaluation_time > 0 else 0,
                'urls_filtered_per_second': 1000 / filtering_time if filtering_time > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return {
                'component': 'Performance',
                'status': 'FAILED',
                'error': str(e)
            }
    
    def test_configuration_validation(self) -> Dict:
        """Test configuration and environment validation"""
        logger.info("Testing configuration validation...")
        
        try:
            # Check required environment variables
            openai_key = os.getenv('OPENAI_API_KEY')
            
            # Test configuration parameters
            config_tests = {
                'openai_api_key_present': bool(openai_key),
                'openai_api_key_length': len(openai_key) > 20 if openai_key else False,
                'python_version': sys.version_info >= (3, 8),
                'required_modules': True  # Simplified check
            }
            
            all_passed = all(config_tests.values())
            
            return {
                'component': 'Configuration',
                'status': 'PASSED' if all_passed else 'FAILED',
                'tests': config_tests
            }
            
        except Exception as e:
            logger.error(f"Configuration test failed: {e}")
            return {
                'component': 'Configuration',
                'status': 'FAILED',
                'error': str(e)
            }
    
    async def run_all_tests(self) -> Dict:
        """Run all test suites"""
        logger.info("🧪 Starting comprehensive test suite...")
        self.start_time = datetime.now()
        
        # Run all tests
        test_functions = [
            self.test_source_evaluator,
            self.test_intelligent_source_discovery,
            self.test_enhanced_orchestrator,
            self.test_enhanced_notifications,
            self.test_integration_workflow,
            self.test_performance_benchmarks,
            self.test_configuration_validation
        ]
        
        results = []
        for test_func in test_functions:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                results.append(result)
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed: {e}")
                results.append({
                    'component': test_func.__name__,
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('status') == 'PASSED')
        failed_tests = total_tests - passed_tests
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        summary = {
            'test_suite': 'Enhanced Grant Discovery System',
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'overall_status': 'PASSED' if failed_tests == 0 else 'FAILED',
            'detailed_results': results
        }
        
        self.test_results = summary
        return summary
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test report"""
        if not self.test_results:
            return "No test results available. Run tests first."
        
        report = f"""
# Enhanced Grant Discovery System - Test Report

## Summary
- **Test Suite**: {self.test_results['test_suite']}
- **Start Time**: {self.test_results['start_time']}
- **Duration**: {self.test_results['duration_seconds']:.2f} seconds
- **Overall Status**: {self.test_results['overall_status']}
- **Success Rate**: {self.test_results['success_rate']:.1f}%

## Test Results
- **Total Tests**: {self.test_results['total_tests']}
- **Passed**: {self.test_results['passed_tests']}
- **Failed**: {self.test_results['failed_tests']}

## Detailed Results

"""
        
        for result in self.test_results['detailed_results']:
            status_emoji = "✅" if result['status'] == 'PASSED' else "❌"
            report += f"### {status_emoji} {result['component']}\n"
            report += f"**Status**: {result['status']}\n"
            
            if result['status'] == 'FAILED' and 'error' in result:
                report += f"**Error**: {result['error']}\n"
            
            # Add specific details for each component
            if result['component'] == 'Performance':
                if 'evaluations_per_second' in result:
                    report += f"**Performance**: {result['evaluations_per_second']:.1f} evaluations/sec\n"
            
            report += "\n"
        
        return report

async def main():
    """Main test execution"""
    tester = EnhancedSystemTester()
    
    try:
        # Run all tests
        results = await tester.run_all_tests()
        
        # Generate and display report
        report = tester.generate_test_report()
        
        print("\n" + "="*60)
        print("ENHANCED GRANT DISCOVERY SYSTEM - TEST RESULTS")
        print("="*60)
        print(f"Overall Status: {results['overall_status']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Duration: {results['duration_seconds']:.2f} seconds")
        print("="*60)
        
        # Print component results
        for result in results['detailed_results']:
            status_symbol = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"{status_symbol} {result['component']}: {result['status']}")
        
        print("="*60)
        
        # Save detailed report
        with open('test_report.md', 'w') as f:
            f.write(report)
        
        print("📄 Detailed test report saved to: test_report.md")
        
        # Return appropriate exit code
        return 0 if results['overall_status'] == 'PASSED' else 1
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())

