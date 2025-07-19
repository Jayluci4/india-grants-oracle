from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Grant(Base):
    __tablename__ = 'grants'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    bucket = Column(String)  # Ideation | MVP Prototype | Early Stage | Growth | Infra
    instrument = Column(JSON)  # ["grant", "convertible_debenture"]
    min_ticket_lakh = Column(Float)
    max_ticket_lakh = Column(Float)
    typical_ticket_lakh = Column(Float)
    deadline_type = Column(String)  # rolling | batch_call | annual | closed_waitlist
    next_deadline_iso = Column(String)
    eligibility_flags = Column(JSON)
    sector_tags = Column(JSON)
    state_scope = Column(String)
    agency = Column(String)
    source_urls = Column(JSON)
    confidence = Column(Float)
    last_seen_iso = Column(DateTime, default=datetime.utcnow)
    created_iso = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='live')  # live | expired | draft
    
    # Enhancement 1: Confidence Scoring and Data Lineage
    data_lineage = Column(JSON)  # {"source_type": "official_portal", "deadline_found": true, "extraction_method": "api"}
    
    # Enhancement 2: Smart Deduplication
    original_id = Column(String)  # ID of the original grant if this is a duplicate
    is_duplicate = Column(Boolean, default=False)
    
    # Enhancement 3: Eligibility Matching Score
    eligibility_criteria = Column(JSON)  # {"stage": ["early", "growth"], "sectors": ["tech"], "location": ["national"]}
    target_audience = Column(JSON)  # {"company_age_max": 5, "revenue_max": 100, "team_size_max": 50}
    
    # Enhancement 4: Grant Status Monitoring
    last_checked_iso = Column(DateTime, default=datetime.utcnow)
    status_reason = Column(String)  # "deadline_passed", "application_closed", "website_unavailable"
    
    # Enhancement 5: Application Complexity Indicator
    application_complexity = Column(String, default='medium')  # simple | medium | complex | very_complex

class DatabaseManager:
    def __init__(self, database_url=None):
        if database_url is None:
            # Use SQLite for development by default
            database_url = os.getenv('DATABASE_URL', 'sqlite:///grants.db')
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        return self.SessionLocal()
        
    def upsert_grant(self, grant_data):
        session = self.get_session()
        try:
            # Check if grant exists
            existing_grant = session.query(Grant).filter(Grant.id == grant_data['id']).first()
            
            if existing_grant:
                # Update existing grant
                for key, value in grant_data.items():
                    setattr(existing_grant, key, value)
                existing_grant.last_seen_iso = datetime.utcnow()
            else:
                # Create new grant
                grant = Grant(**grant_data)
                session.add(grant)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error upserting grant: {e}")
            return False
        finally:
            session.close()
            
    def get_grants(self, filters=None, limit=None):
        session = self.get_session()
        try:
            query = session.query(Grant)
            
            if filters:
                if 'bucket' in filters:
                    query = query.filter(Grant.bucket == filters['bucket'])
                if 'status' in filters:
                    query = query.filter(Grant.status == filters['status'])
                if 'min_amount' in filters:
                    query = query.filter(Grant.min_ticket_lakh >= filters['min_amount'])
                if 'max_amount' in filters:
                    query = query.filter(Grant.max_ticket_lakh <= filters['max_amount'])
            
            if limit:
                query = query.limit(limit)
                
            return query.all()
        finally:
            session.close()

