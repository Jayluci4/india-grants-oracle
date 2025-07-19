-- India Startup Grant Oracle - Database Setup Script
-- Run this after deploying to GCP to initialize the database

-- Create the grants table with proper indexes
CREATE TABLE IF NOT EXISTS grants (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    bucket VARCHAR(50),
    instrument JSONB,
    min_ticket_lakh DECIMAL(10,2),
    max_ticket_lakh DECIMAL(10,2),
    typical_ticket_lakh DECIMAL(10,2),
    deadline_type VARCHAR(50),
    next_deadline_iso VARCHAR(50),
    eligibility_flags JSONB,
    sector_tags JSONB,
    state_scope VARCHAR(100),
    agency VARCHAR(200),
    source_urls JSONB,
    confidence DECIMAL(3,2),
    last_seen_iso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_iso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'live',
    
    -- Enhancement 1: Confidence Scoring and Data Lineage
    data_lineage JSONB,
    
    -- Enhancement 2: Smart Deduplication
    original_id VARCHAR(50),
    is_duplicate BOOLEAN DEFAULT FALSE,
    
    -- Enhancement 3: Eligibility Matching Score
    eligibility_criteria JSONB,
    target_audience JSONB,
    
    -- Enhancement 4: Grant Status Monitoring
    last_checked_iso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_reason VARCHAR(100),
    
    -- Enhancement 5: Application Complexity Indicator
    application_complexity VARCHAR(20) DEFAULT 'medium'
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_grants_status ON grants(status);
CREATE INDEX IF NOT EXISTS idx_grants_bucket ON grants(bucket);
CREATE INDEX IF NOT EXISTS idx_grants_agency ON grants(agency);
CREATE INDEX IF NOT EXISTS idx_grants_state_scope ON grants(state_scope);
CREATE INDEX IF NOT EXISTS idx_grants_deadline ON grants(next_deadline_iso);
CREATE INDEX IF NOT EXISTS idx_grants_amount ON grants(typical_ticket_lakh);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_grants_instrument_gin ON grants USING GIN(instrument);
CREATE INDEX IF NOT EXISTS idx_grants_eligibility_gin ON grants USING GIN(eligibility_flags);
CREATE INDEX IF NOT EXISTS idx_grants_sectors_gin ON grants USING GIN(sector_tags);

-- Create text search index for title and agency
CREATE INDEX IF NOT EXISTS idx_grants_text_search ON grants USING GIN(to_tsvector('english', title || ' ' || agency));

-- Insert sample data
INSERT INTO grants (
    id, title, bucket, instrument, min_ticket_lakh, max_ticket_lakh, typical_ticket_lakh,
    deadline_type, next_deadline_iso, eligibility_flags, sector_tags, state_scope,
    agency, source_urls, confidence, status
) VALUES 
(
    'sisfs_seed_grant',
    'Startup India Seed Fund Scheme',
    'Early Stage',
    '["grant", "convertible_debenture"]'::jsonb,
    20, 70, 60,
    'rolling',
    '2025-12-31T23:59:59Z',
    '["dpiit_recognised", "<2_years", "indian_promoters"]'::jsonb,
    '["tech_agnostic"]'::jsonb,
    'national',
    'DPIIT, GoI',
    '["https://seedfund.startupindia.gov.in"]'::jsonb,
    0.95,
    'live'
),
(
    'birac_leap_grant',
    'BIRAC LEAP Grant for Biotechnology Startups',
    'Early Stage',
    '["grant"]'::jsonb,
    50, 100, 75,
    'batch_call',
    '2025-08-31T23:59:59Z',
    '["biotech_startup", "innovation_focus"]'::jsonb,
    '["biotechnology", "healthcare", "life_sciences"]'::jsonb,
    'national',
    'BIRAC, DBT, GoI',
    '["https://birac.nic.in/call_details.aspx"]'::jsonb,
    0.90,
    'live'
),
(
    'karnataka_startup_grant',
    'Karnataka Startup Grant Scheme',
    'MVP Prototype',
    '["grant", "soft_loan"]'::jsonb,
    10, 25, 15,
    'annual',
    '2025-09-30T23:59:59Z',
    '["karnataka_based", "tech_startup"]'::jsonb,
    '["technology", "innovation"]'::jsonb,
    'Karnataka',
    'Karnataka Innovation and Technology Society',
    '["https://startup.karnataka.gov.in"]'::jsonb,
    0.85,
    'live'
),
(
    'tdb_technopreneur_grant',
    'TDB Technopreneur Promotion Programme',
    'Growth',
    '["grant", "soft_loan"]'::jsonb,
    100, 500, 250,
    'batch_call',
    '2025-10-15T23:59:59Z',
    '["tech_innovation", "commercialization"]'::jsonb,
    '["technology", "manufacturing", "services"]'::jsonb,
    'national',
    'Technology Development Board, DST',
    '["https://tdb.gov.in"]'::jsonb,
    0.88,
    'live'
),
(
    'meity_samridh_grant',
    'MeitY SAMRIDH Accelerator Programme',
    'Early Stage',
    '["grant"]'::jsonb,
    40, 40, 40,
    'batch_call',
    '2025-07-31T23:59:59Z',
    '["software_product", "indian_startup"]'::jsonb,
    '["software", "technology", "digital"]'::jsonb,
    'national',
    'Ministry of Electronics and IT',
    '["https://www.meity.gov.in"]'::jsonb,
    0.92,
    'live'
)
ON CONFLICT (id) DO NOTHING;

-- Create a view for active grants with calculated fields
CREATE OR REPLACE VIEW active_grants AS
SELECT 
    *,
    CASE 
        WHEN next_deadline_iso IS NOT NULL 
        THEN EXTRACT(DAYS FROM (next_deadline_iso::timestamp - CURRENT_TIMESTAMP))
        ELSE NULL 
    END as days_to_deadline,
    CASE 
        WHEN typical_ticket_lakh >= 100 THEN 'High'
        WHEN typical_ticket_lakh >= 25 THEN 'Medium'
        ELSE 'Low'
    END as funding_tier
FROM grants 
WHERE status = 'live';

-- Grant summary statistics
CREATE OR REPLACE VIEW grant_statistics AS
SELECT 
    COUNT(*) as total_grants,
    COUNT(*) FILTER (WHERE status = 'live') as live_grants,
    COUNT(*) FILTER (WHERE status = 'expired') as expired_grants,
    AVG(typical_ticket_lakh) as avg_funding_amount,
    MAX(typical_ticket_lakh) as max_funding_amount,
    MIN(typical_ticket_lakh) as min_funding_amount,
    COUNT(DISTINCT agency) as unique_agencies,
    COUNT(DISTINCT state_scope) as coverage_states
FROM grants;

-- Grants by bucket summary
CREATE OR REPLACE VIEW grants_by_bucket AS
SELECT 
    bucket,
    COUNT(*) as grant_count,
    AVG(typical_ticket_lakh) as avg_amount,
    MIN(typical_ticket_lakh) as min_amount,
    MAX(typical_ticket_lakh) as max_amount
FROM grants 
WHERE status = 'live'
GROUP BY bucket
ORDER BY grant_count DESC;

COMMIT;

