#!/usr/bin/env python3
"""
Robust CSV processing with corruption detection and recovery
"""

import pandas as pd
import numpy as np
import csv
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from unicode_logging_fix import create_safe_logger

logger = create_safe_logger(__name__)

@dataclass
class CSVAnalysis:
    """Analysis results for a CSV file"""
    file_size: int
    encoding: str
    delimiter: str
    has_header: bool
    column_count: int
    row_count: int
    likely_delimiters: List[str]
    corruption_indicators: List[str]
    data_types: Dict[str, str]
    sample_rows: List[Dict]

class CSVCorruptionError(Exception):
    """Raised when CSV corruption is detected"""
    pass

class ColumnMappingError(Exception):
    """Raised when column mapping fails"""
    pass

class RobustCSVProcessor:
    """Multi-stage CSV processing with corruption detection and recovery"""
    
    def __init__(self):
        self.corruption_patterns = [
            r'\d+,\d+,\d+',  # Likely shifted data
            r'[^\w\s€$₹£¥₽₱₩]+\d+[^\w\s€$₹£¥₽₱₩]+',  # Mixed symbols and numbers
            r'^\d+$',  # Row starts with number (likely shifted)
        ]
        
    def process_csv(self, file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Main CSV processing method with multiple fallback strategies
        """
        logger.info(f"Starting robust CSV processing for: {file_path}")
        
        # Stage 1: Raw file analysis
        raw_analysis = self.analyze_raw_csv(file_path)
        logger.info(f"CSV Analysis: {raw_analysis}")
        
        # Stage 2: Multiple parsing attempts with different strategies
        parsing_strategies = self.get_parsing_strategies(raw_analysis)
        
        for strategy in parsing_strategies:
            try:
                logger.info(f"Trying strategy: {strategy.__class__.__name__}")
                df = strategy.parse(file_path, raw_analysis)
                
                if df is not None and self.validate_csv_structure(df):
                    logger.info(f"Success with strategy: {strategy.__class__.__name__}")
                    return df, {'strategy': strategy.__class__.__name__, 'analysis': raw_analysis}
                    
            except Exception as e:
                logger.warning(f"Strategy {strategy.__class__.__name__} failed: {str(e)}")
                continue
        
        # Stage 3: Manual column mapping fallback
        logger.warning("All automatic strategies failed, attempting manual recovery")
        return self.manual_column_recovery(file_path, raw_analysis)
    
    def analyze_raw_csv(self, file_path: Path) -> CSVAnalysis:
        """Analyze raw CSV file for corruption indicators"""
        file_size = file_path.stat().st_size
        
        # Try different encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        encoding = 'utf-8'
        
        for enc in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    sample = f.read(1000)  # Read first 1000 chars
                    encoding = enc
                    break
            except UnicodeDecodeError:
                continue
        
        # Detect delimiter
        likely_delimiters = self.detect_delimiter(file_path, encoding)
        
        # Read sample data
        try:
            sample_df = pd.read_csv(file_path, encoding=encoding, nrows=5)
            column_count = len(sample_df.columns)
            row_count = len(sample_df)
            has_header = True
        except Exception:
            # Try without header
            try:
                sample_df = pd.read_csv(file_path, encoding=encoding, nrows=5, header=None)
                column_count = len(sample_df.columns)
                row_count = len(sample_df)
                has_header = False
            except Exception:
                column_count = 0
                row_count = 0
                has_header = False
                sample_df = pd.DataFrame()
        
        # Detect corruption indicators
        corruption_indicators = self.detect_corruption_indicators(file_path, encoding)
        
        # Analyze data types
        data_types = {}
        if not sample_df.empty:
            for col in sample_df.columns:
                data_types[str(col)] = str(sample_df[col].dtype)
        
        # Get sample rows
        sample_rows = []
        if not sample_df.empty:
            for _, row in sample_df.head(3).iterrows():
                sample_rows.append(row.to_dict())
        
        return CSVAnalysis(
            file_size=file_size,
            encoding=encoding,
            delimiter=likely_delimiters[0] if likely_delimiters else ',',
            has_header=has_header,
            column_count=column_count,
            row_count=row_count,
            likely_delimiters=likely_delimiters,
            corruption_indicators=corruption_indicators,
            data_types=data_types,
            sample_rows=sample_rows
        )
    
    def detect_delimiter(self, file_path: Path, encoding: str) -> List[str]:
        """Detect likely CSV delimiter"""
        delimiters = [',', ';', '\t', '|']
        delimiter_counts = {}
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                sample = f.read(1000)
                
            for delim in delimiters:
                count = sample.count(delim)
                delimiter_counts[delim] = count
            
            # Return delimiters sorted by frequency
            return sorted(delimiter_counts.keys(), key=lambda x: delimiter_counts[x], reverse=True)
        except Exception:
            return [',']
    
    def detect_corruption_indicators(self, file_path: Path, encoding: str) -> List[str]:
        """Detect indicators of CSV corruption"""
        indicators = []
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()[:10]  # Check first 10 lines
            
            for i, line in enumerate(lines):
                for pattern in self.corruption_patterns:
                    if re.search(pattern, line):
                        indicators.append(f"Line {i+1}: Pattern '{pattern}' detected")
            
            # Check for consistent column counts
            column_counts = []
            for line in lines:
                if line.strip():
                    column_counts.append(line.count(',') + 1)
            
            if len(set(column_counts)) > 1:
                indicators.append(f"Inconsistent column counts: {set(column_counts)}")
                
        except Exception as e:
            indicators.append(f"Error analyzing file: {str(e)}")
        
        return indicators
    
    def get_parsing_strategies(self, analysis: CSVAnalysis):
        """Get list of parsing strategies to try"""
        strategies = [
            StandardCSVStrategy(),
            DelimiterDetectionStrategy(analysis.likely_delimiters),
        ]
        
        if analysis.corruption_indicators:
            strategies.append(CorruptedColumnStrategy())
        
        strategies.append(ManualMappingStrategy())
        
        return strategies
    
    def validate_csv_structure(self, df: pd.DataFrame) -> bool:
        """Validate that CSV structure is reasonable"""
        if df.empty:
            return False
        
        if len(df.columns) < 3:  # Need at least date, description, amount
            return False
        
        # Check for reasonable data types
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) == 0:
            # Check if any column contains numeric data
            has_numeric = False
            for col in df.columns:
                if df[col].astype(str).str.contains(r'\d+\.?\d*').any():
                    has_numeric = True
                    break
            if not has_numeric:
                return False
        
        return True
    
    def manual_column_recovery(self, file_path: Path, analysis: CSVAnalysis) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Manual recovery when automatic parsing fails"""
        logger.warning(f"Manual recovery for {file_path}")
        
        # Create a minimal recovery
        try:
            df = pd.read_csv(file_path, encoding=analysis.encoding)
            
            # Basic cleanup
            df = df.dropna(how='all')  # Remove completely empty rows
            df.columns = [str(col).strip() for col in df.columns]  # Clean column names
            
            return df, {'strategy': 'manual_recovery', 'analysis': analysis}
            
        except Exception as e:
            logger.error(f"Manual recovery failed: {str(e)}")
            raise CSVCorruptionError(f"Could not recover CSV: {str(e)}")

class StandardCSVStrategy:
    """Standard CSV parsing strategy"""
    
    def parse(self, file_path: Path, analysis: CSVAnalysis) -> Optional[pd.DataFrame]:
        """Parse using standard pandas CSV reading"""
        try:
            df = pd.read_csv(file_path, encoding=analysis.encoding)
            return df
        except Exception:
            return None

class DelimiterDetectionStrategy:
    """Strategy that tries different delimiters"""
    
    def __init__(self, likely_delimiters: List[str]):
        self.likely_delimiters = likely_delimiters
    
    def parse(self, file_path: Path, analysis: CSVAnalysis) -> Optional[pd.DataFrame]:
        """Parse using detected delimiters"""
        for delimiter in self.likely_delimiters:
            try:
                df = pd.read_csv(file_path, encoding=analysis.encoding, delimiter=delimiter)
                if len(df.columns) > 2:  # Reasonable number of columns
                    return df
            except Exception:
                continue
        return None

class CorruptedColumnStrategy:
    """Strategy for handling corrupted column data"""
    
    def parse(self, file_path: Path, analysis: CSVAnalysis) -> Optional[pd.DataFrame]:
        """Parse with corruption handling"""
        try:
            # Try reading without header first
            df = pd.read_csv(file_path, encoding=analysis.encoding, header=None)
            
            # If we have enough columns, try to infer structure
            if len(df.columns) >= 3:
                # Try to detect which row might be the header
                for i in range(min(3, len(df))):
                    row = df.iloc[i]
                    # Check if this row looks like a header
                    if row.astype(str).str.contains(r'[a-zA-Z]').sum() >= 2:
                        # Use this row as header
                        df.columns = row
                        df = df.drop(df.index[i])
                        return df
            
            return df
            
        except Exception:
            return None

class ManualMappingStrategy:
    """Fallback strategy with manual column mapping"""
    
    def parse(self, file_path: Path, analysis: CSVAnalysis) -> Optional[pd.DataFrame]:
        """Parse with manual column detection"""
        try:
            df = pd.read_csv(file_path, encoding=analysis.encoding)
            
            # Basic data cleaning
            df = df.dropna(how='all')
            df.columns = [str(col).strip() for col in df.columns]
            
            return df
            
        except Exception:
            return None
