"""
Matching algorithms for drug comparison
"""
import streamlit as st
import re
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Optional
from config import Config

class PriceMatcher:
    """Class for price similarity calculations"""
    
    def __init__(self, tolerance_percentage: Optional[float] = None, max_ratio: Optional[float] = None):
        self.tolerance_percentage = tolerance_percentage or Config.DEFAULT_PRICE_TOLERANCE
        self.max_ratio = max_ratio or Config.DEFAULT_MAX_PRICE_RATIO
    
    def calculate_price_similarity(self, price1: float, price2: float) -> float:
        """
        Calculate price similarity between two prices
        
        Args:
            price1: First price
            price2: Second price
            
        Returns:
            Similarity score between 0 and 1
        """
        # Handle cases where one or both prices are 0 or invalid
        if price1 <= 0 or price2 <= 0:
            return 0.0
        
        # Calculate percentage difference
        avg_price = (price1 + price2) / 2
        price_diff = abs(price1 - price2)
        percentage_diff = (price_diff / avg_price) * 100
        
        # Perfect match within tolerance
        if percentage_diff <= self.tolerance_percentage:
            return 1.0
        
        # Calculate ratio-based similarity
        ratio = max(price1, price2) / min(price1, price2)
        
        # If ratio is too high, return 0
        if ratio > self.max_ratio:
            return 0.0
        
        # Linear decay based on ratio
        # ratio 1.0 -> similarity 1.0
        # ratio max_ratio -> similarity 0.0
        similarity = max(0.0, 1.0 - (ratio - 1.0) / (self.max_ratio - 1.0))
        
        return similarity
    
    def get_price_analysis(self, price1: float, price2: float) -> Dict:
        """Get detailed price analysis"""
        if price1 <= 0 or price2 <= 0:
            return {
                'similarity': 0.0,
                'difference': 'N/A',
                'percentage_diff': 'N/A',
                'ratio': 'N/A',
                'analysis': 'Invalid price data'
            }
        
        similarity = self.calculate_price_similarity(price1, price2)
        difference = abs(price1 - price2)
        avg_price = (price1 + price2) / 2
        percentage_diff = (difference / avg_price) * 100
        ratio = max(price1, price2) / min(price1, price2)
        
        # Analysis text
        if similarity >= 0.9:
            analysis = "Excellent price match"
        elif similarity >= 0.7:
            analysis = "Good price match"
        elif similarity >= 0.5:
            analysis = "Moderate price difference"
        elif similarity >= 0.3:
            analysis = "Significant price difference"
        else:
            analysis = "Large price difference"
        
        return {
            'similarity': similarity,
            'difference': difference,
            'percentage_diff': percentage_diff,
            'ratio': ratio,
            'analysis': analysis
        }

