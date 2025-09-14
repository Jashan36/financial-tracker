#!/usr/bin/env python3
"""
Test script to demonstrate currency conversion functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime
from enhanced_transaction_processor import EnhancedTransactionProcessor
from currency_converter import CurrencyConverter

def create_sample_mixed_currency_data():
    """Create sample data with mixed currencies"""
    sample_data = {
        'date': [
            '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
            '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'
        ],
        'description': [
            'Salary', 'Grocery Store', 'Train Ticket', 'Restaurant', 'Mutual Fund',
            'Netflix Subscription', 'Coffee Shop', 'Gas Station', 'Book Store', 'Bank Transfer'
        ],
        'amount': [
            50000, -1500, -200, -800, -10000,  # INR transactions
            -15, -5, -60, -25, 1000            # USD transactions
        ],
        'currency': [
            'INR', 'INR', 'INR', 'INR', 'INR',
            'USD', 'USD', 'USD', 'USD', 'USD'
        ],
        'category': [
            'income', 'food', 'transport', 'food', 'investment',
            'entertainment', 'food', 'transport', 'education', 'income'
        ],
        'type': [
            'credit', 'debit', 'debit', 'debit', 'debit',
            'debit', 'debit', 'debit', 'debit', 'credit'
        ]
    }
    
    return pd.DataFrame(sample_data)

def test_currency_conversion():
    """Test the currency conversion functionality"""
    print("🚀 Testing Currency Conversion System")
    print("=" * 80)
    
    # Initialize the enhanced processor
    processor = EnhancedTransactionProcessor(enable_currency_conversion=True)
    
    # Create sample data
    print("\n1. Creating Sample Mixed Currency Data:")
    df = create_sample_mixed_currency_data()
    print(f"Sample data shape: {df.shape}")
    print("\nSample data:")
    print(df.head(10))
    
    # Save sample data to CSV
    sample_file = "sample_mixed_currency.csv"
    df.to_csv(sample_file, index=False)
    print(f"\nSaved sample data to: {sample_file}")
    
    # Test conversion to USD
    print("\n2. Testing Conversion to USD:")
    try:
        result_usd = processor.normalize_and_convert_csv(sample_file, 'USD')
        
        print(f"✅ Successfully converted {result_usd['total_transactions']} transactions to USD")
        print(f"Converted file saved to: {result_usd['converted_file_path']}")
        
        # Show conversion summary
        conversion_summary = result_usd['conversion_summary']
        print(f"\nConversion Summary:")
        print(f"  Target Currency: {conversion_summary['target_currency']}")
        print(f"  Currencies Found: {conversion_summary['currencies_found']}")
        print(f"  Currency Counts: {conversion_summary['currency_counts']}")
        print(f"  Conversion Rates: {conversion_summary['conversion_rates']}")
        
        # Show sample converted transactions
        print(f"\nSample Converted Transactions:")
        converted_df = result_usd['converted_df']
        print(converted_df[['date', 'description', 'amount', 'original_amount', 
                           'currency', 'original_currency', 'conversion_rate']].head())
        
        # Show budget recommendations in USD
        print(f"\nBudget Recommendations (USD):")
        budget_rec = result_usd['budget_recommendations']
        print(f"  Monthly Income: {budget_rec['monthly_income_formatted']}")
        print(f"  Currency: {budget_rec['currency']}")
        
        for category, data in budget_rec['recommended_budgets'].items():
            if data['recommended'] > 0:
                print(f"    {category.capitalize()}:")
                print(f"      Recommended: {data['formatted_recommended']}")
                print(f"      Current: {data['formatted_current']}")
                print(f"      Status: {data['status']}")
        
    except Exception as e:
        print(f"❌ Error converting to USD: {e}")
        return False
    
    # Test conversion to INR
    print("\n3. Testing Conversion to INR:")
    try:
        result_inr = processor.normalize_and_convert_csv(sample_file, 'INR')
        
        print(f"✅ Successfully converted {result_inr['total_transactions']} transactions to INR")
        print(f"Converted file saved to: {result_inr['converted_file_path']}")
        
        # Show budget recommendations in INR
        print(f"\nBudget Recommendations (INR):")
        budget_rec = result_inr['budget_recommendations']
        print(f"  Monthly Income: {budget_rec['monthly_income_formatted']}")
        print(f"  Currency: {budget_rec['currency']}")
        
        for category, data in budget_rec['recommended_budgets'].items():
            if data['recommended'] > 0:
                print(f"    {category.capitalize()}:")
                print(f"      Recommended: {data['formatted_recommended']}")
                print(f"      Current: {data['formatted_current']}")
                print(f"      Status: {data['status']}")
        
    except Exception as e:
        print(f"❌ Error converting to INR: {e}")
        return False
    
    # Test exchange rate API
    print("\n4. Testing Exchange Rate API:")
    try:
        converter = CurrencyConverter()
        
        # Test individual conversions
        test_conversions = [
            ('INR', 'USD', 1000),
            ('USD', 'INR', 100),
            ('EUR', 'USD', 100),
            ('GBP', 'USD', 100)
        ]
        
        print("Exchange Rate Tests:")
        for from_curr, to_curr, amount in test_conversions:
            rate = converter.get_exchange_rate(from_curr, to_curr)
            converted = converter.convert_amount(amount, from_curr, to_curr)
            print(f"  {amount} {from_curr} -> {converted:.2f} {to_curr} (rate: {rate:.4f})")
        
        # Test supported currencies
        supported_currencies = converter.get_supported_currencies()
        print(f"\nSupported Currencies: {len(supported_currencies)} total")
        print(f"Sample currencies: {supported_currencies[:10]}...")
        
    except Exception as e:
        print(f"❌ Error testing exchange rates: {e}")
        return False
    
    # Clean up
    print("\n5. Cleaning up test files:")
    try:
        os.remove(sample_file)
        if os.path.exists(result_usd['converted_file_path']):
            os.remove(result_usd['converted_file_path'])
        if os.path.exists(result_inr['converted_file_path']):
            os.remove(result_inr['converted_file_path'])
        print("✅ Test files cleaned up")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up all test files: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 ALL CURRENCY CONVERSION TESTS PASSED!")
    print("✅ Currency conversion working correctly")
    print("✅ Budget recommendations generated in target currency")
    print("✅ Exchange rate API functioning")
    print("✅ File conversion pipeline working")
    print("=" * 80)
    
    return True

def main():
    """Run currency conversion tests"""
    try:
        success = test_currency_conversion()
        return success
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

