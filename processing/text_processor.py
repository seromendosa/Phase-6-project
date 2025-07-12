"""
Text processing utilities for pharmaceutical data
"""
import pandas as pd
import re
from typing import Dict, Set
from config import Config

class DrugTextProcessor:
    """Enhanced text processing for pharmaceutical data"""
    
    def __init__(self):
        # Medical abbreviations and standardizations
        self.abbreviations = Config.MEDICAL_ABBREVIATIONS
        
        # Common dosage forms
        self.dosage_forms = Config.DOSAGE_FORMS
    
    def clean_text(self, text: str) -> str:
        """Clean and standardize text"""
        if pd.isna(text) or text is None:
            return ""
        
        text = str(text).upper().strip()
        
        # Remove special characters except spaces, parentheses, and hyphens
        text = re.sub(r'[^\w\s\(\)\-]', ' ', text)
        
        # Apply abbreviation standardization
        for abbrev, full_form in self.abbreviations.items():
            text = re.sub(rf'\b{abbrev}\b', full_form, text)
        
        # Clean multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_strength(self, text: str) -> str:
        """Extract and standardize strength information"""
        if pd.isna(text) or text is None:
            return ""
        
        text = str(text).upper()
        
        # Patterns for strength extraction
        patterns = [
            r'(\d+\.?\d*)\s*(MG|MILLIGRAM|MCG|MICROGRAM|G|GRAM|ML|MILLILITER|IU|INTERNATIONAL_UNIT|%)',
            r'(\d+\.?\d*)\s*(UNITS?)',
        ]
        
        strengths = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                value, unit = match
                strengths.append(f"{value} {unit}")
        
        return " + ".join(strengths) if strengths else text
    
    def extract_dosage_form(self, text: str) -> str:
        """Extract dosage form"""
        if pd.isna(text) or text is None:
            return ""
        
        text = str(text).upper()
        
        for form in self.dosage_forms:
            if form in text:
                return form
        
        return text
    
    def clean_price(self, price) -> float:
        """Clean and standardize price information"""
        if pd.isna(price) or price is None:
            return 0.0
        
        # If it's already a number
        if isinstance(price, (int, float)):
            return float(price)
        
        # If it's a string, clean it
        price_str = str(price).strip()
        
        # Remove currency symbols and common formatting
        price_str = re.sub(r'[^\d\.\,]', '', price_str)
        
        # Handle comma as decimal separator (some regions use comma)
        if ',' in price_str and '.' not in price_str:
            price_str = price_str.replace(',', '.')
        elif ',' in price_str and '.' in price_str:
            # Remove commas (thousand separators)
            price_str = price_str.replace(',', '')
        
        try:
            return float(price_str)
        except (ValueError, TypeError):
            return 0.0
    
    def validate_drug_data(self, data: Dict) -> Dict[str, bool]:
        """Validate drug data fields"""
        validation = {}
        
        # Check required fields
        required_fields = ['code', 'brand_name', 'generic_name', 'strength', 'dosage_form']
        for field in required_fields:
            value = data.get(field, '')
            validation[f'{field}_valid'] = bool(value and str(value).strip())
        
        # Check price field
        price = data.get('price', 0.0)
        validation['price_valid'] = isinstance(price, (int, float)) and price >= 0
        
        return validation 