#!/usr/bin/env python3
"""
Demo script showing currency conversion functionality
This matches the workflow you described in your message
"""

import pandas as pd
from datetime import datetime
from enhanced_transaction_processor import EnhancedTransactionProcessor

def create_sample_bank_statement():
    """Create a sample bank statement with mixed currencies"""
    data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'Description': ['Salary Credit', 'Grocery Purchase', 'Train Ticket', 'Restaurant Bill', 'Investment'],
        'Amount': [50000, -1500, -200, -800, -10000],
        'Currency': ['INR', 'INR', 'INR', 'INR', 'INR'],
        'Type': ['Credit', 'Debit', 'Debit', 'Debit', 'Debit'],
        'Category': ['Income', 'Food', 'Transport', 'Food', 'Investment']
    }
    
    df = pd.DataFrame(data)
    return df

def main():
    """Demo the currency conversion pipeline"""
    print("🏦 Financial Tracker - Currency Conversion Demo")
    print("=" * 60)
    
    # Create sample data
    print("\n1. Creating Sample Bank Statement:")
    df = create_sample_bank_statement()
    print(df)
    
    # Save to CSV
    sample_file = "fake_bank_statement.csv"
    df.to_csv(sample_file, index=False)
    print(f"\nSaved to: {sample_file}")
    
    # Initialize enhanced processor
    print("\n2. Initializing Enhanced Transaction Processor:")
    processor = EnhancedTransactionProcessor(enable_currency_conversion=True)
    print("✅ Processor initialized with currency conversion enabled")
    
    # Convert to USD (matching your workflow)
    print("\n3. Converting to USD:")
    try:
        result = processor.normalize_and_convert_csv(sample_file, target_currency='USD')
        
        print(f"✅ Conversion successful!")
        print(f"   Total transactions: {result['total_transactions']}")
        print(f"   Converted file: {result['converted_file_path']}")
        
        # Show conversion summary
        summary = result['conversion_summary']
        print(f"\n4. Conversion Summary:")
        print(f"   Target Currency: {summary['target_currency']}")
        print(f"   Currencies Found: {summary['currencies_found']}")
        print(f"   Currency Counts: {summary['currency_counts']}")
        print(f"   Conversion Rates: {summary['conversion_rates']}")
        
        # Show converted data sample
        print(f"\n5. Converted Data Sample:")
        converted_df = result['converted_df']
        display_columns = ['date', 'description', 'amount', 'original_amount', 
                          'currency', 'original_currency', 'conversion_rate']
        print(converted_df[display_columns].head())
        
        # Show budget recommendations
        print(f"\n6. Budget Recommendations (USD):")
        budget = result['budget_recommendations']
        print(f"   Monthly Income: {budget['monthly_income_formatted']}")
        
        for category, data in budget['recommended_budgets'].items():
            if data['recommended'] > 0:
                print(f"   {category.capitalize()}: {data['formatted_recommended']}")
        
        print(f"\n✅ Demo completed successfully!")
        print(f"📁 Check the converted file: {result['converted_file_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Clean up
    import os
    try:
        os.remove(sample_file)
        print(f"\n🧹 Cleaned up sample file")
    except:
        pass
    
    return True

if __name__ == "__main__":
    main()

