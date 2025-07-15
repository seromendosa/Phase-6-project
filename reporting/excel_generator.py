"""
Excel report generation for drug matching results
"""
import pandas as pd
import io
from typing import Dict, List
from datetime import datetime
from config import Config

class ExcelReportGenerator:
    """Generate comprehensive Excel reports for drug matching results"""
    
    def __init__(self):
        self.config = Config
    
    def create_report(self, matches: List[Dict], dha_df: pd.DataFrame, doh_df: pd.DataFrame) -> bytes:
        """Create comprehensive Excel report with price analysis"""
        
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter', mode='w') as writer:  # type: ignore
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format(Config.EXCEL_FORMATS['header'])
            confidence_formats = {
                level: workbook.add_format(format_dict)
                for level, format_dict in Config.EXCEL_FORMATS['confidence_colors'].items()
            }
            
            # 1. Matches Sheet
            if matches:
                matches_df = pd.DataFrame(matches)
                matches_df.to_excel(writer, sheet_name='Drug_Matches', index=False)
                
                worksheet = writer.sheets['Drug_Matches']
                
                # Apply header format
                for col_num, value in enumerate(matches_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Apply confidence color coding
                confidence_col = matches_df.columns.get_loc('Confidence_Level')
                for row_num, confidence in enumerate(matches_df['Confidence_Level'], 1):
                    format_to_use = confidence_formats.get(confidence, workbook.add_format({'border': 1}))
                    worksheet.write(row_num, confidence_col, confidence, format_to_use)
                
                # Auto-adjust column widths
                for i, col in enumerate(matches_df.columns):
                    max_len = max(len(str(col)), matches_df[col].astype(str).str.len().max())
                    worksheet.set_column(i, i, min(max_len + 2, 50))
            
            # 2. Summary Sheet
            summary_data = self._create_summary_data(matches, dha_df, doh_df)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format summary sheet
            summary_worksheet = writer.sheets['Summary']
            for col_num, value in enumerate(summary_df.columns.values):
                summary_worksheet.write(0, col_num, value, header_format)
            
            summary_worksheet.set_column(0, 0, 25)
            summary_worksheet.set_column(1, 1, 20)
            
            # 3. Unmatched DHA Drugs
            unmatched_dha = self._get_unmatched_dha(matches, dha_df)
            unmatched_dha.to_excel(writer, sheet_name='Unmatched_DHA', index=False)
            
            # Format unmatched sheet
            unmatched_worksheet = writer.sheets['Unmatched_DHA']
            for col_num, value in enumerate(unmatched_dha.columns.values):
                unmatched_worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            for i, col in enumerate(unmatched_dha.columns):
                if len(unmatched_dha) > 0:
                    try:
                        max_len = max(len(str(col)), unmatched_dha[col].astype(str).str.len().max())
                    except:
                        max_len = len(str(col))
                else:
                    max_len = len(str(col))
                unmatched_worksheet.set_column(i, i, min(max_len + 2, 50))
            
            # 4. Price Analysis Sheet
            if matches:
                price_df = self._create_price_analysis(matches)
                price_df.to_excel(writer, sheet_name='Price_Analysis', index=False)
                
                # Format price analysis sheet
                price_worksheet = writer.sheets['Price_Analysis']
                for col_num, value in enumerate(price_df.columns.values):
                    price_worksheet.write(0, col_num, value, header_format)
                
                # Auto-adjust column widths
                for i, col in enumerate(price_df.columns):
                    if len(price_df) > 0:
                        try:
                            max_len = max(len(str(col)), price_df[col].astype(str).str.len().max())
                        except:
                            max_len = len(str(col))
                    else:
                        max_len = len(str(col))
                    price_worksheet.set_column(i, i, min(max_len + 2, 50))
        
        return buffer.getvalue()
    
    def _create_summary_data(self, matches: List[Dict], dha_df: pd.DataFrame, doh_df: pd.DataFrame) -> Dict:
        """Create summary data for the report"""
        summary_data = {
            'Metric': [
                'Total DHA Drugs',
                'Total DOH Drugs', 
                'Total Matches Found',
                'Match Rate (%)',
                'Very High Confidence',
                'High Confidence',
                'Medium Confidence',
                'Low Confidence',
                'Very Low Confidence',
                'Average Overall Score',
                'Average Brand Similarity',
                'Average Generic Similarity',
                'Average Strength Similarity',
                'Average Dosage Similarity',
                'Average Price Similarity',
                'Average Package Size Similarity',
                'Average Price Difference',
                'Perfect Price Matches',
                'Processing Date'
            ],
            'Value': []
        }
        
        if matches:
            matches_df = pd.DataFrame(matches)
            confidence_counts = matches_df['Confidence_Level'].value_counts()
            
            # Price analysis
            price_diff = abs(matches_df['DHA_Price'] - matches_df['DOH_Price'])
            perfect_price_matches = len(matches_df[matches_df['Price_Similarity'] >= 0.95])
            
            summary_data['Value'] = [
                len(dha_df),
                len(doh_df),
                len(matches),
                f"{len(matches) / len(dha_df) * 100:.1f}%",
                confidence_counts.get('Very High', 0),
                confidence_counts.get('High', 0),
                confidence_counts.get('Medium', 0),
                confidence_counts.get('Low', 0),
                confidence_counts.get('Very Low', 0),
                f"{matches_df['Overall_Score'].mean():.3f}",
                f"{matches_df['Brand_Similarity'].mean():.3f}",
                f"{matches_df['Generic_Similarity'].mean():.3f}",
                f"{matches_df['Strength_Similarity'].mean():.3f}",
                f"{matches_df['Dosage_Similarity'].mean():.3f}",
                f"{matches_df['Price_Similarity'].mean():.3f}",
                f"{matches_df['Package_Size_Similarity'].mean():.3f}",
                f"{price_diff.mean():.2f}",
                perfect_price_matches,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        else:
            summary_data['Value'] = [
                len(dha_df), len(doh_df), 0, '0%', 0, 0, 0, 0, 0,
                'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 0,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        
        return summary_data
    
    def _get_unmatched_dha(self, matches: List[Dict], dha_df: pd.DataFrame) -> pd.DataFrame:
        """Get unmatched DHA drugs"""
        if matches:
            matched_dha_codes = {match['DHA_Code'] for match in matches}
            unmatched_dha = dha_df[~dha_df.iloc[:, 0].astype(str).isin(matched_dha_codes)]
        else:
            unmatched_dha = dha_df
        # Ensure always DataFrame
        if isinstance(unmatched_dha, pd.Series):
            unmatched_dha = unmatched_dha.to_frame().T
        return unmatched_dha
    
    def _create_price_analysis(self, matches: List[Dict]) -> pd.DataFrame:
        """Create price analysis data"""
        from processing.matchers import PriceMatcher
        
        price_analysis_data = []
        price_matcher = PriceMatcher()
        
        for match in matches:
            dha_price = match['DHA_Price']
            doh_price = match['DOH_Price']
            analysis = price_matcher.get_price_analysis(dha_price, doh_price)
            
            price_analysis_data.append({
                'DHA_Code': match['DHA_Code'],
                'DOH_Code': match['DOH_Code'],
                'DHA_Price': dha_price,
                'DOH_Price': doh_price,
                'Price_Difference': analysis['difference'],
                'Percentage_Difference': f"{analysis['percentage_diff']:.1f}%" if analysis['percentage_diff'] != 'N/A' else 'N/A',
                'Price_Ratio': f"{analysis['ratio']:.2f}" if analysis['ratio'] != 'N/A' else 'N/A',
                'Price_Similarity': match['Price_Similarity'],
                'Analysis': analysis['analysis']
            })
        
        return pd.DataFrame(price_analysis_data) 