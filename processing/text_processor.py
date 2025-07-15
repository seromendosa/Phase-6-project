"""
Enhanced Text Processing for Drug Names
Handles combination drugs, abbreviations, and phonetic matching
"""
import re
import string
from typing import List, Dict, Tuple
import pandas as pd
from difflib import SequenceMatcher
import jellyfish
from config import Config

class EnhancedDrugTextProcessor:
    """Enhanced text processor for drug names with combination drug support"""
    
    def __init__(self):
        # Enhanced medical abbreviations
        self.medical_abbreviations = {
            # Common drug abbreviations
            'MG': 'MILLIGRAM', 'MCG': 'MICROGRAM', 'G': 'GRAM',
            'ML': 'MILLILITER', 'L': 'LITER', 'IU': 'INTERNATIONAL_UNIT',
            'TAB': 'TABLET', 'TABS': 'TABLETS', 'CAP': 'CAPSULE', 
            'CAPS': 'CAPSULES', 'INJ': 'INJECTION', 'SYR': 'SYRUP',
            'SUSP': 'SUSPENSION', 'SOL': 'SOLUTION', 'CR': 'CREAM',
            'OINT': 'OINTMENT', 'DROPS': 'DROPS', 'SPRAY': 'SPRAY',
            'PATCH': 'PATCH', 'GEL': 'GEL', 'LOTION': 'LOTION',
            
            # Combination drug indicators
            '+': 'PLUS', '&': 'AND', '/': 'WITH',
            'COMB': 'COMBINATION', 'COMP': 'COMPOUND',
            
            # Common drug name abbreviations
            'ACID': 'ACID', 'SOD': 'SODIUM', 'POT': 'POTASSIUM',
            'CAL': 'CALCIUM', 'MAG': 'MAGNESIUM', 'ZINC': 'ZINC',
            'VIT': 'VITAMIN', 'VITAMIN': 'VITAMIN',
            'HCL': 'HYDROCHLORIDE', 'SULF': 'SULFATE',
            'PHOS': 'PHOSPHATE', 'CIT': 'CITRATE',
            'ACET': 'ACETATE', 'GLUC': 'GLUCONATE',
            'LACT': 'LACTATE', 'MAL': 'MALEATE',
            'FUM': 'FUMARATE', 'TAR': 'TARTRATE',
            
            # Dosage form abbreviations
            'SR': 'SUSTAINED_RELEASE', 'ER': 'EXTENDED_RELEASE',
            'XR': 'EXTENDED_RELEASE', 'CR': 'CONTROLLED_RELEASE',
            'IR': 'IMMEDIATE_RELEASE', 'LA': 'LONG_ACTING',
            'SA': 'SHORT_ACTING', 'PR': 'PROLONGED_RELEASE'
        }
        
        # Combination drug patterns
        self.combination_patterns = [
            r'(\w+)\s*[+&/]\s*(\w+)',  # Drug + Drug
            r'(\w+)\s+AND\s+(\w+)',    # Drug AND Drug
            r'(\w+)\s+WITH\s+(\w+)',   # Drug WITH Drug
            r'(\w+)\s+COMBINATION',    # Drug COMBINATION
            r'(\w+)\s+COMPOUND',       # Drug COMPOUND
        ]
        
        # Strength conversion patterns
        self.strength_patterns = {
            r'(\d+(?:\.\d+)?)\s*MG': lambda x: float(x) * 1,
            r'(\d+(?:\.\d+)?)\s*G': lambda x: float(x) * 1000,
            r'(\d+(?:\.\d+)?)\s*MCG': lambda x: float(x) * 0.001,
            r'(\d+(?:\.\d+)?)\s*KG': lambda x: float(x) * 1000000,
        }
    
    def normalize_text(self, text: str) -> str:
        """Enhanced text normalization with abbreviation expansion"""
        if not text or pd.isna(text):
            return ""
        
        text = str(text).upper().strip()
        
        # Expand medical abbreviations
        for abbrev, full in self.medical_abbreviations.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, full, text)
        
        # Remove extra whitespace and punctuation
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_combination_drugs(self, text: str) -> List[str]:
        """Extract individual drugs from combination drug names"""
        if not text:
            return []
        
        normalized_text = self.normalize_text(text)
        drugs = []
        
        # Check for combination patterns
        for pattern in self.combination_patterns:
            matches = re.findall(pattern, normalized_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        drugs.extend([drug.strip() for drug in match if drug.strip()])
                    else:
                        drugs.append(match.strip())
                break
        
        # If no combination pattern found, treat as single drug
        if not drugs:
            drugs = [normalized_text]
        
        # Clean and filter drugs
        cleaned_drugs = []
        for drug in drugs:
            cleaned = self.clean_drug_name(drug)
            if cleaned and len(cleaned) > 2:  # Filter out very short names
                cleaned_drugs.append(cleaned)
        
        return list(set(cleaned_drugs))  # Remove duplicates
    
    def clean_drug_name(self, text: str) -> str:
        """Clean individual drug name"""
        if not text:
            return ""
        
        # Remove common prefixes/suffixes that don't affect matching
        prefixes_to_remove = ['THE ', 'A ', 'AN ']
        suffixes_to_remove = [' TABLET', ' CAPSULE', ' INJECTION', ' SYRUP']
        
        cleaned = text.upper().strip()
        
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        
        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)]
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def normalize_strength(self, strength: str) -> float:
        """Normalize strength values to milligrams for comparison"""
        if not strength or pd.isna(strength):
            return 0.0
        
        strength_str = str(strength).upper().strip()
        
        # Try to extract numeric value and unit
        for pattern, conversion_func in self.strength_patterns.items():
            match = re.search(pattern, strength_str)
            if match:
                try:
                    value = float(match.group(1))
                    return conversion_func(value)
                except (ValueError, TypeError):
                    continue
        
        # If no pattern matches, try to extract just the number
        numeric_match = re.search(r'(\d+(?:\.\d+)?)', strength_str)
        if numeric_match:
            try:
                return float(numeric_match.group(1))
            except (ValueError, TypeError):
                pass
        
        return 0.0
    
    def calculate_combination_similarity(self, drug1: str, drug2: str) -> float:
        """Calculate similarity for combination drugs"""
        if not drug1 or not drug2:
            return 0.0
        
        # Extract individual drugs from combination names
        drugs1 = self.extract_combination_drugs(drug1)
        drugs2 = self.extract_combination_drugs(drug2)
        
        if not drugs1 or not drugs2:
            return 0.0
        
        # Calculate similarity matrix between all drugs
        similarity_matrix = []
        for d1 in drugs1:
            row = []
            for d2 in drugs2:
                # Calculate multiple similarity measures
                exact_match = 1.0 if d1 == d2 else 0.0
                sequence_sim = SequenceMatcher(None, d1, d2).ratio()
                
                # Weighted combination
                combined_sim = (exact_match * 0.5 + sequence_sim * 0.5) # Removed phonetic_sim
                row.append(combined_sim)
            similarity_matrix.append(row)
        
        # Calculate overall similarity using Hungarian algorithm or greedy approach
        if len(drugs1) == 1 and len(drugs2) == 1:
            # Single drug comparison
            return similarity_matrix[0][0]
        else:
            # Multiple drug comparison - use greedy matching
            total_similarity = 0.0
            matched_pairs = 0
            
            # Simple greedy matching
            used_drugs2 = set()
            for i, d1 in enumerate(drugs1):
                best_match = -1
                best_sim = 0.0
                
                for j, d2 in enumerate(drugs2):
                    if j not in used_drugs2 and similarity_matrix[i][j] > best_sim:
                        best_sim = similarity_matrix[i][j]
                        best_match = j
                
                if best_match != -1:
                    total_similarity += best_sim
                    used_drugs2.add(best_match)
                    matched_pairs += 1
            
            # Calculate average similarity
            if matched_pairs > 0:
                return total_similarity / max(len(drugs1), len(drugs2))
            
            return 0.0
    
    def clean_price(self, price) -> float:
        """Clean and convert price to float"""
        if pd.isna(price) or price is None:
            return 0.0
        
        try:
            # Remove currency symbols and commas
            price_str = str(price).replace('$', '').replace(',', '').strip()
            return float(price_str)
        except (ValueError, TypeError):
            return 0.0 

    def extract_package_size(self, text: str) -> tuple:
        """
        Extract and normalize package size from a string.
        Returns (amount, unit, raw_string).
        Handles patterns like:
        - 2x15, 10x10, 25*4
        - 10'S BLISTER x 10
        - 100 TABLETS (25'S BLISTER *4)
        - 15 ML, 30, 100
        - bottle of 100ml, strip of 10 tablets, pack of 3x10
        - Handles parentheses, mixed delimiters, and flexible unit detection
        """
        if not text or pd.isna(text):
            return (None, None, "")
        raw = str(text).strip()
        normalized = raw.upper().replace("'S", "")
        import re
        # Remove content in parentheses for main extraction, but keep for fallback
        normalized_main = re.sub(r'\([^)]*\)', '', normalized)
        # 1. Multiplicative pattern: 2x15, 10x10, 25*4, 3X10, 3 X 10, etc.
        mult_match = re.findall(r'(\d+)\s*[x\*]\s*(\d+)', normalized_main)
        if mult_match:
            total = 1
            for m in mult_match[0]:
                total *= int(m)
            # Try to find unit after the pattern or in the rest of the string
            unit_match = re.search(r'(TABLET|CAPSULE|ML|BOTTLE|BLISTER|DROP|VIAL|AMPOULE|SYRINGE|SACHET|SUPPOSITORY|PATCH|POWDER|GRANULE|LOZENGE|SPRAY|INHALER|DOSE|PIECE|STRIP|TUBE|BAG|PACK|KIT|CARTRIDGE|PEN|DEVICE|SYRUP|SOLUTION|SUSPENSION|EMULSION|CREAM|OINTMENT|GEL|LOTION|DROPPER)', normalized_main)
            unit = unit_match.group(1) if unit_match else None
            return (total, unit, raw)
        # 2. Patterns like 'bottle of 100ml', 'strip of 10 tablets', 'pack of 3x10'
        flexible_match = re.match(r'(BOTTLE|STRIP|PACK|BOX|TUBE|BAG|KIT|CARTRIDGE|PEN|DEVICE|SACHET|BLISTER|VIAL|AMPOULE|SYRINGE|SUPPOSITORY|PATCH|POWDER|GRANULE|LOZENGE|SPRAY|INHALER|DOSE|PIECE|TABLET|CAPSULE|ML|GEL|CREAM|OINTMENT|LOTION|DROPPER)[\s\-_]*OF[\s\-_]*(\d+(?:\.\d+)?)([A-Z]*)', normalized_main)
        if flexible_match:
            unit = flexible_match.group(1)
            amount = float(flexible_match.group(2))
            subunit = flexible_match.group(3) if flexible_match.group(3) else None
            if subunit:
                unit = f"{unit} {subunit}"
            return (amount, unit, raw)
        # 3. Simple number with unit: 15 ML, 100 TABLETS, etc.
        num_unit_match = re.match(r'(\d+(?:\.\d+)?)\s*(TABLET|CAPSULE|ML|BOTTLE|BLISTER|DROP|VIAL|AMPOULE|SYRINGE|SACHET|SUPPOSITORY|PATCH|POWDER|GRANULE|LOZENGE|SPRAY|INHALER|DOSE|PIECE|STRIP|TUBE|BAG|PACK|KIT|CARTRIDGE|PEN|DEVICE|SYRUP|SOLUTION|SUSPENSION|EMULSION|CREAM|OINTMENT|GEL|LOTION|DROPPER)?', normalized_main)
        if num_unit_match:
            amount = float(num_unit_match.group(1))
            unit = num_unit_match.group(2) if num_unit_match.group(2) else None
            return (amount, unit, raw)
        # 4. Simple number only: 30, 100, etc.
        num_match = re.match(r'^(\d+(?:\.\d+)?)$', normalized_main)
        if num_match:
            amount = float(num_match.group(1))
            return (amount, None, raw)
        # 5. Parentheses: try to extract from inside if main fails
        paren_match = re.search(r'\(([^)]*)\)', normalized)
        if paren_match:
            inside = paren_match.group(1)
            # Try multiplicative inside parentheses
            mult_inside = re.findall(r'(\d+)\s*[x\*]\s*(\d+)', inside)
            if mult_inside:
                total = 1
                for m in mult_inside[0]:
                    total *= int(m)
                unit_match = re.search(r'(TABLET|CAPSULE|ML|BOTTLE|BLISTER|DROP|VIAL|AMPOULE|SYRINGE|SACHET|SUPPOSITORY|PATCH|POWDER|GRANULE|LOZENGE|SPRAY|INHALER|DOSE|PIECE|STRIP|TUBE|BAG|PACK|KIT|CARTRIDGE|PEN|DEVICE|SYRUP|SOLUTION|SUSPENSION|EMULSION|CREAM|OINTMENT|GEL|LOTION|DROPPER)', inside)
                unit = unit_match.group(1) if unit_match else None
                return (total, unit, raw)
        # 6. Fallback: return raw string
        return (None, None, raw) 