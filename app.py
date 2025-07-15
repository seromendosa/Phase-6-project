"""
Main Drug Matching System Application
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.manager import DatabaseManager
from processing.matchers import EnhancedDrugMatcher as DrugMatcher
from processing.text_processor import EnhancedDrugTextProcessor as DrugTextProcessor
from reporting.excel_generator import ExcelReportGenerator
from ui.components import UIComponents

class DrugMatchingApp:
    """Main application class"""
    
    def __init__(self):
        self.config = Config
        self.db_manager = None
        self.matcher = None
        self.excel_generator = ExcelReportGenerator()
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = None
        if 'matcher' not in st.session_state:
            st.session_state.matcher = DrugMatcher()
        if 'dha_df' not in st.session_state:
            st.session_state.dha_df = None
        if 'doh_df' not in st.session_state:
            st.session_state.doh_df = None
        if 'matches' not in st.session_state:
            st.session_state.matches = None
    
    def setup_page(self):
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title=self.config.APP_TITLE,
            page_icon=self.config.APP_ICON,
            layout=self.config.PAGE_LAYOUT
        )
        
        st.title("💊 Drug Matching System")
        st.markdown("### DHA ↔ DOH Drug Code Matching with Price Analysis")
    
    def handle_database_connection(self, db_config: Dict):
        """Handle database connection"""
        if db_config['action'] == 'connect_db':
            try:
                from urllib.parse import quote_plus
                encoded_password = quote_plus(db_config['password'])
                db_url = f"postgresql://{db_config['user']}:{encoded_password}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
                
                st.info("Testing database connection...")
                
                # Test connection first
                from sqlalchemy import create_engine, text
                engine = create_engine(db_url, connect_args={"connect_timeout": 5})
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                engine.dispose()
                
                # Create database manager
                st.session_state.db_manager = DatabaseManager(db_url)
                st.session_state.matcher = DrugMatcher(st.session_state.db_manager)
                st.success("✅ Database connected successfully!")
                
            except Exception as e:
                st.error(f"❌ Database connection failed: {str(e)}")
                st.write("**Troubleshooting tips:**")
                st.write("- Ensure PostgreSQL is running")
                st.write("- Check if database exists")
                st.write("- Verify credentials")
                st.write("- Install: `pip install psycopg2-binary`")
        
        elif db_config['action'] == 'disconnect_db':
            if st.session_state.db_manager:
                st.session_state.db_manager.close_connection()
                st.session_state.db_manager = None
                st.session_state.matcher = DrugMatcher()
                st.success("✅ Database disconnected")
            else:
                st.info("ℹ️ No database connection to disconnect")
    
    def render_database_status(self):
        """Render database connection status"""
        if st.session_state.db_manager is not None:
            st.success("🟢 Database Connected")
            st.write("**Live saving enabled** - Results will be saved to database as they're processed")
            
            # Database management options
            with st.expander("🔧 Database Management", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📋 Show Table Structure"):
                        columns = st.session_state.db_manager.get_table_info()
                        if columns:
                            st.write("**Current table structure:**")
                            for col in columns:
                                st.write(f"- {col[0]} ({col[1]}, nullable: {col[2]})")
                
                with col2:
                    if st.button("🔄 Recreate Table"):
                        st.session_state.show_recreate_warning = True
                    if st.session_state.get("show_recreate_warning", False):
                        st.warning("⚠️ This will delete ALL results in the drug_results table and cannot be undone.")
                        confirm = st.checkbox("I understand and want to recreate the table.", key="recreate_confirm")
                        if confirm:
                            if st.button("✅ Confirm Table Recreation", key="confirm_recreate_btn"):
                                st.session_state.db_manager.recreate_table()
                                st.success("✅ drug_results table recreated successfully. All previous results have been deleted.")
                                st.session_state.show_recreate_warning = False
                                st.session_state.recreate_confirm = False
                                st.rerun()
                
                # Manual SQL fix option
                st.write("**Manual SQL Fix (if automatic fails):**")
                st.code("""
