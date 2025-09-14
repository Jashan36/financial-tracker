#!/usr/bin/env python3
"""
Financial Tracker - Streamlit Version
A comprehensive personal finance tracking application with multi-currency support
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import tempfile
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Import existing modules (preserving all logic)
from transaction_processor import TransactionProcessor, ValidationError, ProcessingError
from budget_analyzer import BudgetAnalyzer
from enhanced_transaction_processor import EnhancedTransactionProcessor
from currency_converter import CurrencyConverter
from config import get_config

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

# Page configuration
st.set_page_config(
    page_title="Financial Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'primary_currency' not in st.session_state:
    st.session_state.primary_currency = 'USD'
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = 'idle'

# Initialize processors (using existing logic)
@st.cache_resource
def initialize_processors():
    """Initialize all processors with caching"""
    try:
        config = get_config()
        transaction_processor = TransactionProcessor(model_path=str(config.MODEL_PATH))
        budget_analyzer = BudgetAnalyzer()
        currency_converter = CurrencyConverter()
        enhanced_processor = EnhancedTransactionProcessor(
            enable_currency_conversion=True, 
            cache=None  # Streamlit handles caching differently
        )
        return transaction_processor, budget_analyzer, enhanced_processor, currency_converter
    except Exception as e:
        st.error(f"Failed to initialize processors: {str(e)}")
        return None, None, None, None

# Validation function (from Flask app)
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

# File upload and processing function
def process_uploaded_file(uploaded_file, transaction_processor):
    """Process uploaded file using existing logic"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        logger.info(f"Processing file: {uploaded_file.name}")
        
        # Process based on file type
        if uploaded_file.name.lower().endswith('.csv'):
            # Try different encodings
            encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            transactions = None
            
            for encoding in encodings_to_try:
                try:
                    transactions = transaction_processor.process_file(tmp_file_path, encoding=encoding)
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
                
        elif uploaded_file.name.lower().endswith('.pdf'):
            transactions = transaction_processor.process_file(tmp_file_path)
        else:
            raise ValidationError(f"Unsupported file type: {uploaded_file.name.split('.')[-1]}")
        
        if not transactions:
            raise ValidationError("No transactions found in the file")
        
        # Validate extracted transactions
        validation_result = validate_transaction_data(transactions)
        if not validation_result['valid']:
            raise ValidationError(f"File contains invalid transaction data: {validation_result['error']}")
        
        # Determine primary currency
        try:
            primary_currency = transaction_processor.determine_primary_currency(transactions)
            logger.info(f"Primary currency detected: {primary_currency}")
        except Exception as e:
            logger.warning(f"Could not determine primary currency: {e}")
            primary_currency = 'USD'
        
        # Clean up temporary file
        Path(tmp_file_path).unlink(missing_ok=True)
        
        return transactions, primary_currency
        
    except Exception as e:
        # Clean up on error
        Path(tmp_file_path).unlink(missing_ok=True)
        raise

