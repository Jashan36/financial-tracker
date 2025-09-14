from flask import Flask, render_template, request, jsonify, send_file, session, flash, redirect, url_for, abort
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_limiter import Limiter
import logging.config
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
from transaction_processor import TransactionProcessor, ValidationError, ProcessingError
from budget_analyzer import BudgetAnalyzer
from config import get_config, Config
from enhanced_transaction_processor import EnhancedTransactionProcessor
import tempfile
import logging
import uuid
from functools import wraps
from pathlib import Path
import time
from werkzeug.exceptions import RequestEntityTooLarge
from typing import Dict, List, Any

# Initialize Flask app with configuration
config = get_config()
app = Flask(__name__)
app.config.from_object(config)

# Initialize extensions
CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure logging
logging.config.dictConfig(config.LOG_CONFIG)
logger = logging.getLogger(__name__)

# Initialize processors with enhanced configuration
transaction_processor = TransactionProcessor(model_path=str(config.MODEL_PATH))
budget_analyzer = BudgetAnalyzer()
enhanced_processor = EnhancedTransactionProcessor(enable_currency_conversion=True, cache=cache)

# Session management
app.permanent_session_lifetime = timedelta(hours=2)

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    if config.get_environment_config().get('SECURITY_HEADERS_ENABLED', False):
        for header, value in config.SECURITY_HEADERS.items():
            response.headers[header] = value
    return response

# Error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle validation errors"""
    logger.warning(f"Validation error: {str(e)}")
    return jsonify({'error': f'Validation error: {str(e)}', 'type': 'validation'}), 400

