#!/usr/bin/env python3
"""
Test script for SQLite setup
"""

import os
import sys
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.models import DatabaseManager, Grant

def test_sqlite_setup():
    """Test SQLite database setup and basic operations"""
    print("🧪 Testing SQLite Setup...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Create tables
    print("Creating tables...")
    db_manager.create_tables()
    print("✅ Tables created successfully")
    
    # Test inserting a sample grant
    sample_grant = {
        'id': 'test-grant-001',
        'title': 'Test Startup Grant',
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
        'agency': 'Test Agency',
        'source_urls': ['https://example.com/grant'],
        'confidence': 0.85,
        'status': 'live'
    }
    
    print("Inserting sample grant...")
    success = db_manager.upsert_grant(sample_grant)
    if success:
        print("✅ Sample grant inserted successfully")
    else:
        print("❌ Failed to insert sample grant")
        return False
    
    # Test retrieving grants
    print("Retrieving grants...")
    grants = db_manager.get_grants()
    print(f"✅ Found {len(grants)} grants in database")
    
    # Test filtering
    print("Testing filters...")
    live_grants = db_manager.get_grants(filters={'status': 'live'})
    print(f"✅ Found {len(live_grants)} live grants")
    
    # Test updating grant
    print("Testing grant update...")
    updated_grant = sample_grant.copy()
    updated_grant['title'] = 'Updated Test Startup Grant'
    success = db_manager.upsert_grant(updated_grant)
    if success:
        print("✅ Grant updated successfully")
    else:
        print("❌ Failed to update grant")
        return False
    
    # Verify update
    updated_grants = db_manager.get_grants(filters={'status': 'live'})
    for grant in updated_grants:
        if grant.id == 'test-grant-001':
            print(f"✅ Grant title updated to: {grant.title}")
            break
    
    print("\n🎉 SQLite setup test completed successfully!")
    return True

def test_main_integration():
    """Test main.py integration with SQLite"""
    print("\n🔗 Testing Main Integration...")
    
    try:
        # Import and test main components
        from main import GrantOracleMain
        
        oracle = GrantOracleMain()
        print("✅ GrantOracleMain initialized successfully")
        
        # Test database connection
        grants = oracle.db_manager.get_grants()
        print(f"✅ Database connection working - {len(grants)} grants found")
        
        print("🎉 Main integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Main integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting SQLite Setup Tests...")
    
    # Test 1: Basic SQLite setup
    test1_success = test_sqlite_setup()
    
    # Test 2: Main integration
    test2_success = test_main_integration()
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! SQLite setup is working correctly.")
        print("\nYou can now run the system with:")
        print("python main.py --mode discovery")
        print("python main.py --mode api")
        print("python main.py --mode full")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 