-- Run this in your PostgreSQL client if automatic column addition fails:
ALTER TABLE drug_matches ADD COLUMN IF NOT EXISTS dha_price FLOAT DEFAULT 0.0;
ALTER TABLE drug_matches ADD COLUMN IF NOT EXISTS doh_price FLOAT DEFAULT 0.0;
ALTER TABLE drug_matches ADD COLUMN IF NOT EXISTS price_similarity FLOAT DEFAULT 0.0;
                """, language="sql")
        else:
            st.error("🔴 Database Not Connected")
            st.write("**Local mode** - Results will only be stored in memory")
    
    def run_matching_process(self, dha_df: pd.DataFrame, doh_df: pd.DataFrame, 
                           threshold: float, weights: Dict, price_config: Dict, bidirectional: bool = False) -> List[Dict]:
        """Run the drug matching process"""
        with st.spinner("Matching drugs with price analysis..."):
            start_time = datetime.now()
            
            # Update price matcher settings
            st.session_state.matcher.price_matcher.tolerance_percentage = price_config['price_tolerance']
            st.session_state.matcher.price_matcher.max_ratio = price_config['max_price_ratio']
            
            # Perform matching
            matches = self._match_drugs(dha_df, doh_df, threshold, weights, bidirectional=bidirectional)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Store matches in session state
            st.session_state.matches = matches
            
            # Display summary
            st.success(f"✅ Matching completed in {processing_time:.2f} seconds!")
            st.info(f"📊 Results: {len(matches)} matches found")

            # Show maximum possible matches (bidirectional)
            max_possible_matches = len(dha_df) + len(doh_df)
            st.info(f"🔢 Maximum possible matches: {max_possible_matches} (DHA: {len(dha_df)} + DOH: {len(doh_df)})")
            
            if st.session_state.db_manager:
                unmatched_dha = st.session_state.db_manager.get_unmatched_count()
                unmatched_doh = st.session_state.db_manager.get_unmatched_count()
                st.info(f"📊 Unmatched: {unmatched_dha} DHA drugs, {unmatched_doh} DOH drugs")
            
            return matches
    
    def _match_drugs(self, dha_df: pd.DataFrame, doh_df: pd.DataFrame, 
                    threshold: float, weights: Dict, bidirectional: bool = False) -> List[Dict]:
        """Internal method to perform drug matching with one-to-many (all above threshold) matching"""
        matches = []
        unmatched_dha_count = 0
        unmatched_doh_count = 0
        
        # Clear previous results if database is connected
        if st.session_state.db_manager:
            try:
                st.session_state.db_manager.clear_results()
                st.success("✅ Previous results cleared from database")
            except Exception as e:
                st.warning(f"⚠️ Could not clear previous results: {str(e)}")
        
        # Prepare DOH generics for vectorizer training
        doh_generics = doh_df.iloc[:, 2].tolist() if len(doh_df.columns) > 2 else []
        
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_dha = len(dha_df)
        saved_count = 0
        processed_count = 0
        
        # Batch processing configuration
        BATCH_SIZE = 100  # Process 100 drugs at a time
        checkpoint_interval = 50  # Save checkpoint every 50 drugs
        
        # Resume functionality - check for existing progress
        start_index = 0
        if st.session_state.db_manager:
            try:
                # Check if we have existing matches for this session
                existing_matches = st.session_state.db_manager.get_matched_drugs()
                if existing_matches:
                    # Find the last processed DHA code
                    processed_dha_codes = {match.dha_code for match in existing_matches}
                    for idx, (_, dha_row) in enumerate(dha_df.iterrows()):
                        dha_code = str(dha_row.iloc[0]) if len(dha_row) > 0 else ""
                        if dha_code not in processed_dha_codes:
                            start_index = idx
                            break
                    
                    if start_index > 0:
                        st.info(f"🔄 Resuming from drug {start_index + 1} of {total_dha} (found {len(processed_dha_codes)} already processed)")
                        # Load existing matches
                        matches = [match.to_dict() for match in existing_matches]
                        saved_count = len(matches)
                        processed_count = start_index
            except Exception as e:
                st.warning(f"⚠️ Could not check for existing progress: {str(e)}")
        
        # Process drugs in batches (DHA → DOH)
        for batch_start in range(start_index, total_dha, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, total_dha)
            batch_dha = dha_df.iloc[batch_start:batch_end]
            
            # Process each drug in the current batch
            for idx, (_, dha_row) in enumerate(batch_dha.iterrows()):
                actual_idx = batch_start + idx
                progress = (actual_idx + 1) / total_dha
                progress_bar.progress(progress)
                status_text.text(f'Processing DHA drug {actual_idx + 1} of {total_dha} (Batch {batch_start//BATCH_SIZE + 1}, Processed: {processed_count})')
                
                dha_code = str(dha_row.iloc[0]) if len(dha_row) > 0 else ""
                dha_brand = str(dha_row.iloc[1]) if len(dha_row) > 1 else ""
                dha_generic = str(dha_row.iloc[2]) if len(dha_row) > 2 else ""
                dha_strength = str(dha_row.iloc[3]) if len(dha_row) > 3 else ""
                dha_dosage = str(dha_row.iloc[4]) if len(dha_row) > 4 else ""
                dha_price = st.session_state.matcher.processor.clean_price(dha_row.iloc[5]) if len(dha_row) > 5 else 0.0
                dha_package_size = str(dha_row.iloc[6]) if len(dha_row) > 6 else ""
                dha_unit = str(dha_row.iloc[7]) if len(dha_row) > 7 else ""
                dha_unit_category = str(dha_row.iloc[8]) if len(dha_row) > 8 else ""
                
                if len(doh_df) == 0:
                    if st.session_state.db_manager:
                        dha_drug_data = {
                            'code': dha_code,
                            'brand_name': dha_brand,
                            'generic_name': dha_generic,
                            'strength': dha_strength,
                            'dosage_form': dha_dosage,
                            'price': dha_price,
                            'package_size': dha_package_size,
                            'unit': dha_unit,
                            'unit_category': dha_unit_category
                        }
                        st.session_state.db_manager.save_unmatched_drug(
                            dha_drug_data, best_match_score=0.0, best_match_doh_code=None, search_reason="No DOH drugs available"
                        )
                    unmatched_dha_count += 1
                    processed_count += 1
                    continue
                
                # --- One-to-many matching logic ---
                matches_for_this_dha = []
                best_score = 0
                best_match = None
                best_doh_code = None
                
                for _, doh_row in doh_df.iterrows():
                    doh_code = str(doh_row.iloc[0]) if len(doh_row) > 0 else ""
                    doh_brand = str(doh_row.iloc[1]) if len(doh_row) > 1 else ""
                    doh_generic = str(doh_row.iloc[2]) if len(doh_row) > 2 else ""
                    doh_strength = str(doh_row.iloc[3]) if len(doh_row) > 3 else ""
                    doh_dosage = str(doh_row.iloc[4]) if len(doh_row) > 4 else ""
                    doh_price = st.session_state.matcher.processor.clean_price(doh_row.iloc[5]) if len(doh_row) > 5 else 0.0
                    doh_package_size = str(doh_row.iloc[6]) if len(doh_row) > 6 else ""
                    doh_unit = str(doh_row.iloc[7]) if len(doh_row) > 7 else ""
                    doh_unit_category = str(doh_row.iloc[8]) if len(doh_row) > 8 else ""
                    
                    brand_sim = st.session_state.matcher.calculate_brand_similarity(dha_brand, doh_brand)
                    strength_sim = st.session_state.matcher.calculate_strength_similarity(dha_strength, doh_strength)
                    dosage_sim = st.session_state.matcher.calculate_dosage_similarity(dha_dosage, doh_dosage)
                    price_sim = st.session_state.matcher.price_matcher.calculate_price_similarity(dha_price, doh_price)
                    generic_match = st.session_state.matcher.generic_matcher.best_match(
                        dha_generic, doh_generic, doh_generics
                    )
                    generic_sim = generic_match['final_score']
                    package_size_sim = st.session_state.matcher.calculate_package_size_similarity(dha_package_size, doh_package_size)
                    unit_sim = st.session_state.matcher.calculate_unit_similarity(dha_unit, doh_unit)
                    unit_category_sim = st.session_state.matcher.calculate_unit_category_similarity(dha_unit_category, doh_unit_category)

                    applied_weights = weights.copy()
                    manual_review_flag = False
                    # Add new weights if not present
                    if 'package_size' not in applied_weights:
                        applied_weights['package_size'] = 0.10
                    if 'unit' not in applied_weights:
                        applied_weights['unit'] = 0.05
                    if 'unit_category' not in applied_weights:
                        applied_weights['unit_category'] = 0.05
                    # Reduce price weight to keep total at 1.0 if needed
                    if 'price' in applied_weights:
                        applied_weights['price'] = max(0.0, applied_weights['price'] - 0.10)
                    total_weight = sum(applied_weights.values())
                    if total_weight > 0:
                        for k in applied_weights:
                            applied_weights[k] = applied_weights[k] / total_weight
                    overall_score = (
                        brand_sim * applied_weights.get('brand', 0.0) +
                        strength_sim * applied_weights.get('strength', 0.0) +
                        dosage_sim * applied_weights.get('dosage', 0.0) +
                        generic_sim * applied_weights.get('generic', 0.0) +
                        price_sim * applied_weights.get('price', 0.0) +
                        package_size_sim * applied_weights.get('package_size', 0.0) +
                        unit_sim * applied_weights.get('unit', 0.0) +
                        unit_category_sim * applied_weights.get('unit_category', 0.0)
                    )

                    if overall_score > best_score:
                        best_score = overall_score
                        best_doh_code = doh_code
                        best_match = None  # Will be set below

                    if overall_score >= threshold:
                        confidence_level = st.session_state.matcher.get_confidence_level(overall_score)
                        match = {
                            'DHA_Code': dha_code,
                            'DOH_Code': doh_code,
                            'DHA_Brand_Name': dha_brand,
                            'DOH_Brand_Name': doh_brand,
                            'DHA_Generic_Name': dha_generic,
                            'DOH_Generic_Name': doh_generic,
                            'DHA_Strength': dha_strength,
                            'DOH_Strength': doh_strength,
                            'DHA_Dosage_Form': dha_dosage,
                            'DOH_Dosage_Form': doh_dosage,
                            'DHA_Price': float(dha_price),
                            'DOH_Price': float(doh_price),
                            'DHA_Package_Size': dha_package_size,
                            'DOH_Package_Size': doh_package_size,
                            'DHA_Unit': dha_unit,
                            'DOH_Unit': doh_unit,
                            'DHA_Unit_Category': dha_unit_category,
                            'DOH_Unit_Category': doh_unit_category,
                            'Brand_Similarity': float(round(brand_sim, 3)),
                            'Generic_Similarity': float(round(generic_sim, 3)),
                            'Strength_Similarity': float(round(strength_sim, 3)),
                            'Dosage_Similarity': float(round(dosage_sim, 3)),
                            'Price_Similarity': float(round(price_sim, 3)),
                            'Package_Size_Similarity': float(round(package_size_sim, 3)),
                            'Unit_Similarity': float(round(unit_sim, 3)),
                            'Unit_Category_Similarity': float(round(unit_category_sim, 3)),
                            'Overall_Score': float(round(overall_score, 3)),
                            'Confidence_Level': confidence_level,
                            'Fuzzy_Score': float(round(generic_match['fuzzy_score'], 3)),
                            'Vector_Score': float(round(generic_match['vector_score'], 3)),
                            'Semantic_Score': float(round(generic_match['semantic_score'], 3)),
                            'Matching_Method': generic_match['method'],
                            'Matched_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Applied_Weights': applied_weights,
                            'Manual_Review_Flag': manual_review_flag,
                            'Is_Best_Match': False  # Will be set later
                        }
                        matches_for_this_dha.append(match)

                # After all DOH drugs, flag the best match (if any)
                if matches_for_this_dha:
                    # Find the match with the highest score
                    best_idx = max(range(len(matches_for_this_dha)), key=lambda i: matches_for_this_dha[i]['Overall_Score'])
                    matches_for_this_dha[best_idx]['Is_Best_Match'] = True
                    matches.extend(matches_for_this_dha)
                    # Save all matches to DB
                    if st.session_state.db_manager:
                        for match in matches_for_this_dha:
                            try:
                                st.session_state.db_manager.save_match(match)
                                saved_count += 1
                            except Exception as e:
                                st.warning(f"⚠️ Could not save match to database: {str(e)}")
                    processed_count += 1
                else:
                    # Save unmatched DHA drug
                    if st.session_state.db_manager:
                        try:
                            dha_drug_data = {
                                'code': dha_code,
                                'brand_name': dha_brand,
                                'generic_name': dha_generic,
                                'strength': dha_strength,
                                'dosage_form': dha_dosage,
                                'price': dha_price,
                                'package_size': dha_package_size,
                                'unit': dha_unit,
                                'unit_category': dha_unit_category
                            }
                            search_reason = f"No matches above threshold {threshold}"
                            st.session_state.db_manager.save_unmatched_drug(
                                dha_drug_data, best_match_score=best_score, best_match_doh_code=best_doh_code, search_reason=search_reason
                            )
                        except Exception as e:
                            st.warning(f"⚠️ Could not save unmatched DHA drug to database: {str(e)}")
                    unmatched_dha_count += 1
                    processed_count += 1
                
                # Checkpoint saving every N drugs
                if processed_count % checkpoint_interval == 0:
                    if st.session_state.db_manager:
                        try:
                            st.info(f"💾 Checkpoint saved at drug {processed_count}")
                        except Exception as e:
                            st.warning(f"⚠️ Could not save checkpoint: {str(e)}")
            
            # Batch completion notification
            if batch_end < total_dha:
                st.success(f"✅ Batch {batch_start//BATCH_SIZE + 1} completed: {batch_end} of {total_dha} drugs processed")
        
        progress_bar.empty()
        status_text.empty()
        
        if st.session_state.db_manager:
            st.success(f"✅ Matching completed! {saved_count} matches and {unmatched_dha_count} unmatched DHA drugs saved to database. Total processed: {processed_count}")

        # Only run bidirectional pass if enabled
        if bidirectional:
            # --- Bidirectional Matching: DOH → DHA pass ---
            # Find all matched DOH codes from the first pass
            matched_doh_codes = set()
            for match in matches:
                if 'DOH_Code' in match and match['Overall_Score'] >= threshold:
                    matched_doh_codes.add(match['DOH_Code'])

            total_doh = len(doh_df)
            unmatched_doh_count = 0
            for doh_idx, doh_row in doh_df.iterrows():
                doh_code = str(doh_row.iloc[0]) if len(doh_row) > 0 else ""
                if doh_code in matched_doh_codes:
                    continue  # Already matched in first pass

                doh_brand = str(doh_row.iloc[1]) if len(doh_row) > 1 else ""
                doh_generic = str(doh_row.iloc[2]) if len(doh_row) > 2 else ""
                doh_strength = str(doh_row.iloc[3]) if len(doh_row) > 3 else ""
                doh_dosage = str(doh_row.iloc[4]) if len(doh_row) > 4 else ""
                doh_price = st.session_state.matcher.processor.clean_price(doh_row.iloc[5]) if len(doh_row) > 5 else 0.0
                doh_package_size = str(doh_row.iloc[6]) if len(doh_row) > 6 else ""
                doh_unit = str(doh_row.iloc[7]) if len(doh_row) > 7 else ""
                doh_unit_category = str(doh_row.iloc[8]) if len(doh_row) > 8 else ""

                best_score = 0
                best_dha_code = None
                for _, dha_row in dha_df.iterrows():
                    dha_code = str(dha_row.iloc[0]) if len(dha_row) > 0 else ""
                    dha_brand = str(dha_row.iloc[1]) if len(dha_row) > 1 else ""
                    dha_generic = str(dha_row.iloc[2]) if len(dha_row) > 2 else ""
                    dha_strength = str(dha_row.iloc[3]) if len(dha_row) > 3 else ""
                    dha_dosage = str(dha_row.iloc[4]) if len(dha_row) > 4 else ""
                    dha_price = st.session_state.matcher.processor.clean_price(dha_row.iloc[5]) if len(dha_row) > 5 else 0.0
                    dha_package_size = str(dha_row.iloc[6]) if len(dha_row) > 6 else ""
                    dha_unit = str(dha_row.iloc[7]) if len(dha_row) > 7 else ""
                    dha_unit_category = str(dha_row.iloc[8]) if len(dha_row) > 8 else ""

                    brand_sim = st.session_state.matcher.calculate_brand_similarity(doh_brand, dha_brand)
                    strength_sim = st.session_state.matcher.calculate_strength_similarity(doh_strength, dha_strength)
                    dosage_sim = st.session_state.matcher.calculate_dosage_similarity(doh_dosage, dha_dosage)
                    price_sim = st.session_state.matcher.price_matcher.calculate_price_similarity(doh_price, dha_price)
                    generic_match = st.session_state.matcher.generic_matcher.best_match(
                        doh_generic, dha_generic, doh_df.iloc[:, 2].tolist() if len(doh_df.columns) > 2 else []
                    )
                    generic_sim = generic_match['final_score']
                    package_size_sim = st.session_state.matcher.calculate_package_size_similarity(doh_package_size, dha_package_size)
                    unit_sim = st.session_state.matcher.calculate_unit_similarity(doh_unit, dha_unit)
                    unit_category_sim = st.session_state.matcher.calculate_unit_category_similarity(doh_unit_category, dha_unit_category)

                    applied_weights = weights.copy()
                    if 'package_size' not in applied_weights:
                        applied_weights['package_size'] = 0.10
                    if 'unit' not in applied_weights:
                        applied_weights['unit'] = 0.05
                    if 'unit_category' not in applied_weights:
                        applied_weights['unit_category'] = 0.05
                    if 'price' in applied_weights:
                        applied_weights['price'] = max(0.0, applied_weights['price'] - 0.10)
                    total_weight = sum(applied_weights.values())
                    if total_weight > 0:
                        for k in applied_weights:
                            applied_weights[k] = applied_weights[k] / total_weight
                    overall_score = (
                        brand_sim * applied_weights.get('brand', 0.0) +
                        strength_sim * applied_weights.get('strength', 0.0) +
                        dosage_sim * applied_weights.get('dosage', 0.0) +
                        generic_sim * applied_weights.get('generic', 0.0) +
                        price_sim * applied_weights.get('price', 0.0) +
                        package_size_sim * applied_weights.get('package_size', 0.0) +
                        unit_sim * applied_weights.get('unit', 0.0) +
                        unit_category_sim * applied_weights.get('unit_category', 0.0)
                    )
                    if overall_score > best_score:
                        best_score = overall_score
                        best_dha_code = dha_code
                # If no match above threshold, save as unmatched DOH drug
                if best_score < threshold:
                    if st.session_state.db_manager:
                        doh_drug_data = {
                            'code': doh_code,
                            'brand_name': doh_brand,
                            'generic_name': doh_generic,
                            'strength': doh_strength,
                            'dosage_form': doh_dosage,
                            'price': doh_price,
                            'package_size': doh_package_size,
                            'unit': doh_unit,
                            'unit_category': doh_unit_category
                        }
                        search_reason = f"No matches above threshold {threshold}"
                        st.session_state.db_manager.save_unmatched_drug(
                            doh_drug_data, best_match_score=best_score, best_match_doh_code=best_dha_code, search_reason=search_reason
                        )
                    unmatched_doh_count += 1

            if st.session_state.db_manager:
                st.success(f"✅ Bidirectional matching completed! {unmatched_doh_count} unmatched DOH drugs saved to database.")

        return matches
    

    
    def render_download_section(self, filtered_df: pd.DataFrame, results_df: pd.DataFrame):
        """Render download section"""
        st.subheader("📥 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download filtered results as CSV
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📄 Download Filtered Results (CSV)",
                data=csv,
                file_name=f"drug_matches_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download currently filtered results as CSV"
            )
        
        with col2:
            # Download all results as CSV
            all_csv = results_df.to_csv(index=False)
            st.download_button(
                label="📄 Download All Results (CSV)",
                data=all_csv,
                file_name=f"drug_matches_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download all matching results as CSV"
            )
        
        with col3:
            # Download comprehensive Excel report
            try:
                excel_data = self.excel_generator.create_report(
                    st.session_state.matches, 
                    st.session_state.dha_df, 
                    st.session_state.doh_df
                )
                st.download_button(
                    label="📊 Download Complete Report (Excel)",
                    data=excel_data,
                    file_name=f"drug_matching_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download comprehensive Excel report with multiple sheets including price analysis"
                )
            except Exception as e:
                st.error(f"Error creating Excel report: {e}")
    
    def run(self):
        """Main application run method"""
        self.setup_page()
        
        # Sidebar configuration
        sidebar_config = UIComponents.render_sidebar_config()
        
        # Handle database connection
        if sidebar_config.get('action') != 'none':
            self.handle_database_connection(sidebar_config)
        
        # Show database status
        self.render_database_status()
        
        # Main tabs
        tab1, tab2, tab3 = st.tabs([
            "📁 Data Upload",
            "🔍 Matching Process", 
            "📊 Results & Download"
        ])
        
        with tab1:
            dha_df, doh_df = UIComponents.render_data_upload()
            if dha_df is not None:
                st.session_state.dha_df = dha_df
                st.session_state.dha_file_name = dha_df.name
            if doh_df is not None:
                st.session_state.doh_df = doh_df
                st.session_state.doh_file_name = doh_df.name
        
        with tab2:
            if st.session_state.dha_df is None or st.session_state.doh_df is None:
                st.warning("⚠️ Please upload both DHA and DOH files first")
                return
            
            # Get configuration from sidebar
            matching_config = sidebar_config.get('matching_config', {})
            price_config = sidebar_config.get('price_config', {})
            
            # Render matching process
            process_config = UIComponents.render_matching_process(
                st.session_state.dha_df, 
                st.session_state.doh_df, 
                matching_config
            )
            
            if process_config:
                # Run matching process
                matches = self.run_matching_process(
                    process_config['dha_df'],
                    process_config['doh_df'],
                    matching_config.get('threshold', self.config.DEFAULT_THRESHOLD),
                    matching_config.get('weights', self.config.DEFAULT_WEIGHTS),
                    price_config,
                    matching_config.get('bidirectional', False) # Pass bidirectional option
                )
        
        with tab3:
            if st.session_state.matches is None:
                st.info("ℹ️ No matching results yet. Please run the matching process first.")
                return
            
            # Render results
            result = UIComponents.render_results(
                st.session_state.matches,
                st.session_state.dha_df,
                st.session_state.doh_df
            )
            
            if result is not None:
                filtered_df, results_df = result
                # Ensure both are DataFrames
                if isinstance(filtered_df, pd.DataFrame) and isinstance(results_df, pd.DataFrame):
                    # Render download section
                    self.render_download_section(filtered_df, results_df)

def main():
    """Main entry point"""
    app = DrugMatchingApp()
    app.run()

if __name__ == "__main__":
    main() 