@app.errorhandler(ProcessingError)
def handle_processing_error(e):
    """Handle processing errors"""
    logger.error(f"Processing error: {str(e)}")
    return jsonify({'error': f'Processing error: {str(e)}', 'type': 'processing'}), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle file too large errors"""
    logger.warning(f"File too large: {str(e)}")
    return jsonify({'error': 'File size too large. Maximum allowed size is 16MB.', 'type': 'file_size'}), 413

@app.errorhandler(404)
def handle_not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found', 'type': 'not_found'}), 404

@app.errorhandler(500)
def handle_internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error', 'type': 'internal'}), 500

# Utility functions
def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['session_id']

def validate_transaction_data(transactions):
    """Comprehensive validation of transaction data"""
    try:
        if not isinstance(transactions, list):
            return {'valid': False, 'error': 'Transactions must be a list'}
        
        if not transactions:
            return {'valid': False, 'error': 'No transactions provided'}
        
        # Validate each transaction
        required_fields = ['date', 'description', 'amount', 'category']
        for i, transaction in enumerate(transactions):
            if not isinstance(transaction, dict):
                return {'valid': False, 'error': f'Transaction {i+1} must be a dictionary'}
            
            # Check required fields
            missing_fields = [field for field in required_fields if field not in transaction]
            if missing_fields:
                return {'valid': False, 'error': f'Transaction {i+1} missing required fields: {missing_fields}'}
            
            # Validate amount
            try:
                amount = float(transaction['amount'])
                if not isinstance(amount, (int, float)) or not isinstance(transaction['amount'], (int, float, str)):
                    return {'valid': False, 'error': f'Transaction {i+1} amount must be numeric'}
            except (ValueError, TypeError):
                return {'valid': False, 'error': f'Transaction {i+1} amount must be a valid number'}
            
            # Validate date format
            date_str = str(transaction['date'])
            if not date_str or len(date_str) < 4:
                return {'valid': False, 'error': f'Transaction {i+1} date appears invalid'}
            
            # Validate description
            if not transaction['description'] or not str(transaction['description']).strip():
                return {'valid': False, 'error': f'Transaction {i+1} description cannot be empty'}
            
            # Validate category
            if not transaction['category'] or not str(transaction['category']).strip():
                return {'valid': False, 'error': f'Transaction {i+1} category cannot be empty'}
        
        # Check for reasonable transaction count
        if len(transactions) > 10000:
            return {'valid': False, 'error': 'Too many transactions (max 10,000 allowed)'}
        
        return {'valid': True, 'error': None}
        
    except Exception as e:
        return {'valid': False, 'error': f'Validation error: {str(e)}'}

def validate_json_request(required_fields: List[str]):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON', 'type': 'validation'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided', 'type': 'validation'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {missing_fields}', 
                    'type': 'validation'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_request_info():
    """Log request information"""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

# Routes
@app.route('/')
@limiter.limit("100 per hour")
def index():
    """Main application page"""
    session_id = get_session_id()
    logger.info(f"Index page accessed by session: {session_id}")
    return render_template('index.html', session_id=session_id)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'components': {
            'transaction_processor': 'ok',
            'budget_analyzer': 'ok',
            'ml_model': 'ok' if transaction_processor.ml_model else 'not_loaded'
        }
    })

@app.route('/upload', methods=['POST'])
@limiter.limit("20 per hour")
def upload_file():
    """Enhanced file upload with comprehensive validation and caching"""
    start_time = time.time()
    session_id = get_session_id()
    file_path = None
    
    # Log request info for debugging
    logger.info(f"Upload request received - Session: {session_id}")
    is_xhr = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Check if request has file
        if 'file' not in request.files:
            logger.warning(f"No file in request - Session: {session_id}")
            error_msg = 'No file selected. Please choose a file to upload.'
            if is_xhr:
                return jsonify({'error': error_msg, 'type': 'validation'}), 400
            flash(error_msg, 'error')
            return redirect(url_for('index'))
            
        file = request.files['file']
        if not file.filename:
            logger.warning(f"Empty filename received - Session: {session_id}")
            error_msg = 'No file selected. Please choose a file to upload.'
            if is_xhr:
                return jsonify({'error': error_msg, 'type': 'validation'}), 400
            flash(error_msg, 'error')
            return redirect(url_for('index'))
            
        # Check file size
        if request.content_length and request.content_length > config.MAX_CONTENT_LENGTH:
            error_msg = f'File size exceeds the limit of {config.MAX_CONTENT_LENGTH / (1024 * 1024):.1f}MB'
            logger.warning(f"{error_msg} - Session: {session_id}")
            if is_xhr:
                return jsonify({'error': error_msg, 'type': 'validation'}), 413
            flash(error_msg, 'error')
            return redirect(url_for('index'))
        
        # Initialize response tracking
        processing_status = {
            'stage': 'initializing',
            'progress': 0,
            'message': 'Starting upload process'
        }
        
        file = request.files['file']
        if not file.filename:
            return jsonify({
                'error': 'No file selected',
                'type': 'validation'
            }), 400
        
        # Validate file type with more detailed error message
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.ALLOWED_EXTENSIONS:
            supported_formats = ', '.join(config.ALLOWED_EXTENSIONS)
            return jsonify({
                'error': f'Unsupported file type "{file_ext}". Please upload a {supported_formats} file.',
                'details': {
                    'uploaded_type': file_ext,
                    'allowed_types': list(config.ALLOWED_EXTENSIONS)
                },
                'type': 'validation'
            }), 400
        
        # Generate unique filename and ensure upload directory exists
        try:
            config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            unique_filename = f"{session_id}_{int(time.time())}_{secure_filename(file.filename)}"
            file_path = config.UPLOAD_FOLDER / unique_filename
            
            # Save file
            file.save(str(file_path))
            logger.info(f"File uploaded: {file.filename} -> {unique_filename} (Session: {session_id})")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({
                'error': 'Failed to save uploaded file',
                'type': 'upload'
            }), 500
        
        try:
            # Process the file with explicit encoding for CSV files
            if str(file_path).lower().endswith('.csv'):
                # Try different encodings for CSV files
                encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
                transactions = None
                
                for encoding in encodings_to_try:
                    try:
                        transactions = transaction_processor.process_file(str(file_path), encoding=encoding)
                        logger.info(f"Successfully processed CSV with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        logger.warning(f"Failed to process CSV with {encoding} encoding, trying next...")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing CSV with {encoding}: {str(e)}")
                        continue
                
                if not transactions:
                    raise ValidationError("Could not process CSV file with any supported encoding")
                    
            elif str(file_path).lower().endswith('.pdf'):
                transactions = transaction_processor.process_file(str(file_path))
            else:
                raise ValidationError(f"Unsupported file type: {file_path.suffix}")

            if not transactions:
                raise ValidationError("No transactions found in the file")
            
            # Determine primary currency from transactions
            primary_currency = transaction_processor.determine_primary_currency(transactions)
            logger.info(f"Primary currency detected: {primary_currency}")
            
            # Store transactions in cache for this session
            cache_key = f"transactions_{session_id}"
            cache.set(cache_key, transactions, timeout=3600)  # Cache for 1 hour
            
            # Store primary currency in session
            session['primary_currency'] = primary_currency
            
            processing_time = time.time() - start_time
            logger.info(f"File processed successfully in {processing_time:.2f}s: {len(transactions)} transactions")
            
            # Clean up uploaded file
            file_path.unlink(missing_ok=True)
            
            response_data = {
                'success': True,
                'transactions': transactions,
                'message': f'Successfully processed {len(transactions)} transactions',
                'processing_time': round(processing_time, 2),
                'session_id': session_id,
                'primary_currency': primary_currency,
                'stats': {
                    'total_transactions': len(transactions),
                    'categories': len(set(t.get('category', 'unknown') for t in transactions)),
                    'currencies': list(set(t.get('currency', 'USD') for t in transactions)),
                    'date_range': {
                        'start': min(t.get('date') for t in transactions) if transactions else None,
                        'end': max(t.get('date') for t in transactions) if transactions else None
                    }
                },
                'status': {
                    'stage': 'completed',
                    'progress': 100,
                    'message': 'Processing complete'
                }
            }
            
            # Log successful processing
            logger.info(f"Successfully processed file for session {session_id}: {response_data['stats']}")
            
            return jsonify(response_data)
            
        except (ValidationError, ProcessingError) as e:
            # Clean up on validation/processing error
            file_path.unlink(missing_ok=True)
            raise  # Re-raise to be handled by error handlers
            
        except Exception as e:
            # Clean up on unexpected error
            file_path.unlink(missing_ok=True)
            logger.error(f"Unexpected error processing file {file.filename}: {str(e)}")
            return jsonify({
                'error': 'An unexpected error occurred while processing the file',
                'type': 'processing'
            }), 500
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({
            'error': 'File upload failed',
            'type': 'upload'
        }), 500

@app.route('/upload-status/<session_id>', methods=['GET'])
def check_upload_status(session_id):
    """Check the status of a file upload"""
    cache_key = f"upload_status_{session_id}"
    status = cache.get(cache_key)
    if status:
        return jsonify(status)
    return jsonify({'status': 'unknown'})

@app.route('/analyze', methods=['POST'])
@limiter.limit("30 per hour")
@validate_json_request(['transactions'])
@cache.memoize(timeout=300)  # Cache for 5 minutes
def analyze_transactions():
    """Enhanced analysis with comprehensive error handling and validation"""
    log_request_info()
    session_id = get_session_id()
    
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        logger.info(f"Analysis request received for session {session_id}")
        logger.info(f"Transaction count: {len(transactions)}")
        
        # Validate input data
        if not transactions:
            # Try to get from cache if no transactions provided
            cache_key = f"transactions_{session_id}"
            cached_transactions = cache.get(cache_key)
            if cached_transactions:
                transactions = cached_transactions
                logger.info(f"Using {len(transactions)} cached transactions for session {session_id}")
            else:
                logger.warning(f"No transactions provided and none found in cache for session {session_id}")
                return jsonify({
                    'error': 'No transactions provided and none found in cache',
                    'type': 'validation'
                }), 400
        
        # Comprehensive transaction validation
        validation_result = validate_transaction_data(transactions)
        if not validation_result['valid']:
            logger.error(f"Transaction validation failed: {validation_result['error']}")
            return jsonify({
                'error': validation_result['error'],
                'type': 'validation'
            }), 400
        
        start_time = time.time()
        logger.info(f"Starting analysis of {len(transactions)} transactions for session {session_id}")
        
        # Determine the primary currency from transactions
        currencies = {}
        for t in transactions:
            curr = t.get('currency', 'USD')
            currencies[curr] = currencies.get(curr, 0) + 1
        primary_currency = max(currencies.items(), key=lambda x: x[1])[0] if currencies else 'USD'
        
        logger.info(f"Primary currency determined: {primary_currency} (currencies found: {list(currencies.keys())})")

        # Analyze spending patterns with error handling
        logger.info("Analyzing spending patterns...")
        spending_analysis = budget_analyzer.analyze_spending(transactions)
        
        # Check if spending analysis returned an error
        if 'error' in spending_analysis:
            logger.error(f"Spending analysis failed: {spending_analysis['error']}")
            return jsonify({
                'error': f"Spending analysis failed: {spending_analysis['error']}",
                'type': 'processing'
            }), 500
        
        spending_analysis['currency'] = primary_currency  # Add currency to analysis
        logger.info("Spending analysis completed successfully")
        
        # Generate budget recommendations with error handling
        logger.info("Generating budget recommendations...")
        budget_recommendations = budget_analyzer.generate_recommendations(transactions, primary_currency)
        
        # Check if budget recommendations returned an error
        if 'error' in budget_recommendations:
            logger.error(f"Budget recommendations failed: {budget_recommendations['error']}")
            return jsonify({
                'error': f"Budget recommendations failed: {budget_recommendations['error']}",
                'type': 'processing'
            }), 500
        
        processing_time = time.time() - start_time
        logger.info(f"Analysis completed successfully in {processing_time:.2f}s for session {session_id}")
        
        # Log analysis summary
        logger.info(f"Analysis summary - Expenses: {spending_analysis.get('total_expenses', 0)}, "
                   f"Categories: {len(spending_analysis.get('category_breakdown', {}))}, "
                   f"Currency: {primary_currency}")
        
        return jsonify({
            'success': True,
            'spending_analysis': spending_analysis,
            'budget_recommendations': budget_recommendations,
            'processing_time': round(processing_time, 2),
            'session_id': session_id,
            'primary_currency': primary_currency,
            'transaction_count': len(transactions)
        })
        
    except Exception as e:
        logger.error(f"Unexpected error analyzing transactions for session {session_id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': f'Failed to analyze transactions: {str(e)}',
            'type': 'processing',
            'details': 'Check server logs for more information'
        }), 500

@app.route('/charts', methods=['POST'])
def generate_charts():
    data = request.get_json()
    transactions = data.get('transactions', [])
    
    if not transactions:
        return jsonify({'error': 'No transactions provided'}), 400
    
    try:
        print(f"Generating charts for {len(transactions)} transactions")
        
        # Generate various charts
        charts = {}
        
        # Get primary currency from session
        primary_currency = session.get('primary_currency', 'USD')
        
        # Monthly spending trend
        monthly_chart = budget_analyzer.create_monthly_spending_chart(transactions, primary_currency)
        charts['monthly_spending'] = monthly_chart
        print(f"Monthly chart: {monthly_chart}")
        
        # Category breakdown
        category_chart = budget_analyzer.create_category_chart(transactions, primary_currency)
        charts['category_breakdown'] = category_chart
        print(f"Category chart: {category_chart}")
        
        # Daily spending pattern
        daily_chart = budget_analyzer.create_daily_pattern_chart(transactions, primary_currency)
        charts['daily_pattern'] = daily_chart
        print(f"Daily chart: {daily_chart}")
        
        # Budget vs actual comparison
        budget_chart = budget_analyzer.create_budget_vs_actual_chart(transactions, primary_currency)
        charts['budget_vs_actual'] = budget_chart
        print(f"Budget chart: {budget_chart}")
        
        return jsonify({
            'success': True,
            'charts': charts
        })
        
    except Exception as e:
        logger.error(f"Error generating charts: {str(e)}")
        return jsonify({
            'error': f'Chart generation failed: {str(e)}',
            'type': 'processing'
        }), 500

@app.route('/convert-currency', methods=['POST'])
@limiter.limit("20 per hour")
def convert_currency():
    """Convert transactions to a target currency"""
    log_request_info()
    
    try:
        data = request.get_json()
        target_currency = data.get('target_currency', 'USD')
        transactions = data.get('transactions', [])
        
        if not transactions:
            # Try to get from cache
            session_id = get_session_id()
            cache_key = f"transactions_{session_id}"
            cached_transactions = cache.get(cache_key)
            if cached_transactions:
                transactions = cached_transactions
            else:
                return jsonify({
                    'error': 'No transactions provided and none found in cache',
                    'type': 'validation'
                }), 400
        
        if not isinstance(target_currency, str) or len(target_currency) != 3:
            return jsonify({
                'error': 'Invalid target currency. Must be a 3-letter currency code',
                'type': 'validation'
            }), 400
        
        # Convert transactions
        converted_transactions = enhanced_processor.currency_converter.convert_transactions(
            transactions, target_currency.upper()
        )
        
        # Get conversion summary
        conversion_summary = enhanced_processor.currency_converter.get_conversion_summary(
            transactions, target_currency.upper()
        )
        
        # Generate updated analysis with converted amounts
        budget_recommendations = budget_analyzer.generate_recommendations(
            converted_transactions, target_currency.upper()
        )
        
        spending_analysis = budget_analyzer.analyze_spending(converted_transactions)
        
        # Cache converted transactions
        session_id = get_session_id()
        cache_key = f"transactions_{session_id}"
        cache.set(cache_key, converted_transactions, timeout=3600)
        session['primary_currency'] = target_currency.upper()
        
        logger.info(f"Successfully converted {len(transactions)} transactions to {target_currency}")
        
        return jsonify({
            'success': True,
            'converted_transactions': converted_transactions,
            'target_currency': target_currency.upper(),
            'conversion_summary': conversion_summary,
            'budget_recommendations': budget_recommendations,
            'spending_analysis': spending_analysis,
            'message': f'Successfully converted {len(transactions)} transactions to {target_currency.upper()}'
        })
        
    except Exception as e:
        logger.error(f"Error converting currency: {str(e)}")
        return jsonify({
            'error': f'Currency conversion failed: {str(e)}',
            'type': 'processing'
        }), 500

@app.route('/upload-with-conversion', methods=['POST'])
@limiter.limit("10 per hour")
def upload_with_conversion():
    """Upload file and convert to target currency"""
    log_request_info()
    
    try:
        # Get target currency from form data
        target_currency = request.form.get('target_currency', 'USD').upper()
        
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'type': 'validation'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'type': 'validation'
            }), 400
        
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.pdf')):
            return jsonify({
                'error': 'Invalid file type. Only CSV and PDF files are supported.',
                'type': 'validation'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = Path(tempfile.gettempdir()) / f"{uuid.uuid4()}_{filename}"
        file.save(file_path)
        
        session_id = get_session_id()
        
        try:
            # Process with currency conversion
            if file.filename.lower().endswith('.csv'):
                result = enhanced_processor.normalize_and_convert_csv(
                    file_path, target_currency
                )
            else:
                # For PDF files, use regular processing then convert
                transactions = transaction_processor.process_file(str(file_path))
                converted_transactions = enhanced_processor.currency_converter.convert_transactions(
                    transactions, target_currency
                )
                
                result = {
                    'converted_transactions': converted_transactions,
                    'target_currency': target_currency,
                    'conversion_summary': enhanced_processor.currency_converter.get_conversion_summary(
                        transactions, target_currency
                    ),
                    'total_transactions': len(converted_transactions)
                }
            
            # Cache results
            cache_key = f"transactions_{session_id}"
            cache.set(cache_key, result['converted_transactions'], timeout=3600)
            session['primary_currency'] = target_currency
            
            # Clean up uploaded file
            file_path.unlink(missing_ok=True)
            
            logger.info(f"Successfully processed file with currency conversion to {target_currency}")
            
            return jsonify({
                'success': True,
                'transactions': result['converted_transactions'],
                'target_currency': target_currency,
                'conversion_summary': result['conversion_summary'],
                'converted_file_path': result.get('converted_file_path'),
                'total_transactions': result['total_transactions'],
                'session_id': session_id,
                'message': f'Successfully processed {result["total_transactions"]} transactions converted to {target_currency}'
            })
            
        except Exception as e:
            # Clean up on error
            file_path.unlink(missing_ok=True)
            raise
            
    except Exception as e:
        logger.error(f"Error in upload with conversion: {str(e)}")
        return jsonify({
            'error': f'File processing failed: {str(e)}',
            'type': 'processing'
        }), 500

@app.route('/exchange-rates', methods=['GET'])
def get_exchange_rates():
    """Get current exchange rates for supported currencies"""
    try:
        target_currency = request.args.get('base', 'USD').upper()
        currencies = request.args.get('currencies', '').split(',')
        
        if not currencies or currencies == ['']:
            # Return rates for common currencies
            currencies = ['EUR', 'GBP', 'INR', 'JPY', 'CAD', 'AUD', 'CHF', 'BRL', 'MYR', 'SGD']
        
        # Clean up currency codes
        currencies = [c.strip().upper() for c in currencies if c.strip()]
        
        rates = {}
        for currency in currencies:
            if currency != target_currency:
                rate = enhanced_processor.currency_converter.get_exchange_rate(currency, target_currency)
                rates[currency] = rate
        
        return jsonify({
            'success': True,
            'base_currency': target_currency,
            'rates': rates,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting exchange rates: {str(e)}")
        return jsonify({
            'error': f'Failed to get exchange rates: {str(e)}',
            'type': 'processing'
        }), 500

@app.route('/supported-currencies', methods=['GET'])
def get_supported_currencies():
    """Get list of supported currencies"""
    try:
        currencies = enhanced_processor.currency_converter.get_supported_currencies()
        
        return jsonify({
            'success': True,
            'currencies': currencies,
            'total_count': len(currencies)
        })
        
    except Exception as e:
        logger.error(f"Error getting supported currencies: {str(e)}")
        return jsonify({
            'error': f'Failed to get supported currencies: {str(e)}',
            'type': 'processing'
        }), 500

@app.route('/debug/logs', methods=['GET'])
def get_debug_logs():
    """Get recent server logs for debugging (development only)"""
    try:
        # Only allow in development mode
        if not app.debug:
            return jsonify({'error': 'Debug endpoint only available in development mode'}), 403
        
        # Read recent log entries
        log_file = 'financial_tracker.log'
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Get last 50 lines
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                return jsonify({
                    'success': True,
                    'logs': recent_lines,
                    'total_lines': len(lines)
                })
        else:
            return jsonify({
                'success': True,
                'logs': ['No log file found'],
                'total_lines': 0
            })
            
    except Exception as e:
        logger.error(f"Error getting debug logs: {str(e)}")
        return jsonify({
            'error': f'Failed to get debug logs: {str(e)}',
            'type': 'processing'
        }), 500

@app.route('/debug/test-analysis', methods=['POST'])
def test_analysis_debug():
    """Test analysis with sample data (development only)"""
    try:
        # Only allow in development mode
        if not app.debug:
            return jsonify({'error': 'Debug endpoint only available in development mode'}), 403
        
        # Create test transactions
        test_transactions = [
            {
                'date': '2024-01-01',
                'description': 'Test Transaction 1',
                'amount': -100.0,
                'category': 'food',
                'currency': 'USD',
                'type': 'debit'
            },
            {
                'date': '2024-01-02',
                'description': 'Test Transaction 2',
                'amount': 500.0,
                'category': 'income',
                'currency': 'USD',
                'type': 'credit'
            }
        ]
        
        logger.info("Running debug analysis test")
        
        # Test budget analyzer
        spending_analysis = budget_analyzer.analyze_spending(test_transactions)
        budget_recommendations = budget_analyzer.generate_recommendations(test_transactions, 'USD')
        
        return jsonify({
            'success': True,
            'test_transactions': test_transactions,
            'spending_analysis': spending_analysis,
            'budget_recommendations': budget_recommendations,
            'message': 'Debug analysis test completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Debug analysis test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'Debug analysis test failed: {str(e)}',
            'type': 'debug'
        }), 500

@app.route('/export', methods=['POST'])
def export_data():
    data = request.get_json()
    transactions = data.get('transactions', [])
    
    if not transactions:
        return jsonify({'error': 'No transactions provided'}), 400
    
    try:
        # Create DataFrame
        df = pd.DataFrame(transactions)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        
        # Send file
        return send_file(tmp_path, as_attachment=True, download_name='transactions.csv')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 