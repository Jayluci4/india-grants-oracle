#!/usr/bin/env python3
"""
Simple API server for testing the Grant Oracle
"""

import sys
import os
sys.path.append('src')

from flask import Flask, jsonify
from flask_cors import CORS
from database.models import DatabaseManager

app = Flask(__name__)
CORS(app)

# Initialize database
db_manager = DatabaseManager()

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        "message": "India Startup Grant Oracle API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "/grants": "GET - List all grants",
            "/stats": "GET - Get database statistics",
            "/health": "GET - Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        grants = db_manager.get_grants(limit=1)
        db_status = "connected"
        grant_count = len(db_manager.get_grants())
    except Exception as e:
        db_status = f"error: {str(e)}"
        grant_count = 0
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "grant_count": grant_count
    })

@app.route('/grants', methods=['GET'])
def get_grants():
    """Get all grants"""
    try:
        grants = db_manager.get_grants()
        
        grants_data = []
        for grant in grants:
            grants_data.append({
                'id': grant.id,
                'title': grant.title,
                'agency': grant.agency,
                'bucket': grant.bucket,
                'min_ticket_lakh': grant.min_ticket_lakh,
                'max_ticket_lakh': grant.max_ticket_lakh,
                'typical_ticket_lakh': grant.typical_ticket_lakh,
                'deadline_type': grant.deadline_type,
                'next_deadline_iso': grant.next_deadline_iso,
                'eligibility_flags': grant.eligibility_flags,
                'sector_tags': grant.sector_tags,
                'state_scope': grant.state_scope,
                'status': grant.status
            })
        
        return jsonify({
            "grants": grants_data,
            "count": len(grants_data)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        grants = db_manager.get_grants()
        
        total_grants = len(grants)
        live_grants = len([g for g in grants if g.status == 'live'])
        
        bucket_stats = {}
        for grant in grants:
            bucket = grant.bucket or 'Unknown'
            bucket_stats[bucket] = bucket_stats.get(bucket, 0) + 1
        
        return jsonify({
            "total_grants": total_grants,
            "live_grants": live_grants,
            "grants_by_bucket": bucket_stats
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🏗️ Starting India Startup Grant Oracle API...")
    print("Database URL:", os.getenv('DATABASE_URL', 'postgresql://grants:grants@localhost:5432/grantsdb'))
    
    app.run(host='0.0.0.0', port=8000, debug=False)

