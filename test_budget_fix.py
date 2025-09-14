#!/usr/bin/env python3
"""
Test script to verify budget analyzer works correctly
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_budget_analyzer():
    """Test budget analyzer with sample data"""
    try:
        from budget_analyzer import BudgetAnalyzer
        
        # Create sample transactions
        sample_transactions = [
            {
                'date': '2024-01-01',
                'description': 'Salary',
                'amount': 5000.0,
                'category': 'income',
                'currency': 'USD'
            },
            {
                'date': '2024-01-02',
                'description': 'Grocery Store',
                'amount': -150.0,
                'category': 'groceries',
                'currency': 'USD'
            },
            {
                'date': '2024-01-03',
                'description': 'Gas Station',
                'amount': -50.0,
                'category': 'transport',
                'currency': 'USD'
            },
            {
                'date': '2024-01-04',
                'description': 'Restaurant',
                'amount': -75.0,
                'category': 'food & dining',
                'currency': 'USD'
            }
        ]
        
        # Test budget analyzer
        analyzer = BudgetAnalyzer()
        
        # Test spending analysis
        logger.info("Testing spending analysis...")
        spending_analysis = analyzer.analyze_spending(sample_transactions)
        logger.info(f"Spending analysis result: {type(spending_analysis)}")
        
        if isinstance(spending_analysis, dict) and 'error' in spending_analysis:
            logger.error(f"Spending analysis failed: {spending_analysis['error']}")
            return False
        
        # Test budget recommendations
        logger.info("Testing budget recommendations...")
        budget_recommendations = analyzer.generate_recommendations(sample_transactions, 'USD')
        logger.info(f"Budget recommendations result: {type(budget_recommendations)}")
        
        if isinstance(budget_recommendations, dict) and 'error' in budget_recommendations:
            logger.error(f"Budget recommendations failed: {budget_recommendations['error']}")
            return False
        
        logger.info("✅ All tests passed!")
        logger.info(f"Budget recommendations keys: {list(budget_recommendations.keys()) if budget_recommendations else 'None'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_budget_analyzer()
    sys.exit(0 if success else 1)
