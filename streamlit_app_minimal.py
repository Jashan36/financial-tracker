#!/usr/bin/env python3
"""
Financial Tracker - Minimal Streamlit Version
A lightweight version that works without heavy dependencies
"""

import streamlit as st
import pandas as pd
import logging
import tempfile
import time
from pathlib import Path
import json
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Financial Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'primary_currency' not in st.session_state:
    st.session_state.primary_currency = 'USD'

# Simple CSV processor (no heavy dependencies)
def process_csv_file(uploaded_file):
    """Simple CSV processing without external dependencies"""
    try:
        # Read CSV content
        content = uploaded_file.getvalue().decode('utf-8')
        lines = content.strip().split('\n')
        
        if len(lines) < 2:
            raise Exception("CSV file must have at least a header and one data row")
        
        # Parse header
        header = lines[0].split(',')
        header = [col.strip().lower() for col in header]
        
        # Check required columns
        required_columns = ['date', 'description', 'amount']
        missing_columns = [col for col in required_columns if col not in header]
        
        if missing_columns:
            raise Exception(f"Missing required columns: {missing_columns}")
        
        # Parse data rows
        transactions = []
        for i, line in enumerate(lines[1:], 1):
            if not line.strip():
                continue
                
            try:
                values = line.split(',')
                if len(values) < len(header):
                    continue
                
                # Create transaction record
                transaction = {}
                for j, col in enumerate(header):
                    if j < len(values):
                        value = values[j].strip()
                        
                        if col == 'amount':
                            try:
                                transaction['amount'] = float(value)
                            except ValueError:
                                continue
                        elif col == 'date':
                            transaction['date'] = value
                        elif col == 'description':
                            transaction['description'] = value
                        else:
                            transaction[col] = value
                
                # Add default category if missing
                if 'category' not in transaction:
                    transaction['category'] = 'uncategorized'
                
                # Add default currency if missing
                if 'currency' not in transaction:
                    transaction['currency'] = 'USD'
                
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Skipping row {i}: {e}")
                continue
        
        if not transactions:
            raise Exception("No valid transactions found in the file")
        
        # Determine primary currency
        currencies = {}
        for t in transactions:
            curr = t.get('currency', 'USD')
            currencies[curr] = currencies.get(curr, 0) + 1
        
        primary_currency = max(currencies.items(), key=lambda x: x[1])[0] if currencies else 'USD'
        
        return transactions, primary_currency
        
    except Exception as e:
        raise Exception(f"Failed to process CSV file: {str(e)}")

