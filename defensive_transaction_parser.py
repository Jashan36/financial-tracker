#!/usr/bin/env python3
"""
Defensive transaction parsing with multiple strategies and fallbacks
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from unicode_logging_fix import create_safe_logger

logger = create_safe_logger(__name__)

@dataclass
class ParsingResult:
    """Result of transaction parsing attempt"""
    success: bool
    transaction: Optional[Dict[str, Any]]
    strategy_used: str
    confidence: float
    error_message: Optional[str] = None

class DefensiveTransactionParser:
    """Defensive transaction parser with multiple strategies"""
    
    def __init__(self):
        self.currency_symbols = {
            '€': 'EUR', '$': 'USD', '₹': 'INR', '£': 'GBP', '¥': 'JPY',
            '₽': 'RUB', '₱': 'PHP', '₩': 'KRW', '฿': 'THB', '₿': 'BTC',
            'C$': 'CAD', 'A$': 'AUD', 'R$': 'BRL', 'RM': 'MYR', 'S$': 'SGD',
            'HK$': 'HKD', 'NZ$': 'NZD', 'Rp': 'IDR'
        }
        
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'
        ]
    
    def parse_transaction_row(self, row, index=None) -> ParsingResult:
        """
        Main parsing method that tries multiple strategies
        """
        if index is not None:
            logger.debug(f"Parsing row {index}")
        
        # Try multiple parsing strategies
        strategies = [
            ('standard_parsing', self.standard_parsing),
            ('fuzzy_column_matching', self.fuzzy_column_matching),
            ('pattern_based_extraction', self.pattern_based_extraction),
            ('manual_field_detection', self.manual_field_detection),
            ('emergency_fallback', self.emergency_fallback)
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                result = strategy_func(row, index)
                if result.success:
                    logger.debug(f"Success with strategy: {strategy_name}")
                    return result
                else:
                    logger.debug(f"Strategy {strategy_name} failed: {result.error_message}")
            except Exception as e:
                logger.debug(f"Strategy {strategy_name} error: {str(e)}")
                continue
        
        # If all strategies fail
        return ParsingResult(
            success=False,
            transaction=None,
            strategy_used='all_failed',
            confidence=0.0,
            error_message="All parsing strategies failed"
        )
    
    def standard_parsing(self, row, index=None) -> ParsingResult:
        """Standard parsing with expected column structure"""
        try:
            # Convert to dict if needed
            if hasattr(row, 'to_dict'):
                row_data = row.to_dict()
            else:
                row_data = dict(row)
            
            # Normalize column names
            normalized_data = {}
            for key, value in row_data.items():
                normalized_data[str(key).lower().strip()] = value
            
            # Extract required fields
            date_str = normalized_data.get('date', '')
            description = normalized_data.get('description', '')
            amount_str = str(normalized_data.get('amount', ''))
            trans_type = normalized_data.get('type', 'Debit')
            category = normalized_data.get('category', 'Other')
            
            # Validate required fields
            if not date_str or not description or not amount_str:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='standard_parsing',
                    confidence=0.0,
                    error_message="Missing required fields"
                )
            
            # Parse date
            date_obj = self.parse_date(date_str)
            if not date_obj:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='standard_parsing',
                    confidence=0.0,
                    error_message=f"Could not parse date: {date_str}"
                )
            
            # Parse amount and currency
            amount_result = self.parse_amount_with_currency(amount_str)
            if not amount_result['success']:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='standard_parsing',
                    confidence=0.0,
                    error_message=f"Could not parse amount: {amount_str}"
                )
            
            # Create transaction
            transaction = {
                'date': date_obj.strftime('%Y-%m-%d'),
                'description': str(description).strip(),
                'amount': amount_result['amount'],
                'currency': amount_result['currency'],
                'type': 'debit' if str(trans_type).lower() in ['debit', 'expense', 'withdrawal'] else 'credit',
                'category': str(category).strip().lower(),
                'confidence_score': 0.9
            }
            
            return ParsingResult(
                success=True,
                transaction=transaction,
                strategy_used='standard_parsing',
                confidence=0.9
            )
            
        except Exception as e:
            return ParsingResult(
                success=False,
                transaction=None,
                strategy_used='standard_parsing',
                confidence=0.0,
                error_message=str(e)
            )
    
    def fuzzy_column_matching(self, row, index=None) -> ParsingResult:
        """Fuzzy column matching by content analysis"""
        try:
            row_data = dict(row) if hasattr(row, 'to_dict') else dict(row)
            
            # Analyze each column's content to identify fields
            detected_fields = {}
            
            for col, value in row_data.items():
                value_str = str(value).strip()
                
                # Detect date field
                if self.looks_like_date(value_str) and 'date' not in detected_fields:
                    detected_fields['date'] = value_str
                
                # Detect amount field
                elif self.looks_like_amount(value_str) and 'amount' not in detected_fields:
                    detected_fields['amount'] = value_str
                
                # Detect description field
                elif self.looks_like_description(value_str) and 'description' not in detected_fields:
                    detected_fields['description'] = value_str
            
            # Check if we found required fields
            if len(detected_fields) < 3:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='fuzzy_column_matching',
                    confidence=0.0,
                    error_message="Could not identify required fields"
                )
            
            # Parse the detected fields
            date_obj = self.parse_date(detected_fields['date'])
            if not date_obj:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='fuzzy_column_matching',
                    confidence=0.0,
                    error_message="Could not parse detected date"
                )
            
            amount_result = self.parse_amount_with_currency(detected_fields['amount'])
            if not amount_result['success']:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='fuzzy_column_matching',
                    confidence=0.0,
                    error_message="Could not parse detected amount"
                )
            
            transaction = {
                'date': date_obj.strftime('%Y-%m-%d'),
                'description': detected_fields['description'],
                'amount': amount_result['amount'],
                'currency': amount_result['currency'],
                'type': 'debit' if amount_result['amount'] < 0 else 'credit',
                'category': 'other',
                'confidence_score': 0.7
            }
            
            return ParsingResult(
                success=True,
                transaction=transaction,
                strategy_used='fuzzy_column_matching',
                confidence=0.7
            )
            
        except Exception as e:
            return ParsingResult(
                success=False,
                transaction=None,
                strategy_used='fuzzy_column_matching',
                confidence=0.0,
                error_message=str(e)
            )
    
    def pattern_based_extraction(self, row, index=None) -> ParsingResult:
        """Extract transaction data using regex patterns"""
        try:
            # Convert row to string and look for patterns
            row_str = ' '.join(str(val) for val in row.values if pd.notna(val))
            
            # Extract date pattern
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})', row_str)
            if not date_match:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='pattern_based_extraction',
                    confidence=0.0,
                    error_message="No date pattern found"
                )
            
            date_str = date_match.group(1)
            date_obj = self.parse_date(date_str)
            if not date_obj:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='pattern_based_extraction',
                    confidence=0.0,
                    error_message="Could not parse extracted date"
                )
            
            # Extract amount pattern
            amount_match = re.search(r'([€$₹£¥₽₱₩]?\d+[.,]\d{2})', row_str)
            if not amount_match:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='pattern_based_extraction',
                    confidence=0.0,
                    error_message="No amount pattern found"
                )
            
            amount_str = amount_match.group(1)
            amount_result = self.parse_amount_with_currency(amount_str)
            if not amount_result['success']:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='pattern_based_extraction',
                    confidence=0.0,
                    error_message="Could not parse extracted amount"
                )
            
            # Extract description (everything that's not date or amount)
            description = row_str
            description = re.sub(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}', '', description)
            description = re.sub(r'[€$₹£¥₽₱₩]?\d+[.,]\d{2}', '', description)
            description = description.strip()
            
            if not description:
                description = "Unknown transaction"
            
            transaction = {
                'date': date_obj.strftime('%Y-%m-%d'),
                'description': description,
                'amount': amount_result['amount'],
                'currency': amount_result['currency'],
                'type': 'debit' if amount_result['amount'] < 0 else 'credit',
                'category': 'other',
                'confidence_score': 0.6
            }
            
            return ParsingResult(
                success=True,
                transaction=transaction,
                strategy_used='pattern_based_extraction',
                confidence=0.6
            )
            
        except Exception as e:
            return ParsingResult(
                success=False,
                transaction=None,
                strategy_used='pattern_based_extraction',
                confidence=0.0,
                error_message=str(e)
            )
    
    def manual_field_detection(self, row, index=None) -> ParsingResult:
        """Manual field detection based on data types and content"""
        try:
            row_data = dict(row) if hasattr(row, 'to_dict') else dict(row)
            
            # Sort columns by likelihood of containing specific data types
            date_candidates = []
            amount_candidates = []
            description_candidates = []
            
            for col, value in row_data.items():
                value_str = str(value).strip()
                
                if self.looks_like_date(value_str):
                    date_candidates.append((col, value_str))
                elif self.looks_like_amount(value_str):
                    amount_candidates.append((col, value_str))
                elif self.looks_like_description(value_str):
                    description_candidates.append((col, value_str))
            
            # Use the best candidates
            if not date_candidates or not amount_candidates:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='manual_field_detection',
                    confidence=0.0,
                    error_message="Could not find date or amount candidates"
                )
            
            # Parse the best candidates
            date_obj = self.parse_date(date_candidates[0][1])
            amount_result = self.parse_amount_with_currency(amount_candidates[0][1])
            
            if not date_obj or not amount_result['success']:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='manual_field_detection',
                    confidence=0.0,
                    error_message="Could not parse detected fields"
                )
            
            description = description_candidates[0][1] if description_candidates else "Unknown transaction"
            
            transaction = {
                'date': date_obj.strftime('%Y-%m-%d'),
                'description': description,
                'amount': amount_result['amount'],
                'currency': amount_result['currency'],
                'type': 'debit' if amount_result['amount'] < 0 else 'credit',
                'category': 'other',
                'confidence_score': 0.5
            }
            
            return ParsingResult(
                success=True,
                transaction=transaction,
                strategy_used='manual_field_detection',
                confidence=0.5
            )
            
        except Exception as e:
            return ParsingResult(
                success=False,
                transaction=None,
                strategy_used='manual_field_detection',
                confidence=0.0,
                error_message=str(e)
            )
    
    def emergency_fallback(self, row, index=None) -> ParsingResult:
        """Emergency fallback that creates a minimal transaction"""
        try:
            # Just try to extract any date and amount from the row
            row_str = ' '.join(str(val) for val in row.values if pd.notna(val))
            
            # Look for any date-like pattern
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', row_str)
            if not date_match:
                date_str = datetime.now().strftime('%Y-%m-%d')
            else:
                date_str = date_match.group(1)
            
            # Look for any number that might be an amount
            amount_match = re.search(r'(\d+[.,]?\d*)', row_str)
            if not amount_match:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='emergency_fallback',
                    confidence=0.0,
                    error_message="No amount found"
                )
            
            amount_str = amount_match.group(1)
            amount_result = self.parse_amount_with_currency(amount_str)
            
            if not amount_result['success']:
                return ParsingResult(
                    success=False,
                    transaction=None,
                    strategy_used='emergency_fallback',
                    confidence=0.0,
                    error_message="Could not parse emergency amount"
                )
            
            transaction = {
                'date': date_str,
                'description': 'Unknown transaction',
                'amount': amount_result['amount'],
                'currency': amount_result['currency'],
                'type': 'debit' if amount_result['amount'] < 0 else 'credit',
                'category': 'other',
                'confidence_score': 0.2
            }
            
            return ParsingResult(
                success=True,
                transaction=transaction,
                strategy_used='emergency_fallback',
                confidence=0.2
            )
            
        except Exception as e:
            return ParsingResult(
                success=False,
                transaction=None,
                strategy_used='emergency_fallback',
                confidence=0.0,
                error_message=str(e)
            )
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support"""
        if not date_str or str(date_str).lower() == 'nan':
            return None
        
        date_str = str(date_str).strip()
        
        for fmt in self.date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date
            except ValueError:
                continue
        
        return None
    
    def parse_amount_with_currency(self, amount_str: str) -> Dict[str, Any]:
        """Parse amount string and detect currency"""
        if not amount_str or str(amount_str).lower() == 'nan':
            return {'success': False, 'error': 'Empty amount string'}
        
        amount_str = str(amount_str).strip()
        
        # Detect currency
        currency = 'USD'  # Default
        for symbol, curr_code in self.currency_symbols.items():
            if symbol in amount_str:
                currency = curr_code
                break
        
        # Clean amount string
        cleaned = re.sub(r'[^\d\.,\-\+]', '', amount_str)
        
        if not cleaned:
            return {'success': False, 'error': 'No numeric value found'}
        
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Both comma and dot present
            last_comma = cleaned.rfind(',')
            last_dot = cleaned.rfind('.')
            
            if last_comma > last_dot:
                # European format: 1.234,56 -> 1234.56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # US format: 1,234.56 -> 1234.56
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Only comma present - determine if thousands or decimal separator
            comma_pos = cleaned.rfind(',')
            after_comma = cleaned[comma_pos+1:]
            
            if len(after_comma) <= 2:
                # Likely decimal separator
                cleaned = cleaned.replace(',', '.')
            else:
                # Likely thousands separator
                cleaned = cleaned.replace(',', '')
        
        try:
            amount = float(cleaned)
            return {
                'success': True,
                'amount': amount,
                'currency': currency
            }
        except ValueError:
            return {'success': False, 'error': f'Could not convert to float: {cleaned}'}
    
    def looks_like_date(self, value: str) -> bool:
        """Check if value looks like a date"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}'
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value):
                return True
        
        return False
    
    def looks_like_amount(self, value: str) -> bool:
        """Check if value looks like an amount"""
        amount_patterns = [
            r'[€$₹£¥₽₱₩]\d+',
            r'\d+\.\d{2}',
            r'\d+,\d{2}',
            r'\d+'
        ]
        
        for pattern in amount_patterns:
            if re.match(pattern, value):
                return True
        
        return False
    
    def looks_like_description(self, value: str) -> bool:
        """Check if value looks like a description"""
        # Descriptions typically contain letters and are longer than 3 characters
        return (len(value) > 3 and 
                re.search(r'[a-zA-Z]', value) and 
                not re.match(r'^\d+$', value))
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate a parsed transaction"""
        required_fields = ['date', 'description', 'amount', 'currency']
        
        for field in required_fields:
            if field not in transaction or not transaction[field]:
                return False
        
        # Validate amount is numeric
        try:
            float(transaction['amount'])
        except (ValueError, TypeError):
            return False
        
        # Validate date format
        try:
            datetime.strptime(transaction['date'], '%Y-%m-%d')
        except ValueError:
            return False
        
        return True
