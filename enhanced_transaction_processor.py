#!/usr/bin/env python3
"""
Enhanced Transaction Processor with Currency Conversion Support
"""

import pandas as pd
import logging
from typing import List, Dict, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedTransactionProcessor:
    """Enhanced transaction processor with currency conversion support"""
    
    def __init__(self, enable_currency_conversion: bool = True, cache=None):
        self.enable_conversion = enable_currency_conversion
        # Import here to avoid circular imports
        from currency_converter import CurrencyConverter
        self.currency_converter = CurrencyConverter(cache) if enable_currency_conversion else None
        from budget_analyzer import BudgetAnalyzer
        self.budget_analyzer = BudgetAnalyzer()
    
    def normalize_and_convert_csv(self, file_path: Union[str, Path], 
                                target_currency: str = 'USD',
                                encoding: Optional[str] = None) -> Dict:
        """Normalize CSV data and convert to target currency"""
        logger.info(f"Converting CSV with normalization to {target_currency}: {file_path}")
        
        try:
            # Read CSV
            if encoding:
                df = pd.read_csv(file_path, encoding=encoding)
            else:
                encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
                df = None
                for enc in encodings_to_try:
                    try:
                        df = pd.read_csv(file_path, encoding=enc)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    raise ValueError("Could not read CSV file with any supported encoding")
            
            # Normalize data
            normalized_df = self._normalize_dataframe(df)
            
            # Convert to target currency
            if self.enable_conversion and self.currency_converter:
                converted_df = self.currency_converter.convert_dataframe(
                    normalized_df, target_currency
                )
            else:
                converted_df = normalized_df
            
            # Save converted CSV
            converted_file_path = self._save_converted_csv(converted_df, file_path, target_currency)
            
            # Convert to transactions list
            transactions_list = self._dataframe_to_transactions(converted_df, target_currency)
            
            # Generate analysis
            budget_recommendations = self.budget_analyzer.generate_recommendations(
                transactions_list, target_currency
            )
            
            spending_analysis = self.budget_analyzer.analyze_spending(transactions_list)
            
            result = {
                'original_df': df,
                'converted_df': converted_df,
                'converted_transactions': transactions_list,
                'converted_file_path': str(converted_file_path),
                'target_currency': target_currency,
                'budget_recommendations': budget_recommendations,
                'spending_analysis': spending_analysis,
                'total_transactions': len(transactions_list),
                'conversion_summary': self.currency_converter.get_conversion_summary(
                    transactions_list, target_currency
                ) if self.enable_conversion else {}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in CSV conversion pipeline: {e}")
            raise
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame (lowercase columns, parse dates, coerce amounts)"""
        if df.empty:
            return df
        
        normalized_df = df.copy()
        
        # Lowercase column names
        normalized_df.columns = [col.lower().strip() for col in normalized_df.columns]
        
        # Parse dates
        date_columns = ['date', 'transaction_date', 'posted_date', 'post_date', 'trans_date']
        for col in date_columns:
            if col in normalized_df.columns:
                try:
                    normalized_df[col] = pd.to_datetime(normalized_df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Failed to parse date column {col}: {e}")
        
        # Coerce amounts to numeric
        amount_columns = ['amount', 'debit', 'credit', 'transaction_amount', 'sum', 'total', 'value']
        for col in amount_columns:
            if col in normalized_df.columns:
                try:
                    normalized_df[col] = pd.to_numeric(normalized_df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Failed to coerce amount column {col}: {e}")
        
        # Handle Type column to set signs for income vs expense
        if 'type' in normalized_df.columns:
            mask = normalized_df['type'].str.lower().isin(['debit', 'expense', 'withdrawal', 'payment'])
            if 'amount' in normalized_df.columns:
                normalized_df.loc[mask, 'amount'] = -abs(normalized_df.loc[mask, 'amount'])
        
        return normalized_df
    
    def _dataframe_to_transactions(self, df: pd.DataFrame, target_currency: str) -> List[Dict]:
        """Convert DataFrame to transactions list format"""
        transactions_list = []
        
        for _, row in df.iterrows():
            transaction = {
                'date': str(row.get('date', '')),
                'description': str(row.get('description', '')),
                'amount': float(row.get('amount', 0)),
                'currency': str(row.get('display_currency', target_currency)),
                'category': str(row.get('category', 'other')),
                'type': str(row.get('type', 'expense')),
                'confidence_score': float(row.get('confidence_score', 0.0))
            }
            
            # Add conversion info if available
            if 'original_amount' in row and 'original_currency' in row:
                transaction['original_amount'] = float(row['original_amount'])
                transaction['original_currency'] = str(row['original_currency'])
                transaction['conversion_rate'] = float(row.get('conversion_rate', 1.0))
            
            transactions_list.append(transaction)
        
        return transactions_list
    
    def _save_converted_csv(self, df: pd.DataFrame, original_file_path: Union[str, Path], 
                          target_currency: str) -> Path:
        """Save converted DataFrame to CSV"""
        original_path = Path(original_file_path)
        converted_filename = f"{original_path.stem}_converted_to_{target_currency}.csv"
        converted_path = original_path.parent / converted_filename
        
        df.to_csv(converted_path, index=False, encoding='utf-8')
        logger.info(f"Saved converted CSV to: {converted_path}")
        
        return converted_path