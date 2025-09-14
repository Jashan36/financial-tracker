import pandas as pd
import re
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os
import logging
import hashlib
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from concurrent.futures import ThreadPoolExecutor

import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

@dataclass
class TransactionData:
    """Data class for transaction information"""
    date: str
    description: str
    amount: float
    category: str
    type: str
    currency: str = 'USD'  # Default to USD if not specified
    confidence_score: float = 0.0
    merchant: Optional[str] = None
    location: Optional[str] = None

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass

class TransactionProcessor:
    def __init__(self, model_path: str = "models/categorization_model.pkl", config=None):
        self.config = config or Config()
        self.chunk_size = self.config.CHUNK_SIZE
        self.max_rows = self.config.MAX_ROWS
        self.max_columns = self.config.MAX_COLUMNS
        self.num_workers = self.config.NUM_WORKERS
        # Enhanced currency detection and mapping
        self.currency_symbols = {
            '$': 'USD', 'US$': 'USD', 'USD': 'USD',
            '₹': 'INR', 'Rs': 'INR', 'INR': 'INR', 'Rs.': 'INR',
            '€': 'EUR', 'EUR': 'EUR', 'Euro': 'EUR',
            '£': 'GBP', 'GBP': 'GBP', 'Pound': 'GBP',
            '¥': 'JPY', 'JPY': 'JPY', 'Yen': 'JPY',
            '₿': 'BTC', 'BTC': 'BTC', 'Bitcoin': 'BTC',
            'CAD': 'CAD', 'C$': 'CAD',
            'AUD': 'AUD', 'A$': 'AUD',
            'CHF': 'CHF',
            'CNY': 'CNY', '¥': 'CNY',
            'SEK': 'SEK',
            'NOK': 'NOK',
            'DKK': 'DKK',
            'PLN': 'PLN',
            'CZK': 'CZK',
            'HUF': 'HUF',
            'RUB': 'RUB',
            'BRL': 'BRL', 'R$': 'BRL',
            'MXN': 'MXN',
            'ZAR': 'ZAR',
            'KRW': 'KRW', '₩': 'KRW',
            'SGD': 'SGD', 'S$': 'SGD',
            'HKD': 'HKD', 'HK$': 'HKD',
            'NZD': 'NZD', 'NZ$': 'NZD',
            'THB': 'THB', '฿': 'THB',
            'MYR': 'MYR',
            'IDR': 'IDR',
            'PHP': 'PHP', '₱': 'PHP'
        }
        
        # Currency formatting information
        self.currency_info = {
            'USD': {'symbol': '$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'INR': {'symbol': '₹', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'EUR': {'symbol': '€', 'position': 'after', 'decimal_places': 2, 'thousand_separator': '.', 'decimal_separator': ','},
            'GBP': {'symbol': '£', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'JPY': {'symbol': '¥', 'position': 'before', 'decimal_places': 0, 'thousand_separator': ',', 'decimal_separator': '.'},
            'BTC': {'symbol': '₿', 'position': 'before', 'decimal_places': 8, 'thousand_separator': ',', 'decimal_separator': '.'},
            'CAD': {'symbol': 'C$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'AUD': {'symbol': 'A$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'CHF': {'symbol': 'CHF', 'position': 'after', 'decimal_places': 2, 'thousand_separator': "'", 'decimal_separator': '.'},
            'CNY': {'symbol': '¥', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'SEK': {'symbol': 'kr', 'position': 'after', 'decimal_places': 2, 'thousand_separator': ' ', 'decimal_separator': ','},
            'NOK': {'symbol': 'kr', 'position': 'after', 'decimal_places': 2, 'thousand_separator': ' ', 'decimal_separator': ','},
            'DKK': {'symbol': 'kr', 'position': 'after', 'decimal_places': 2, 'thousand_separator': '.', 'decimal_separator': ','},
            'PLN': {'symbol': 'zł', 'position': 'after', 'decimal_places': 2, 'thousand_separator': ' ', 'decimal_separator': ','},
            'CZK': {'symbol': 'Kč', 'position': 'after', 'decimal_places': 2, 'thousand_separator': ' ', 'decimal_separator': ','},
            'HUF': {'symbol': 'Ft', 'position': 'after', 'decimal_places': 0, 'thousand_separator': ' ', 'decimal_separator': ','},
            'RUB': {'symbol': '₽', 'position': 'after', 'decimal_places': 2, 'thousand_separator': ' ', 'decimal_separator': ','},
            'BRL': {'symbol': 'R$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': '.', 'decimal_separator': ','},
            'MXN': {'symbol': '$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'ZAR': {'symbol': 'R', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'KRW': {'symbol': '₩', 'position': 'before', 'decimal_places': 0, 'thousand_separator': ',', 'decimal_separator': '.'},
            'SGD': {'symbol': 'S$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'HKD': {'symbol': 'HK$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'NZD': {'symbol': 'NZ$', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'THB': {'symbol': '฿', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'MYR': {'symbol': 'RM', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'},
            'IDR': {'symbol': 'Rp', 'position': 'before', 'decimal_places': 0, 'thousand_separator': '.', 'decimal_separator': ','},
            'PHP': {'symbol': '₱', 'position': 'before', 'decimal_places': 2, 'thousand_separator': ',', 'decimal_separator': '.'}
        }
        
        # Enhanced category mapping with more keywords and patterns
        self.categories = {
            'food': {
                'keywords': ['restaurant', 'cafe', 'grocery', 'food', 'meal', 'dining', 'takeout', 'delivery', 'coffee', 'lunch', 'dinner', 'breakfast', 'pizza', 'burger', 'sushi', 'mcdonalds', 'starbucks', 'subway', 'dominos', 'chipotle', 'panera', 'taco bell', 'wendys', 'kfc', 'burger king', 'dairy queen', 'tim hortons', 'dunkin', 'five guys', 'in-n-out'],
                'emoji': '🍽️',
                'patterns': [r'\b(restaurant|cafe|bistro|diner|eatery|food|grocery|market)\b']
            },
            'transport': {
                'keywords': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'parking', 'metro', 'bus', 'train', 'subway', 'transport', 'commute', 'shell', 'exxon', 'chevron', 'bp', 'valero', 'mobil', 'citgo', 'sunoco', 'speedway', 'wawa'],
                'emoji': '🚗',
                'patterns': [r'\b(uber|lyft|taxi|gas|fuel|parking|metro|bus|train)\b']
            },
            'entertainment': {
                'keywords': ['movie', 'theater', 'concert', 'show', 'game', 'netflix', 'spotify', 'amazon prime', 'entertainment', 'fun', 'hulu', 'disney+', 'youtube', 'ticketmaster', 'fandango', 'cinema', 'amc', 'regal', 'imax', 'paramount', 'universal', 'warner bros'],
                'emoji': '🎬',
                'patterns': [r'\b(movie|theater|cinema|concert|show|netflix|spotify)\b']
            },
            'shopping': {
                'keywords': ['amazon', 'walmart', 'target', 'mall', 'store', 'shop', 'retail', 'clothing', 'electronics', 'shopping', 'best buy', 'home depot', 'lowes', 'costco', 'sams club', 'macys', 'nordstrom', 'kohls', 'tj maxx', 'marshalls', 'ross', 'old navy', 'gap'],
                'emoji': '🛍️',
                'patterns': [r'\b(amazon|walmart|target|shop|store|retail|mall)\b']
            },
            'utilities': {
                'keywords': ['electric', 'water', 'gas', 'internet', 'phone', 'cable', 'utility', 'bill', 'service', 'verizon', 'at&t', 'comcast', 'xfinity', 'duke energy', 'pg&e', 'spectrum', 'cox', 'directv', 'dish'],
                'emoji': '💡',
                'patterns': [r'\b(electric|water|gas|internet|phone|cable|utility)\b']
            },
            'healthcare': {
                'keywords': ['doctor', 'hospital', 'pharmacy', 'medical', 'health', 'dental', 'vision', 'insurance', 'cvs', 'walgreens', 'rite aid', 'kroger pharmacy', 'urgent care', 'clinic', 'dentist', 'optometrist'],
                'emoji': '🏥',
                'patterns': [r'\b(doctor|hospital|pharmacy|medical|health|dental)\b']
            },
            'education': {
                'keywords': ['school', 'university', 'college', 'course', 'book', 'tuition', 'education', 'learning', 'textbook', 'library', 'coursera', 'udemy', 'khan academy', 'edx', 'skillshare'],
                'emoji': '📚',
                'patterns': [r'\b(school|university|college|course|education|tuition)\b']
            },
            'travel': {
                'keywords': ['hotel', 'airline', 'flight', 'vacation', 'trip', 'travel', 'booking', 'reservation', 'marriott', 'hilton', 'airbnb', 'expedia', 'booking.com', 'priceline', 'kayak', 'travelocity', 'orbitz'],
                'emoji': '✈️',
                'patterns': [r'\b(hotel|airline|flight|vacation|trip|travel|booking)\b']
            },
            'insurance': {
                'keywords': ['car insurance', 'home insurance', 'life insurance', 'health insurance', 'insurance', 'geico', 'state farm', 'allstate', 'progressive', 'usaa', 'liberty mutual', 'farmers'],
                'emoji': '🛡️',
                'patterns': [r'\b(insurance|geico|state farm|allstate|progressive)\b']
            },
            'investment': {
                'keywords': ['investment', 'stock', 'bond', 'fund', 'portfolio', 'trading', 'brokerage', 'fidelity', 'vanguard', 'schwab', 'robinhood', 'etrade', 'td ameritrade', 'merrill lynch', '401k', 'ira'],
                'emoji': '📈',
                'patterns': [r'\b(investment|stock|bond|fund|portfolio|trading|brokerage)\b']
            },
            'other': {
                'keywords': [],
                'emoji': '📦',
                'patterns': []
            }
        }
        
        self.stop_words = set(stopwords.words('english'))
        self.model_path = Path(model_path)
        self.ml_model = None
        self.vectorizer = None
        
        # File validation settings
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        self.allowed_extensions = {'.csv'}
        self.required_csv_columns = {'date', 'description', 'amount'}
        
        # Load or initialize ML model
        self._load_or_initialize_model()
    
    def _load_or_initialize_model(self):
        """Load existing ML model or create new one"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.ml_model = model_data['model']
                    self.vectorizer = model_data['vectorizer']
                logger.info("Loaded existing categorization model")
            else:
                self._initialize_default_model()
                logger.info("Initialized default categorization model")
        except Exception as e:
            logger.warning(f"Error loading model: {e}. Using default model.")
            self._initialize_default_model()
    
    def _initialize_default_model(self):
        """Initialize default ML model with sample data"""
        # Create sample training data from categories
        training_data = []
        labels = []
        
        for category, info in self.categories.items():
            if category != 'other':
                for keyword in info['keywords']:
                    training_data.append(keyword)
                    labels.append(category)
        
        if training_data:
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            self.ml_model = Pipeline([
                ('tfidf', self.vectorizer),
                ('classifier', MultinomialNB())
            ])
            
            # Train with sample data
            self.ml_model.fit(training_data, labels)
            self._save_model()
    
    def _save_model(self):
        """Save the ML model to disk"""
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            model_data = {
                'model': self.ml_model,
                'vectorizer': self.vectorizer
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def validate_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """Comprehensive file validation"""
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            return False, f"File size ({file_size / (1024*1024):.1f}MB) exceeds maximum allowed size ({self.max_file_size / (1024*1024):.1f}MB)"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check file extension
        if file_path.suffix.lower() not in self.allowed_extensions:
            return False, f"Unsupported file type: {file_path.suffix}. Allowed types: {', '.join(self.allowed_extensions)}"
        
        # Check file integrity
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, nrows=5)  # Read first 5 rows for validation
                if df.empty:
                    return False, "CSV file appears to be empty"
        except Exception as e:
            return False, f"File appears to be corrupted: {str(e)}"
        
        return True, "File validation successful"
    
    def process_file(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> List[Dict]:
        """Process uploaded CSV file and return categorized transactions"""
        file_path = Path(file_path)
        
        # Validate file first
        is_valid, message = self.validate_file(file_path)
        if not is_valid:
            raise ValidationError(message)
        
        logger.info(f"Processing file: {file_path.name} ({file_path.stat().st_size / 1024:.1f}KB)")
        
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.csv':
                transactions = self._process_csv(file_path, encoding=encoding)
            else:
                raise ValidationError(f"Unsupported file format: {file_extension}. Only CSV files are supported.")
            
            # Validate processed transactions
            valid_transactions = self._validate_transactions(transactions)
            
            # Calculate file hash for caching/duplicate detection
            file_hash = self._calculate_file_hash(file_path)
            
            logger.info(f"Successfully processed {len(valid_transactions)} valid transactions from {file_path.name}")
            return valid_transactions
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise ProcessingError(f"Failed to process file: {str(e)}")
    
    def determine_primary_currency(self, transactions: List[Dict]) -> str:
        """Determine the primary currency from a list of transactions"""
        if not transactions:
            return 'USD'
            
        currency_counts = {}
        currency_totals = {}
        
        for transaction in transactions:
            currency = transaction.get('currency', 'USD')
            amount = abs(transaction.get('amount', 0))
            
            currency_counts[currency] = currency_counts.get(currency, 0) + 1
            currency_totals[currency] = currency_totals.get(currency, 0) + amount
        
        # Determine primary currency based on both frequency and total value
        primary_currency = 'USD'
        max_score = 0
        
        for currency in currency_counts.keys():
            # Score combines frequency (70%) and total value (30%)
            frequency_score = currency_counts[currency] / len(transactions)
            value_score = currency_totals[currency] / sum(currency_totals.values()) if sum(currency_totals.values()) > 0 else 0
            
            total_score = (frequency_score * 0.7) + (value_score * 0.3)
            
            if total_score > max_score:
                max_score = total_score
                primary_currency = currency
        
        return primary_currency
    
    def format_currency_amount(self, amount: float, currency: str) -> str:
        """Format amount according to currency conventions"""
        if currency not in self.currency_info:
            currency = 'USD'
            
        info = self.currency_info[currency]
        symbol = info['symbol']
        position = info['position']
        decimal_places = info['decimal_places']
        thousand_sep = info['thousand_separator']
        decimal_sep = info['decimal_separator']
        
        # Format the number
        if decimal_places == 0:
            formatted_amount = f"{int(abs(amount)):,}".replace(',', thousand_sep)
        else:
            formatted_amount = f"{abs(amount):.{decimal_places}f}".replace('.', decimal_sep)
            if thousand_sep != ',':
                # Add thousand separators
                parts = formatted_amount.split(decimal_sep)
                parts[0] = f"{int(parts[0]):,}".replace(',', thousand_sep)
                formatted_amount = decimal_sep.join(parts)
        
        # Add currency symbol
        if position == 'before':
            return f"{symbol}{formatted_amount}"
        else:
            return f"{formatted_amount} {symbol}"
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for caching/duplicate detection"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _validate_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Validate and clean processed transactions with more lenient validation"""
        valid_transactions = []
        validation_errors = []
        
        for i, transaction in enumerate(transactions):
            try:
                # More lenient validation - check for required fields
                required_fields = ['date', 'description', 'amount']
                missing_fields = [field for field in required_fields if field not in transaction or not transaction[field]]
                
                if missing_fields:
                    validation_errors.append(f"Transaction {i+1}: Missing fields {missing_fields}")
                    continue
                
                # Validate amount - be more flexible with types
                amount = transaction['amount']
                if amount is None:
                    validation_errors.append(f"Transaction {i+1}: Amount is None")
                    continue
                
                # Try to convert amount to float if it's not already
                try:
                    if not isinstance(amount, (int, float)):
                        amount = float(str(amount))
                    transaction['amount'] = amount
                except (ValueError, TypeError):
                    validation_errors.append(f"Transaction {i+1}: Cannot convert amount '{amount}' to number")
                    continue
                
                # Validate description
                description = str(transaction['description']).strip()
                if not description or description.lower() in ['nan', 'null', '']:
                    validation_errors.append(f"Transaction {i+1}: Empty or invalid description")
                    continue
                transaction['description'] = description
                
                # Ensure currency field exists
                if 'currency' not in transaction:
                    transaction['currency'] = 'USD'
                
                # Add confidence score if missing
                if 'confidence_score' not in transaction:
                    transaction['confidence_score'] = 0.7  # Default confidence
                
                # Add transaction type if missing
                if 'type' not in transaction:
                    transaction['type'] = 'debit' if amount < 0 else 'credit'
                
                # Add category if missing
                if 'category' not in transaction:
                    transaction['category'] = 'other'
                
                valid_transactions.append(transaction)
                
            except Exception as e:
                validation_errors.append(f"Transaction {i+1}: Validation error - {str(e)}")
                continue
        
        # Log validation errors for debugging
        if validation_errors:
            logger.warning(f"Transaction validation errors (showing first 5):")
            for error in validation_errors[:5]:
                logger.warning(f"  {error}")
        
        if not valid_transactions:
            error_summary = "; ".join(validation_errors[:3]) if validation_errors else "Unknown validation errors"
            raise ValidationError(f"No valid transactions found in file. Errors: {error_summary}")
        
        logger.info(f"Successfully validated {len(valid_transactions)} transactions (rejected {len(validation_errors)})")
        return valid_transactions
    
    def _process_csv(self, file_path, encoding='utf-8'):
        """Process CSV file and categorize transactions with optimized data processing"""
        try:
            # First, check file size and determine processing strategy
            file_size = os.path.getsize(file_path)
            logger.info(f"Processing CSV file: {file_size / 1024:.1f}KB")
            
            # For large files, use chunked processing
            if file_size > 5 * 1024 * 1024:  # 5MB
                return self._process_csv_chunked(file_path, encoding)
            
            # Read CSV with proper error handling
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            logger.info(f"Columns: {list(df.columns)}")
            
            # Debug: Show first few rows
            logger.info(f"Sample data:\n{df.head().to_string()}")
            
            # Fix split currency columns
            df = self._fix_split_currency_columns(df)
            
            # Process transactions
            valid_transactions = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    transaction = self.parse_transaction_row(row, index=idx)
                    if transaction:
                        valid_transactions.append(transaction)
                    else:
                        errors.append(f"Row {idx}: Failed to create transaction")
                except Exception as e:
                    errors.append(f"Row {idx}: {str(e)}")
            
            # Log detailed errors for debugging
            if errors:
                logger.warning(f"CSV processing errors (showing first 5):")
                for error in errors[:5]:
                    logger.warning(f"  {error}")
            
            if not valid_transactions:
                error_summary = "; ".join(errors[:3]) if errors else "Unknown processing errors"
                raise ValueError(f"No valid transactions found in CSV file. Errors: {error_summary}")
            
            logger.info(f"Successfully processed {len(valid_transactions)} transactions from CSV (rejected {len(errors)} rows)")
            return valid_transactions
            
        except Exception as e:
            raise Exception(f"Error processing CSV file: {str(e)}")
    
    def _process_csv_chunked(self, file_path, encoding='utf-8'):
        """Process large CSV files in chunks to avoid memory issues"""
        try:
            transactions = []
            chunk_size = 1000  # Process 1000 rows at a time
            
            # First, read a small sample to identify columns
            sample_df = pd.read_csv(file_path, nrows=10, encoding=encoding)
            sample_df.columns = [col.lower().strip() for col in sample_df.columns]
            
            # Map columns using the sample
            column_mapping = {
                'date': ['date', 'transaction_date', 'posted_date', 'post_date', 'trans_date'],
                'description': ['description', 'merchant', 'payee', 'transaction_description', 'details', 'memo', 'note'],
                'amount': ['amount', 'debit', 'credit', 'transaction_amount', 'sum', 'total', 'value'],
                'type': ['type', 'transaction_type', 'trans_type', 'debit_credit']
            }
            
            actual_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col in sample_df.columns:
                    if any(name in col.lower() for name in possible_names):
                        actual_columns[target_col] = col
                        break
            
            if not actual_columns:
                raise ValueError("Could not identify required columns in CSV")
            
            logger.info(f"Processing large CSV in chunks. Column mapping: {actual_columns}")
            
            # Process file in chunks
            chunk_iter = pd.read_csv(file_path, chunksize=chunk_size, encoding=encoding)
            total_processed = 0
            
            for chunk_idx, chunk_df in enumerate(chunk_iter):
                chunk_df.columns = [col.lower().strip() for col in chunk_df.columns]
                
                for idx, row in chunk_df.iterrows():
                    try:
                        transaction = self._create_transaction(row, actual_columns)
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        logger.warning(f"Error processing row {total_processed + idx + 1}: {str(e)}")
                        continue
                
                total_processed += len(chunk_df)
                logger.info(f"Processed chunk {chunk_idx + 1}: {len(transactions)} valid transactions so far")
                
                # Safety check to prevent excessive memory usage
                if total_processed > self.max_rows:
                    logger.warning(f"Reached maximum processing limit of {self.max_rows} rows")
                    break
            
            if not transactions:
                raise ValueError("No valid transactions found in CSV file")
            
            logger.info(f"Successfully processed {len(transactions)} transactions from large CSV file")
            return transactions
            
        except Exception as e:
            raise Exception(f"Error processing large CSV file: {str(e)}")
    
    def parse_transaction_row(self, row, index=None):
        """Parse CSV row into Transaction object"""
        try:
            # Convert pandas Series to dict and normalize column names
            if hasattr(row, 'to_dict'):
                row_data = row.to_dict()
            else:
                row_data = dict(row)
                
            # Case-insensitive column mapping
            normalized_data = {}
            for key, value in row_data.items():
                normalized_data[str(key).lower().strip()] = value
            
            # Extract fields with fallbacks
            date_str = normalized_data.get('date', '')
            description = normalized_data.get('description', '')
            amount_str = str(normalized_data.get('amount', ''))
            trans_type = normalized_data.get('type', 'Debit')
            category = normalized_data.get('category', 'Other')
            
            # Parse date
            date_obj = self._parse_date(date_str)
            if not date_obj:
                raise ValueError(f"Invalid date: {date_str}")
            
            # Parse amount and currency
            if not amount_str or str(amount_str).strip() in ['', 'nan', 'None']:
                raise ValueError(f"Invalid amount: {amount_str}")
                
            amount_value, currency = self._parse_amount(amount_str)
            if amount_value is None:
                raise ValueError(f"Could not parse amount: {amount_str}")
            
            # Determine if it's expense or income
            is_expense = str(trans_type).lower() in ['debit', 'expense', 'withdrawal']
            
            # Create transaction dictionary
            transaction = {
                'date': date_obj.strftime('%Y-%m-%d'),
                'description': str(description).strip(),
                'amount': amount_value,
                'currency': currency,
                'type': 'debit' if is_expense else 'credit',
                'category': str(category).strip().lower(),
                'confidence_score': 0.7  # Default confidence
            }
            
            # Add categorization if not provided
            if not transaction['category'] or transaction['category'] in ['other', '']:
                category, confidence = self._categorize_transaction(transaction['description'])
                transaction['category'] = category
                transaction['confidence_score'] = confidence
            
            return transaction
            
        except Exception as e:
            if index is not None:
                logger.error(f"Row {index} parse error: {str(e)} | Data: {dict(row)}")
            return None
    
    def _create_transaction(self, row, column_mapping):
        """Legacy method - redirect to new parse_transaction_row"""
        return self.parse_transaction_row(row)
    
    def _parse_date(self, date_str):
        """Parse date string with multiple format support"""
        if not date_str or str(date_str).lower() == 'nan':
            return None
            
        date_str = str(date_str).strip()
        
        # Handle month names
        month_mapping = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        # Replace month names with numbers
        for month, num in month_mapping.items():
            date_str = re.sub(rf'\b{month}\b', num, date_str, flags=re.IGNORECASE)
        
        # Common date formats with priority order
        date_formats = [
            '%Y-%m-%d',    # 2024-01-15
            '%m/%d/%Y',    # 01/15/2024
            '%d/%m/%Y',    # 15/01/2024
            '%Y/%m/%d',    # 2024/01/15
            '%d-%m-%Y',    # 15-01-2024
            '%m-%d-%Y',    # 01-15-2024
            '%Y-%m-%d %H:%M:%S',  # 2024-01-15 10:30:00
            '%m/%d/%Y %H:%M:%S',  # 01/15/2024 10:30:00
            '%d/%m/%Y %H:%M:%S',  # 15/01/2024 10:30:00
            '%m/%d/%y', '%m-%d-%y', '%d/%m/%y', '%d-%m-%y',
            '%m/%d', '%m-%d'  # Handle dates without year (assume current year)
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # If no year specified, use current year
                if fmt in ['%m/%d', '%m-%d']:
                    current_year = datetime.now().year
                    parsed_date = parsed_date.replace(year=current_year)
                # Return date object (not datetime)
                return parsed_date.date()
            except ValueError:
                continue
        
        return None
    
    def detect_currency_from_amount(self, amount_str):
        """Detect currency from amount string with improved pattern matching"""
        if not amount_str:
            return 'USD'
            
        amount_str = str(amount_str).strip()
        
        # Currency patterns with priority order (more specific patterns first)
        currency_patterns = [
            # Specific prefixes first (more specific patterns)
            (r'C\$', 'CAD'),
            (r'A\$', 'AUD'), 
            (r'R\$', 'BRL'),
            (r'RM', 'MYR'),
            (r'S\$', 'SGD'),
            (r'HK\$', 'HKD'),
            (r'NZ\$', 'NZD'),
            (r'Rp', 'IDR'),
            
            # Single character symbols
            (r'₹', 'INR'),
            (r'€', 'EUR'),
            (r'£', 'GBP'),
            (r'₱', 'PHP'),
            (r'₽', 'RUB'),
            (r'₩', 'KRW'),
            (r'฿', 'THB'),
            (r'₿', 'BTC'),
            
            # Dollar symbol - default to USD unless specified otherwise
            (r'^\$', 'USD'),  # Default $ to USD
            
            # Yen symbols - default to JPY for international use
            (r'¥', 'JPY'),  # Default ¥ to JPY (more common internationally)
            (r'￥', 'CNY'),  # Chinese yen symbol
            
            # Text codes
            (r'\bUSD\b', 'USD'),
            (r'\bINR\b', 'INR'),
            (r'\bEUR\b', 'EUR'),
            (r'\bGBP\b', 'GBP'),
            (r'\bJPY\b', 'JPY'),
            (r'\bCAD\b', 'CAD'),
            (r'\bAUD\b', 'AUD'),
            (r'\bCHF\b', 'CHF'),
            (r'\bCNY\b', 'CNY'),
            (r'\bSEK\b', 'SEK'),
            (r'\bNOK\b', 'NOK'),
            (r'\bDKK\b', 'DKK'),
            (r'\bPLN\b', 'PLN'),
            (r'\bCZK\b', 'CZK'),
            (r'\bHUF\b', 'HUF'),
            (r'\bRUB\b', 'RUB'),
            (r'\bBRL\b', 'BRL'),
            (r'\bMXN\b', 'MXN'),
            (r'\bZAR\b', 'ZAR'),
            (r'\bKRW\b', 'KRW'),
            (r'\bSGD\b', 'SGD'),
            (r'\bHKD\b', 'HKD'),
            (r'\bNZD\b', 'NZD'),
            (r'\bTHB\b', 'THB'),
            (r'\bMYR\b', 'MYR'),
            (r'\bIDR\b', 'IDR'),
            (r'\bPHP\b', 'PHP'),
        ]
        
        for pattern, currency in currency_patterns:
            if re.search(pattern, amount_str):
                return currency
            
        return 'USD'  # Default fallback
    
    def _parse_amount(self, amount_str):
        """Parse amount string to float with currency detection and improved format handling"""
        if not amount_str or str(amount_str).lower() == 'nan':
            return None, 'USD'
            
        try:
            amount_str = str(amount_str).strip()
            
            # Detect currency first
            currency = self.detect_currency_from_amount(amount_str)
            
            # Remove currency symbols and letters, keep numbers, commas, dots, and signs
            cleaned = re.sub(r'[^\d\.,\-\+]', '', amount_str)
            
            if not cleaned:
                return None, currency
            
            # Handle different decimal separators based on currency and format
            if ',' in cleaned and '.' in cleaned:
                # Both comma and dot present - determine which is decimal separator
                last_comma = cleaned.rfind(',')
                last_dot = cleaned.rfind('.')
                
                if last_comma > last_dot:
                    # European format: 1.234,56 -> 1234.56
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    # US format: 1,234.56 -> 1234.56
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Only comma present - determine if it's thousands separator or decimal
                comma_pos = cleaned.rfind(',')
                after_comma = cleaned[comma_pos+1:]
                
                if len(after_comma) <= 2 and len(after_comma) > 0:
                    # Likely decimal separator (1-2 digits after comma)
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Likely thousands separator
                    cleaned = cleaned.replace(',', '')
            
            # Handle negative amounts
            is_negative = cleaned.startswith('-')
            cleaned = cleaned.replace('-', '').replace('+', '')
            
            if cleaned:
                amount = float(cleaned)
                if is_negative:
                    amount = -amount
                
                # Handle very large or small amounts
                if abs(amount) > 1000000000 or (abs(amount) < 0.000001 and amount != 0):
                    return None, currency
                    
                return amount, currency
                
        except (ValueError, TypeError) as e:
            logger.debug(f"Amount parsing failed for '{amount_str}': {str(e)}")
            pass
        
        return None, 'USD'
    
    def _fix_split_currency_columns(self, df):
        """Fix cases where EUR amounts are split across columns"""
        if len(df.columns) > 5:  # More columns than expected
            amount_cols = [col for col in df.columns if 'amount' in col.lower()]
            
            if len(amount_cols) == 0:
                # Look for numeric columns that might be split currency
                try:
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) >= 2:
                        # Assume last two numeric columns are currency parts
                        df['Amount'] = df[numeric_cols[-2]].astype(str) + '.' + df[numeric_cols[-1]].astype(str).str.zfill(2)
                        logger.info(f"Fixed split currency columns: {numeric_cols[-2]} + {numeric_cols[-1]} -> Amount")
                except Exception as e:
                    logger.debug(f"Could not fix split currency columns: {str(e)}")
                    
        return df
    
    def safe_log(self, message):
        """Safe logging method that handles Unicode encoding issues"""
        try:
            logger.info(message)
        except UnicodeEncodeError:
            safe_message = message.encode('ascii', 'replace').decode('ascii')
            logger.info(safe_message)
    
    def _categorize_transaction(self, description: str) -> Tuple[str, float]:
        """Automatically categorize transaction using hybrid ML + rule-based approach"""
        if not description or not description.strip():
            return 'other', 0.0
            
        description_clean = description.lower().strip()
        
        # Try ML model first
        ml_category, ml_confidence = self._ml_categorize(description_clean)
        
        # Use rule-based as fallback or validation
        rule_category, rule_confidence = self._rule_based_categorize(description_clean)
        
        # Combine results - prefer ML if confidence is high, otherwise use rule-based
        if ml_confidence >= 0.7:
            return ml_category, ml_confidence
        elif rule_confidence >= 0.8:
            return rule_category, rule_confidence
        elif ml_confidence >= 0.5:
            return ml_category, ml_confidence
        elif rule_confidence >= 0.5:
            return rule_category, rule_confidence
        else:
            # Return the one with higher confidence
            if ml_confidence >= rule_confidence:
                return ml_category, ml_confidence
            else:
                return rule_category, rule_confidence
    
    def _ml_categorize(self, description: str) -> Tuple[str, float]:
        """Use ML model for categorization"""
        try:
            if self.ml_model is None:
                return 'other', 0.0
            
            # Get prediction probabilities
            probabilities = self.ml_model.predict_proba([description])[0]
            classes = self.ml_model.classes_
            
            # Find best prediction
            max_prob_idx = probabilities.argmax()
            predicted_category = classes[max_prob_idx]
            confidence = probabilities[max_prob_idx]
            
            return predicted_category, confidence
            
        except Exception as e:
            logger.debug(f"ML categorization failed: {e}")
            return 'other', 0.0
    
    def _rule_based_categorize(self, description: str) -> Tuple[str, float]:
        """Enhanced rule-based categorization with scoring"""
        # Tokenize and clean description
        tokens = word_tokenize(description)
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        # Score each category
        category_scores = {}
        
        for category, info in self.categories.items():
            if category == 'other':
                continue
                
            score = 0
            keywords = info.get('keywords', [])
            patterns = info.get('patterns', [])
            
            # Keyword matching with weighted scoring
            for keyword in keywords:
                # Exact match gets higher score
                if keyword == description:
                    score += 3.0
                elif keyword in description:
                    # Longer keywords get higher scores
                    score += len(keyword.split()) * 1.5
                    
                # Token matching
                for token in tokens:
                    if keyword == token:
                        score += 2.0
                    elif keyword in token or token in keyword:
                        score += 0.5
            
            # Pattern matching
            for pattern in patterns:
                try:
                    if re.search(pattern, description, re.IGNORECASE):
                        score += 2.0
                except re.error:
                    continue
            
            if score > 0:
                category_scores[category] = score
        
        # Normalize scores and find best match
        if not category_scores:
            return 'other', 0.0
        
        max_score = max(category_scores.values())
        best_category = max(category_scores, key=category_scores.get)
        
        # Convert score to confidence (0-1 range)
        confidence = min(max_score / 10.0, 1.0)  # Normalize to 0-1
        
        return best_category, confidence
    
    def get_category_summary(self, transactions):
        """Get summary of transactions by category"""
        if not transactions:
            return {}
        
        summary = {}
        for transaction in transactions:
            category = transaction.get('category', 'other')
            amount = abs(transaction.get('amount', 0))
            
            if category not in summary:
                summary[category] = {'count': 0, 'total': 0.0}
            
            summary[category]['count'] += 1
            summary[category]['total'] += amount
        
        return summary
    
    def export_to_csv(self, transactions, output_path):
        """Export processed transactions to CSV"""
        try:
            df = pd.DataFrame(transactions)
            df.to_csv(output_path, index=False)
            logger.info(f"Transactions exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def validate_transaction(self, transaction):
        """Validate a single transaction"""
        required_fields = ['date', 'description', 'amount', 'category', 'type']
        
        for field in required_fields:
            if field not in transaction:
                return False, f"Missing required field: {field}"
        
        if not transaction['date'] or not transaction['description']:
            return False, "Date and description cannot be empty"
        
        if transaction['amount'] is None:
            return False, "Invalid amount"
        
        return True, "Transaction is valid" 