#!/usr/bin/env python3
"""
Data sanitization layer for cleaning CSV data
"""

import pandas as pd
import numpy as np
import re
import unicodedata
from typing import Dict, List, Any, Optional
from unicode_logging_fix import create_safe_logger

logger = create_safe_logger(__name__)

class DataSanitizer:
    """Sanitizes and cleans CSV data before processing"""
    
    def __init__(self):
        self.currency_symbols = {
            '€', '$', '₹', '£', '¥', '₽', '₱', '₩', '฿', '₿',
            'C$', 'A$', 'R$', 'RM', 'S$', 'HK$', 'NZ$'
        }
        
    def sanitize_csv_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main sanitization method that applies all cleaning steps
        """
        logger.info(f"Starting data sanitization for {len(df)} rows, {len(df.columns)} columns")
        
        original_df = df.copy()
        
        try:
            # Step 1: Fix shifted columns
            df = self.fix_shifted_columns(df)
            
            # Step 2: Merge split currency columns
            df = self.merge_split_currency_columns(df)
            
            # Step 3: Normalize Unicode symbols
            df = self.normalize_unicode_symbols(df)
            
            # Step 4: Clean whitespace and quotes
            df = self.clean_whitespace_and_quotes(df)
            
            # Step 5: Fix common CSV export artifacts
            df = self.fix_csv_artifacts(df)
            
            # Step 6: Validate and report changes
            changes = self.validate_sanitization(original_df, df)
            logger.info(f"Sanitization completed. Changes: {changes}")
            
            return df
            
        except Exception as e:
            logger.error(f"Data sanitization failed: {str(e)}")
            return original_df  # Return original data if sanitization fails
    
    def fix_shifted_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and fix shifted column data"""
        if len(df.columns) < 3:
            return df
        
        # Look for patterns that indicate column shifting
        shifted_rows = []
        
        for idx, row in df.iterrows():
            if self.detect_shifted_row(row):
                shifted_rows.append(idx)
        
        if shifted_rows:
            logger.info(f"Detected {len(shifted_rows)} shifted rows")
            
            # Try to realign shifted data
            for idx in shifted_rows:
                df.loc[idx] = self.realign_row(df.loc[idx])
        
        return df
    
    def detect_shifted_row(self, row) -> bool:
        """Detect if a row has shifted column data"""
        # Check if first column looks like a date but other columns don't match expected types
        first_col = str(row.iloc[0])
        
        # If first column looks like a description or amount, it might be shifted
        if (re.search(r'[a-zA-Z]{3,}', first_col) or 
            re.search(r'[€$₹£¥₽₱₩]', first_col)):
            return True
        
        return False
    
    def realign_row(self, row) -> pd.Series:
        """Attempt to realign a shifted row"""
        # This is a simplified realignment - in practice, you'd need more sophisticated logic
        # based on the specific corruption patterns observed
        
        # For now, just return the row as-is
        # In a production system, you'd implement pattern-based realignment
        return row
    
    def merge_split_currency_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merge currency amounts that are split across multiple columns"""
        
        # Look for columns that might contain split currency amounts
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Check if we can merge the last two numeric columns
            last_two_cols = numeric_cols[-2:]
            
            # Check if these columns look like split currency (e.g., 89 and 99 -> 89.99)
            sample_values = df[last_two_cols].head(10)
            
            # If the second column has values mostly between 0-99, it might be decimal parts
            second_col_values = sample_values.iloc[:, 1]
            if second_col_values.max() <= 99 and second_col_values.min() >= 0:
                # Merge the columns
                new_amount = (df[last_two_cols[0]].astype(str) + '.' + 
                            df[last_two_cols[1]].astype(str).str.zfill(2))
                
                # Replace the first column with merged amount
                df[last_two_cols[0]] = new_amount
                
                # Drop the second column
                df = df.drop(columns=[last_two_cols[1]])
                
                logger.info(f"Merged split currency columns: {last_two_cols[0]} + {last_two_cols[1]}")
        
        return df
    
    def normalize_unicode_symbols(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Unicode currency symbols"""
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Normalize Unicode characters
                df[col] = df[col].astype(str).apply(self.normalize_unicode_string)
        
        return df
    
    def normalize_unicode_string(self, text: str) -> str:
        """Normalize a single Unicode string"""
        if pd.isna(text) or text == 'nan':
            return text
        
        try:
            # Normalize Unicode characters
            normalized = unicodedata.normalize('NFKC', text)
            
            # Replace common problematic characters
            replacements = {
                '€': '€',  # Ensure Euro symbol is correct
                '₹': '₹',  # Ensure Rupee symbol is correct
                '£': '£',  # Ensure Pound symbol is correct
                '¥': '¥',  # Ensure Yen symbol is correct
            }
            
            for old, new in replacements.items():
                normalized = normalized.replace(old, new)
            
            return normalized
            
        except Exception:
            return text
    
    def clean_whitespace_and_quotes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean whitespace and quote artifacts"""
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Strip whitespace
                df[col] = df[col].astype(str).str.strip()
                
                # Remove extra quotes
                df[col] = df[col].str.replace(r'^["\']|["\']$', '', regex=True)
                
                # Clean up multiple spaces
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
                
                # Handle empty strings
                df[col] = df[col].replace('', np.nan)
        
        return df
    
    def fix_csv_artifacts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix common CSV export artifacts"""
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove rows that are just separators or headers
        for idx, row in df.iterrows():
            row_str = ' '.join(str(val) for val in row.values if pd.notna(val))
            
            # Skip rows that look like separators or headers
            if (re.match(r'^[-=_]+$', row_str) or 
                re.match(r'^(date|description|amount|type|category)', row_str, re.IGNORECASE)):
                df = df.drop(idx)
        
        # Reset index after dropping rows
        df = df.reset_index(drop=True)
        
        return df
    
    def validate_sanitization(self, original_df: pd.DataFrame, sanitized_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate sanitization and report changes"""
        
        changes = {
            'rows_removed': len(original_df) - len(sanitized_df),
            'columns_changed': len(original_df.columns) - len(sanitized_df.columns),
            'empty_cells_before': original_df.isnull().sum().sum(),
            'empty_cells_after': sanitized_df.isnull().sum().sum(),
        }
        
        return changes

class ColumnDetector:
    """Detects and maps columns intelligently"""
    
    def __init__(self):
        self.column_patterns = {
            'date': [
                r'date', r'transaction_date', r'posted_date', r'post_date', 
                r'trans_date', r'effective_date', r'settlement_date'
            ],
            'description': [
                r'description', r'merchant', r'payee', r'transaction_description', 
                r'details', r'memo', r'note', r'payee_name', r'narrative', r'reference'
            ],
            'amount': [
                r'amount', r'debit', r'credit', r'transaction_amount', 
                r'sum', r'total', r'value', r'balance', r'transaction_value'
            ],
            'type': [
                r'type', r'transaction_type', r'trans_type', r'debit_credit', 
                r'dr_cr', r'direction'
            ],
            'currency': [
                r'currency', r'curr', r'ccy'
            ]
        }
    
    def detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detect column mapping for a DataFrame"""
        detected = {}
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            for field_type, patterns in self.column_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, col_lower):
                        detected[field_type] = col
                        break
                if field_type in detected:
                    break
        
        return detected
    
    def fuzzy_column_matching(self, df: pd.DataFrame) -> Dict[str, str]:
        """Use fuzzy matching to detect columns by content"""
        detected = {}
        
        # Analyze each column's content
        for col in df.columns:
            sample_values = df[col].dropna().head(10).astype(str)
            
            # Check for date patterns
            if self.is_date_column(sample_values):
                detected['date'] = col
                continue
            
            # Check for amount patterns
            if self.is_amount_column(sample_values):
                detected['amount'] = col
                continue
            
            # Check for description patterns
            if self.is_description_column(sample_values):
                detected['description'] = col
                continue
        
        return detected
    
    def is_date_column(self, values: pd.Series) -> bool:
        """Check if column contains dates"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            if values.str.contains(pattern).sum() >= len(values) * 0.7:  # 70% match
                return True
        
        return False
    
    def is_amount_column(self, values: pd.Series) -> bool:
        """Check if column contains amounts"""
        amount_patterns = [
            r'[€$₹£¥₽₱₩]\d+',  # Currency symbols
            r'\d+\.\d{2}',      # Decimal amounts
            r'\d+,\d{2}',       # European decimal format
        ]
        
        for pattern in amount_patterns:
            if values.str.contains(pattern).sum() >= len(values) * 0.5:  # 50% match
                return True
        
        return False
    
    def is_description_column(self, values: pd.Series) -> bool:
        """Check if column contains descriptions"""
        # Descriptions typically contain letters and are longer
        if values.str.len().mean() > 5 and values.str.contains(r'[a-zA-Z]').sum() >= len(values) * 0.8:
            return True
        
        return False
