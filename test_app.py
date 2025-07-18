#!/usr/bin/env python3
"""
Simple test script to verify application components
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from models.database import DrugMatch, Base
        print("✅ Database models imported successfully")
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    try:
        from database.manager import DatabaseManager
        print("✅ Database manager imported successfully")
    except Exception as e:
        print(f"❌ Database manager import failed: {e}")
        return False
    
    try:
        from processing.text_processor import DrugTextProcessor
        print("✅ Text processor imported successfully")
    except Exception as e:
        print(f"❌ Text processor import failed: {e}")
        return False
    
    try:
        from processing.matchers import DrugMatcher, PriceMatcher, GenericNameMatcher
        print("✅ Matchers imported successfully")
    except Exception as e:
        print(f"❌ Matchers import failed: {e}")
        return False
    
    try:
        from reporting.excel_generator import ExcelReportGenerator
        print("✅ Excel generator imported successfully")
    except Exception as e:
        print(f"❌ Excel generator import failed: {e}")
        return False
    
    try:
        from ui.components import UIComponents
        print("✅ UI components imported successfully")
    except Exception as e:
        print(f"❌ UI components import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import Config
        
        # Test config validation
        validation = Config.validate_config()
        if validation['valid']:
            print("✅ Configuration is valid")
        else:
            print(f"⚠️ Configuration issues: {validation['issues']}")
        
        # Test database URL generation
        db_url = Config.get_database_url()
        print(f"✅ Database URL generated: {db_url[:20]}...")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_text_processor():
    """Test text processing"""
    print("\n🔍 Testing text processor...")
    
    try:
        from processing.text_processor import DrugTextProcessor
        
        processor = DrugTextProcessor()
        
        # Test text cleaning
        cleaned = processor.clean_text("Panadol 500mg TAB")
        print(f"✅ Text cleaning: 'Panadol 500mg TAB' -> '{cleaned}'")
        
        # Test strength extraction
        strength = processor.extract_strength("500mg tablet")
        print(f"✅ Strength extraction: '500mg tablet' -> '{strength}'")
        
        # Test price cleaning
        price = processor.clean_price("15.50")
        print(f"✅ Price cleaning: '15.50' -> {price}")
        
        return True
    except Exception as e:
        print(f"❌ Text processor test failed: {e}")
        return False

def test_matchers():
    """Test matching algorithms"""
    print("\n🔍 Testing matchers...")
    
    try:
        from processing.matchers import PriceMatcher, GenericNameMatcher
        
        # Test price matcher
        price_matcher = PriceMatcher()
        similarity = price_matcher.calculate_price_similarity(10.0, 12.0)
        print(f"✅ Price similarity (10.0, 12.0): {similarity:.3f}")
        
        # Test generic matcher
        generic_matcher = GenericNameMatcher()
        fuzzy_score = generic_matcher.fuzzy_match("Paracetamol", "Acetaminophen")
        print(f"✅ Generic fuzzy match: {fuzzy_score:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Matchers test failed: {e}")
        return False

def test_advanced_weighting():
    """Test advanced conditional weighting logic in matching process"""
    import pandas as pd
    from app import DrugMatchingApp
    app = DrugMatchingApp()
    # Create mock data
    dha_data = [
        ["DHA001", "BrandA", "Paracetamol", "500mg", "Tablet", 10.0],
        ["DHA002", "BrandB", "Ibuprofen", "200mg", "Capsule", 12.0],
        ["DHA003", "BrandC", "Amoxicillin", "250mg", "Capsule", 15.0],
        ["DHA004", "BrandA", "Paracetamol", "500mg", "Tablet", 10.0], # identical to DOH
        ["DHA005", "BrandA", "Paracetamol", "1000mg", "Tablet", 20.0], # brand match, strength mismatch
    ]
    doh_data = [
        ["DOH001", "BrandA", "Paracetamol", "500mg", "Tablet", 10.0],
        ["DOH002", "BrandB", "Ibuprofen", "200mg", "Capsule", 12.0],
        ["DOH003", "BrandC", "Amoxicillin", "250mg", "Capsule", 15.0],
        ["DOH004", "BrandA", "Paracetamol", "1000mg", "Tablet", 20.0],
    ]
    dha_df = pd.DataFrame(dha_data)  # No columns specified
    doh_df = pd.DataFrame(doh_data)  # No columns specified
    # Use default weights and threshold
    weights = app.config.DEFAULT_WEIGHTS
    threshold = 0.7
    price_config = {"price_tolerance": 20.0, "max_price_ratio": 5.0}
    # Run matching
    matches = app._match_drugs(dha_df, doh_df, threshold, weights, "test-session")
    # Check that advanced logic is applied
    for match in matches:
        print(f"Match: DHA {match['DHA_Code']} <-> DOH {match['DOH_Code']}")
        print(f"  Brand Sim: {match['Brand_Similarity']}, Strength Sim: {match['Strength_Similarity']}, Dosage Sim: {match['Dosage_Similarity']}")
        print(f"  Applied Weights: {match['Applied_Weights']}")
        print(f"  Manual Review Flag: {match['Manual_Review_Flag']}")
        # If brand is identical, generic weight should be 0
        if match['Brand_Similarity'] >= 0.95:
            assert match['Applied_Weights']['generic'] == 0.0
        # If brand is identical but strength or dosage is low, manual review flag should be True
        if match['Brand_Similarity'] >= 0.95 and (match['Strength_Similarity'] < 0.8 or match['Dosage_Similarity'] < 0.8):
            assert match['Manual_Review_Flag'] is True
    print("Advanced weighting logic test passed.")

def test_strength_similarity_perfect_and_imperfect():
    from processing.matchers import EnhancedDrugMatcher
    matcher = EnhancedDrugMatcher()
    # Identical strengths
    assert matcher.calculate_strength_similarity('500 mg', '500 mg') == 1.0
    # Nearly identical strengths (within tolerance)
    assert matcher.calculate_strength_similarity('500 mg', '500.009 mg') == 1.0
    # Slightly different strengths (outside tolerance)
    sim = matcher.calculate_strength_similarity('500 mg', '495 mg')
    print(f"Similarity for 500 mg vs 495 mg: {sim}")
    assert 0.7 < sim < 1.0
    # Very different strengths
    sim2 = matcher.calculate_strength_similarity('500 mg', '250 mg')
    print(f"Similarity for 500 mg vs 250 mg: {sim2}")
    assert sim2 < 0.7

def main():
    """Run all tests"""
    print("🧪 Drug Matching System Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_text_processor,
        test_matchers
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application components are working correctly.")
        print("💡 You can now run the application with: python run.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 