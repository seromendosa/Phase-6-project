"""
Database models for the Drug Matching System
Only the unified DrugResult model and drug_results table are used.
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
    dha_package_size = Column(String, nullable=True)
    dha_unit = Column(String, nullable=True)
    dha_unit_category = Column(String, nullable=True)
    
    # Match Information (for matched drugs)
    doh_code = Column(String, nullable=True)
    doh_brand_name = Column(String, nullable=True)
    doh_generic_name = Column(String, nullable=True)
    doh_strength = Column(String, nullable=True)
    doh_dosage_form = Column(String, nullable=True)
    doh_price = Column(Float, nullable=True)
    doh_package_size = Column(String, nullable=True)
    doh_unit = Column(String, nullable=True)
    doh_unit_category = Column(String, nullable=True)
    
    # Similarity Scores
    brand_similarity = Column(Float, nullable=True)
    generic_similarity = Column(Float, nullable=True)
    strength_similarity = Column(Float, nullable=True)
    dosage_similarity = Column(Float, nullable=True)
    price_similarity = Column(Float, nullable=True)
    package_size_similarity = Column(Float, nullable=True)
    unit_similarity = Column(Float, nullable=True)
    unit_category_similarity = Column(Float, nullable=True)
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
    batch_id = Column(String, nullable=True)  # For batch/session tracking
    
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
            'dha_package_size': self.dha_package_size,
            'dha_unit': self.dha_unit,
            'dha_unit_category': self.dha_unit_category,
            'doh_code': self.doh_code,
            'doh_brand_name': self.doh_brand_name,
            'doh_generic_name': self.doh_generic_name,
            'doh_strength': self.doh_strength,
            'doh_dosage_form': self.doh_dosage_form,
            'doh_price': self.doh_price,
            'doh_package_size': self.doh_package_size,
            'doh_unit': self.doh_unit,
            'doh_unit_category': self.doh_unit_category,
            'brand_similarity': self.brand_similarity,
            'generic_similarity': self.generic_similarity,
            'strength_similarity': self.strength_similarity,
            'dosage_similarity': self.dosage_similarity,
            'price_similarity': self.price_similarity,
            'package_size_similarity': self.package_size_similarity,
            'unit_similarity': self.unit_similarity,
            'unit_category_similarity': self.unit_category_similarity,
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
            'batch_id': self.batch_id,
            'processed_at': self.processed_at.isoformat() if self.processed_at is not None else None
        } 