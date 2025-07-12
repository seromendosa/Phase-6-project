# Drug Matching System

A production-ready drug matching application that compares DHA and DOH drug datasets with advanced price analysis capabilities.

## 🏗️ Project Structure

```
drug-matching-system/
├── app.py                      # Main application entry point
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── env_example.txt            # Environment variables template
├── README.md                  # This file
├── DATABASE_FIX_README.md     # Database troubleshooting guide
├── models/                    # Database models
│   ├── __init__.py
│   └── database.py
├── database/                  # Database management
│   ├── __init__.py
│   └── manager.py
├── processing/                # Data processing modules
│   ├── __init__.py
│   ├── text_processor.py
│   └── matchers.py
├── reporting/                 # Report generation
│   ├── __init__.py
│   └── excel_generator.py
└── ui/                       # User interface components
    ├── __init__.py
    └── components.py
```

## 🚀 Features

### Core Functionality
- **Multi-attribute Drug Matching**: Compare drugs by brand name, generic name, strength, dosage form, and price
- **Advanced Price Analysis**: Sophisticated price similarity algorithms with configurable tolerance
- **Hybrid Matching Algorithms**: Combines fuzzy string matching, TF-IDF vectorization, and semantic analysis
- **Real-time Database Integration**: Live saving to PostgreSQL with automatic schema migration
- **Comprehensive Reporting**: Excel reports with multiple sheets and visualizations

### Technical Features
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Configuration Management**: Centralized configuration with environment variable support
- **Error Handling**: Robust error handling with user-friendly messages
- **Database Schema Migration**: Automatic handling of database schema updates
- **Performance Optimization**: Efficient algorithms for large dataset processing

## 📋 Requirements

### System Requirements
- Python 3.8+
- PostgreSQL 12+
- 4GB+ RAM (for large datasets)

### Python Dependencies
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.21.0
scikit-learn>=1.3.0
plotly>=5.15.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
xlsxwriter>=3.1.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd drug-matching-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
1. Install PostgreSQL
2. Create a database
3. Copy `env_example.txt` to `.env` and update database credentials

### 5. Run the Application
```bash
streamlit run app.py
```

## 📊 Data Format

### Expected Excel File Structure
Both DHA and DOH files should have 6 columns in this order:

1. **Drug Code** - Unique identifier
2. **Brand Name** - Commercial name
3. **Generic Name** - Active ingredient name
4. **Strength** - Dosage strength (e.g., "500mg")
5. **Dosage Form** - Form of medication (e.g., "TABLET")
6. **Price** - Cost in numeric format

### Example Data
```
Code    | Brand Name    | Generic Name | Strength | Dosage Form | Price
--------|---------------|--------------|----------|-------------|-------
DHA001  | Panadol       | Paracetamol  | 500mg    | TABLET      | 15.50
DHA002  | Augmentin     | Amoxicillin  | 625mg    | TABLET      | 45.00
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file based on `env_example.txt`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password

# Application Settings
APP_TITLE=Drug Matching System
APP_ICON=💊
PAGE_LAYOUT=wide

# Matching Parameters
DEFAULT_THRESHOLD=0.7
DEFAULT_PRICE_TOLERANCE=20.0
DEFAULT_MAX_PRICE_RATIO=5.0
```

### Matching Parameters
- **Threshold**: Minimum similarity score for a match (0.5-1.0)
- **Weights**: Relative importance of each attribute
- **Price Tolerance**: Percentage difference for perfect price matches
- **Max Price Ratio**: Maximum price ratio for any similarity

## 🔧 Usage

### 1. Database Connection
1. Open the application
2. Go to "Database Settings" in the sidebar
3. Enter your PostgreSQL credentials
4. Click "Connect to Database"

### 2. Data Upload
1. Navigate to "Data Upload" tab
2. Upload DHA Excel file
3. Upload DOH Excel file
4. Verify data preview

### 3. Matching Process
1. Go to "Matching Process" tab
2. Adjust matching parameters if needed
3. Click "Start Matching Process"
4. Monitor progress and results

### 4. Results & Download
1. View results in "Results & Download" tab
2. Filter results by confidence level and scores
3. Download results as CSV or comprehensive Excel report

## 📈 Matching Algorithms

### Generic Name Matching
- **Fuzzy String Matching (40%)**: Handles typos and minor variations
- **TF-IDF Vectorization (35%)**: Semantic similarity using word frequencies
- **Semantic Pattern Matching (25%)**: Active ingredient focus

### Price Matching
- **Tolerance-based**: Perfect matches within specified percentage
- **Ratio-based**: Linear decay based on price ratios
- **Configurable thresholds**: Adjustable tolerance and maximum ratios

### Overall Scoring
Weighted combination of all similarity scores:
```
Overall Score = (Brand × 0.20) + (Generic × 0.30) + (Strength × 0.20) + (Dosage × 0.15) + (Price × 0.15)
```

## 📊 Reports

### Excel Report Contents
1. **Drug_Matches**: All matching results with color-coded confidence
2. **Summary**: Key statistics and metrics
3. **Unmatched_DHA**: Drugs that couldn't be matched
4. **Price_Analysis**: Detailed price comparison and analysis

### Features
- Color-coded confidence levels
- Auto-adjusted column widths
- Formatted headers
- Price difference calculations
- Ready for further analysis

## 🗄️ Database Schema

### drug_matches Table
```sql
CREATE TABLE drug_matches (
    id SERIAL PRIMARY KEY,
    dha_code VARCHAR,
    doh_code VARCHAR,
    dha_brand_name VARCHAR,
    doh_brand_name VARCHAR,
    dha_generic_name VARCHAR,
    doh_generic_name VARCHAR,
    dha_strength VARCHAR,
    doh_strength VARCHAR,
    dha_dosage_form VARCHAR,
    doh_dosage_form VARCHAR,
    dha_price FLOAT DEFAULT 0.0,
    doh_price FLOAT DEFAULT 0.0,
    brand_similarity FLOAT,
    generic_similarity FLOAT,
    strength_similarity FLOAT,
    dosage_similarity FLOAT,
    price_similarity FLOAT DEFAULT 0.0,
    overall_score FLOAT,
    confidence_level VARCHAR,
    fuzzy_score FLOAT,
    vector_score FLOAT,
    semantic_score FLOAT,
    matching_method VARCHAR,
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Errors
- Ensure PostgreSQL is running
- Verify database credentials
- Check if database exists
- Install `psycopg2-binary` if needed

#### Missing Price Columns Error
See `DATABASE_FIX_README.md` for detailed instructions on fixing database schema issues.

#### Performance Issues
- Reduce dataset size for testing
- Adjust matching threshold
- Use database connection for large datasets

### Getting Help
1. Check the database fix guide: `DATABASE_FIX_README.md`
2. Review error messages in the application
3. Verify data format matches expected structure
4. Check database permissions

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies
4. Run with process manager (e.g., systemd, supervisor)
5. Set up reverse proxy (nginx) if needed

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the database fix guide
3. Open an issue on GitHub
4. Contact the development team

---

**Note**: This application is designed for pharmaceutical data analysis and should be used in compliance with relevant data protection regulations. 