# Analysis function
def perform_analysis(transactions, budget_analyzer, primary_currency):
    """Perform analysis using existing logic"""
    try:
        logger.info(f"Starting analysis of {len(transactions)} transactions")
        
        # Analyze spending patterns
        spending_analysis = budget_analyzer.analyze_spending(transactions)
        if 'error' in spending_analysis:
            raise Exception(f"Spending analysis failed: {spending_analysis['error']}")
        
        spending_analysis['currency'] = primary_currency
        
        # Generate budget recommendations
        budget_recommendations = budget_analyzer.generate_recommendations(transactions, primary_currency)
        if 'error' in budget_recommendations:
            raise Exception(f"Budget recommendations failed: {budget_recommendations['error']}")
        
        logger.info("Analysis completed successfully")
        
        return {
            'spending_analysis': spending_analysis,
            'budget_recommendations': budget_recommendations
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

# Main Streamlit app
def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">💰 Financial Tracker</h1>', unsafe_allow_html=True)
    st.markdown("### Comprehensive Personal Finance Analysis with Multi-Currency Support")
    
    # Initialize processors
    transaction_processor, budget_analyzer, enhanced_processor, currency_converter = initialize_processors()
    
    if not all([transaction_processor, budget_analyzer, enhanced_processor, currency_converter]):
        st.error("Failed to initialize application. Please check the logs.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")
        
        # File upload
        st.subheader("📁 Upload Transactions")
        uploaded_file = st.file_uploader(
            "Choose a CSV or PDF file",
            type=['csv', 'pdf'],
            help="Upload your bank statement or transaction file"
        )
        
        if uploaded_file is not None:
            if st.button("🔄 Process File", type="primary"):
                with st.spinner("Processing file..."):
                    try:
                        start_time = time.time()
                        transactions, primary_currency = process_uploaded_file(uploaded_file, transaction_processor)
                        
                        # Store in session state
                        st.session_state.transactions = transactions
                        st.session_state.primary_currency = primary_currency
                        
                        processing_time = time.time() - start_time
                        
                        st.success(f"✅ Successfully processed {len(transactions)} transactions in {processing_time:.2f}s")
                        st.info(f"Primary currency detected: {primary_currency}")
                        
                        # Clear previous analysis
                        st.session_state.analysis_results = {}
                        
                    except Exception as e:
                        st.error(f"❌ File processing failed: {str(e)}")
                        logger.error(f"File processing error: {str(e)}")
        
        # Analysis controls
        st.subheader("🔍 Analysis Controls")
        
        if st.session_state.transactions:
            if st.button("📈 Run Analysis", type="primary"):
                with st.spinner("Analyzing transactions..."):
                    try:
                        analysis_results = perform_analysis(
                            st.session_state.transactions, 
                            budget_analyzer, 
                            st.session_state.primary_currency
                        )
                        st.session_state.analysis_results = analysis_results
                        st.success("✅ Analysis completed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        logger.error(f"Analysis error: {str(e)}")
        
        # Currency conversion
        st.subheader("💱 Currency Conversion")
        
        if st.session_state.transactions:
            target_currency = st.selectbox(
                "Convert to currency:",
                ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD'],
                index=0
            )
            
            if st.button("🔄 Convert Currency"):
                with st.spinner("Converting currency..."):
                    try:
                        converted_transactions = enhanced_processor.currency_converter.convert_transactions(
                            st.session_state.transactions, 
                            target_currency
                        )
                        st.session_state.transactions = converted_transactions
                        st.session_state.primary_currency = target_currency
                        st.success(f"✅ Converted to {target_currency}")
                        
                        # Clear analysis since data changed
                        st.session_state.analysis_results = {}
                        
                    except Exception as e:
                        st.error(f"❌ Currency conversion failed: {str(e)}")
        
        # Clear data
        if st.button("🗑️ Clear All Data"):
            st.session_state.transactions = []
            st.session_state.analysis_results = {}
            st.session_state.primary_currency = 'USD'
            st.success("✅ Data cleared")
    
    # Main content area
    if not st.session_state.transactions:
        # Welcome screen
        st.markdown("""
        ### Welcome to Financial Tracker! 🎉
        
        **Get started by uploading your transaction file:**
        
        1. **📁 Upload File**: Use the sidebar to upload a CSV or PDF file
        2. **🔍 Analyze**: Click "Run Analysis" to get insights
        3. **📊 View Results**: Explore your financial data with interactive charts
        
        **Supported Features:**
        - ✅ Multi-currency support with automatic detection
        - ✅ PDF and CSV file processing
        - ✅ Advanced categorization using AI
        - ✅ Budget recommendations
        - ✅ Interactive visualizations
        - ✅ Currency conversion
        """)
        
        # Sample data option
        if st.button("📊 Load Sample Data"):
            try:
                # Load sample data
                sample_file = "sample_data.csv"
                if Path(sample_file).exists():
                    transactions, primary_currency = process_uploaded_file(
                        type('obj', (object,), {'name': sample_file, 'getvalue': lambda: Path(sample_file).read_bytes()})(),
                        transaction_processor
                    )
                    st.session_state.transactions = transactions
                    st.session_state.primary_currency = primary_currency
                    st.success("✅ Sample data loaded!")
                    st.rerun()
                else:
                    st.error("Sample data file not found")
            except Exception as e:
                st.error(f"Failed to load sample data: {str(e)}")
    
    else:
        # Display transaction data
        st.header("📋 Transaction Data")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", len(st.session_state.transactions))
        
        with col2:
            total_amount = sum(abs(t.get('amount', 0)) for t in st.session_state.transactions)
            st.metric("Total Amount", f"{total_amount:,.2f} {st.session_state.primary_currency}")
        
        with col3:
            categories = len(set(t.get('category', 'unknown') for t in st.session_state.transactions))
            st.metric("Categories", categories)
        
        with col4:
            currencies = len(set(t.get('currency', 'USD') for t in st.session_state.transactions))
            st.metric("Currencies", currencies)
        
        # Transaction table
        if st.checkbox("📋 Show Transaction Table"):
            try:
                df = pd.DataFrame(st.session_state.transactions)
                
                # Validate DataFrame
                if df.empty:
                    st.warning("⚠️ No transaction data to display.")
                else:
                    # Clean up the DataFrame for display
                    if 'date' in df.columns:
                        try:
                            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                        except:
                            pass  # Keep original format if conversion fails
                    
                    st.dataframe(df, use_container_width=True)
                    
                    # Show summary statistics
                    st.subheader("📊 Data Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Rows", len(df))
                        st.metric("Columns", len(df.columns))
                    
                    with col2:
                        if 'amount' in df.columns:
                            try:
                                total_amount = df['amount'].astype(float).sum()
                                st.metric("Total Amount", f"{total_amount:,.2f}")
                            except:
                                st.metric("Total Amount", "N/A")
                        
                        if 'category' in df.columns:
                            unique_categories = df['category'].nunique()
                            st.metric("Unique Categories", unique_categories)
                            
            except Exception as e:
                st.error(f"❌ Error displaying transaction table: {str(e)}")
                logger.error(f"Table display error: {str(e)}")
                
                # Show raw data for debugging
                st.subheader("🔍 Raw Transaction Data")
                st.json(st.session_state.transactions[:5])  # Show first 5 transactions
        
        # Analysis results
        if st.session_state.analysis_results:
            st.header("📊 Analysis Results")
            
            try:
                spending_analysis = st.session_state.analysis_results.get('spending_analysis', {})
                budget_recommendations = st.session_state.analysis_results.get('budget_recommendations', {})
                
                # Validate analysis results
                if not spending_analysis and not budget_recommendations:
                    st.warning("⚠️ No analysis results available.")
                    return
            
            # Spending analysis
            if spending_analysis and 'error' not in spending_analysis:
                st.subheader("💰 Spending Analysis")
                
                # Key metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_expenses = spending_analysis.get('total_expenses', 0)
                    st.metric("Total Expenses", f"{total_expenses:,.2f} {st.session_state.primary_currency}")
                
                with col2:
                    avg_daily = spending_analysis.get('average_daily_spending', 0)
                    st.metric("Average Daily", f"{avg_daily:,.2f} {st.session_state.primary_currency}")
                
                with col3:
                    monthly_income = spending_analysis.get('monthly_income', 0)
                    st.metric("Monthly Income", f"{monthly_income:,.2f} {st.session_state.primary_currency}")
                
                # Category breakdown
                if 'category_breakdown' in spending_analysis:
                    st.subheader("📊 Category Breakdown")
                    
                    category_data = spending_analysis['category_breakdown']
                    if category_data:
                        # Clean and validate data
                        categories = []
                        amounts = []
                        
                        for category, amount in category_data.items():
                            if category and amount is not None:
                                try:
                                    # Ensure amount is numeric
                                    numeric_amount = float(amount)
                                    if not pd.isna(numeric_amount):
                                        categories.append(str(category))
                                        amounts.append(numeric_amount)
                                except (ValueError, TypeError):
                                    continue
                        
                        # Only create charts if we have valid data
                        if categories and amounts and len(categories) == len(amounts):
                            # Create pie chart
                            fig = px.pie(
                                values=amounts,
                                names=categories,
                                title="Spending by Category"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Create bar chart
                            fig2 = px.bar(
                                x=categories,
                                y=amounts,
                                title="Spending by Category (Bar Chart)",
                                labels={'x': 'Category', 'y': f'Amount ({st.session_state.primary_currency})'}
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.warning("⚠️ Category data is incomplete or invalid. Cannot display charts.")
                            
                            # Display raw data for debugging
                            st.subheader("Raw Category Data:")
                            st.json(category_data)
            
            # Budget recommendations
            if budget_recommendations and 'error' not in budget_recommendations:
                st.subheader("🎯 Budget Recommendations")
                
                if 'recommendations' in budget_recommendations:
                    recommendations = budget_recommendations['recommendations']
                    
                    for category, data in recommendations.items():
                        with st.expander(f"💡 {category}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Recommended:** {data.get('formatted_recommended', 'N/A')}")
                                st.write(f"**Current:** {data.get('formatted_current', 'N/A')}")
                            
                            with col2:
                                status = data.get('status', 'Unknown')
                                if 'Over Budget' in status:
                                    st.error(f"⚠️ {status}")
                                elif 'Under Budget' in status:
                                    st.success(f"✅ {status}")
                                else:
                                    st.info(f"ℹ️ {status}")
            
            # Alerts
            if 'alerts' in budget_recommendations:
                alerts = budget_recommendations['alerts']
                if alerts:
                    st.subheader("🚨 Budget Alerts")
                    for alert in alerts:
                        st.warning(alert)
            
            except Exception as e:
                st.error(f"❌ Error displaying analysis results: {str(e)}")
                logger.error(f"Analysis display error: {str(e)}")
                
                # Show raw data for debugging
                st.subheader("🔍 Debug Information")
                st.json(st.session_state.analysis_results)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💰 Financial Tracker - Built with Streamlit | Multi-Currency Support | AI-Powered Analysis</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