# Simple analysis function
def simple_analysis(transactions):
    """Simple analysis without heavy dependencies"""
    try:
        if not transactions:
            return {}
        
        # Basic spending analysis
        total_amount = sum(abs(t.get('amount', 0)) for t in transactions)
        expenses = sum(abs(t.get('amount', 0)) for t in transactions if t.get('amount', 0) < 0)
        income = sum(t.get('amount', 0) for t in transactions if t.get('amount', 0) > 0)
        
        # Category breakdown
        category_totals = {}
        for t in transactions:
            category = t.get('category', 'uncategorized')
            amount = abs(t.get('amount', 0))
            category_totals[category] = category_totals.get(category, 0) + amount
        
        # Currency breakdown
        currency_totals = {}
        for t in transactions:
            currency = t.get('currency', 'USD')
            amount = abs(t.get('amount', 0))
            currency_totals[currency] = currency_totals.get(currency, 0) + amount
        
        return {
            'total_transactions': len(transactions),
            'total_amount': total_amount,
            'total_expenses': expenses,
            'total_income': income,
            'category_breakdown': category_totals,
            'currency_breakdown': currency_totals,
            'average_transaction': total_amount / len(transactions) if transactions else 0
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {'error': str(e)}

# Main app
def main():
    """Main Streamlit application"""
    
    try:
        # Header
        st.title("💰 Financial Tracker (Minimal Version)")
        st.markdown("### Simple Personal Finance Analysis")
        
        # Sidebar
        with st.sidebar:
            st.header("📊 Navigation")
            
            # File upload
            st.subheader("📁 Upload CSV File")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="Upload your transaction CSV file"
            )
            
            if uploaded_file is not None:
                if st.button("🔄 Process File", type="primary"):
                    with st.spinner("Processing file..."):
                        try:
                            start_time = time.time()
                            transactions, primary_currency = process_csv_file(uploaded_file)
                            
                            # Store in session state
                            st.session_state.transactions = transactions
                            st.session_state.primary_currency = primary_currency
                            
                            processing_time = time.time() - start_time
                            
                            st.success(f"✅ Successfully processed {len(transactions)} transactions in {processing_time:.2f}s")
                            st.info(f"Primary currency detected: {primary_currency}")
                            
                        except Exception as e:
                            st.error(f"❌ File processing failed: {str(e)}")
                            logger.error(f"File processing error: {str(e)}")
            
            # Clear data
            if st.button("🗑️ Clear All Data"):
                st.session_state.transactions = []
                st.session_state.primary_currency = 'USD'
                st.success("✅ Data cleared")
        
        # Main content
        if not st.session_state.transactions:
            # Welcome screen
            st.markdown("""
            ### Welcome to Financial Tracker! 🎉
            
            **This is a minimal version that works without heavy dependencies.**
            
            **To get started:**
            1. **📁 Upload CSV**: Use the sidebar to upload a CSV file
            2. **📊 View Analysis**: See your transaction analysis below
            
            **CSV Format Required:**
            - Must have columns: `date`, `description`, `amount`
            - Optional columns: `category`, `currency`
            - Date format: YYYY-MM-DD or MM/DD/YYYY
            - Amount: Positive for income, negative for expenses
            
            **Example CSV:**
            ```
            date,description,amount,category,currency
            2024-01-01,Grocery Store,-50.00,food,USD
            2024-01-02,Salary,3000.00,income,USD
            ```
            """)
            
            # Sample data
            if st.button("📊 Create Sample Data"):
                sample_transactions = [
                    {'date': '2024-01-01', 'description': 'Grocery Store', 'amount': -50.0, 'category': 'food', 'currency': 'USD'},
                    {'date': '2024-01-02', 'description': 'Gas Station', 'amount': -30.0, 'category': 'transport', 'currency': 'USD'},
                    {'date': '2024-01-03', 'description': 'Salary', 'amount': 3000.0, 'category': 'income', 'currency': 'USD'},
                    {'date': '2024-01-04', 'description': 'Restaurant', 'amount': -25.0, 'category': 'food', 'currency': 'USD'},
                    {'date': '2024-01-05', 'description': 'Coffee Shop', 'amount': -5.0, 'category': 'food', 'currency': 'USD'},
                ]
                
                st.session_state.transactions = sample_transactions
                st.session_state.primary_currency = 'USD'
                st.success("✅ Sample data created!")
                st.rerun()
        
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
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="transactions.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error displaying table: {str(e)}")
            
            # Analysis
            st.header("📊 Analysis")
            
            try:
                analysis = simple_analysis(st.session_state.transactions)
                
                if 'error' in analysis:
                    st.error(f"❌ Analysis failed: {analysis['error']}")
                else:
                    # Key metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Expenses", f"{analysis['total_expenses']:,.2f} {st.session_state.primary_currency}")
                    
                    with col2:
                        st.metric("Total Income", f"{analysis['total_income']:,.2f} {st.session_state.primary_currency}")
                    
                    with col3:
                        st.metric("Average Transaction", f"{analysis['average_transaction']:,.2f} {st.session_state.primary_currency}")
                    
                    # Category breakdown
                    if analysis['category_breakdown']:
                        st.subheader("📊 Category Breakdown")
                        
                        category_df = pd.DataFrame([
                            {'Category': cat, 'Amount': amount}
                            for cat, amount in analysis['category_breakdown'].items()
                        ]).sort_values('Amount', ascending=False)
                        
                        st.dataframe(category_df, use_container_width=True)
                        
                        # Simple bar chart using Streamlit's built-in chart
                        st.bar_chart(category_df.set_index('Category'))
                    
                    # Currency breakdown
                    if analysis['currency_breakdown']:
                        st.subheader("💱 Currency Breakdown")
                        
                        currency_df = pd.DataFrame([
                            {'Currency': curr, 'Amount': amount}
                            for curr, amount in analysis['currency_breakdown'].items()
                        ]).sort_values('Amount', ascending=False)
                        
                        st.dataframe(currency_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Analysis error: {str(e)}")
                logger.error(f"Analysis error: {str(e)}")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>💰 Financial Tracker - Minimal Version | Basic CSV Analysis</p>
            <p>For full features, install all dependencies and use streamlit_app.py</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()

