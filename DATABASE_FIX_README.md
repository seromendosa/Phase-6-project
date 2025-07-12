# Database Schema Fix for Drug Matching Application

## Problem
The error `column "dha_price" of relation "drug_matches" does not exist` occurs because the database table was created before the price columns were added to the application.

## Solution

### Option 1: Automatic Fix (Recommended)
The application now includes automatic database schema migration. When you connect to the database, it will automatically:

1. Check for missing price columns
2. Add them if they don't exist
3. Show success messages for each column added

### Option 2: Manual SQL Fix
If the automatic fix doesn't work, you can run these SQL commands directly in your PostgreSQL client:

```sql
-- Add missing price columns
ALTER TABLE drug_matches ADD COLUMN IF NOT EXISTS dha_price FLOAT DEFAULT 0.0;
ALTER TABLE drug_matches ADD COLUMN IF NOT EXISTS doh_price FLOAT DEFAULT 0.0;
ALTER TABLE drug_matches ADD COLUMN IF NOT EXISTS price_similarity FLOAT DEFAULT 0.0;
```

### Option 3: Recreate Table
If you want to start fresh, you can use the "Recreate Table" option in the Database Management section of the application. This will:

1. Drop the existing table
2. Recreate it with the current schema including all price columns
3. **Warning**: This will delete all existing data

## Required Price Columns

The application now expects these price-related columns in the `drug_matches` table:

- `dha_price` (FLOAT) - Price from DHA dataset
- `doh_price` (FLOAT) - Price from DOH dataset  
- `price_similarity` (FLOAT) - Calculated price similarity score

## Testing the Fix

1. Connect to your database in the application
2. Check the "Database Management" section in the sidebar
3. Use "Show Table Structure" to verify all columns exist
4. If columns are missing, use "Recreate Table" or run the manual SQL commands

## Expected Table Structure

After the fix, your `drug_matches` table should have these columns:

```
id (INTEGER, PRIMARY KEY)
dha_code (VARCHAR)
doh_code (VARCHAR)
dha_brand_name (VARCHAR)
doh_brand_name (VARCHAR)
dha_generic_name (VARCHAR)
doh_generic_name (VARCHAR)
dha_strength (VARCHAR)
doh_strength (VARCHAR)
dha_dosage_form (VARCHAR)
doh_dosage_form (VARCHAR)
dha_price (FLOAT)           ← NEW
doh_price (FLOAT)           ← NEW
brand_similarity (FLOAT)
generic_similarity (FLOAT)
strength_similarity (FLOAT)
dosage_similarity (FLOAT)
price_similarity (FLOAT)    ← NEW
overall_score (FLOAT)
confidence_level (VARCHAR)
fuzzy_score (FLOAT)
vector_score (FLOAT)
semantic_score (FLOAT)
matching_method (VARCHAR)
matched_at (TIMESTAMP)
```

## Troubleshooting

### If automatic fix fails:
1. Check database permissions - your user needs ALTER TABLE privileges
2. Ensure the table exists before trying to add columns
3. Try the manual SQL commands
4. Use the "Recreate Table" option as a last resort

### If you get permission errors:
```sql
-- Grant necessary permissions (run as database owner)
GRANT ALL PRIVILEGES ON TABLE drug_matches TO your_username;
GRANT USAGE ON SCHEMA public TO your_username;
```

### If the table doesn't exist:
The application will create it automatically when you first connect, but if you need to create it manually:

```sql
-- Create the table with all required columns
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

## Success Indicators

After applying the fix, you should see:
- ✅ Success messages when connecting to the database
- ✅ No more "column does not exist" errors
- ✅ Successful saving of matches to the database
- ✅ Price data included in all reports and exports 