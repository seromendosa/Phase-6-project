"""
Enhanced Drug Matching Algorithms
Includes combination drug support and improved similarity calculations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from processing.text_processor import EnhancedDrugTextProcessor
from processing.price_matcher import PriceMatcher

class EnhancedGenericNameMatcher:
    """Enhanced generic name matcher with combination drug support"""
    
    def __init__(self):
        self.processor = EnhancedDrugTextProcessor()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.generic_names = []
        
    def train_vectorizer(self, generic_names: List[str]):
        """Train TF-IDF vectorizer on generic names"""
        if not generic_names:
            return
        
        # Clean and normalize generic names
        cleaned_names = []
        for name in generic_names:
            if name and pd.notna(name):
                # Handle combination drugs
                drugs = self.processor.extract_combination_drugs(str(name))
                cleaned_names.extend(drugs)
        
        if not cleaned_names:
            return
        
        # Remove duplicates and empty strings
        cleaned_names = list(set([name for name in cleaned_names if name.strip()]))
        
        # Train vectorizer
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.9,
            stop_words=None
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(cleaned_names)
        self.generic_names = cleaned_names
    
    def best_match(self, query_generic: str, target_generic: str, all_generics: Optional[List[str]] = None) -> Dict:
        """Find best match using multiple algorithms including combination drug support"""
        if not query_generic or not target_generic:
            return {
                'final_score': 0.0,
                'fuzzy_score': 0.0,
                'vector_score': 0.0,
                'semantic_score': 0.0,
                'method': 'none'
            }
        
        # Extract combination drugs
        query_drugs = self.processor.extract_combination_drugs(query_generic)
        target_drugs = self.processor.extract_combination_drugs(target_generic)
        
        # Calculate combination similarity
        combination_sim = self.processor.calculate_combination_similarity(query_generic, target_generic)
        
        # Calculate individual similarity scores
        fuzzy_score = fuzz.ratio(query_generic.upper(), target_generic.upper()) / 100.0
        
        # Vector similarity (if vectorizer is trained)
        vector_score = 0.0
        if self.vectorizer is not None and all_generics:
            try:
                query_vector = self.vectorizer.transform([query_generic])
                target_vector = self.vectorizer.transform([target_generic])
                vector_score = cosine_similarity(query_vector, target_vector)[0][0]
            except:
                vector_score = 0.0
        
        # Weighted combination of scores (redistribute weights)
        final_score = (
            combination_sim * 0.5 +
            fuzzy_score * 0.3 +
            vector_score * 0.2
        )
        
        # Determine method used
        if combination_sim > 0.8:
            method = 'combination'
        elif fuzzy_score > 0.8:
            method = 'fuzzy'
        elif vector_score > 0.8:
            method = 'vector'
        else:
            method = 'combined'
        
        return {
            'final_score': final_score,
            'fuzzy_score': fuzzy_score,
            'vector_score': vector_score,
            'semantic_score': combination_sim,
            'method': method
        }

class EnhancedDrugMatcher:
    """
    Enhanced drug matcher with improved algorithms.
    Compares drugs using brand, generic, strength, dosage, price, and package size.
    Each attribute has its own similarity function. Results are combined using weighted sum.
    """
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.processor = EnhancedDrugTextProcessor()
        self.generic_matcher = EnhancedGenericNameMatcher()
        self.price_matcher = PriceMatcher()
        
    def calculate_brand_similarity(self, brand1: str, brand2: str) -> float:
        """Calculate brand name similarity with enhanced processing (no phonetic)"""
        if not brand1 or not brand2:
            return 0.0
        
        # Normalize brand names
        norm_brand1 = self.processor.normalize_text(brand1)
        norm_brand2 = self.processor.normalize_text(brand2)
        
        # Exact match
        if norm_brand1 == norm_brand2:
            return 1.0
        
        # Fuzzy matching only
        fuzzy_score = fuzz.ratio(norm_brand1, norm_brand2) / 100.0
        
        return fuzzy_score
    
    def calculate_strength_similarity(self, strength1: str, strength2: str) -> float:
        """Calculate strength similarity with normalized comparison"""
        if not strength1 or not strength2:
            return 0.0
        
        # Normalize strengths to milligrams
        norm_strength1 = self.processor.normalize_strength(strength1)
        norm_strength2 = self.processor.normalize_strength(strength2)
        
        if norm_strength1 == 0.0 or norm_strength2 == 0.0:
            return 0.0
        
        # Calculate similarity based on ratio
        ratio = min(norm_strength1, norm_strength2) / max(norm_strength1, norm_strength2)
        
        # Apply sigmoid function for better scoring
        import math
        similarity = 1.0 / (1.0 + math.exp(-10 * (ratio - 0.8)))
        
        return similarity
    
    def calculate_dosage_similarity(self, dosage1: str, dosage2: str) -> float:
        """Calculate dosage form similarity with enhanced matching"""
        if not dosage1 or not dosage2:
            return 0.0
        
        # Normalize dosage forms
        norm_dosage1 = self.processor.normalize_text(dosage1)
        norm_dosage2 = self.processor.normalize_text(dosage2)
        
        # Exact match
        if norm_dosage1 == norm_dosage2:
            return 1.0
        
        # Fuzzy matching
        fuzzy_score = fuzz.ratio(norm_dosage1, norm_dosage2) / 100.0
        
        # Check for similar forms (e.g., tablet vs tablets)
        if 'TABLET' in norm_dosage1 and 'TABLET' in norm_dosage2:
            return 0.9
        elif 'CAPSULE' in norm_dosage1 and 'CAPSULE' in norm_dosage2:
            return 0.9
        elif 'INJECTION' in norm_dosage1 and 'INJECTION' in norm_dosage2:
            return 0.9
        
        return fuzzy_score
    
    def calculate_package_size_similarity(self, pkg1: str, pkg2: str) -> float:
        """
        Compare package sizes using numeric, unit, and fuzzy string logic.
        - If both are numeric and units match (or are None), compare numerically with tolerance.
        - If units differ, penalize score.
        - If not numeric, use fuzzy string similarity.
        - Returns a float between 0 and 1.
        """
        if not pkg1 and not pkg2:
            return 1.0
        if not pkg1 or not pkg2:
            return 0.0
        p1_amt, p1_unit, p1_raw = self.processor.extract_package_size(pkg1)
        p2_amt, p2_unit, p2_raw = self.processor.extract_package_size(pkg2)
        # If both are numeric and units match (or are None), compare numerically
        if p1_amt is not None and p2_amt is not None:
            if (p1_unit == p2_unit) or (p1_unit is None or p2_unit is None):
                # Allow small tolerance (e.g., ±5%)
                if p1_amt == 0 or p2_amt == 0:
                    return 0.0
                ratio = min(p1_amt, p2_amt) / max(p1_amt, p2_amt)
                if ratio > 0.95:
                    return 1.0
                elif ratio > 0.85:
                    return 0.9
                elif ratio > 0.7:
                    return 0.7
                else:
                    return ratio
            else:
                # Units differ, penalize
                return 0.5 * (min(p1_amt, p2_amt) / max(p1_amt, p2_amt))
        # If not numeric, use fuzzy string similarity
        from fuzzywuzzy import fuzz
        fuzzy_score = fuzz.ratio(str(p1_raw), str(p2_raw)) / 100.0
        return fuzzy_score

    def calculate_unit_similarity(self, unit1: str, unit2: str) -> float:
        """Calculate similarity between units (e.g., mg, ml, tablet)"""
        if not unit1 and not unit2:
            return 1.0
        if not unit1 or not unit2:
            return 0.0
        norm1 = self.processor.normalize_text(unit1)
        norm2 = self.processor.normalize_text(unit2)
        if norm1 == norm2:
            return 1.0
        from fuzzywuzzy import fuzz
        return fuzz.ratio(norm1, norm2) / 100.0

    def calculate_unit_category_similarity(self, cat1: str, cat2: str) -> float:
        """Calculate similarity between unit categories (e.g., solid, liquid)"""
        if not cat1 and not cat2:
            return 1.0
        if not cat1 or not cat2:
            return 0.0
        norm1 = self.processor.normalize_text(cat1)
        norm2 = self.processor.normalize_text(cat2)
        if norm1 == norm2:
            return 1.0
        from fuzzywuzzy import fuzz
        return fuzz.ratio(norm1, norm2) / 100.0
    
    def get_confidence_level(self, score: float) -> str:
        """
        Get confidence level based on overall score.
        Returns: 'Very High', 'High', 'Medium', 'Low', or 'Very Low'.
        """
        if score >= 0.95:
            return "Very High"
        elif score >= 0.85:
            return "High"
        elif score >= 0.75:
            return "Medium"
        elif score >= 0.65:
            return "Low"
        else:
            return "Very Low" 