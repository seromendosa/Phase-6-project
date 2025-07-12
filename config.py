"""
Configuration settings for the Drug Matching System
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'mohamedelkhatieb')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'samsunG@')
    
    # Application Settings
    APP_TITLE = "Drug Matching System"
    APP_ICON = "💊"
    PAGE_LAYOUT = "wide"
    
    # Default Matching Parameters
    DEFAULT_THRESHOLD = 0.7
    DEFAULT_WEIGHTS = {
        'brand': 0.20,
        'generic': 0.30,
        'strength': 0.20,
        'dosage': 0.15,
        'price': 0.15
    }
    
    # Price Matching Settings
    DEFAULT_PRICE_TOLERANCE = 20.0
    DEFAULT_MAX_PRICE_RATIO = 5.0
    
    # File Upload Settings
    ALLOWED_FILE_TYPES = ['xlsx', 'xls']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Database Table Configuration
    TABLE_NAME = 'drug_matches'
    
    # Medical Abbreviations
    MEDICAL_ABBREVIATIONS = {
        'MG': 'MILLIGRAM', 'MCG': 'MICROGRAM', 'G': 'GRAM',
        'ML': 'MILLILITER', 'L': 'LITER', 'IU': 'INTERNATIONAL_UNIT',
        'TAB': 'TABLET', 'TABS': 'TABLETS', 'CAP': 'CAPSULE', 
        'CAPS': 'CAPSULES', 'INJ': 'INJECTION', 'SYR': 'SYRUP',
        'SUSP': 'SUSPENSION', 'SOL': 'SOLUTION', 'CR': 'CREAM',
        'OINT': 'OINTMENT', 'DROPS': 'DROPS', 'SPRAY': 'SPRAY',
        'PATCH': 'PATCH', 'GEL': 'GEL', 'LOTION': 'LOTION'
    }
    
    # Dosage Forms
    DOSAGE_FORMS = {
        'TABLET', 'TABLETS', 'CAPSULE', 'CAPSULES', 'INJECTION',
        'SYRUP', 'SUSPENSION', 'SOLUTION', 'CREAM', 'OINTMENT',
        'DROPS', 'SPRAY', 'PATCH', 'GEL', 'LOTION', 'POWDER'
    }
    
    # Confidence Level Thresholds
    CONFIDENCE_THRESHOLDS = {
        'Very High': 0.95,
        'High': 0.85,
        'Medium': 0.75,
        'Low': 0.65,
        'Very Low': 0.0
    }
    
    # Excel Report Settings
    EXCEL_FORMATS = {
        'header': {
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        },
        'confidence_colors': {
            'Very High': {'fg_color': '#C6EFCE', 'border': 1},
            'High': {'fg_color': '#D4E6F1', 'border': 1},
            'Medium': {'fg_color': '#FCF3CF', 'border': 1},
            'Low': {'fg_color': '#FADBD8', 'border': 1},
            'Very Low': {'fg_color': '#EBDEF0', 'border': 1}
        }
    }
    
    @classmethod
    def get_database_url(cls) -> str:
        """Generate database URL from configuration"""
        from urllib.parse import quote_plus
        encoded_password = quote_plus(cls.DB_PASSWORD)
        return f"postgresql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Check database configuration
        if not cls.DB_HOST:
            issues.append("DB_HOST not set")
        if not cls.DB_NAME:
            issues.append("DB_NAME not set")
        if not cls.DB_USER:
            issues.append("DB_USER not set")
        
        # Check weight configuration
        total_weight = sum(cls.DEFAULT_WEIGHTS.values())
        if abs(total_weight - 1.0) > 0.01:
            issues.append(f"Weights don't sum to 1.0 (current: {total_weight})")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        } 