class GenericNameMatcher:
    """Multiple approaches for generic name matching"""
    
    def __init__(self):
        from processing.text_processor import DrugTextProcessor
        self.processor = DrugTextProcessor()
        self.vectorizer = None
    
    def fuzzy_match(self, name1: str, name2: str) -> float:
        """Simple fuzzy string matching"""
        if not name1 or not name2:
            return 0.0
        
        # Clean names
        clean1 = self.processor.clean_text(name1)
        clean2 = self.processor.clean_text(name2)
        
        # Multiple fuzzy matching approaches
        ratio = fuzz.ratio(clean1, clean2)
        partial_ratio = fuzz.partial_ratio(clean1, clean2)
        token_sort = fuzz.token_sort_ratio(clean1, clean2)
        token_set = fuzz.token_set_ratio(clean1, clean2)
        
        # Weighted average
        score = (ratio * 0.3 + partial_ratio * 0.2 + token_sort * 0.25 + token_set * 0.25) / 100
        
        return score
    
    def vectorized_match(self, name1: str, name2: str, doh_generics: Optional[List[str]] = None) -> float:
        """TF-IDF vectorized matching"""
        if not name1 or not name2:
            return 0.0
        
        try:
            # Clean names
            clean1 = self.processor.clean_text(name1)
            clean2 = self.processor.clean_text(name2)
            
            # Create or use existing vectorizer
            if self.vectorizer is None and doh_generics:
                # Train vectorizer on DOH generics
                all_generics = [self.processor.clean_text(g) for g in doh_generics if g]
                all_generics.extend([clean1, clean2])
                
                self.vectorizer = TfidfVectorizer(
                    ngram_range=(1, 2),
                    analyzer='word',
                    stop_words=None,
                    max_features=1000
                )
                self.vectorizer.fit(all_generics)
            
            if self.vectorizer:
                # Vectorize the two names
                vec1 = self.vectorizer.transform([clean1])
                vec2 = self.vectorizer.transform([clean2])
                
                # Calculate cosine similarity
                similarity = cosine_similarity(vec1, vec2)[0][0]
                return similarity
            
        except Exception as e:
            st.warning(f"Vectorized matching error: {e}")
        
        # Fallback to fuzzy matching
        return self.fuzzy_match(name1, name2)
    
    def semantic_match(self, name1: str, name2: str) -> float:
        """Semantic matching based on drug name patterns"""
        if not name1 or not name2:
            return 0.0
        
        clean1 = self.processor.clean_text(name1)
        clean2 = self.processor.clean_text(name2)
        
        # Extract potential active ingredients (first few words)
        words1 = clean1.split()[:3]  # First 3 words usually contain active ingredient
        words2 = clean2.split()[:3]
        
        # Check for exact matches in key words
        exact_matches = len(set(words1) & set(words2))
        total_unique = len(set(words1) | set(words2))
        
        if total_unique == 0:
            return 0.0
        
        semantic_score = exact_matches / total_unique
        
        # Combine with fuzzy score
        fuzzy_score = self.fuzzy_match(name1, name2)
        
        return (semantic_score * 0.6 + fuzzy_score * 0.4)
    
    def best_match(self, name1: str, name2: str, doh_generics: Optional[List[str]] = None) -> Dict:
        """Get best match using all methods"""
        fuzzy_score = self.fuzzy_match(name1, name2)
        vector_score = self.vectorized_match(name1, name2, doh_generics)
        semantic_score = self.semantic_match(name1, name2)
        
        # Weighted combination
        final_score = (fuzzy_score * 0.4 + vector_score * 0.35 + semantic_score * 0.25)
        
        return {
            'fuzzy_score': fuzzy_score,
            'vector_score': vector_score,
            'semantic_score': semantic_score,
            'final_score': final_score,
            'method': 'hybrid'
        }

class DrugMatcher:
    """Main drug matching class with price support"""
    
    def __init__(self, db_manager=None):
        from processing.text_processor import DrugTextProcessor
        self.processor = DrugTextProcessor()
        self.generic_matcher = GenericNameMatcher()
        self.price_matcher = PriceMatcher()
        self.db_manager = db_manager
    
    def calculate_brand_similarity(self, brand1: str, brand2: str) -> float:
        """Calculate brand name similarity"""
        if not brand1 or not brand2:
            return 0.0
        
        clean1 = self.processor.clean_text(brand1)
        clean2 = self.processor.clean_text(brand2)
        
        return fuzz.ratio(clean1, clean2) / 100
    
    def calculate_strength_similarity(self, strength1: str, strength2: str) -> float:
        """Calculate strength similarity"""
        if not strength1 or not strength2:
            return 0.0
        
        # Extract and compare numeric values
        extract1 = self.processor.extract_strength(strength1)
        extract2 = self.processor.extract_strength(strength2)
        
        if extract1 == extract2:
            return 1.0
        
        # Extract numbers for comparison
        nums1 = re.findall(r'\d+\.?\d*', extract1)
        nums2 = re.findall(r'\d+\.?\d*', extract2)
        
        if nums1 and nums2:
            try:
                val1 = float(nums1[0])
                val2 = float(nums2[0])
                
                if val1 == val2:
                    return 0.9
                
                # Calculate relative difference
                diff = abs(val1 - val2) / max(val1, val2)
                return max(0, 1 - diff)
                
            except ValueError:
                pass
        
        # Fallback to fuzzy matching
        return fuzz.ratio(extract1, extract2) / 100
    
    def calculate_dosage_similarity(self, dosage1: str, dosage2: str) -> float:
        """Calculate dosage form similarity"""
        if not dosage1 or not dosage2:
            return 0.0
        
        form1 = self.processor.extract_dosage_form(dosage1)
        form2 = self.processor.extract_dosage_form(dosage2)
        
        if form1 == form2:
            return 1.0
        
        return fuzz.ratio(form1, form2) / 100
    
    def get_confidence_level(self, score: float) -> str:
        """Determine confidence level based on score"""
        for level, threshold in Config.CONFIDENCE_THRESHOLDS.items():
            if score >= threshold:
                return level
        return "Very Low" 