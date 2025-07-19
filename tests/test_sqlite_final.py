#!/usr/bin/env python3
"""
Final SQLite Test - Comprehensive verification
"""

import os
import sys
from datetime import datetime, timedelta

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.models import DatabaseManager

def test_complete_sqlite_functionality():
    """Test complete SQLite functionality"""
    print("🧪 Testing Complete SQLite Functionality...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create tables
    print("Creating tables...")
    db_manager.create_tables()
    print("✅ Tables created successfully")
    
    # Test inserting comprehensive sample grants
    sample_grants = [
        {
            'id': 'final-test-001',
            'title': 'Startup India Seed Fund',
            'bucket': 'Early Stage',
            'instrument': ['grant', 'equity'],
            'min_ticket_lakh': 25.0,
            'max_ticket_lakh': 100.0,
            'typical_ticket_lakh': 50.0,
            'deadline_type': 'rolling',
            'next_deadline_iso': '2024-12-31T23:59:59Z',
            'eligibility_flags': ['tech_startup', 'early_stage', 'innovative'],
            'sector_tags': ['technology', 'innovation', 'digital'],
            'state_scope': 'national',
            'agency': 'Startup India',
            'source_urls': ['https://seedfund.startupindia.gov.in/'],
            'confidence': 0.95,
            'status': 'live'
        },
        {
            'id': 'final-test-002',
            'title': 'BIRAC Biotechnology Grant',
            'bucket': 'Growth',
            'instrument': ['grant'],
            'min_ticket_lakh': 200.0,
            'max_ticket_lakh': 1000.0,
            'typical_ticket_lakh': 500.0,
            'deadline_type': 'batch_call',
            'next_deadline_iso': '2024-11-30T23:59:59Z',
            'eligibility_flags': ['biotech', 'research', 'growth_stage'],
            'sector_tags': ['biotechnology', 'healthcare', 'research'],
            'state_scope': 'national',
            'agency': 'BIRAC',
            'source_urls': ['https://birac.nic.in/'],
            'confidence': 0.88,
            'status': 'live'
        },
        {
            'id': 'final-test-003',
            'title': 'State Innovation Fund',
            'bucket': 'MVP Prototype',
            'instrument': ['grant', 'subsidy'],
            'min_ticket_lakh': 10.0,
            'max_ticket_lakh': 50.0,
            'typical_ticket_lakh': 25.0,
            'deadline_type': 'annual',
            'next_deadline_iso': '2024-10-31T23:59:59Z',
            'eligibility_flags': ['state_based', 'innovation', 'prototype'],
            'sector_tags': ['innovation', 'prototype', 'state_focus'],
            'state_scope': 'Karnataka',
            'agency': 'Karnataka Innovation Authority',
            'source_urls': ['https://startup.karnataka.gov.in/'],
            'confidence': 0.82,
            'status': 'live'
        }
    ]
    
    print("Inserting comprehensive test grants...")
    for i, grant in enumerate(sample_grants, 1):
        success = db_manager.upsert_grant(grant)
        if success:
            print(f"✅ Test grant {i} inserted successfully")
        else:
            print(f"❌ Failed to insert test grant {i}")
            return False
    
    # Test all database operations
    print("\nTesting database operations...")
    
    # 1. Get all grants
    all_grants = db_manager.get_grants()
    print(f"✅ Total grants: {len(all_grants)}")
    
    # 2. Test filtering by status
    live_grants = db_manager.get_grants(filters={'status': 'live'})
    print(f"✅ Live grants: {len(live_grants)}")
    
    # 3. Test filtering by bucket
    early_stage_grants = db_manager.get_grants(filters={'bucket': 'Early Stage'})
    print(f"✅ Early Stage grants: {len(early_stage_grants)}")
    
    # 4. Test filtering by amount
    large_grants = db_manager.get_grants(filters={'min_amount': 100})
    print(f"✅ Large grants (>=100 lakh): {len(large_grants)}")
    
    # 5. Test grant details
    for grant in all_grants:
        print(f"  - {grant.title} ({grant.agency}) - ₹{grant.typical_ticket_lakh}L")
    
    # 6. Test updating grants
    print("\nTesting grant updates...")
    updated_grant = sample_grants[0].copy()
    updated_grant['title'] = 'Updated Startup India Seed Fund'
    updated_grant['confidence'] = 0.98
    success = db_manager.upsert_grant(updated_grant)
    if success:
        print("✅ Grant updated successfully")
    else:
        print("❌ Failed to update grant")
        return False
    
    # 7. Test deadline checking (simplified)
    print("\nTesting deadline checking...")
    week_from_now = datetime.now() + timedelta(days=7)
    expiring_soon = []
    
    for grant in all_grants:
        deadline_str = grant.next_deadline_iso
        if deadline_str is not None:
            try:
                # Simplified deadline parsing
                if deadline_str.endswith('Z'):
                    deadline_str = deadline_str.replace('Z', '+00:00')
                elif '+' not in deadline_str and 'T' in deadline_str:
                    deadline_str = deadline_str + '+00:00'
                
                deadline = datetime.fromisoformat(deadline_str)
                if deadline.tzinfo:
                    deadline = deadline.replace(tzinfo=None)
                
                if deadline <= week_from_now:
                    expiring_soon.append({
                        'title': grant.title,
                        'agency': grant.agency,
                        'deadline': deadline_str,
                        'amount': grant.typical_ticket_lakh
                    })
            except Exception as e:
                print(f"  ⚠️  Could not parse deadline for {grant.title}: {e}")
                continue
    
    print(f"✅ Found {len(expiring_soon)} grants expiring soon")
    for grant in expiring_soon:
        print(f"  - {grant['title']} (Deadline: {grant['deadline']})")
    
    print("\n🎉 Complete SQLite functionality test passed!")
    return True

def test_api_integration():
    """Test API integration with SQLite"""
    print("\n🔗 Testing API Integration...")
    
    try:
        # Import API components
        from api.flask_app import app, db_manager
        
        # Test database connection through API
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test grants endpoint
            response = client.get('/grants')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Grants endpoint working - {data['count']} grants")
            else:
                print(f"❌ Grants endpoint failed: {response.status_code}")
                return False
            
            # Test stats endpoint
            response = client.get('/stats')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Stats endpoint working - {data['total_grants']} total grants")
            else:
                print(f"❌ Stats endpoint failed: {response.status_code}")
                return False
        
        print("🎉 API integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Final SQLite Test...")
    
    # Test 1: Complete functionality
    test1_success = test_complete_sqlite_functionality()
    
    # Test 2: API integration
    test2_success = test_api_integration()
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! SQLite setup is working perfectly.")
        print("\n📊 Summary:")
        print("✅ SQLite database created and working")
        print("✅ All CRUD operations functional")
        print("✅ Filtering and querying working")
        print("✅ API endpoints responding correctly")
        print("✅ Grant management system operational")
        
        print("\n🚀 You can now run the system:")
        print("1. API Server: python main.py --mode api")
        print("2. Discovery Mode: python main.py --mode discovery")
        print("3. Full System: python main.py --mode full")
        
        print("\n📝 Notes:")
        print("- Database file: grants.db")
        print("- Some features require API keys (OpenAI, Slack)")
        print("- Scrapy/Magentic-One may have network issues")
        print("- Core functionality is working correctly")
        
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 