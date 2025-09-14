import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json

class BudgetAnalyzer:
    def __init__(self):
        self.standard_budgets = {
            'food': 0.15,        # 15% of income
            'transport': 0.10,    # 10% of income
            'entertainment': 0.05, # 5% of income
            'shopping': 0.10,     # 10% of income
            'utilities': 0.08,    # 8% of income
            'healthcare': 0.08,   # 8% of income
            'education': 0.05,    # 5% of income
            'travel': 0.05,       # 5% of income
            'insurance': 0.08,    # 8% of income
            'investment': 0.20,   # 20% of income
            'other': 0.06         # 6% of income
        }
        
        # Currency formatting information
        self.currency_formats = {
            'USD': {'symbol': '$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'INR': {'symbol': '₹', 'position': 'before', 'decimals': 2, 'separator': ','},
            'EUR': {'symbol': '€', 'position': 'after', 'decimals': 2, 'separator': ','},
            'GBP': {'symbol': '£', 'position': 'before', 'decimals': 2, 'separator': ','},
            'JPY': {'symbol': '¥', 'position': 'before', 'decimals': 0, 'separator': ','},
            'CAD': {'symbol': 'C$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'AUD': {'symbol': 'A$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'CHF': {'symbol': 'CHF', 'position': 'after', 'decimals': 2, 'separator': ','},
            'SEK': {'symbol': 'kr', 'position': 'after', 'decimals': 2, 'separator': ','},
            'NOK': {'symbol': 'kr', 'position': 'after', 'decimals': 2, 'separator': ','},
            'DKK': {'symbol': 'kr', 'position': 'after', 'decimals': 2, 'separator': ','},
            'PLN': {'symbol': 'zł', 'position': 'after', 'decimals': 2, 'separator': ','},
            'CZK': {'symbol': 'Kč', 'position': 'after', 'decimals': 2, 'separator': ','},
            'HUF': {'symbol': 'Ft', 'position': 'after', 'decimals': 2, 'separator': ','},
            'RUB': {'symbol': '₽', 'position': 'after', 'decimals': 2, 'separator': ','},
            'BRL': {'symbol': 'R$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MXN': {'symbol': '$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ARS': {'symbol': '$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'CLP': {'symbol': '$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'COP': {'symbol': '$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'PEN': {'symbol': 'S/', 'position': 'before', 'decimals': 2, 'separator': ','},
            'UYU': {'symbol': '$U', 'position': 'before', 'decimals': 2, 'separator': ','},
            'VES': {'symbol': 'Bs.S', 'position': 'before', 'decimals': 2, 'separator': ','},
            'CNY': {'symbol': '¥', 'position': 'before', 'decimals': 2, 'separator': ','},
            'KRW': {'symbol': '₩', 'position': 'before', 'decimals': 0, 'separator': ','},
            'THB': {'symbol': '฿', 'position': 'before', 'decimals': 2, 'separator': ','},
            'VND': {'symbol': '₫', 'position': 'after', 'decimals': 0, 'separator': ','},
            'IDR': {'symbol': 'Rp', 'position': 'before', 'decimals': 0, 'separator': ','},
            'MYR': {'symbol': 'RM', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SGD': {'symbol': 'S$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'HKD': {'symbol': 'HK$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'TWD': {'symbol': 'NT$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'NZD': {'symbol': 'NZ$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'PHP': {'symbol': '₱', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ZAR': {'symbol': 'R', 'position': 'before', 'decimals': 2, 'separator': ','},
            'EGP': {'symbol': '£', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MAD': {'symbol': 'MAD', 'position': 'after', 'decimals': 2, 'separator': ','},
            'NGN': {'symbol': '₦', 'position': 'before', 'decimals': 2, 'separator': ','},
            'KES': {'symbol': 'KSh', 'position': 'before', 'decimals': 2, 'separator': ','},
            'GHS': {'symbol': '₵', 'position': 'before', 'decimals': 2, 'separator': ','},
            'TZS': {'symbol': 'TSh', 'position': 'before', 'decimals': 2, 'separator': ','},
            'UGX': {'symbol': 'USh', 'position': 'before', 'decimals': 2, 'separator': ','},
            'RWF': {'symbol': 'RF', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ETB': {'symbol': 'Br', 'position': 'before', 'decimals': 2, 'separator': ','},
            'TRY': {'symbol': '₺', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ILS': {'symbol': '₪', 'position': 'before', 'decimals': 2, 'separator': ','},
            'AED': {'symbol': 'د.إ', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SAR': {'symbol': 'ر.س', 'position': 'before', 'decimals': 2, 'separator': ','},
            'QAR': {'symbol': 'ر.ق', 'position': 'before', 'decimals': 2, 'separator': ','},
            'KWD': {'symbol': 'د.ك', 'position': 'before', 'decimals': 3, 'separator': ','},
            'BHD': {'symbol': 'د.ب', 'position': 'before', 'decimals': 3, 'separator': ','},
            'OMR': {'symbol': 'ر.ع.', 'position': 'before', 'decimals': 3, 'separator': ','},
            'JOD': {'symbol': 'د.ا', 'position': 'before', 'decimals': 3, 'separator': ','},
            'LBP': {'symbol': 'ل.ل', 'position': 'before', 'decimals': 2, 'separator': ','},
            'PKR': {'symbol': '₨', 'position': 'before', 'decimals': 2, 'separator': ','},
            'LKR': {'symbol': '₨', 'position': 'before', 'decimals': 2, 'separator': ','},
            'NPR': {'symbol': '₨', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BDT': {'symbol': '৳', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MMK': {'symbol': 'K', 'position': 'before', 'decimals': 2, 'separator': ','},
            'LAK': {'symbol': '₭', 'position': 'before', 'decimals': 2, 'separator': ','},
            'KHR': {'symbol': '៛', 'position': 'after', 'decimals': 2, 'separator': ','},
            'MOP': {'symbol': 'MOP$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BND': {'symbol': 'B$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'FJD': {'symbol': 'FJ$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'PGK': {'symbol': 'K', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SBD': {'symbol': 'SI$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'TOP': {'symbol': 'T$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'VUV': {'symbol': 'VT', 'position': 'after', 'decimals': 0, 'separator': ','},
            'WST': {'symbol': 'WS$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'XPF': {'symbol': '₣', 'position': 'after', 'decimals': 0, 'separator': ','},
            'AOA': {'symbol': 'Kz', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BWP': {'symbol': 'P', 'position': 'before', 'decimals': 2, 'separator': ','},
            'LSL': {'symbol': 'L', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SZL': {'symbol': 'E', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ZMW': {'symbol': 'ZK', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BIF': {'symbol': 'FBu', 'position': 'before', 'decimals': 2, 'separator': ','},
            'DJF': {'symbol': 'Fdj', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ERN': {'symbol': 'Nfk', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SOS': {'symbol': 'S', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SSP': {'symbol': '£', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SYP': {'symbol': '£', 'position': 'before', 'decimals': 2, 'separator': ','},
            'YER': {'symbol': '﷼', 'position': 'before', 'decimals': 2, 'separator': ','},
            'AFN': {'symbol': '؋', 'position': 'before', 'decimals': 2, 'separator': ','},
            'AMD': {'symbol': '֏', 'position': 'before', 'decimals': 2, 'separator': ','},
            'AZN': {'symbol': '₼', 'position': 'before', 'decimals': 2, 'separator': ','},
            'GEL': {'symbol': '₾', 'position': 'before', 'decimals': 2, 'separator': ','},
            'KGS': {'symbol': 'лв', 'position': 'after', 'decimals': 2, 'separator': ','},
            'KZT': {'symbol': '₸', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MDL': {'symbol': 'L', 'position': 'before', 'decimals': 2, 'separator': ','},
            'TJS': {'symbol': 'SM', 'position': 'before', 'decimals': 2, 'separator': ','},
            'TMT': {'symbol': 'T', 'position': 'before', 'decimals': 2, 'separator': ','},
            'UZS': {'symbol': 'лв', 'position': 'after', 'decimals': 2, 'separator': ','},
            'UAH': {'symbol': '₴', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BYN': {'symbol': 'Br', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MKD': {'symbol': 'ден', 'position': 'after', 'decimals': 2, 'separator': ','},
            'RSD': {'symbol': 'дин.', 'position': 'after', 'decimals': 2, 'separator': ','},
            'BAM': {'symbol': 'КМ', 'position': 'after', 'decimals': 2, 'separator': ','},
            'BGN': {'symbol': 'лв', 'position': 'after', 'decimals': 2, 'separator': ','},
            'HRK': {'symbol': 'kn', 'position': 'after', 'decimals': 2, 'separator': ','},
            'RON': {'symbol': 'lei', 'position': 'after', 'decimals': 2, 'separator': ','},
            'ALL': {'symbol': 'L', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ISK': {'symbol': 'kr', 'position': 'after', 'decimals': 0, 'separator': ','},
            'MDL': {'symbol': 'L', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MGA': {'symbol': 'Ar', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MUR': {'symbol': '₨', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SCR': {'symbol': '₨', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SLL': {'symbol': 'Le', 'position': 'before', 'decimals': 2, 'separator': ','},
            'LRD': {'symbol': 'L$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'CDF': {'symbol': 'FC', 'position': 'before', 'decimals': 2, 'separator': ','},
            'XAF': {'symbol': 'FCFA', 'position': 'after', 'decimals': 0, 'separator': ','},
            'XOF': {'symbol': 'CFA', 'position': 'after', 'decimals': 0, 'separator': ','},
            'KMF': {'symbol': 'CF', 'position': 'before', 'decimals': 2, 'separator': ','},
            'STN': {'symbol': 'Db', 'position': 'before', 'decimals': 2, 'separator': ','},
            'MZN': {'symbol': 'MT', 'position': 'before', 'decimals': 2, 'separator': ','},
            'NAD': {'symbol': 'N$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'ZWL': {'symbol': 'Z$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BMD': {'symbol': 'B$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BSD': {'symbol': 'B$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BBD': {'symbol': 'Bds$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'BZD': {'symbol': 'BZ$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'XCD': {'symbol': 'EC$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'DOP': {'symbol': 'RD$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'GTQ': {'symbol': 'Q', 'position': 'before', 'decimals': 2, 'separator': ','},
            'HNL': {'symbol': 'L', 'position': 'before', 'decimals': 2, 'separator': ','},
            'JMD': {'symbol': 'J$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'NIO': {'symbol': 'C$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'PYG': {'symbol': '₲', 'position': 'before', 'decimals': 2, 'separator': ','},
            'SRD': {'symbol': 'Sr$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'TTD': {'symbol': 'TT$', 'position': 'before', 'decimals': 2, 'separator': ','},
            'VES': {'symbol': 'Bs.S', 'position': 'before', 'decimals': 2, 'separator': ','},
            'XDR': {'symbol': 'XDR', 'position': 'after', 'decimals': 2, 'separator': ','},
            'BTC': {'symbol': '₿', 'position': 'before', 'decimals': 8, 'separator': ','},
            'ETH': {'symbol': 'Ξ', 'position': 'before', 'decimals': 6, 'separator': ','}
        }
    
    def format_currency(self, amount, currency='USD'):
        """Format amount according to currency conventions"""
        if currency not in self.currency_formats:
            # Fallback for unknown currencies
            return f"{amount:,.2f} {currency}"
        
        format_info = self.currency_formats[currency]
        symbol = format_info['symbol']
        position = format_info['position']
        decimals = format_info['decimals']
        
        # Format the number with appropriate decimal places
        if decimals == 0:
            formatted_amount = f"{amount:,.0f}"
        else:
            formatted_amount = f"{amount:,.{decimals}f}"
        
        # Add currency symbol in correct position
        if position == 'before':
            return f"{symbol}{formatted_amount}"
        else:
            return f"{formatted_amount} {symbol}"
    
    def analyze_spending(self, transactions):
        """Analyze spending patterns and provide insights with multi-currency support"""
        if not transactions:
            return {}
        
        try:
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            return {'error': f'Failed to process transaction data: {str(e)}'}
        
        try:
            print(f"DataFrame shape: {df.shape}")
            print(f"Amount range: {df['amount'].min()} to {df['amount'].max()}")
            print(f"Sample amounts: {df['amount'].head().tolist()}")
            
            # Get currency information
            currencies = df['currency'].unique() if 'currency' in df.columns else ['USD']
            primary_currency = currencies[0] if len(currencies) == 1 else self._determine_primary_currency(df)
            
            print(f"Currencies found: {currencies}")
            print(f"Primary currency: {primary_currency}")
            
            # Filter out credits (income)
            expenses = df[df['amount'] < 0].copy()
            expenses['amount'] = expenses['amount'].abs()
            
            print(f"Expenses count: {len(expenses)}")
            
            if expenses.empty:
                return {'message': 'No expenses found in transactions', 'currency': primary_currency}
            
            # Basic statistics
            total_expenses = expenses['amount'].sum()
            avg_daily_expense = expenses.groupby(expenses['date'].dt.date)['amount'].sum().mean()
            
            # Category analysis
            category_spending = expenses.groupby('category')['amount'].agg(['sum', 'count', 'mean']).round(2)
            category_spending['percentage'] = (category_spending['sum'] / total_expenses * 100).round(2)
            
            # Monthly analysis
            monthly_spending = expenses.groupby(expenses['date'].dt.to_period('M'))['amount'].sum()
            
            # Spending patterns
            daily_pattern = expenses.groupby(expenses['date'].dt.dayofweek)['amount'].sum()
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_pattern.index = day_names
            
            # Top merchants
            top_merchants = expenses.groupby('description')['amount'].sum().sort_values(ascending=False).head(10)
            
            analysis = {
                'total_expenses': round(total_expenses, 2),
                'avg_daily_expense': round(avg_daily_expense, 2),
                'total_transactions': len(expenses),
                'currency': primary_currency,
                'currencies_found': list(currencies),
                'category_breakdown': category_spending.to_dict('index'),
                'monthly_spending': monthly_spending.to_dict(),
                'daily_pattern': daily_pattern.to_dict(),
                'top_merchants': top_merchants.to_dict(),
                'analysis_period': {
                    'start_date': expenses['date'].min().strftime('%Y-%m-%d'),
                    'end_date': expenses['date'].max().strftime('%Y-%m-%d'),
                    'days': (expenses['date'].max() - expenses['date'].min()).days
                }
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error in analyze_spending analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'error': f'Failed to analyze spending patterns: {str(e)}'}
    
    def _determine_primary_currency(self, df):
        """Determine primary currency from transaction data"""
        try:
            if 'currency' not in df.columns:
                return 'USD'
            
            # Method 1: By transaction volume (total absolute amount)
            # Fix: Use copy to avoid modifying original DataFrame
            df_copy = df.copy()
            df_copy['abs_amount'] = df_copy['amount'].abs()
            currency_totals = df_copy.groupby('currency')['abs_amount'].sum()
            
            # Method 2: By transaction count (backup method)
            currency_counts = df['currency'].value_counts()
            
            # Use volume-based detection (more reliable for financial data)
            if not currency_totals.empty:
                primary_currency = currency_totals.idxmax()
                print(f"Primary currency determined by volume: {primary_currency} (total: {currency_totals[primary_currency]:,.2f})")
                return primary_currency
            
            # Fallback to frequency-based detection
            elif not currency_counts.empty:
                primary_currency = currency_counts.index[0]  # Most frequent currency
                print(f"Primary currency determined by frequency: {primary_currency} (count: {currency_counts.iloc[0]})")
                return primary_currency
            
            # Final fallback
            else:
                print("No currency data found, defaulting to USD")
                return 'USD'
                
        except Exception as e:
            print(f"Could not determine primary currency: {e}")
            import traceback
            traceback.print_exc()
            return 'USD'  # Default fallback
    
    def generate_recommendations(self, transactions, primary_currency=None):
        """Generate budget recommendations based on spending patterns with proper currency support"""
        if not transactions:
            return {}
        
        try:
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'])
        except Exception as e:
            print(f"Error creating DataFrame in generate_recommendations: {e}")
            return {'error': f'Failed to process transaction data: {str(e)}'}
        
        try:
            # Detect primary currency if not provided
            if primary_currency is None:
                primary_currency = self._determine_primary_currency(df)
            
            # Calculate monthly income (credits)
            monthly_income = df[df['amount'] > 0].groupby(df['date'].dt.to_period('M'))['amount'].sum().mean()
            
            if monthly_income == 0:
                return {'message': 'No income data found to generate recommendations', 'currency': primary_currency}
            
            # Calculate current spending by category
            expenses = df[df['amount'] < 0].copy()
            expenses['amount'] = expenses['amount'].abs()
            current_spending = expenses.groupby('category')['amount'].sum()
            
            recommendations = {
                'monthly_income': round(monthly_income, 2),
                'monthly_income_formatted': self.format_currency(monthly_income, primary_currency),
                'currency': primary_currency,
                'recommended_budgets': {},
                'savings_potential': {},
                'alerts': []
            }
            
            # Generate category-specific recommendations
            for category, percentage in self.standard_budgets.items():
                recommended_amount = monthly_income * percentage
                current_amount = current_spending.get(category, 0)
                
                recommendations['recommended_budgets'][category] = {
                    'recommended': round(recommended_amount, 2),
                    'current': round(current_amount, 2),
                    'difference': round(recommended_amount - current_amount, 2),
                    'percentage_of_income': round(percentage * 100, 1),
                    'formatted_recommended': self.format_currency(recommended_amount, primary_currency),
                    'formatted_current': self.format_currency(current_amount, primary_currency),
                    'formatted_difference': self.format_currency(recommended_amount - current_amount, primary_currency),
                    'currency': primary_currency,
                    'status': 'Under Budget' if current_amount <= recommended_amount else 'Over Budget'
                }
                
                # Calculate savings potential
                if current_amount > recommended_amount:
                    savings = current_amount - recommended_amount
                    recommendations['savings_potential'][category] = round(savings, 2)
                    
                    # Generate alerts for overspending
                    if savings > recommended_amount * 0.2:  # 20% over budget
                        formatted_savings = self.format_currency(savings, primary_currency)
                        recommendations['alerts'].append({
                            'category': category,
                            'message': f'You are spending {formatted_savings} more than recommended in {category}',
                            'severity': 'high' if savings > recommended_amount * 0.5 else 'medium'
                        })
            
            # Overall recommendations
            total_recommended = monthly_income * 0.8  # 80% for expenses, 20% for savings
            total_current = current_spending.sum()
            
            if total_current > total_recommended:
                formatted_current = self.format_currency(total_current, primary_currency)
                formatted_recommended = self.format_currency(total_recommended, primary_currency)
                recommendations['alerts'].append({
                    'category': 'overall',
                    'message': f'Your total spending ({formatted_current}) exceeds the recommended budget ({formatted_recommended})',
                    'severity': 'high'
                })
            
            # Savings recommendations
            if monthly_income > 0:
                savings_rate = (monthly_income - total_current) / monthly_income
                if savings_rate < 0.2:
                    recommendations['alerts'].append({
                        'category': 'savings',
                        'message': f'Your savings rate is {savings_rate:.1%}. Consider increasing it to at least 20%',
                        'severity': 'medium'
                    })
            
            return recommendations
            
        except Exception as e:
            print(f"Error in generate_recommendations analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'error': f'Failed to generate budget recommendations: {str(e)}'}
    
    def create_monthly_spending_chart(self, transactions, primary_currency=None):
        """Create monthly spending trend chart with proper currency support"""
        if not transactions:
            print("No transactions provided for monthly chart")
            return {}
        
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Detect primary currency if not provided
        if primary_currency is None:
            primary_currency = self._determine_primary_currency(df)
        
        print(f"Monthly chart - DataFrame shape: {df.shape}")
        print(f"Monthly chart - Amount range: {df['amount'].min()} to {df['amount'].max()}")
        print(f"Monthly chart - Primary currency: {primary_currency}")
        
        # Filter expenses and group by month
        expenses = df[df['amount'] < 0].copy()
        expenses['amount'] = expenses['amount'].abs()
        
        print(f"Monthly chart - Expenses count: {len(expenses)}")
        
        if expenses.empty:
            print("No expenses found for monthly chart")
            return {}
        
        monthly_data = expenses.groupby(expenses['date'].dt.to_period('M'))['amount'].sum().reset_index()
        monthly_data['date'] = monthly_data['date'].astype(str)
        
        print(f"Monthly chart - Monthly data: {monthly_data}")
        
        # Format currency label
        currency_label = f"Total Spending ({primary_currency})"
        
        # Create chart
        fig = px.line(monthly_data, x='date', y='amount', 
                     title='Monthly Spending Trends',
                     labels={'date': 'Month', 'amount': currency_label})
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title=currency_label,
            hovermode='x unified'
        )
        
        chart_json = json.loads(fig.to_json())
        print(f"Monthly chart - Chart JSON keys: {list(chart_json.keys())}")
        return chart_json
    
    def create_category_chart(self, transactions, primary_currency=None):
        """Create spending by category chart with proper currency support"""
        if not transactions:
            return {}
        
        df = pd.DataFrame(transactions)
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Detect primary currency if not provided
        if primary_currency is None:
            primary_currency = self._determine_primary_currency(df)
        
        # Filter expenses and group by category
        expenses = df[df['amount'] < 0].copy()
        expenses['amount'] = expenses['amount'].abs()
        category_data = expenses.groupby('category')['amount'].sum().reset_index()
        
        # Create pie chart
        fig = px.pie(category_data, values='amount', names='category',
                    title=f'Spending by Category ({primary_currency})')
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return json.loads(fig.to_json())
    
    def create_daily_pattern_chart(self, transactions, primary_currency=None):
        """Create daily spending pattern chart with proper currency support"""
        if not transactions:
            return {}
        
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Detect primary currency if not provided
        if primary_currency is None:
            primary_currency = self._determine_primary_currency(df)
        
        # Filter expenses and group by day of week
        expenses = df[df['amount'] < 0].copy()
        expenses['amount'] = expenses['amount'].abs()
        daily_data = expenses.groupby(expenses['date'].dt.dayofweek)['amount'].mean().reset_index()
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_data['day'] = daily_data['date'].map(lambda x: day_names[x])
        
        # Format currency label
        currency_label = f"Average Spending ({primary_currency})"
        
        # Create bar chart
        fig = px.bar(daily_data, x='day', y='amount',
                    title='Average Daily Spending by Day of Week',
                    labels={'day': 'Day of Week', 'amount': currency_label})
        
        fig.update_layout(
            xaxis_title="Day of Week",
            yaxis_title=currency_label
        )
        
        return json.loads(fig.to_json())
    
    def create_budget_vs_actual_chart(self, transactions, primary_currency=None):
        """Create budget vs actual spending comparison chart with proper currency support"""
        if not transactions:
            return {}
        
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # Detect primary currency if not provided
        if primary_currency is None:
            primary_currency = self._determine_primary_currency(df)
        
        # Calculate monthly income
        monthly_income = df[df['amount'] > 0].groupby(df['date'].dt.to_period('M'))['amount'].sum().mean()
        
        if monthly_income == 0:
            return {}
        
        # Calculate actual spending by category
        expenses = df[df['amount'] < 0].copy()
        expenses['amount'] = expenses['amount'].abs()
        actual_spending = expenses.groupby('category')['amount'].sum()
        
        # Create comparison data
        comparison_data = []
        for category, percentage in self.standard_budgets.items():
            recommended = monthly_income * percentage
            actual = actual_spending.get(category, 0)
            
            comparison_data.append({
                'category': category,
                'recommended': recommended,
                'actual': actual,
                'difference': actual - recommended
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Recommended',
            x=comparison_df['category'],
            y=comparison_df['recommended'],
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Actual',
            x=comparison_df['category'],
            y=comparison_df['actual'],
            marker_color='lightcoral'
        ))
        
        # Format currency label
        currency_label = f"Amount ({primary_currency})"
        
        fig.update_layout(
            title=f'Budget vs Actual Spending by Category ({primary_currency})',
            xaxis_title="Category",
            yaxis_title=currency_label,
            barmode='group'
        )
        
        return json.loads(fig.to_json()) 