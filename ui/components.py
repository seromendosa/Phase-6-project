"""
UI components for the Drug Matching System
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from typing import Dict, List, Optional
from config import Config

class UIComponents:
    """UI components for the application"""
    
    @staticmethod
    def render_sidebar_config():
        """Render sidebar configuration"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Initialize default config
            config = {
                'action': 'none',
                'matching_config': {
                    'threshold': Config.DEFAULT_THRESHOLD,
                    'weights': Config.DEFAULT_WEIGHTS
                },
                'price_config': {
                    'price_tolerance': Config.DEFAULT_PRICE_TOLERANCE,
                    'max_price_ratio': Config.DEFAULT_MAX_PRICE_RATIO
                }
            }
            
            # Database configuration
            with st.expander("🗄️ Database Settings", expanded=False):
                st.subheader("PostgreSQL Connection")
                db_host = st.text_input("Host", value=Config.DB_HOST)
                db_port = st.text_input("Port", value=Config.DB_PORT)
                db_name = st.text_input("Database Name", value=Config.DB_NAME)
                db_user = st.text_input("Username", value=Config.DB_USER)
                db_password = st.text_input("Password", type="password", value=Config.DB_PASSWORD)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔌 Connect to Database"):
                        config.update({
                            'action': 'connect_db',
                            'host': db_host,
                            'port': db_port,
                            'name': db_name,
                            'user': db_user,
                            'password': db_password
                        })
                
                with col2:
                    if st.button("🔌 Disconnect"):
                        config['action'] = 'disconnect_db'
            
            # Matching parameters
            with st.expander("🎯 Matching Settings", expanded=True):
                threshold = st.slider("Matching Threshold", 0.5, 1.0, Config.DEFAULT_THRESHOLD, 0.05)
                
                st.write("**Adjust Weight Distribution:**")
                brand_weight = st.slider("Brand Name Weight", 0.0, 1.0, Config.DEFAULT_WEIGHTS['brand'], 0.05)
                generic_weight = st.slider("Generic Name Weight", 0.0, 1.0, Config.DEFAULT_WEIGHTS['generic'], 0.05)
                strength_weight = st.slider("Strength Weight", 0.0, 1.0, Config.DEFAULT_WEIGHTS['strength'], 0.05)
                dosage_weight = st.slider("Dosage Form Weight", 0.0, 1.0, Config.DEFAULT_WEIGHTS['dosage'], 0.05)
                price_weight = st.slider("Price Weight", 0.0, 1.0, Config.DEFAULT_WEIGHTS['price'], 0.05)
                
                # Normalize weights
                total_weight = brand_weight + generic_weight + strength_weight + dosage_weight + price_weight
                if total_weight > 0:
                    weights = {
                        'brand': brand_weight / total_weight,
                        'generic': generic_weight / total_weight,
                        'strength': strength_weight / total_weight,
                        'dosage': dosage_weight / total_weight,
                        'price': price_weight / total_weight
                    }
                    
                    st.info(f"""
                    **Normalized Weights:**
                    - Brand: {weights['brand']:.2f}
                    - Generic: {weights['generic']:.2f}
                    - Strength: {weights['strength']:.2f}
                    - Dosage: {weights['dosage']:.2f}
                    - Price: {weights['price']:.2f}
                    """)
                else:
                    weights = Config.DEFAULT_WEIGHTS
                
                config['matching_config'].update({
                    'threshold': threshold,
                    'weights': weights
                })
            
            # Price matching settings
            with st.expander("💰 Price Matching Settings", expanded=False):
                st.write("**Price Similarity Parameters:**")
                price_tolerance = st.slider("Price Tolerance (%)", 5.0, 50.0, Config.DEFAULT_PRICE_TOLERANCE, 5.0)
                max_price_ratio = st.slider("Max Price Ratio", 2.0, 10.0, Config.DEFAULT_MAX_PRICE_RATIO, 0.5)
                
                st.info(f"""
                **Current Settings:**
                - Prices within {price_tolerance}% are considered perfect matches
                - Maximum price ratio for any similarity: {max_price_ratio}:1
                - Prices beyond this ratio get 0% similarity
                """)
                
                config['price_config'].update({
                    'price_tolerance': price_tolerance,
                    'max_price_ratio': max_price_ratio
                })
            
            return config
    
    @staticmethod
    def render_data_upload():
        """Render data upload section"""
        st.header("📁 Upload Drug Lists")
        
        col1, col2 = st.columns(2)
        
        dha_df = None
        doh_df = None
        
        with col1:
            st.subheader("DHA Drug List")
            dha_file = st.file_uploader("Upload DHA Excel file", type=Config.ALLOWED_FILE_TYPES, key="dha")
            
            if dha_file:
                try:
                    dha_df = pd.read_excel(dha_file)
                    dha_df.name = dha_file.name  # Store filename
                    st.success(f"✅ DHA file loaded: {len(dha_df)} drugs")
                    
                    # Show preview
                    st.write("**Preview:**")
                    st.dataframe(dha_df.head())
                    
                    # Show column mapping
                    st.write("**Expected columns:**")
                    st.write("1. Drug Code, 2. Brand Name, 3. Generic Name, 4. Strength, 5. Dosage Form, 6. Price")
                    
                    # Validate columns
                    if len(dha_df.columns) < 6:
                        st.warning(f"⚠️ Expected 6 columns, found {len(dha_df.columns)}. Please ensure Price column is included.")
                    
                except Exception as e:
                    st.error(f"Error loading DHA file: {e}")
                    dha_df = None
        
        with col2:
            st.subheader("DOH Drug List")
            doh_file = st.file_uploader("Upload DOH Excel file", type=Config.ALLOWED_FILE_TYPES, key="doh")
            
            if doh_file:
                try:
                    doh_df = pd.read_excel(doh_file)
                    doh_df.name = doh_file.name  # Store filename
                    st.success(f"✅ DOH file loaded: {len(doh_df)} drugs")
                    
                    # Show preview
                    st.write("**Preview:**")
                    st.dataframe(doh_df.head())
                    
                    # Show column mapping
                    st.write("**Expected columns:**")
                    st.write("1. Drug Code, 2. Brand Name, 3. Generic Name, 4. Strength, 5. Dosage Form, 6. Price")
                    
                    # Validate columns
                    if len(doh_df.columns) < 6:
                        st.warning(f"⚠️ Expected 6 columns, found {len(doh_df.columns)}. Please ensure Price column is included.")
                    
                except Exception as e:
                    st.error(f"Error loading DOH file: {e}")
                    doh_df = None
        
        return dha_df, doh_df
    
    @staticmethod
    def validate_data_quality(dha_df: pd.DataFrame, doh_df: pd.DataFrame) -> Dict:
        """Validate data quality before processing"""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'stats': {}
        }
        
        # Check for required columns
        if len(dha_df.columns) < 6:
            validation_results['errors'].append("DHA file must have at least 6 columns")
            validation_results['is_valid'] = False
        
        if len(doh_df.columns) < 6:
            validation_results['errors'].append("DOH file must have at least 6 columns")
            validation_results['is_valid'] = False
        
        if not validation_results['is_valid']:
            return validation_results
        
        # Check for empty datasets
        if len(dha_df) == 0:
            validation_results['errors'].append("DHA file is empty")
            validation_results['is_valid'] = False
        
        if len(doh_df) == 0:
            validation_results['errors'].append("DOH file is empty")
            validation_results['is_valid'] = False
        
        # Check for missing values in critical columns
        try:
            dha_missing_codes = dha_df.iloc[:, 0].isna().sum()
        except:
            dha_missing_codes = 0
            
        try:
            dha_missing_brands = dha_df.iloc[:, 1].isna().sum()
        except:
            dha_missing_brands = 0
            
        try:
            dha_missing_generics = dha_df.iloc[:, 2].isna().sum()
        except:
            dha_missing_generics = 0
        
        try:
            doh_missing_codes = doh_df.iloc[:, 0].isna().sum()
        except:
            doh_missing_codes = 0
            
        try:
            doh_missing_brands = doh_df.iloc[:, 1].isna().sum()
        except:
            doh_missing_brands = 0
            
        try:
            doh_missing_generics = doh_df.iloc[:, 2].isna().sum()
        except:
            doh_missing_generics = 0
        
        if dha_missing_codes > 0:
            validation_results['warnings'].append(f"DHA file has {dha_missing_codes} missing drug codes")
        
        if dha_missing_brands > 0:
            validation_results['warnings'].append(f"DHA file has {dha_missing_brands} missing brand names")
        
        if dha_missing_generics > 0:
            validation_results['warnings'].append(f"DHA file has {dha_missing_generics} missing generic names")
        
        if doh_missing_codes > 0:
            validation_results['warnings'].append(f"DOH file has {doh_missing_codes} missing drug codes")
        
        if doh_missing_brands > 0:
            validation_results['warnings'].append(f"DOH file has {doh_missing_brands} missing brand names")
        
        if doh_missing_generics > 0:
            validation_results['warnings'].append(f"DOH file has {doh_missing_generics} missing generic names")
        
        # Check for duplicates
        dha_duplicate_codes = dha_df.iloc[:, 0].duplicated().sum()
        doh_duplicate_codes = doh_df.iloc[:, 0].duplicated().sum()
        
        if dha_duplicate_codes > 0:
            validation_results['warnings'].append(f"DHA file has {dha_duplicate_codes} duplicate drug codes")
        
        if doh_duplicate_codes > 0:
            validation_results['warnings'].append(f"DOH file has {doh_duplicate_codes} duplicate drug codes")
        
        # Check price data quality
        dha_prices = pd.to_numeric(dha_df.iloc[:, 5], errors='coerce')
        doh_prices = pd.to_numeric(doh_df.iloc[:, 5], errors='coerce')
        
        dha_invalid_prices = dha_prices.isna().sum()
        doh_invalid_prices = doh_prices.isna().sum()
        
        if dha_invalid_prices > 0:
            validation_results['warnings'].append(f"DHA file has {dha_invalid_prices} invalid price values")
        
        if doh_invalid_prices > 0:
            validation_results['warnings'].append(f"DOH file has {doh_invalid_prices} invalid price values")
        
        # Check for negative prices
        if isinstance(dha_prices, pd.Series):
            dha_negative_prices = (dha_prices < 0).sum()
            if dha_negative_prices > 0:
                validation_results['warnings'].append(f"DHA file has {dha_negative_prices} negative prices")
        
        if isinstance(doh_prices, pd.Series):
            doh_negative_prices = (doh_prices < 0).sum()
            if doh_negative_prices > 0:
                validation_results['warnings'].append(f"DOH file has {doh_negative_prices} negative prices")
        
        # Compile statistics
        validation_results['stats'] = {
            'dha_total': len(dha_df),
            'doh_total': len(doh_df),
            'dha_missing_codes': dha_missing_codes,
            'dha_missing_brands': dha_missing_brands,
            'dha_missing_generics': dha_missing_generics,
            'doh_missing_codes': doh_missing_codes,
            'doh_missing_brands': doh_missing_brands,
            'doh_missing_generics': doh_missing_generics,
            'dha_duplicates': dha_duplicate_codes,
            'doh_duplicates': doh_duplicate_codes,
            'dha_invalid_prices': dha_invalid_prices,
            'doh_invalid_prices': doh_invalid_prices
        }
        
        return validation_results
    
    @staticmethod
    def render_data_validation(validation_results: Dict):
        """Render data validation results"""
        st.subheader("🔍 Data Quality Validation")
        
        if validation_results['is_valid']:
            st.success("✅ Data validation passed!")
        else:
            st.error("❌ Data validation failed!")
        
        # Show statistics
        stats = validation_results['stats']
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**DHA File Statistics:**")
            st.write(f"- Total drugs: {stats['dha_total']}")
            st.write(f"- Missing codes: {stats['dha_missing_codes']}")
            st.write(f"- Missing brands: {stats['dha_missing_brands']}")
            st.write(f"- Missing generics: {stats['dha_missing_generics']}")
            st.write(f"- Duplicate codes: {stats['dha_duplicates']}")
            st.write(f"- Invalid prices: {stats['dha_invalid_prices']}")
        
        with col2:
            st.write("**DOH File Statistics:**")
            st.write(f"- Total drugs: {stats['doh_total']}")
            st.write(f"- Missing codes: {stats['doh_missing_codes']}")
            st.write(f"- Missing brands: {stats['doh_missing_brands']}")
            st.write(f"- Missing generics: {stats['doh_missing_generics']}")
            st.write(f"- Duplicate codes: {stats['doh_duplicates']}")
            st.write(f"- Invalid prices: {stats['doh_invalid_prices']}")
        
        # Show warnings
        if validation_results['warnings']:
            st.warning("⚠️ **Warnings:**")
            for warning in validation_results['warnings']:
                st.write(f"- {warning}")
        
        # Show errors
        if validation_results['errors']:
            st.error("❌ **Errors:**")
            for error in validation_results['errors']:
                st.write(f"- {error}")
        
        return validation_results['is_valid']
    
    @staticmethod
    def render_matching_process(dha_df: pd.DataFrame, doh_df: pd.DataFrame, config: Dict):
        """Render matching process section"""
        st.header("🔍 Drug Matching Process")
        
        # Validate data structure
        if len(dha_df.columns) < 6 or len(doh_df.columns) < 6:
            st.error("❌ Both files must have at least 6 columns (including Price column)")
            return None
        
        # Data quality validation
        with st.expander("🔍 Data Quality Check", expanded=True):
            validation_results = UIComponents.validate_data_quality(dha_df, doh_df)
            is_valid = UIComponents.render_data_validation(validation_results)
            
            if not is_valid:
                st.error("❌ Please fix data quality issues before proceeding")
                return None
        
        # Show dataset info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("DHA Drugs", len(dha_df))
        with col2:
            st.metric("DOH Drugs", len(doh_df))
        with col3:
            st.metric("Max Possible Matches", min(len(dha_df), len(doh_df)))
        
        # Price data preview
        with st.expander("💰 Price Data Preview", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**DHA Price Statistics:**")
                dha_prices = pd.to_numeric(dha_df.iloc[:, 5], errors='coerce')
                if isinstance(dha_prices, pd.Series):
                    st.write(f"- Valid prices: {dha_prices.notna().sum()}/{len(dha_prices)}")
                    if dha_prices.notna().sum() > 0:
                        st.write(f"- Average price: {dha_prices.mean():.2f}")
                        st.write(f"- Price range: {dha_prices.min():.2f} - {dha_prices.max():.2f}")
                    else:
                        st.write("- No valid price data found")
                else:
                    st.write("- Could not process price data")
            
            with col2:
                st.write("**DOH Price Statistics:**")
                doh_prices = pd.to_numeric(doh_df.iloc[:, 5], errors='coerce')
                if isinstance(doh_prices, pd.Series):
                    st.write(f"- Valid prices: {doh_prices.notna().sum()}/{len(doh_prices)}")
                    if doh_prices.notna().sum() > 0:
                        st.write(f"- Average price: {doh_prices.mean():.2f}")
                        st.write(f"- Price range: {doh_prices.min():.2f} - {doh_prices.max():.2f}")
                    else:
                        st.write("- No valid price data found")
                else:
                    st.write("- Could not process price data")
        
        # Add partial results export option
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start Matching Process", type="primary"):
                return {
                    'dha_df': dha_df,
                    'doh_df': doh_df,
                    'config': config
                }
        
        with col2:
            if st.button("💾 Export Partial Results", help="Export current results if processing was interrupted"):
                # This will be handled in the main app
                st.info("Partial results export will be available during processing")
        
        return None
    
    @staticmethod
    def render_results(matches: List[Dict], dha_df: pd.DataFrame, doh_df: pd.DataFrame):
        """Render results section"""
        st.header("📊 Results & Analysis")
        
        if not matches:
            st.warning("⚠️ No matches found. Try adjusting the threshold or weights.")
            return
        
        # Convert matches to DataFrame
        matches_df = pd.DataFrame(matches)
        
        # Display summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Matches", len(matches))
        
        with col2:
            avg_score = matches_df['Overall_Score'].mean()
            st.metric("Average Score", f"{avg_score:.3f}")
        
        with col3:
            high_conf = len(matches_df[matches_df['Confidence_Level'].isin(['Very High', 'High'])])
            st.metric("High Confidence", high_conf)
        
        with col4:
            avg_price_sim = matches_df['Price_Similarity'].mean()
            st.metric("Avg Price Similarity", f"{avg_price_sim:.3f}")
        
        with col5:
            match_rate = len(matches) / len(dha_df) * 100
            st.metric("Match Rate", f"{match_rate:.1f}%")
        
        # Show unmatched drugs if database is connected
        if st.session_state.db_manager:
            with st.expander("📋 Unmatched Drugs Analysis", expanded=False):
                unmatched_dha = st.session_state.db_manager.get_unmatched_drugs('DHA')
                unmatched_doh = st.session_state.db_manager.get_unmatched_drugs('DOH')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Unmatched DHA Drugs")
                    if unmatched_dha:
                        unmatched_dha_df = pd.DataFrame([drug.to_dict() for drug in unmatched_dha])
                        st.dataframe(unmatched_dha_df[['drug_code', 'brand_name', 'generic_name', 'best_match_score', 'search_reason']])
                        
                        # Show reasons for no matches
                        reasons = unmatched_dha_df['search_reason'].value_counts()
                        st.write("**Reasons for no matches:**")
                        for reason, count in reasons.items():
                            st.write(f"- {reason}: {count}")
                    else:
                        st.info("No unmatched DHA drugs found")
                
                with col2:
                    st.subheader("Unmatched DOH Drugs")
                    if unmatched_doh:
                        unmatched_doh_df = pd.DataFrame([drug.to_dict() for drug in unmatched_doh])
                        st.dataframe(unmatched_doh_df[['drug_code', 'brand_name', 'generic_name', 'best_match_score', 'search_reason']])
                    else:
                        st.info("No unmatched DOH drugs found")
        
        # Show search sessions if database is connected
        if st.session_state.db_manager:
            with st.expander("📈 Search History", expanded=False):
                search_sessions = st.session_state.db_manager.get_search_sessions()
                if search_sessions:
                    sessions_df = pd.DataFrame([session.to_dict() for session in search_sessions])
                    
                    # Show recent sessions
                    st.subheader("Recent Search Sessions")
                    recent_sessions = sessions_df.head(5)[['session_id', 'dha_file_name', 'doh_file_name', 
                                                         'matches_count', 'unmatched_dha_count', 'processing_time', 'started_at']]
                    st.dataframe(recent_sessions)
                    
                    # Show session statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Sessions", len(sessions_df))
                    with col2:
                        avg_matches = sessions_df['matches_count'].mean()
                        st.metric("Avg Matches per Session", f"{avg_matches:.1f}")
                    with col3:
                        avg_time = sessions_df['processing_time'].mean()
                        st.metric("Avg Processing Time", f"{avg_time:.1f}s")
                else:
                    st.info("No search sessions found")
        
        # Confidence distribution
        confidence_dist = matches_df['Confidence_Level'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Confidence distribution chart
            if not confidence_dist.empty:
                fig = px.pie(
                    values=confidence_dist.values,
                    names=confidence_dist.index,
                    title="Confidence Level Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Component similarity comparison
            component_means = {
                'Brand': matches_df['Brand_Similarity'].mean(),
                'Generic': matches_df['Generic_Similarity'].mean(),
                'Strength': matches_df['Strength_Similarity'].mean(),
                'Dosage': matches_df['Dosage_Similarity'].mean(),
                'Price': matches_df['Price_Similarity'].mean()
            }
            
            fig_components = px.bar(
                x=list(component_means.keys()),
                y=list(component_means.values()),
                title="Average Component Similarities",
                color=list(component_means.values()),
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_components, use_container_width=True)
        
        # Results table with filtering
        st.subheader("🔍 Detailed Results")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence_filter = st.multiselect(
                "Filter by Confidence",
                options=matches_df['Confidence_Level'].unique(),
                default=matches_df['Confidence_Level'].unique()
            )
        
        with col2:
            min_score = st.slider(
                "Minimum Overall Score",
                min_value=float(matches_df['Overall_Score'].min()),
                max_value=float(matches_df['Overall_Score'].max()),
                value=float(matches_df['Overall_Score'].min()),
                step=0.01
            )
        
        with col3:
            min_price_sim = st.slider(
                "Minimum Price Similarity",
                min_value=float(matches_df['Price_Similarity'].min()),
                max_value=float(matches_df['Price_Similarity'].max()),
                value=float(matches_df['Price_Similarity'].min()),
                step=0.01
            )
        
        # Apply filters
        filtered_df = matches_df[
            (matches_df['Confidence_Level'].isin(confidence_filter)) &
            (matches_df['Overall_Score'] >= min_score) &
            (matches_df['Price_Similarity'] >= min_price_sim)
        ]
        
        st.info(f"Showing {len(filtered_df)} of {len(matches_df)} matches")
        
        # Display filtered results
        st.dataframe(
            filtered_df.style.apply(
                lambda x: ['background-color: #e6f3ff' if x['Confidence_Level'] in ['Very High', 'High'] 
                          else 'background-color: #fff2e6' if x['Confidence_Level'] == 'Medium'
                          else 'background-color: #ffe6e6' for _ in range(len(x))],
                axis=1
            ),
            use_container_width=True
        )
        
        return filtered_df, matches_df 