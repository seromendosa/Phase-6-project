"""
Database management for the Drug Matching System
"""
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os
import json
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base, DrugResult
from config import Config

class DatabaseManager:
    """
    Database connection and management for the Drug Matching System.
    Only the unified drug_results table is used for all results.
    """
    
    def __init__(self, db_url: str):
        try:
            # Configure connection args based on database type
            connect_args = {}
            if "postgresql" in db_url.lower():
                connect_args = {"connect_timeout": 10}
            elif "sqlite" in db_url.lower():
                connect_args = {}
            
            self.engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False,
                connect_args=connect_args
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            self.SessionFactory = sessionmaker(bind=self.engine)
            
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionFactory()
    
    def clear_results(self, batch_id: Optional[str] = None):
        """Clear all previous results"""
        session = self.get_session()
        try:
            query = session.query(DrugResult)
            if batch_id:
                query = query.filter(DrugResult.batch_id == batch_id)
            query.delete()
            session.commit()
            st.success("✅ Results cleared from database")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_search_session(self, dha_file_name: str, doh_file_name: str, 
                            dha_count: int, doh_count: int, threshold: float, 
                            weights: Dict) -> str:
        """(Deprecated) Placeholder for legacy session tracking. No longer used."""
        return str(uuid.uuid4())
    
    def save_drug_result(self, drug_data: Dict, status: str, match_data: Optional[Dict] = None, batch_id: Optional[str] = None):
        """Save a drug result to the unified table"""
        session = self.get_session()
        try:
            def safe_convert(value):
                if hasattr(value, 'item'):
                    return value.item()
                elif isinstance(value, (int, float)):
                    return float(value)
                else:
                    return value
            drug_result = DrugResult(
                dha_code=str(drug_data.get('code', '')),
                dha_brand_name=str(drug_data.get('brand_name', '')),
                dha_generic_name=str(drug_data.get('generic_name', '')),
                dha_strength=str(drug_data.get('strength', '')),
                dha_dosage_form=str(drug_data.get('dosage_form', '')),
                dha_price=safe_convert(drug_data.get('price', 0.0)),
                dha_package_size=str(drug_data.get('package_size', drug_data.get('DHA_Package_Size', ''))),
                dha_unit=str(drug_data.get('unit', drug_data.get('DHA_Unit', ''))),  # NEW
                dha_unit_category=str(drug_data.get('unit_category', drug_data.get('DHA_Unit_Category', ''))),  # NEW
                status=status,
                doh_code=str(match_data.get('DOH_Code', '')) if match_data else None,
                doh_brand_name=str(match_data.get('DOH_Brand_Name', '')) if match_data else None,
                doh_generic_name=str(match_data.get('DOH_Generic_Name', '')) if match_data else None,
                doh_strength=str(match_data.get('DOH_Strength', '')) if match_data else None,
                doh_dosage_form=str(match_data.get('DOH_Dosage_Form', '')) if match_data else None,
                doh_price=safe_convert(match_data.get('DOH_Price', 0.0)) if match_data else None,
                doh_package_size=str(match_data.get('DOH_Package_Size', '')) if match_data else None,
                doh_unit=str(match_data.get('DOH_Unit', '')) if match_data else None,  # NEW
                doh_unit_category=str(match_data.get('DOH_Unit_Category', '')) if match_data else None,  # NEW
                brand_similarity=safe_convert(match_data.get('Brand_Similarity', 0.0)) if match_data else None,
                generic_similarity=safe_convert(match_data.get('Generic_Similarity', 0.0)) if match_data else None,
                strength_similarity=safe_convert(match_data.get('Strength_Similarity', 0.0)) if match_data else None,
                dosage_similarity=safe_convert(match_data.get('Dosage_Similarity', 0.0)) if match_data else None,
                price_similarity=safe_convert(match_data.get('Price_Similarity', 0.0)) if match_data else None,
                package_size_similarity=safe_convert(match_data.get('Package_Size_Similarity', 0.0)) if match_data else None,
                unit_similarity=safe_convert(match_data.get('Unit_Similarity', 0.0)) if match_data else None,  # NEW
                unit_category_similarity=safe_convert(match_data.get('Unit_Category_Similarity', 0.0)) if match_data else None,  # NEW
                overall_score=safe_convert(match_data.get('Overall_Score', 0.0)) if match_data else None,
                confidence_level=str(match_data.get('Confidence_Level', '')) if match_data else None,
                fuzzy_score=safe_convert(match_data.get('Fuzzy_Score', 0.0)) if match_data else None,
                vector_score=safe_convert(match_data.get('Vector_Score', 0.0)) if match_data else None,
                semantic_score=safe_convert(match_data.get('Semantic_Score', 0.0)) if match_data else None,
                matching_method=str(match_data.get('Matching_Method', '')) if match_data else None,
                best_match_score=safe_convert(drug_data.get('best_match_score', 0.0)) if status == 'UNMATCHED' else 0.0,
                best_match_doh_code=str(drug_data.get('best_match_doh_code', '')) if status == 'UNMATCHED' and drug_data.get('best_match_doh_code') else None,
                search_reason=str(drug_data.get('search_reason', '')) if status == 'UNMATCHED' and drug_data.get('search_reason') else None,
                batch_id=batch_id,
                processed_at=datetime.now()
            )
            session.add(drug_result)
            session.commit()
        except Exception as e:
            session.rollback()
            error_msg = str(e)
            if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                st.error(f"❌ Database schema error: {error_msg}")
                st.info("💡 Try using the 'Recreate Table' option in Database Management to fix this issue.")
            else:
                st.error(f"❌ Database error: {error_msg}")
            raise e
        finally:
            session.close()
    
    def save_match(self, match_data: Dict, batch_id: Optional[str] = None):
        dha_drug_data = {
            'code': match_data.get('DHA_Code', ''),
            'brand_name': match_data.get('DHA_Brand_Name', ''),
            'generic_name': match_data.get('DHA_Generic_Name', ''),
            'strength': match_data.get('DHA_Strength', ''),
            'dosage_form': match_data.get('DHA_Dosage_Form', ''),
            'price': match_data.get('DHA_Price', 0.0),
            'package_size': match_data.get('DHA_Package_Size', ''),
            'unit': match_data.get('DHA_Unit', ''),
            'unit_category': match_data.get('DHA_Unit_Category', '')
        }
        self.save_drug_result(dha_drug_data, 'MATCHED', match_data, batch_id=batch_id)
    
    def save_unmatched_drug(self, drug_data: Dict, best_match_score: float = 0.0, best_match_doh_code: Optional[str] = None, search_reason: str = "Below threshold", batch_id: Optional[str] = None):
        drug_data['best_match_score'] = best_match_score
        drug_data['best_match_doh_code'] = best_match_doh_code
        drug_data['search_reason'] = search_reason
        self.save_drug_result(drug_data, 'UNMATCHED', batch_id=batch_id)
    
    def save_manual_review(self, match_data: Dict, review_reason: str):
        """(Deprecated) Placeholder for legacy manual review. No longer used."""
        pass

    def get_all_results(self, batch_id: Optional[str] = None) -> List[DrugResult]:
        """Get all drug results from unified table"""
        session = self.get_session()
        try:
            query = session.query(DrugResult)
            if batch_id:
                query = query.filter(DrugResult.batch_id == batch_id)
            return query.all()
        finally:
            session.close()
    
    def get_matched_drugs(self, batch_id: Optional[str] = None) -> List[DrugResult]:
        """Get all matched drugs from unified table"""
        session = self.get_session()
        try:
            query = session.query(DrugResult).filter(DrugResult.status == 'MATCHED')
            if batch_id:
                query = query.filter(DrugResult.batch_id == batch_id)
            return query.all()
        finally:
            session.close()
    
    def get_unmatched_drugs(self, batch_id: Optional[str] = None) -> List[DrugResult]:
        """Get unmatched drugs from unified table"""
        session = self.get_session()
        try:
            query = session.query(DrugResult).filter(DrugResult.status == 'UNMATCHED')
            if batch_id:
                query = query.filter(DrugResult.batch_id == batch_id)
            return query.all()
        finally:
            session.close()
    
    def get_match_count(self) -> int:
        """Get total number of matched drugs"""
        session = self.get_session()
        try:
            return session.query(DrugResult).filter(DrugResult.status == 'MATCHED').count()
        finally:
            session.close()
    
    def get_unmatched_count(self, source: Optional[str] = None) -> int:
        """Get total number of unmatched drugs"""
        session = self.get_session()
        try:
            query = session.query(DrugResult).filter(DrugResult.status == 'UNMATCHED')
            return query.count()
        finally:
            session.close()
    
    def get_total_count(self) -> int:
        """Get total number of all drug results"""
        session = self.get_session()
        try:
            return session.query(DrugResult).count()
        finally:
            session.close()
    
    def recreate_table(self):
        """
        Recreate the drug_results table with the current schema.
        Drops and recreates only the drug_results table.
        Use this for a clean start or schema update.
        """
        try:
            with self.engine.connect() as conn:
                # Drop only the drug_results table
                conn.execute(text("DROP TABLE IF EXISTS drug_results CASCADE"))
                conn.commit()
                # Recreate tables with current schema
                Base.metadata.create_all(self.engine)
                st.success("✅ drug_results table recreated successfully with current schema")
        except Exception as e:
            st.error(f"❌ Error recreating table: {str(e)}")
    
    def get_table_info(self) -> List:
        """Get information about all tables"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'drug_results'
                    ORDER BY ordinal_position
                """))
                table_info = [(row[0], row[1], row[2]) for row in result]
                return table_info
        except Exception as e:
            st.error(f"❌ Error getting table info: {str(e)}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'engine'):
            self.engine.dispose() 