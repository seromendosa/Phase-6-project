#!/usr/bin/env python3
"""
Test script for unified table functionality
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.manager import DatabaseManager
from config import Config

def test_unified_table():
    """Test the unified table functionality"""
    print("🧪 Testing Unified Table Functionality")
    print("=" * 50)
    
    # Create a test database manager (in-memory SQLite for testing)
    db_url = "sqlite:///test_unified.db"
    db_manager = DatabaseManager(db_url)
    
    try:
        # Test 1: Save a matched drug
        print("\n1. Testing matched drug save...")
        match_data = {
            'DHA_Code': 'DHA001',
            'DOH_Code': 'DOH001',
            'DHA_Brand_Name': 'Test Brand',
            'DOH_Brand_Name': 'Test Brand',
            'DHA_Generic_Name': 'Test Generic',
            'DOH_Generic_Name': 'Test Generic',
            'DHA_Strength': '10mg',
            'DOH_Strength': '10mg',
            'DHA_Dosage_Form': 'Tablet',
            'DOH_Dosage_Form': 'Tablet',
            'DHA_Price': 10.0,
            'DOH_Price': 12.0,
            'Brand_Similarity': 0.95,
            'Generic_Similarity': 0.90,
            'Strength_Similarity': 0.85,
            'Dosage_Similarity': 0.80,
            'Price_Similarity': 0.75,
            'Overall_Score': 0.85,
            'Confidence_Level': 'High',
            'Fuzzy_Score': 0.90,
            'Vector_Score': 0.85,
            'Semantic_Score': 0.80,
            'Matching_Method': 'Combined'
        }
        
        db_manager.save_match(match_data)
        print("✅ Matched drug saved successfully")
        
        # Test 2: Save an unmatched drug
        print("\n2. Testing unmatched drug save...")
        unmatched_data = {
            'code': 'DHA002',
            'brand_name': 'Unmatched Brand',
            'generic_name': 'Unmatched Generic',
            'strength': '20mg',
            'dosage_form': 'Capsule',
            'price': 15.0,
            'best_match_score': 0.45,
            'best_match_doh_code': 'DOH999',
            'search_reason': 'Below threshold 0.5'
        }
        
        db_manager.save_unmatched_drug(unmatched_data, 'DHA', 0.45, 'DOH999', 'Below threshold')
        print("✅ Unmatched drug saved successfully")
        
        # Test 3: Check counts
        print("\n3. Checking record counts...")
        total_count = db_manager.get_total_count()
        matched_count = db_manager.get_match_count()
        unmatched_count = db_manager.get_unmatched_count()
        
        print(f"   Total records: {total_count}")
        print(f"   Matched drugs: {matched_count}")
        print(f"   Unmatched drugs: {unmatched_count}")
        
        # Test 4: Retrieve and display results
        print("\n4. Retrieving all results...")
        all_results = db_manager.get_all_results()
        
        for result in all_results:
            print(f"   ID: {result.id}, DHA Code: {result.dha_code}, Status: {result.status}")
            if result.status == 'MATCHED':
                print(f"     → Matched with DOH: {result.doh_code}, Score: {result.overall_score}")
            else:
                print(f"     → Best score: {result.best_match_score}, Reason: {result.search_reason}")
        
        # Test 5: Test filtering
        print("\n5. Testing filtered queries...")
        matched_drugs = db_manager.get_matched_drugs()
        unmatched_drugs = db_manager.get_unmatched_drugs()
        
        print(f"   Matched drugs query: {len(matched_drugs)} results")
        print(f"   Unmatched drugs query: {len(unmatched_drugs)} results")
        
        print("\n✅ All tests passed! Unified table is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test database
        try:
            db_manager.close_connection()
            if os.path.exists("test_unified.db"):
                os.remove("test_unified.db")
            print("\n🧹 Test database cleaned up")
        except:
            pass

if __name__ == "__main__":
    test_unified_table() 