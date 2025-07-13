"""
Price matching algorithms for drug comparison
"""
from typing import Dict, Optional
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