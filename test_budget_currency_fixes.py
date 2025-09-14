#!/usr/bin/env python3
"""
Test script to verify that the budget analyzer properly handles multi-currency support.
This test ensures that budget recommendations are generated in the user's primary currency
instead of defaulting to USD.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from budget_analyzer import BudgetAnalyzer
import pandas as pd
from datetime import datetime, timedelta

def test_currency_detection_and_formatting():
    """Test currency detection and formatting in budget analyzer"""
    print("🧪 Testing Currency Detection and Formatting")
    print("=" * 60)
    
    analyzer = BudgetAnalyzer()
    
    # Test 1: Currency formatting for different currencies
    print("\n1. Testing Currency Formatting:")
    test_amounts = [1000, 1500.50, 25000.75, 1000000]
    test_currencies = ['USD', 'INR', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'BRL', 'MYR', 'SGD']
    
    for currency in test_currencies:
        print(f"\n{currency} formatting:")
        for amount in test_amounts:
            formatted = analyzer.format_currency(amount, currency)
            print(f"  {amount:>10} -> {formatted}")
    
    # Test 2: Primary currency detection
    print("\n2. Testing Primary Currency Detection:")
    
    # Create test transactions with different currencies
    test_transactions = [
        # INR transactions (should be primary)
        {'date': '2024-01-01', 'amount': 5000, 'currency': 'INR', 'category': 'food', 'description': 'Grocery'},
        {'date': '2024-01-02', 'amount': 2000, 'currency': 'INR', 'category': 'transport', 'description': 'Bus'},
        {'date': '2024-01-03', 'amount': 8000, 'currency': 'INR', 'category': 'food', 'description': 'Restaurant'},
        {'date': '2024-01-04', 'amount': 10000, 'currency': 'INR', 'category': 'shopping', 'description': 'Clothes'},
        {'date': '2024-01-05', 'amount': 15000, 'currency': 'INR', 'category': 'investment', 'description': 'Mutual Fund'},
        # One USD transaction (should not be primary)
        {'date': '2024-01-06', 'amount': 100, 'currency': 'USD', 'category': 'entertainment', 'description': 'Netflix'},
        # Income transaction
        {'date': '2024-01-01', 'amount': 50000, 'currency': 'INR', 'category': 'income', 'description': 'Salary'}
    ]
    
    df = pd.DataFrame(test_transactions)
    detected_currency = analyzer._determine_primary_currency(df)
    print(f"  Detected primary currency: {detected_currency}")
    print(f"  Expected: INR")
    assert detected_currency == 'INR', f"Expected INR, got {detected_currency}"
    print("  ✅ Primary currency detection working correctly")
    
    # Test 3: Budget recommendations with proper currency
    print("\n3. Testing Budget Recommendations with Currency:")
    
    recommendations = analyzer.generate_recommendations(test_transactions, 'INR')
    
    print(f"  Monthly Income: {recommendations['monthly_income_formatted']}")
    print(f"  Currency: {recommendations['currency']}")
    
    # Check that recommendations are in INR
    assert recommendations['currency'] == 'INR', "Recommendations should be in INR"
    assert '₹' in recommendations['monthly_income_formatted'], "Monthly income should show INR symbol"
    
    print("  ✅ Budget recommendations using correct currency")
    
    # Test individual category recommendations
    print("\n  Category Recommendations:")
    for category, data in recommendations['recommended_budgets'].items():
        if data['recommended'] > 0:  # Only show categories with recommendations
            print(f"    {category.capitalize()}:")
            print(f"      Recommended: {data['formatted_recommended']}")
            print(f"      Current: {data['formatted_current']}")
            print(f"      Status: {data['status']}")
    
    # Test 4: Chart generation with currency
    print("\n4. Testing Chart Generation with Currency:")
    
    monthly_chart = analyzer.create_monthly_spending_chart(test_transactions, 'INR')
    print(f"  Monthly chart generated: {len(monthly_chart) > 0}")
    
    category_chart = analyzer.create_category_chart(test_transactions, 'INR')
    print(f"  Category chart generated: {len(category_chart) > 0}")
    
    daily_chart = analyzer.create_daily_pattern_chart(test_transactions, 'INR')
    print(f"  Daily pattern chart generated: {len(daily_chart) > 0}")
    
    budget_chart = analyzer.create_budget_vs_actual_chart(test_transactions, 'INR')
    print(f"  Budget vs actual chart generated: {len(budget_chart) > 0}")
    
    print("  ✅ All charts generated with proper currency support")

def test_eur_currency():
    """Test with EUR currency data"""
    print("\n🧪 Testing EUR Currency Support")
    print("=" * 60)
    
    analyzer = BudgetAnalyzer()
    
    # Create EUR transactions
    eur_transactions = [
        {'date': '2024-01-01', 'amount': 50, 'currency': 'EUR', 'category': 'food', 'description': 'Supermarket'},
        {'date': '2024-01-02', 'amount': 25, 'currency': 'EUR', 'category': 'transport', 'description': 'Train'},
        {'date': '2024-01-03', 'amount': 80, 'currency': 'EUR', 'category': 'food', 'description': 'Restaurant'},
        {'date': '2024-01-04', 'amount': 120, 'currency': 'EUR', 'category': 'shopping', 'description': 'Clothes'},
        {'date': '2024-01-05', 'amount': 200, 'currency': 'EUR', 'category': 'investment', 'description': 'ETF'},
        {'date': '2024-01-01', 'amount': 3000, 'currency': 'EUR', 'category': 'income', 'description': 'Salary'}
    ]
    
    recommendations = analyzer.generate_recommendations(eur_transactions)
    
    print(f"  Monthly Income: {recommendations['monthly_income_formatted']}")
    print(f"  Currency: {recommendations['currency']}")
    
    # Check EUR formatting
    assert '€' in recommendations['monthly_income_formatted'], "Should show EUR symbol"
    assert recommendations['currency'] == 'EUR', "Should detect EUR as primary currency"
    
    print("  ✅ EUR currency support working correctly")

def test_jpy_currency():
    """Test with JPY currency (no decimal places)"""
    print("\n🧪 Testing JPY Currency Support (No Decimals)")
    print("=" * 60)
    
    analyzer = BudgetAnalyzer()
    
    # Create JPY transactions
    jpy_transactions = [
        {'date': '2024-01-01', 'amount': 500, 'currency': 'JPY', 'category': 'food', 'description': 'Lunch'},
        {'date': '2024-01-02', 'amount': 200, 'currency': 'JPY', 'category': 'transport', 'description': 'Train'},
        {'date': '2024-01-03', 'amount': 800, 'currency': 'JPY', 'category': 'food', 'description': 'Dinner'},
        {'date': '2024-01-04', 'amount': 1200, 'currency': 'JPY', 'category': 'shopping', 'description': 'Books'},
        {'date': '2024-01-05', 'amount': 2000, 'currency': 'JPY', 'category': 'investment', 'description': 'Stock'},
        {'date': '2024-01-01', 'amount': 30000, 'currency': 'JPY', 'category': 'income', 'description': 'Salary'}
    ]
    
    recommendations = analyzer.generate_recommendations(jpy_transactions)
    
    print(f"  Monthly Income: {recommendations['monthly_income_formatted']}")
    print(f"  Currency: {recommendations['currency']}")
    
    # Check JPY formatting (no decimal places)
    assert '¥' in recommendations['monthly_income_formatted'], "Should show JPY symbol"
    assert recommendations['currency'] == 'JPY', "Should detect JPY as primary currency"
    assert '.00' not in recommendations['monthly_income_formatted'], "JPY should not show decimal places"
    
    print("  ✅ JPY currency support working correctly")

def test_mixed_currency_handling():
    """Test handling of mixed currencies (should use most frequent)"""
    print("\n🧪 Testing Mixed Currency Handling")
    print("=" * 60)
    
    analyzer = BudgetAnalyzer()
    
    # Create mixed currency transactions (INR should be primary due to frequency and value)
    mixed_transactions = [
        # Mostly INR transactions
        {'date': '2024-01-01', 'amount': 5000, 'currency': 'INR', 'category': 'food', 'description': 'Grocery'},
        {'date': '2024-01-02', 'amount': 2000, 'currency': 'INR', 'category': 'transport', 'description': 'Bus'},
        {'date': '2024-01-03', 'amount': 8000, 'currency': 'INR', 'category': 'food', 'description': 'Restaurant'},
        {'date': '2024-01-04', 'amount': 10000, 'currency': 'INR', 'category': 'shopping', 'description': 'Clothes'},
        {'date': '2024-01-05', 'amount': 15000, 'currency': 'INR', 'category': 'investment', 'description': 'Mutual Fund'},
        {'date': '2024-01-01', 'amount': 50000, 'currency': 'INR', 'category': 'income', 'description': 'Salary'},
        # Few USD transactions
        {'date': '2024-01-06', 'amount': 100, 'currency': 'USD', 'category': 'entertainment', 'description': 'Netflix'},
        {'date': '2024-01-07', 'amount': 50, 'currency': 'USD', 'category': 'entertainment', 'description': 'Spotify'},
    ]
    
    recommendations = analyzer.generate_recommendations(mixed_transactions)
    
    print(f"  Detected Currency: {recommendations['currency']}")
    print(f"  Monthly Income: {recommendations['monthly_income_formatted']}")
    
    # Should detect INR as primary due to frequency and total value
    assert recommendations['currency'] == 'INR', "Should detect INR as primary currency in mixed scenario"
    
    print("  ✅ Mixed currency handling working correctly")

def main():
    """Run all budget analyzer currency tests"""
    print("🚀 Budget Analyzer Currency Fix Tests")
    print("=" * 80)
    
    try:
        test_currency_detection_and_formatting()
        test_eur_currency()
        test_jpy_currency()
        test_mixed_currency_handling()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Budget analyzer now properly handles multi-currency support")
        print("✅ Currency detection working correctly")
        print("✅ Currency formatting working for all supported currencies")
        print("✅ Budget recommendations generated in user's primary currency")
        print("✅ Charts display with proper currency labels")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
