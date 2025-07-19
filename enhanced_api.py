#!/usr/bin/env python3
"""
Enhanced India Startup Grant Oracle API
Includes all 5 enhancements: Confidence Scoring, Deduplication, Eligibility Matching, Status Monitoring, Complexity Indicator
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import os
import sys
from datetime import datetime
import json

# Add src to path for imports
sys.path.append('src')
from enhancements.confidence_scoring import enhance_grant_with_confidence
from enhancements.deduplication import deduplicate_grants
from enhancements.eligibility_matching import calculate_startup_grant_match
from enhancements.status_monitoring import monitor_grant_status
from enhancements.complexity_indicator import calculate_application_complexity

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://grants:grants@localhost:5432/grantsdb')

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def dict_to_grant(row):
    """Convert database row to grant dictionary"""
    return {
        'id': row['id'],
        'title': row['title'],
        'bucket': row['bucket'],
        'instrument': row['instrument'],
        'min_ticket_lakh': row['min_ticket_lakh'],
        'max_ticket_lakh': row['max_ticket_lakh'],
        'typical_ticket_lakh': row['typical_ticket_lakh'],
        'deadline_type': row['deadline_type'],
        'next_deadline_iso': row['next_deadline_iso'],
        'eligibility_flags': row['eligibility_flags'],
        'sector_tags': row['sector_tags'],
        'state_scope': row['state_scope'],
        'agency': row['agency'],
        'source_urls': row['source_urls'],
        'confidence': row['confidence'],
        'last_seen_iso': row['last_seen_iso'].isoformat() if row['last_seen_iso'] else None,
        'created_iso': row['created_iso'].isoformat() if row['created_iso'] else None,
        'status': row['status'],
        # Enhanced fields
        'data_lineage': row.get('data_lineage'),
        'original_id': row.get('original_id'),
        'is_duplicate': row.get('is_duplicate', False),
        'eligibility_criteria': row.get('eligibility_criteria'),
        'target_audience': row.get('target_audience'),
        'last_checked_iso': row['last_checked_iso'].isoformat() if row.get('last_checked_iso') else None,
        'status_reason': row.get('status_reason'),
        'application_complexity': row.get('application_complexity', 'medium')
    }

@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        'name': 'India Startup Grant Oracle - Enhanced API',
        'version': '2.0.0',
        'description': 'Enhanced grant discovery system with AI-powered features',
        'enhancements': [
            'Confidence Scoring & Data Lineage',
            'Smart Deduplication with Fuzzy Matching',
            'Eligibility Matching Score',
            'Grant Status Monitoring',
            'Application Complexity Indicator'
        ],
        'endpoints': {
            '/grants': 'List all grants with filtering',
            '/grants/<id>': 'Get specific grant details',
            '/grants/search': 'Search grants with advanced filters',
            '/grants/match': 'Get personalized grant recommendations',
            '/grants/complexity': 'Analyze application complexity',
            '/grants/monitor': 'Monitor grant status updates',
            '/stats': 'Database and system statistics',
            '/health': 'System health check'
        }
    })

@app.route('/grants')
def get_grants():
    """Get all grants with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with filters
        query = "SELECT * FROM grants WHERE 1=1"
        params = []
        
        # Filter parameters
        bucket = request.args.get('bucket')
        status = request.args.get('status', 'live')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        sector = request.args.get('sector')
        state = request.args.get('state')
        complexity = request.args.get('complexity')
        include_duplicates = request.args.get('include_duplicates', 'false').lower() == 'true'
        
        if bucket:
            query += " AND bucket = %s"
            params.append(bucket)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if min_amount:
            query += " AND (typical_ticket_lakh >= %s OR max_ticket_lakh >= %s)"
            params.extend([min_amount, min_amount])
        
        if max_amount:
            query += " AND (typical_ticket_lakh <= %s OR min_ticket_lakh <= %s)"
            params.extend([max_amount, max_amount])
        
        if sector:
            query += " AND sector_tags @> %s"
            params.append(Json([sector]))
        
        if state:
            query += " AND (state_scope ILIKE %s OR state_scope = 'national')"
            params.append(f'%{state}%')
        
        if complexity:
            query += " AND application_complexity = %s"
            params.append(complexity)
        
        if not include_duplicates:
            query += " AND (is_duplicate = FALSE OR is_duplicate IS NULL)"
        
        # Add ordering
        query += " ORDER BY confidence DESC, typical_ticket_lakh DESC"
        
        # Add limit
        limit = request.args.get('limit', 100, type=int)
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        grants = [dict_to_grant(row) for row in rows]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'grants': grants,
            'count': len(grants),
            'filters_applied': {
                'bucket': bucket,
                'status': status,
                'min_amount': min_amount,
                'max_amount': max_amount,
                'sector': sector,
                'state': state,
                'complexity': complexity,
                'include_duplicates': include_duplicates
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/grants/<grant_id>')
def get_grant(grant_id):
    """Get specific grant details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM grants WHERE id = %s", (grant_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Grant not found'}), 404
        
        grant = dict_to_grant(row)
        
        # Add enhanced analysis
        if request.args.get('include_analysis', 'false').lower() == 'true':
            # Add complexity analysis
            complexity_analysis = calculate_application_complexity(grant)
            grant['complexity_analysis'] = complexity_analysis
            
            # Add status monitoring if requested
            if request.args.get('check_status', 'false').lower() == 'true':
                status_info = monitor_grant_status(grant)
                grant.update(status_info)
        
        cursor.close()
        conn.close()
        
        return jsonify(grant)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/grants/search')
def search_grants():
    """Advanced grant search with text search"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        search_term = request.args.get('q', '')
        
        if search_term:
            query = """
            SELECT * FROM grants 
            WHERE (title ILIKE %s OR agency ILIKE %s)
            AND status = 'live'
            AND (is_duplicate = FALSE OR is_duplicate IS NULL)
            ORDER BY confidence DESC
            LIMIT 50
            """
            search_pattern = f'%{search_term}%'
            cursor.execute(query, (search_pattern, search_pattern))
        else:
            cursor.execute("""
            SELECT * FROM grants 
            WHERE status = 'live' 
            AND (is_duplicate = FALSE OR is_duplicate IS NULL)
            ORDER BY confidence DESC 
            LIMIT 50
            """)
        
        rows = cursor.fetchall()
        grants = [dict_to_grant(row) for row in rows]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'grants': grants,
            'count': len(grants),
            'search_term': search_term
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/grants/match', methods=['POST'])
def match_grants():
    """Get personalized grant recommendations based on startup profile"""
    try:
        startup_profile = request.get_json()
        
        if not startup_profile:
            return jsonify({'error': 'Startup profile required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all live grants
        cursor.execute("""
        SELECT * FROM grants 
        WHERE status = 'live' 
        AND (is_duplicate = FALSE OR is_duplicate IS NULL)
        """)
        rows = cursor.fetchall()
        
        grants_with_scores = []
        
        for row in rows:
            grant = dict_to_grant(row)
            
            # Calculate eligibility match
            match_result = calculate_startup_grant_match(startup_profile, grant)
            
            grant['eligibility_score'] = match_result['overall_score']
            grant['score_breakdown'] = match_result['score_breakdown']
            grant['recommendations'] = match_result['recommendations']
            
            grants_with_scores.append(grant)
        
        # Sort by eligibility score
        grants_with_scores.sort(key=lambda g: g['eligibility_score'], reverse=True)
        
        # Return top matches
        top_matches = grants_with_scores[:20]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'matches': top_matches,
            'count': len(top_matches),
            'startup_profile': startup_profile
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/grants/complexity')
def analyze_complexity():
    """Analyze application complexity for grants"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get grants for complexity analysis
        complexity_filter = request.args.get('complexity')
        
        query = "SELECT * FROM grants WHERE status = 'live'"
        params = []
        
        if complexity_filter:
            query += " AND application_complexity = %s"
            params.append(complexity_filter)
        
        query += " ORDER BY typical_ticket_lakh DESC LIMIT 50"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        grants_with_complexity = []
        
        for row in rows:
            grant = dict_to_grant(row)
            complexity_analysis = calculate_application_complexity(grant)
            grant['complexity_analysis'] = complexity_analysis
            grants_with_complexity.append(grant)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'grants': grants_with_complexity,
            'count': len(grants_with_complexity)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/grants/monitor')
def monitor_grants():
    """Monitor grant status updates"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get grants that need monitoring
        cursor.execute("""
        SELECT * FROM grants 
        WHERE status = 'live' 
        AND (last_checked_iso IS NULL OR last_checked_iso < NOW() - INTERVAL '24 hours')
        LIMIT 10
        """)
        rows = cursor.fetchall()
        
        monitored_grants = []
        
        for row in rows:
            grant = dict_to_grant(row)
            
            # Monitor status
            updated_grant = monitor_grant_status(grant)
            monitored_grants.append(updated_grant)
            
            # Update database with new status
            cursor.execute("""
            UPDATE grants 
            SET last_checked_iso = %s, status = %s, status_reason = %s
            WHERE id = %s
            """, (
                datetime.now(),
                updated_grant.get('status', 'live'),
                updated_grant.get('status_reason'),
                grant['id']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'monitored_grants': monitored_grants,
            'count': len(monitored_grants)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Get database and system statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Basic stats
        cursor.execute("SELECT COUNT(*) as total FROM grants")
        total_grants = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as live FROM grants WHERE status = 'live'")
        live_grants = cursor.fetchone()['live']
        
        cursor.execute("SELECT COUNT(*) as duplicates FROM grants WHERE is_duplicate = TRUE")
        duplicate_grants = cursor.fetchone()['duplicates']
        
        # Status breakdown
        cursor.execute("SELECT status, COUNT(*) as count FROM grants GROUP BY status")
        status_breakdown = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Complexity breakdown
        cursor.execute("SELECT application_complexity, COUNT(*) as count FROM grants GROUP BY application_complexity")
        complexity_breakdown = {row['application_complexity']: row['count'] for row in cursor.fetchall()}
        
        # Bucket breakdown
        cursor.execute("SELECT bucket, COUNT(*) as count FROM grants WHERE status = 'live' GROUP BY bucket")
        bucket_breakdown = {row['bucket']: row['count'] for row in cursor.fetchall()}
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) as avg_confidence FROM grants WHERE status = 'live'")
        avg_confidence = cursor.fetchone()['avg_confidence']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_grants': total_grants,
            'live_grants': live_grants,
            'duplicate_grants': duplicate_grants,
            'average_confidence': round(float(avg_confidence or 0), 2),
            'status_breakdown': status_breakdown,
            'complexity_breakdown': complexity_breakdown,
            'bucket_breakdown': bucket_breakdown,
            'enhancements_active': {
                'confidence_scoring': True,
                'deduplication': True,
                'eligibility_matching': True,
                'status_monitoring': True,
                'complexity_indicator': True
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """System health check"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat(),
            'enhancements': 'active'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced India Startup Grant Oracle API...")
    print(f"Database URL: {DATABASE_URL}")
    app.run(host='0.0.0.0', port=8000, debug=False)

