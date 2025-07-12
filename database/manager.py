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

from models.database import Base, DrugResult, DrugMatch, UnmatchedDrug, SearchSession, ManualReview
from config import Config

class DatabaseManager:
    """Database connection and management"""
    
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
            
            # Check and add missing columns
            self._ensure_price_columns()
            
            # Create session factory
            self.SessionFactory = sessionmaker(bind=self.engine)
            
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def _ensure_price_columns(self):
        """Ensure price columns exist in the database table"""
        try:
            with self.engine.connect() as conn:
                # Check if price columns exist in drug_matches (legacy table)
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'drug_matches' 
                    AND column_name IN ('dha_price', 'doh_price', 'price_similarity')
                """))
                existing_columns = {row[0] for row in result}
                
                # Add missing columns
                if 'dha_price' not in existing_columns:
                    conn.execute(text("ALTER TABLE drug_matches ADD COLUMN dha_price FLOAT DEFAULT 0.0"))
                    st.info("✅ Added dha_price column to database")
                
                if 'doh_price' not in existing_columns:
                    conn.execute(text("ALTER TABLE drug_matches ADD COLUMN doh_price FLOAT DEFAULT 0.0"))
                    st.info("✅ Added doh_price column to database")
                
                if 'price_similarity' not in existing_columns:
                    conn.execute(text("ALTER TABLE drug_matches ADD COLUMN price_similarity FLOAT DEFAULT 0.0"))
                    st.info("✅ Added price_similarity column to database")
                
                conn.commit()
                
        except Exception as e:
            st.warning(f"⚠️ Could not update database schema: {str(e)}")
            st.info("ℹ️ You may need to manually add the missing columns or recreate the table")
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionFactory()
    
    def clear_results(self):
        """Clear all previous results"""
        session = self.get_session()
        try:
            session.query(DrugResult).delete()
            session.query(DrugMatch).delete()
            session.query(UnmatchedDrug).delete()
            session.query(SearchSession).delete()
            session.query(ManualReview).delete() # Added ManualReview deletion
            session.commit()
            st.success("✅ All previous results cleared from database")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_search_session(self, dha_file_name: str, doh_file_name: str, 
                            dha_count: int, doh_count: int, threshold: float, 
                            weights: Dict) -> str:
        """Create a new search session and return session ID"""
        session = self.get_session()
        try:
            session_id = str(uuid.uuid4())
            search_session = SearchSession(
                session_id=session_id,
                dha_file_name=dha_file_name,
                doh_file_name=doh_file_name,
                dha_count=dha_count,
                doh_count=doh_count,
                threshold=threshold,
                weights=json.dumps(weights)
            )
            session.add(search_session)
            session.commit()
            return session_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_search_session(self, session_id: str, matches_count: int, 
                            unmatched_dha_count: int, unmatched_doh_count: int, 
                            processing_time: float):
        """Update search session with final results"""
        session = self.get_session()
        try:
            search_session = session.query(SearchSession).filter(
                SearchSession.session_id == session_id
            ).first()
            
            if search_session:
                search_session.matches_count = matches_count
                search_session.unmatched_dha_count = unmatched_dha_count
                search_session.unmatched_doh_count = unmatched_doh_count
                search_session.processing_time = processing_time
                search_session.completed_at = datetime.now()
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_drug_result(self, drug_data: Dict, status: str, match_data: Optional[Dict] = None):
        """Save a drug result to the unified table"""
        session = self.get_session()
        try:
            # Convert numpy types to Python native types
            def safe_convert(value):
                if hasattr(value, 'item'):  # numpy type
                    return value.item()
                elif isinstance(value, (int, float)):
                    return float(value)
                else:
                    return value
            
            # Create unified drug result
            drug_result = DrugResult(
                # DHA drug information
                dha_code=str(drug_data.get('code', '')),
                dha_brand_name=str(drug_data.get('brand_name', '')),
                dha_generic_name=str(drug_data.get('generic_name', '')),
                dha_strength=str(drug_data.get('strength', '')),
                dha_dosage_form=str(drug_data.get('dosage_form', '')),
                dha_price=safe_convert(drug_data.get('price', 0.0)),
                
                # Status
                status=status,
                
                # Match information (if matched)
                doh_code=str(match_data.get('DOH_Code', '')) if match_data else None,
                doh_brand_name=str(match_data.get('DOH_Brand_Name', '')) if match_data else None,
                doh_generic_name=str(match_data.get('DOH_Generic_Name', '')) if match_data else None,
                doh_strength=str(match_data.get('DOH_Strength', '')) if match_data else None,
                doh_dosage_form=str(match_data.get('DOH_Dosage_Form', '')) if match_data else None,
                doh_price=safe_convert(match_data.get('DOH_Price', 0.0)) if match_data else None,
                
                # Similarity scores (if matched)
                brand_similarity=safe_convert(match_data.get('Brand_Similarity', 0.0)) if match_data else None,
                generic_similarity=safe_convert(match_data.get('Generic_Similarity', 0.0)) if match_data else None,
                strength_similarity=safe_convert(match_data.get('Strength_Similarity', 0.0)) if match_data else None,
                dosage_similarity=safe_convert(match_data.get('Dosage_Similarity', 0.0)) if match_data else None,
                price_similarity=safe_convert(match_data.get('Price_Similarity', 0.0)) if match_data else None,
                overall_score=safe_convert(match_data.get('Overall_Score', 0.0)) if match_data else None,
                
                # Match details (if matched)
                confidence_level=str(match_data.get('Confidence_Level', '')) if match_data else None,
                fuzzy_score=safe_convert(match_data.get('Fuzzy_Score', 0.0)) if match_data else None,
                vector_score=safe_convert(match_data.get('Vector_Score', 0.0)) if match_data else None,
                semantic_score=safe_convert(match_data.get('Semantic_Score', 0.0)) if match_data else None,
                matching_method=str(match_data.get('Matching_Method', '')) if match_data else None,
                
                # Unmatch information (if unmatched)
                best_match_score=safe_convert(drug_data.get('best_match_score', 0.0)) if status == 'UNMATCHED' else 0.0,
                best_match_doh_code=str(drug_data.get('best_match_doh_code', '')) if status == 'UNMATCHED' and drug_data.get('best_match_doh_code') else None,
                search_reason=str(drug_data.get('search_reason', '')) if status == 'UNMATCHED' and drug_data.get('search_reason') else None,
                
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
    
    def save_match(self, match_data: Dict):
        """Save a matched drug (legacy method for backward compatibility)"""
        # Extract DHA drug data from match data
        dha_drug_data = {
            'code': match_data.get('DHA_Code', ''),
            'brand_name': match_data.get('DHA_Brand_Name', ''),
            'generic_name': match_data.get('DHA_Generic_Name', ''),
            'strength': match_data.get('DHA_Strength', ''),
            'dosage_form': match_data.get('DHA_Dosage_Form', ''),
            'price': match_data.get('DHA_Price', 0.0)
        }
        
        # Save to unified table
        self.save_drug_result(dha_drug_data, 'MATCHED', match_data)
    
    def save_unmatched_drug(self, drug_data: Dict, source: str, best_match_score: float = 0.0, 
                           best_match_doh_code: Optional[str] = None, search_reason: str = "Below threshold"):
        """Save an unmatched drug (legacy method for backward compatibility)"""
        # Add unmatched-specific data
        drug_data['best_match_score'] = best_match_score
        drug_data['best_match_doh_code'] = best_match_doh_code
        drug_data['search_reason'] = search_reason
        
        # Save to unified table
        self.save_drug_result(drug_data, 'UNMATCHED')
    
    def save_manual_review(self, match_data: Dict, review_reason: str):
        """Save a match flagged for manual review"""
        session = self.get_session()
        try:
            manual_review = ManualReview(
                dha_code=match_data.get('DHA_Code', ''),
                dha_brand_name=match_data.get('DHA_Brand_Name', ''),
                dha_generic_name=match_data.get('DHA_Generic_Name', ''),
                dha_strength=match_data.get('DHA_Strength', ''),
                dha_dosage_form=match_data.get('DHA_Dosage_Form', ''),
                dha_price=match_data.get('DHA_Price', 0.0),
                doh_code=match_data.get('DOH_Code', ''),
                doh_brand_name=match_data.get('DOH_Brand_Name', ''),
                doh_generic_name=match_data.get('DOH_Generic_Name', ''),
                doh_strength=match_data.get('DOH_Strength', ''),
                doh_dosage_form=match_data.get('DOH_Dosage_Form', ''),
                doh_price=match_data.get('DOH_Price', 0.0),
                brand_similarity=match_data.get('Brand_Similarity', 0.0),
                generic_similarity=match_data.get('Generic_Similarity', 0.0),
                strength_similarity=match_data.get('Strength_Similarity', 0.0),
                dosage_similarity=match_data.get('Dosage_Similarity', 0.0),
                price_similarity=match_data.get('Price_Similarity', 0.0),
                overall_score=match_data.get('Overall_Score', 0.0),
                confidence_level=match_data.get('Confidence_Level', ''),
                fuzzy_score=match_data.get('Fuzzy_Score', 0.0),
                vector_score=match_data.get('Vector_Score', 0.0),
                semantic_score=match_data.get('Semantic_Score', 0.0),
                matching_method=match_data.get('Matching_Method', ''),
                matched_at=datetime.now(),
                review_reason=review_reason,
                review_status='PENDING',
            )
            session.add(manual_review)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_manual_reviews(self, status: str = None):
        """Retrieve manual review records, optionally filtered by status"""
        session = self.get_session()
        try:
            query = session.query(ManualReview)
            if status:
                query = query.filter(ManualReview.review_status == status)
            return query.order_by(ManualReview.matched_at.desc()).all()
        finally:
            session.close()
    
    def get_all_results(self) -> List[DrugResult]:
        """Get all drug results from unified table"""
        session = self.get_session()
        try:
            return session.query(DrugResult).all()
        finally:
            session.close()
    
    def get_matched_drugs(self) -> List[DrugResult]:
        """Get all matched drugs from unified table"""
        session = self.get_session()
        try:
            return session.query(DrugResult).filter(DrugResult.status == 'MATCHED').all()
        finally:
            session.close()
    
    def get_unmatched_drugs(self, source: Optional[str] = None) -> List[DrugResult]:
        """Get unmatched drugs from unified table"""
        session = self.get_session()
        try:
            query = session.query(DrugResult).filter(DrugResult.status == 'UNMATCHED')
            if source:
                # For unified table, we can filter by DHA drugs (source='DHA' means DHA drugs that didn't match)
                # This is a simplified approach - in the unified table, all unmatched are DHA drugs
                pass
            return query.all()
        finally:
            session.close()
    
    def get_search_sessions(self) -> List[SearchSession]:
        """Get all search sessions"""
        session = self.get_session()
        try:
            return session.query(SearchSession).order_by(SearchSession.started_at.desc()).all()
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
        """Recreate all tables with current schema"""
        try:
            with self.engine.connect() as conn:
                # Drop existing tables
                conn.execute(text("DROP TABLE IF EXISTS manual_review CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS drug_results CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS drug_matches CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS unmatched_drugs CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS search_sessions CASCADE"))
                conn.commit()
                
                # Recreate tables with current schema
                Base.metadata.create_all(self.engine)
                st.success("✅ All tables recreated successfully with current schema")
                
        except Exception as e:
            st.error(f"❌ Error recreating tables: {str(e)}")
    
    def get_table_info(self) -> List:
        """Get information about all tables"""
        try:
            with self.engine.connect() as conn:
                tables = ['manual_review', 'drug_results', 'drug_matches', 'unmatched_drugs', 'search_sessions']
                all_info = []
                
                for table in tables:
                    result = conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """))
                    table_info = [(table, row[0], row[1], row[2]) for row in result]
                    all_info.extend(table_info)
                
                return all_info
        except Exception as e:
            st.error(f"❌ Error getting table info: {str(e)}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'engine'):
            self.engine.dispose() 