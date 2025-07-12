"""
Database models for the Drug Matching System
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class DrugResult(Base):
    """Unified model for storing all drug processing results (matched and unmatched)"""
    __tablename__ = 'drug_results'
    
    id = Column(Integer, primary_key=True)
    
    # Drug Information
    dha_code = Column(String)
    dha_brand_name = Column(String)
    dha_generic_name = Column(String)
    dha_strength = Column(String)
    dha_dosage_form = Column(String)
    dha_price = Column(Float)
    
    # Match Information (for matched drugs)
    doh_code = Column(String, nullable=True)
    doh_brand_name = Column(String, nullable=True)
    doh_generic_name = Column(String, nullable=True)
    doh_strength = Column(String, nullable=True)
    doh_dosage_form = Column(String, nullable=True)
    doh_price = Column(Float, nullable=True)
    
    # Similarity Scores
    brand_similarity = Column(Float, nullable=True)
    generic_similarity = Column(Float, nullable=True)
    strength_similarity = Column(Float, nullable=True)
    dosage_similarity = Column(Float, nullable=True)
    price_similarity = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    
    # Match Details
    confidence_level = Column(String, nullable=True)
    fuzzy_score = Column(Float, nullable=True)
    vector_score = Column(Float, nullable=True)
    semantic_score = Column(Float, nullable=True)
    matching_method = Column(String, nullable=True)
    
    # Status and Processing Info
    status = Column(String)  # 'MATCHED' or 'UNMATCHED'
    best_match_score = Column(Float, default=0.0)  # Best score achieved (for unmatched)
    best_match_doh_code = Column(String, nullable=True)  # Best DOH match found (for unmatched)
    search_reason = Column(String, nullable=True)  # Why it didn't match
    
    # Timestamps
    processed_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<DrugResult(id={self.id}, dha_code='{self.dha_code}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'dha_code': self.dha_code,
            'dha_brand_name': self.dha_brand_name,
            'dha_generic_name': self.dha_generic_name,
            'dha_strength': self.dha_strength,
            'dha_dosage_form': self.dha_dosage_form,
            'dha_price': self.dha_price,
            'doh_code': self.doh_code,
            'doh_brand_name': self.doh_brand_name,
            'doh_generic_name': self.doh_generic_name,
            'doh_strength': self.doh_strength,
            'doh_dosage_form': self.doh_dosage_form,
            'doh_price': self.doh_price,
            'brand_similarity': self.brand_similarity,
            'generic_similarity': self.generic_similarity,
            'strength_similarity': self.strength_similarity,
            'dosage_similarity': self.dosage_similarity,
            'price_similarity': self.price_similarity,
            'overall_score': self.overall_score,
            'confidence_level': self.confidence_level,
            'fuzzy_score': self.fuzzy_score,
            'vector_score': self.vector_score,
            'semantic_score': self.semantic_score,
            'matching_method': self.matching_method,
            'status': self.status,
            'best_match_score': self.best_match_score,
            'best_match_doh_code': self.best_match_doh_code,
            'search_reason': self.search_reason,
            'processed_at': self.processed_at.isoformat() if self.processed_at is not None else None
        }

# Legacy models for backward compatibility (can be removed later)
class DrugMatch(Base):
    """Legacy model for storing drug matching results"""
    __tablename__ = 'drug_matches'
    
    id = Column(Integer, primary_key=True)
    dha_code = Column(String)
    doh_code = Column(String)
    dha_brand_name = Column(String)
    doh_brand_name = Column(String)
    dha_generic_name = Column(String)
    doh_generic_name = Column(String)
    dha_strength = Column(String)
    doh_strength = Column(String)
    dha_dosage_form = Column(String)
    doh_dosage_form = Column(String)
    dha_price = Column(Float)
    doh_price = Column(Float)
    brand_similarity = Column(Float)
    generic_similarity = Column(Float)
    strength_similarity = Column(Float)
    dosage_similarity = Column(Float)
    price_similarity = Column(Float)
    overall_score = Column(Float)
    confidence_level = Column(String)
    fuzzy_score = Column(Float)
    vector_score = Column(Float)
    semantic_score = Column(Float)
    matching_method = Column(String)
    matched_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<DrugMatch(id={self.id}, dha_code='{self.dha_code}', doh_code='{self.doh_code}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'dha_code': self.dha_code,
            'doh_code': self.doh_code,
            'dha_brand_name': self.dha_brand_name,
            'doh_brand_name': self.doh_brand_name,
            'dha_generic_name': self.dha_generic_name,
            'doh_generic_name': self.doh_generic_name,
            'dha_strength': self.dha_strength,
            'doh_strength': self.doh_strength,
            'dha_dosage_form': self.dha_dosage_form,
            'doh_dosage_form': self.doh_dosage_form,
            'dha_price': self.dha_price,
            'doh_price': self.doh_price,
            'brand_similarity': self.brand_similarity,
            'generic_similarity': self.generic_similarity,
            'strength_similarity': self.strength_similarity,
            'dosage_similarity': self.dosage_similarity,
            'price_similarity': self.price_similarity,
            'overall_score': self.overall_score,
            'confidence_level': self.confidence_level,
            'fuzzy_score': self.fuzzy_score,
            'vector_score': self.vector_score,
            'semantic_score': self.semantic_score,
            'matching_method': self.matching_method,
            'matched_at': self.matched_at.isoformat() if self.matched_at is not None else None
        }

class UnmatchedDrug(Base):
    """Legacy model for storing unmatched drugs"""
    __tablename__ = 'unmatched_drugs'
    
    id = Column(Integer, primary_key=True)
    source = Column(String)  # 'DHA' or 'DOH'
    drug_code = Column(String)
    brand_name = Column(String)
    generic_name = Column(String)
    strength = Column(String)
    dosage_form = Column(String)
    price = Column(Float)
    best_match_score = Column(Float, default=0.0)  # Best score achieved during search
    best_match_doh_code = Column(String, nullable=True)  # Best DOH match found (if any)
    search_reason = Column(String)  # Why it didn't match (below threshold, no candidates, etc.)
    processed_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<UnmatchedDrug(id={self.id}, source='{self.source}', drug_code='{self.drug_code}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'source': self.source,
            'drug_code': self.drug_code,
            'brand_name': self.brand_name,
            'generic_name': self.generic_name,
            'strength': self.strength,
            'dosage_form': self.dosage_form,
            'price': self.price,
            'best_match_score': self.best_match_score,
            'best_match_doh_code': self.best_match_doh_code,
            'search_reason': self.search_reason,
            'processed_at': self.processed_at.isoformat() if self.processed_at is not None else None
        }

class SearchSession(Base):
    """Model for tracking search sessions"""
    __tablename__ = 'search_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True)
    dha_file_name = Column(String)
    doh_file_name = Column(String)
    dha_count = Column(Integer)
    doh_count = Column(Integer)
    threshold = Column(Float)
    weights = Column(String)  # JSON string of weights
    matches_count = Column(Integer, default=0)
    unmatched_dha_count = Column(Integer, default=0)
    unmatched_doh_count = Column(Integer, default=0)
    processing_time = Column(Float)  # in seconds
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<SearchSession(id={self.id}, session_id='{self.session_id}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'dha_file_name': self.dha_file_name,
            'doh_file_name': self.doh_file_name,
            'dha_count': self.dha_count,
            'doh_count': self.doh_count,
            'threshold': self.threshold,
            'weights': self.weights,
            'matches_count': self.matches_count,
            'unmatched_dha_count': self.unmatched_dha_count,
            'unmatched_doh_count': self.unmatched_doh_count,
            'processing_time': self.processing_time,
            'started_at': self.started_at.isoformat() if self.started_at is not None else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at is not None else None
        } 

class ManualReview(Base):
    """Model for storing matches flagged for manual review"""
    __tablename__ = 'manual_review'

    id = Column(Integer, primary_key=True)
    # Drug info
    dha_code = Column(String)
    dha_brand_name = Column(String)
    dha_generic_name = Column(String)
    dha_strength = Column(String)
    dha_dosage_form = Column(String)
    dha_price = Column(Float)
    doh_code = Column(String)
    doh_brand_name = Column(String)
    doh_generic_name = Column(String)
    doh_strength = Column(String)
    doh_dosage_form = Column(String)
    doh_price = Column(Float)
    # Similarity scores
    brand_similarity = Column(Float)
    generic_similarity = Column(Float)
    strength_similarity = Column(Float)
    dosage_similarity = Column(Float)
    price_similarity = Column(Float)
    overall_score = Column(Float)
    # Match details
    confidence_level = Column(String)
    fuzzy_score = Column(Float)
    vector_score = Column(Float)
    semantic_score = Column(Float)
    matching_method = Column(String)
    matched_at = Column(DateTime, default=datetime.now)
    # Review info
    review_reason = Column(String)  # Why flagged for review
    review_status = Column(String, default='PENDING')  # PENDING, APPROVED, REJECTED
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ManualReview(id={self.id}, dha_code='{self.dha_code}', doh_code='{self.doh_code}', status='{self.review_status}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'dha_code': self.dha_code,
            'dha_brand_name': self.dha_brand_name,
            'dha_generic_name': self.dha_generic_name,
            'dha_strength': self.dha_strength,
            'dha_dosage_form': self.dha_dosage_form,
            'dha_price': self.dha_price,
            'doh_code': self.doh_code,
            'doh_brand_name': self.doh_brand_name,
            'doh_generic_name': self.doh_generic_name,
            'doh_strength': self.doh_strength,
            'doh_dosage_form': self.doh_dosage_form,
            'doh_price': self.doh_price,
            'brand_similarity': self.brand_similarity,
            'generic_similarity': self.generic_similarity,
            'strength_similarity': self.strength_similarity,
            'dosage_similarity': self.dosage_similarity,
            'price_similarity': self.price_similarity,
            'overall_score': self.overall_score,
            'confidence_level': self.confidence_level,
            'fuzzy_score': self.fuzzy_score,
            'vector_score': self.vector_score,
            'semantic_score': self.semantic_score,
            'matching_method': self.matching_method,
            'matched_at': self.matched_at.isoformat() if self.matched_at is not None else None,
            'review_reason': self.review_reason,
            'review_status': self.review_status,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at is not None else None
        } 