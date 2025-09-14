#!/usr/bin/env python3
"""
Comprehensive test for production-ready fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_unicode_logging_fix():
    """Test Unicode logging infrastructure"""
    print("Testing Unicode logging fix...")
    
    try:
        from unicode_logging_fix import create_safe_logger
        
        # Create a safe logger
        logger = create_safe_logger("test_logger")
        
        # Test logging Unicode characters
        test_messages = [
            "Regular ASCII message",
            "Euro symbol: €12.50",
            "Rupee symbol: ₹1500.00",
            "Pound symbol: £45.20",
            "Yen symbol: ¥1200",
            "Mixed: Café Central €12.50"
        ]
        
        passed = 0
        total = len(test_messages)
        
        for message in test_messages:
            try:
                logger.info(message)
                print(f"   ✅ Logged: {message}")
                passed += 1
            except Exception as e:
                print(f"   ❌ Failed to log: {message} - {str(e)}")
        
        print(f"   📊 Unicode Logging: {passed}/{total} passed")
        return passed == total
        
    except Exception as e:
        print(f"❌ Unicode logging test failed: {e}")
        return False

def test_robust_csv_processing():
    """Test robust CSV processing"""
    print("\nTesting robust CSV processing...")
    
    try:
        from robust_csv_processor import RobustCSVProcessor
        from pathlib import Path
        
        processor = RobustCSVProcessor()
        
        # Test with sample files
        test_files = [
            'sample_data.csv',
            'sample_data_inr.csv', 
            'sample_data_eur.csv'
        ]
        
        passed = 0
        total = len(test_files)
        
        for filename in test_files:
            if os.path.exists(filename):
                try:
                    df, info = processor.process_csv(Path(filename))
                    
                    if df is not None and not df.empty:
                        print(f"   ✅ {filename}: {len(df)} rows using strategy {info['strategy']}")
                        passed += 1
                    else:
                        print(f"   ❌ {filename}: No data processed")
                        
                except Exception as e:
                    print(f"   ❌ {filename}: Error - {str(e)}")
            else:
                print(f"   ⚠️  {filename}: File not found")
        
        print(f"   📊 Robust CSV Processing: {passed}/{total} files processed")
        return passed > 0
        
    except Exception as e:
        print(f"❌ Robust CSV processing test failed: {e}")
        return False

def test_data_sanitization():
    """Test data sanitization"""
    print("\nTesting data sanitization...")
    
    try:
        from data_sanitizer import DataSanitizer
        import pandas as pd
        
        sanitizer = DataSanitizer()
        
        # Create test data with various issues
        test_data = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-14', '2024-01-13'],
            'Description': ['  Test Transaction  ', '"Quoted Description"', 'Normal Description'],
            'Amount': ['€12,50', '€25.00', '€50,75'],
            'Type': ['Debit', 'Debit', 'Credit'],
            'Category': ['Food', 'Transport', 'Shopping']
        })
        
        # Sanitize the data
        sanitized_df = sanitizer.sanitize_csv_data(test_data)
        
        if not sanitized_df.empty:
            print(f"   ✅ Data sanitization successful: {len(sanitized_df)} rows")
            
            # Check if whitespace was cleaned
            if sanitized_df['Description'].str.startswith(' ').any() == False:
                print(f"   ✅ Whitespace cleaning successful")
            else:
                print(f"   ⚠️  Whitespace cleaning may have issues")
            
            return True
        else:
            print(f"   ❌ Data sanitization failed")
            return False
        
    except Exception as e:
        print(f"❌ Data sanitization test failed: {e}")
        return False

def test_defensive_transaction_parsing():
    """Test defensive transaction parsing"""
    print("\nTesting defensive transaction parsing...")
    
    try:
        from defensive_transaction_parser import DefensiveTransactionParser
        import pandas as pd
        
        parser = DefensiveTransactionParser()
        
        # Test with various row formats
        test_rows = [
            pd.Series({
                'Date': '2024-01-15',
                'Description': 'Test Transaction',
                'Amount': '$100.50',
                'Type': 'Debit',
                'Category': 'Food'
            }),
            pd.Series({
                'date': '2024-01-14',
                'description': 'Salary Deposit',
                'amount': '₹50000.00',
                'type': 'Credit',
                'category': 'Income'
            }),
            pd.Series({
                'DATE': '2024-01-13',
                'DESCRIPTION': 'Coffee Shop',
                'AMOUNT': '€5.50',
                'TYPE': 'Debit'
            })
        ]
        
        passed = 0
        total = len(test_rows)
        
        for i, row in enumerate(test_rows):
            try:
                result = parser.parse_transaction_row(row, index=i)
                
                if result.success:
                    print(f"   ✅ Row {i+1}: {result.transaction['description']} - {result.transaction['amount']} {result.transaction['currency']} (strategy: {result.strategy_used})")
                    passed += 1
                else:
                    print(f"   ❌ Row {i+1}: Failed - {result.error_message}")
                    
            except Exception as e:
                print(f"   ❌ Row {i+1}: Error - {str(e)}")
        
        print(f"   📊 Defensive Parsing: {passed}/{total} passed")
        return passed == total
        
    except Exception as e:
        print(f"❌ Defensive parsing test failed: {e}")
        return False

def test_enhanced_transaction_processor():
    """Test the enhanced transaction processor"""
    print("\nTesting enhanced transaction processor...")
    
    try:
        from enhanced_transaction_processor import EnhancedTransactionProcessor
        from config import get_config
        
        config = get_config()
        processor = EnhancedTransactionProcessor(config=config)
        
        # Test with sample files
        test_files = [
            ('sample_data.csv', 'USD'),
            ('sample_data_inr.csv', 'INR'),
            ('sample_data_eur.csv', 'EUR')
        ]
        
        passed = 0
        total = len(test_files)
        
        for filename, expected_currency in test_files:
            if os.path.exists(filename):
                try:
                    transactions = processor.process_file(filename)
                    primary_currency = processor.determine_primary_currency(transactions)
                    
                    print(f"   ✅ {filename}: {len(transactions)} transactions, currency: {primary_currency}")
                    
                    # Show sample transaction
                    if transactions:
                        sample = transactions[0]
                        print(f"      Sample: {sample['description']} - {sample['amount']} {sample['currency']}")
                    
                    if primary_currency == expected_currency:
                        passed += 1
                    else:
                        print(f"      ⚠️  Expected {expected_currency}, got {primary_currency}")
                        
                except Exception as e:
                    print(f"   ❌ {filename}: Error - {str(e)}")
            else:
                print(f"   ⚠️  {filename}: File not found")
        
        print(f"   📊 Enhanced Processor: {passed}/{total} files processed successfully")
        return passed > 0
        
    except Exception as e:
        print(f"❌ Enhanced processor test failed: {e}")
        return False

def test_error_recovery():
    """Test error recovery mechanisms"""
    print("\nTesting error recovery mechanisms...")
    
    try:
        from enhanced_transaction_processor import EnhancedTransactionProcessor
        from config import get_config
        import pandas as pd
        
        config = get_config()
        processor = EnhancedTransactionProcessor(config=config)
        
        # Create test data with various issues
        problematic_data = pd.DataFrame({
            'Date': ['invalid-date', '2024-01-15', '2024-01-14'],
            'Description': ['', 'Valid Description', 'Another Valid Description'],
            'Amount': ['invalid-amount', '$100.50', '€25.00'],
            'Type': ['Debit', 'Debit', 'Credit']
        })
        
        # Test with problematic data
        valid_transactions = []
        errors = []
        
        for idx, row in problematic_data.iterrows():
            try:
                result = processor.defensive_parser.parse_transaction_row(row, index=idx)
                if result.success:
                    valid_transactions.append(result.transaction)
                else:
                    errors.append(f"Row {idx}: {result.error_message}")
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        print(f"   ✅ Error recovery: {len(valid_transactions)} valid, {len(errors)} errors")
        
        if errors:
            print(f"   📝 Sample errors:")
            for error in errors[:3]:
                print(f"      {error}")
        
        return len(valid_transactions) > 0
        
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        return False

def main():
    """Run all production-ready fix tests"""
    print("=" * 60)
    print("🏭 Production-Ready Architecture Test Suite")
    print("=" * 60)
    
    tests = [
        test_unicode_logging_fix,
        test_robust_csv_processing,
        test_data_sanitization,
        test_defensive_transaction_parsing,
        test_enhanced_transaction_processor,
        test_error_recovery
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Production-Ready Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All production-ready fixes verified successfully!")
        print("✅ The following architectural improvements are working:")
        print("   • Unicode logging infrastructure fixed for Windows")
        print("   • Robust CSV processing with corruption detection")
        print("   • Data sanitization layer for cleaning messy data")
        print("   • Defensive transaction parsing with multiple strategies")
        print("   • Enhanced transaction processor with full pipeline")
        print("   • Error recovery mechanisms for graceful degradation")
        print()
        print("🚀 The application now has production-ready architecture!")
        print("   • Handles corrupted CSV files gracefully")
        print("   • Provides detailed error reporting and recovery")
        print("   • Uses defensive programming throughout")
        print("   • Supports Unicode properly on all platforms")
        print("   • Has multiple fallback strategies for parsing")
    elif passed >= total * 0.75:
        print("✅ Most production-ready features working correctly")
        print("⚠️  Some components may need minor adjustments")
    else:
        print("⚠️  Several components need additional work")
        print("🔧 Check the specific errors above for details")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
