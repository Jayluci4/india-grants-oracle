#!/usr/bin/env python3
"""
Load seed data from grants_seed_data.json into the database
"""

import json
import sys
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import Json

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://grants:grants@localhost:5432/grantsdb')
    return psycopg2.connect(database_url)

def load_seed_data():
    """Load seed data from JSON file into the database"""
    
    # Read the seed data - handle multiple JSON arrays
    seed_file = '/home/ubuntu/upload/grants_seed_data.json'
    if not os.path.exists(seed_file):
        print(f"❌ Seed data file not found: {seed_file}")
        return False
    
    with open(seed_file, 'r') as f:
        content = f.read()
    
    # Split by the pattern ']  [' to handle multiple JSON arrays
    json_parts = content.split('  ]\n  [')
    seed_data = []
    
    for i, part in enumerate(json_parts):
        if i == 0:
            # First part, just add closing bracket if needed
            if not part.strip().endswith(']'):
                part = part + '  ]'
        elif i == len(json_parts) - 1:
            # Last part, add opening bracket
            part = '  [' + part
        else:
            # Middle parts, add both brackets
            part = '  [' + part + '  ]'
        
        try:
            data = json.loads(part)
            seed_data.extend(data)
            print(f"✅ Parsed JSON part {i+1}: {len(data)} grants")
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing JSON part {i}: {e}")
            # Try to fix common issues
            try:
                # Remove trailing whitespace and try again
                cleaned_part = part.strip()
                data = json.loads(cleaned_part)
                seed_data.extend(data)
                print(f"✅ Parsed JSON part {i+1} after cleaning: {len(data)} grants")
            except:
                print(f"❌ Could not parse JSON part {i} even after cleaning")
                continue
    
    print(f"📊 Found {len(seed_data)} grants in seed data")
    
    # Connect to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM grants")
        print("🗑️  Cleared existing grants data")
        
        # Insert seed data
        inserted_count = 0
        for grant in seed_data:
            try:
                # Map the seed data fields to our database schema
                grant_id = grant.get('slug', f"grant_{inserted_count}")
                title = grant.get('name', 'Unknown Grant')
                bucket = grant.get('stage_bucket', 'Unknown')
                
                # Handle funding amounts
                min_ticket = grant.get('funding_min_lakh')
                max_ticket = grant.get('funding_max_lakh') 
                typical_ticket = grant.get('typical_ticket_lakh')
                
                # Use typical if available, otherwise average of min/max, otherwise max
                if typical_ticket:
                    typical_ticket_lakh = typical_ticket
                elif min_ticket and max_ticket:
                    typical_ticket_lakh = (min_ticket + max_ticket) / 2
                elif max_ticket:
                    typical_ticket_lakh = max_ticket
                elif min_ticket:
                    typical_ticket_lakh = min_ticket
                else:
                    typical_ticket_lakh = 0
                
                # Handle instruments
                instrument_primary = grant.get('instrument_primary', 'grant')
                instruments_other = grant.get('instruments_other', [])
                instruments = [instrument_primary] + instruments_other
                
                # Handle eligibility and benefits
                eligibility_summary = grant.get('eligibility_summary', '')
                key_benefits = grant.get('key_benefits', [])
                
                # Handle sector tags
                sector_tags = grant.get('sector_tags', [])
                
                # Handle geography
                geography_scope = grant.get('geography_scope', 'India')
                state_scope = 'national' if 'India' in geography_scope else geography_scope
                
                # Handle agency/source
                source_primary = grant.get('source_primary', '')
                extra_sources = grant.get('extra_sources', [])
                all_sources = [source_primary] + extra_sources if source_primary else extra_sources
                
                # Handle application mode and deadline
                application_mode = grant.get('application_mode', 'rolling')
                deadline_type = 'rolling' if application_mode == 'rolling' else 'batch_call'
                
                # Set next deadline (placeholder)
                next_deadline = '2025-12-31T23:59:59Z'
                
                # Handle confidence score
                confidence = grant.get('confidence_score', 0.8)
                
                # Insert into database
                insert_query = """
                INSERT INTO grants (
                    id, title, bucket, instrument, min_ticket_lakh, max_ticket_lakh, 
                    typical_ticket_lakh, deadline_type, next_deadline_iso, 
                    eligibility_flags, sector_tags, state_scope, agency, 
                    source_urls, confidence, last_seen_iso, created_iso, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    bucket = EXCLUDED.bucket,
                    instrument = EXCLUDED.instrument,
                    min_ticket_lakh = EXCLUDED.min_ticket_lakh,
                    max_ticket_lakh = EXCLUDED.max_ticket_lakh,
                    typical_ticket_lakh = EXCLUDED.typical_ticket_lakh,
                    deadline_type = EXCLUDED.deadline_type,
                    next_deadline_iso = EXCLUDED.next_deadline_iso,
                    eligibility_flags = EXCLUDED.eligibility_flags,
                    sector_tags = EXCLUDED.sector_tags,
                    state_scope = EXCLUDED.state_scope,
                    agency = EXCLUDED.agency,
                    source_urls = EXCLUDED.source_urls,
                    confidence = EXCLUDED.confidence,
                    last_seen_iso = EXCLUDED.last_seen_iso
                """
                
                cursor.execute(insert_query, (
                    grant_id,
                    title,
                    bucket,
                    Json(instruments),
                    min_ticket,
                    max_ticket,
                    typical_ticket_lakh,
                    deadline_type,
                    next_deadline,
                    Json([eligibility_summary]),
                    Json(sector_tags),
                    state_scope,
                    f"Source: {source_primary}" if source_primary else "Various",
                    Json(all_sources),
                    confidence,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    'live'
                ))
                
                inserted_count += 1
                
            except Exception as e:
                print(f"⚠️  Error inserting grant {grant.get('name', 'Unknown')}: {e}")
                continue
        
        # Commit changes
        conn.commit()
        print(f"✅ Successfully loaded {inserted_count} grants into database")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM grants WHERE status = 'live'")
        count = cursor.fetchone()[0]
        print(f"📊 Total live grants in database: {count}")
        
        # Show sample data
        cursor.execute("SELECT id, title, typical_ticket_lakh, bucket FROM grants LIMIT 5")
        samples = cursor.fetchall()
        print("\n📋 Sample grants loaded:")
        for sample in samples:
            print(f"  • {sample[1]} (₹{sample[2]}L, {sample[3]})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Loading seed data into India Grants Oracle database...")
    success = load_seed_data()
    if success:
        print("✅ Seed data loading completed successfully!")
    else:
        print("❌ Seed data loading failed!")
        sys.exit(1)

