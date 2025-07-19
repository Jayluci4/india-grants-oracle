#!/usr/bin/env python3
"""
Simplified SQLite test - focuses on database functionality
"""

import os
import sys
from datetime import datetime, timedelta

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.models import DatabaseManager

def test_basic_sqlite_operations():
    """Test basic SQLite operations"""
    print("🧪 Testing Basic SQLite Operations...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create tables
    print("Creating tables...")
    db_manager.create_tables()
    print("✅ Tables created successfully")
    
    # Test inserting multiple sample grants
    sample_grants = [
        {
            'id': 'test-grant-001',
            'title': 'Early Stage Tech Grant',
            'bucket': 'Early Stage',
            'instrument': ['grant'],
            'min_ticket_lakh': 10.0,
            'max_ticket_lakh': 50.0,
            'typical_ticket_lakh': 25.0,
            'deadline_type': 'batch_call',
            'next_deadline_iso': '2024-12-31T23:59:59Z',
            'eligibility_flags': ['tech_startup', 'early_stage'],
            'sector_tags': ['technology', 'innovation'],
            'state_scope': 'national',
            'agency': 'Test Agency 1',
            'source_urls': ['https://example.com/grant1'],
            'confidence': 0.85,
            'status': 'live'
        },
        {
            'id': 'test-grant-002',
            'title': 'Growth Stage Funding',
            'bucket': 'Growth',
            'instrument': ['convertible_debenture'],
            'min_ticket_lakh': 100.0,
            'max_ticket_lakh': 500.0,
            'typical_ticket_lakh': 250.0,
            'deadline_type': 'rolling',
            'next_deadline_iso': '2024-11-30T23:59:59Z',
            'eligibility_flags': ['growth_stage', 'revenue_generating'],
            'sector_tags': ['fintech', 'ecommerce'],
            'state_scope': 'national',
            'agency': 'Test Agency 2',
            'source_urls': ['https://example.com/grant2'],
            'confidence': 0.92,
            'status': 'live'
        },
        {
            'id': 'test-grant-003',
            'title': 'Infrastructure Support Grant',
            'bucket': 'Infra',
            'instrument': ['grant'],
            'min_ticket_lakh': 500.0,
            'max_ticket_lakh': 2000.0,
            'typical_ticket_lakh': 1000.0,
            'deadline_type': 'annual',
            'next_deadline_iso': '2024-10-31T23:59:59Z',
            'eligibility_flags': ['established_company', 'infrastructure'],
            'sector_tags': ['infrastructure', 'logistics'],
            'state_scope': 'national',
            'agency': 'Test Agency 3',
            'source_urls': ['https://example.com/grant3'],
            'confidence': 0.78,
            'status': 'live'
        }
    ]
    
    print("Inserting sample grants...")
    for i, grant in enumerate(sample_grants, 1):
        success = db_manager.upsert_grant(grant)
        if success:
            print(f"✅ Sample grant {i} inserted successfully")
        else:
            print(f"❌ Failed to insert sample grant {i}")
            return False
    
    # Test retrieving all grants
    print("\nRetrieving all grants...")
    all_grants = db_manager.get_grants()
    print(f"✅ Found {len(all_grants)} total grants in database")
    
    # Test filtering by status
    print("\nTesting status filter...")
    live_grants = db_manager.get_grants(filters={'status': 'live'})
    print(f"✅ Found {len(live_grants)} live grants")
    
    # Test filtering by bucket
    print("\nTesting bucket filter...")
    early_stage_grants = db_manager.get_grants(filters={'bucket': 'Early Stage'})
    print(f"✅ Found {len(early_stage_grants)} Early Stage grants")
    
    # Test filtering by amount range
    print("\nTesting amount filter...")
    large_grants = db_manager.get_grants(filters={'min_amount': 100})
    print(f"✅ Found {len(large_grants)} grants with min amount >= 100 lakh")
    
    # Test updating a grant
    print("\nTesting grant update...")
    updated_grant = sample_grants[0].copy()
    updated_grant['title'] = 'Updated Early Stage Tech Grant'
    updated_grant['confidence'] = 0.95
    success = db_manager.upsert_grant(updated_grant)
    if success:
        print("✅ Grant updated successfully")
    else:
        print("❌ Failed to update grant")
        return False
    
    # Verify the update
    updated_grants = db_manager.get_grants(filters={'status': 'live'})
    for grant in updated_grants:
        if grant.id == 'test-grant-001':
            print(f"✅ Grant title updated to: {grant.title}")
            print(f"✅ Confidence updated to: {grant.confidence}")
            break
    
    # Test deadline checking functionality
    print("\nTesting deadline checking...")
    week_from_now = datetime.now() + timedelta(days=7)
    expiring_soon = []
    
    for grant in all_grants:
        if grant.next_deadline_iso is not None:
            try:
                deadline = datetime.fromisoformat(grant.next_deadline_iso.replace('Z', '+00:00'))
                if deadline <= week_from_now:
                    expiring_soon.append({
                        'title': grant.title,
                        'agency': grant.agency,
                        'next_deadline_iso': grant.next_deadline_iso,
                        'typical_ticket_lakh': grant.typical_ticket_lakh
                    })
            except Exception as e:
                print(f"Warning: Could not parse deadline for grant {grant.id}: {e}")
                continue
    
    print(f"✅ Found {len(expiring_soon)} grants expiring soon")
    for grant in expiring_soon:
        print(f"  - {grant['title']} (Deadline: {grant['next_deadline_iso']})")
    
    print("\n🎉 Basic SQLite operations test completed successfully!")
    return True

def test_database_manager_methods():
    """Test all database manager methods"""
    print("\n🔧 Testing Database Manager Methods...")
    
    db_manager = DatabaseManager()
    
    # Test session management
    print("Testing session management...")
    session = db_manager.get_session()
    if session:
        print("✅ Session created successfully")
        session.close()
        print("✅ Session closed successfully")
    else:
        print("❌ Failed to create session")
        return False
    
    # Test table creation (should be idempotent)
    print("Testing table creation...")
    try:
        db_manager.create_tables()
        print("✅ Tables created successfully (idempotent)")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False
    
    print("🎉 Database manager methods test completed successfully!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Simplified SQLite Tests...")
    
    # Test 1: Basic operations
    test1_success = test_basic_sqlite_operations()
    
    # Test 2: Database manager methods
    test2_success = test_database_manager_methods()
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! SQLite is working correctly for development.")
        print("\nDatabase file created: grants.db")
        print("\nYou can now:")
        print("1. Run the API server: python main.py --mode api")
        print("2. Run discovery once: python main.py --mode discovery")
        print("3. Run full system: python main.py --mode full")
        print("\nNote: Some features may require API keys (OpenAI, Slack, etc.)")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 