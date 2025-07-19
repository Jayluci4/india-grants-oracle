from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import DatabaseManager, Grant

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
db_manager = DatabaseManager()
db_manager.create_tables()

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        "message": "India Startup Grant Oracle API",
        "version": "1.0.0",
        "endpoints": {
            "/grants": "GET - List all grants with optional filters",
            "/grants/<grant_id>": "GET - Get specific grant details",
            "/stats": "GET - Get database statistics",
            "/health": "GET - Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        grants = db_manager.get_grants(limit=1)
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status
    })

@app.route('/grants', methods=['GET'])
def get_grants():
    """Get grants with optional filtering"""
    try:
        # Parse query parameters
        bucket = request.args.get('bucket')
        status = request.args.get('status', 'live')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        limit = request.args.get('limit', 50, type=int)
        agency = request.args.get('agency')
        sector = request.args.get('sector')
        
        # Build filters
        filters = {}
        if bucket:
            filters['bucket'] = bucket
        if status:
            filters['status'] = status
        if min_amount:
            filters['min_amount'] = min_amount
        if max_amount:
            filters['max_amount'] = max_amount
        
        # Get grants from database
        grants = db_manager.get_grants(filters=filters, limit=limit)
        
        # Convert to JSON-serializable format
        grants_data = []
        for grant in grants:
            grant_dict = {
                'id': grant.id,
                'title': grant.title,
                'bucket': grant.bucket,
                'instrument': grant.instrument,
                'min_ticket_lakh': grant.min_ticket_lakh,
                'max_ticket_lakh': grant.max_ticket_lakh,
                'typical_ticket_lakh': grant.typical_ticket_lakh,
                'deadline_type': grant.deadline_type,
                'next_deadline_iso': grant.next_deadline_iso,
                'eligibility_flags': grant.eligibility_flags,
                'sector_tags': grant.sector_tags,
                'state_scope': grant.state_scope,
                'agency': grant.agency,
                'source_urls': grant.source_urls,
                'confidence': grant.confidence,
                'last_seen_iso': grant.last_seen_iso.isoformat() if grant.last_seen_iso else None,
                'created_iso': grant.created_iso.isoformat() if grant.created_iso else None,
                'status': grant.status
            }
            
            # Apply additional filters
            if agency and agency.lower() not in grant_dict['agency'].lower():
                continue
            if sector and not any(sector.lower() in tag.lower() for tag in grant_dict['sector_tags']):
                continue
                
            grants_data.append(grant_dict)
        
        return jsonify({
            "grants": grants_data,
            "count": len(grants_data),
            "filters_applied": filters,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/grants/<grant_id>', methods=['GET'])
def get_grant_by_id(grant_id):
    """Get specific grant by ID"""
    try:
        session = db_manager.get_session()
        grant = session.query(Grant).filter(Grant.id == grant_id).first()
        session.close()
        
        if not grant:
            return jsonify({
                "error": "Grant not found",
                "grant_id": grant_id
            }), 404
        
        grant_dict = {
            'id': grant.id,
            'title': grant.title,
            'bucket': grant.bucket,
            'instrument': grant.instrument,
            'min_ticket_lakh': grant.min_ticket_lakh,
            'max_ticket_lakh': grant.max_ticket_lakh,
            'typical_ticket_lakh': grant.typical_ticket_lakh,
            'deadline_type': grant.deadline_type,
            'next_deadline_iso': grant.next_deadline_iso,
            'eligibility_flags': grant.eligibility_flags,
            'sector_tags': grant.sector_tags,
            'state_scope': grant.state_scope,
            'agency': grant.agency,
            'source_urls': grant.source_urls,
            'confidence': grant.confidence,
            'last_seen_iso': grant.last_seen_iso.isoformat() if grant.last_seen_iso else None,
            'created_iso': grant.created_iso.isoformat() if grant.created_iso else None,
            'status': grant.status
        }
        
        return jsonify(grant_dict)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "grant_id": grant_id
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        session = db_manager.get_session()
        
        # Total grants
        total_grants = session.query(Grant).count()
        
        # Grants by status
        live_grants = session.query(Grant).filter(Grant.status == 'live').count()
        expired_grants = session.query(Grant).filter(Grant.status == 'expired').count()
        
        # Grants by bucket
        bucket_stats = {}
        buckets = ['Ideation', 'MVP Prototype', 'Early Stage', 'Growth', 'Infra']
        for bucket in buckets:
            count = session.query(Grant).filter(Grant.bucket == bucket).count()
            bucket_stats[bucket] = count
        
        # Recent grants (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_grants = session.query(Grant).filter(
            Grant.created_iso >= week_ago
        ).count()
        
        session.close()
        
        return jsonify({
            "total_grants": total_grants,
            "live_grants": live_grants,
            "expired_grants": expired_grants,
            "recent_grants_7_days": recent_grants,
            "grants_by_bucket": bucket_stats,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/search', methods=['GET'])
def search_grants():
    """Search grants by text query"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                "error": "Query parameter 'q' is required"
            }), 400
        
        session = db_manager.get_session()
        
        # Simple text search in title and agency
        grants = session.query(Grant).filter(
            Grant.title.ilike(f'%{query}%') |
            Grant.agency.ilike(f'%{query}%')
        ).limit(20).all()
        
        session.close()
        
        # Convert to JSON
        grants_data = []
        for grant in grants:
            grants_data.append({
                'id': grant.id,
                'title': grant.title,
                'agency': grant.agency,
                'bucket': grant.bucket,
                'min_ticket_lakh': grant.min_ticket_lakh,
                'max_ticket_lakh': grant.max_ticket_lakh,
                'status': grant.status
            })
        
        return jsonify({
            "query": query,
            "results": grants_data,
            "count": len(grants_data)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

