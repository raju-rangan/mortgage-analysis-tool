"""
Test module for mortgage calculator functions.
"""

import unittest
from mortgage_calculator import (
    calculate_monthly_payment,
    calculate_total_interest,
    calculate_loan_to_value,
    calculate_debt_to_income,
    calculate_pmi,
    calculate_affordability
)


class TestMortgageCalculator(unittest.TestCase):
    """Test cases for mortgage calculator functions."""
    
    def test_calculate_monthly_payment(self):
        """Test monthly payment calculation."""
        # Test case: $300,000 loan, 4.5% interest, 30-year term
        payment = calculate_monthly_payment(300000, 4.5, 30)
        self.assertAlmostEqual(payment, 1520.06, places=2)
        
        # Test case: $200,000 loan, 3.0% interest, 15-year term
        payment = calculate_monthly_payment(200000, 3.0, 15)
        self.assertAlmostEqual(payment, 1381.16, places=2)
        
        # Test case: $100,000 loan, 0% interest, 10-year term
        payment = calculate_monthly_payment(100000, 0, 10)
        self.assertAlmostEqual(payment, 833.33, places=2)
    
    def test_calculate_total_interest(self):
        """Test total interest calculation."""
        # Test case: $300,000 loan, 4.5% interest, 30-year term
        total_interest = calculate_total_interest(300000, 4.5, 30)
        self.assertAlmostEqual(total_interest, 247220.13, places=2)
        
        # Test case: $200,000 loan, 3.0% interest, 15-year term
        total_interest = calculate_total_interest(200000, 3.0, 15)
        self.assertAlmostEqual(total_interest, 48608.20, places=2)
    
    def test_calculate_loan_to_value(self):
        """Test LTV calculation."""
        # Test case: $240,000 loan, $300,000 property value (80% LTV)
        ltv = calculate_loan_to_value(240000, 300000)
        self.assertEqual(ltv, 80.0)
        
        # Test case: $270,000 loan, $300,000 property value (90% LTV)
        ltv = calculate_loan_to_value(270000, 300000)
        self.assertEqual(ltv, 90.0)
    
    def test_calculate_debt_to_income(self):
        """Test DTI calculation."""
        # Test case: $6,000 monthly income, $2,400 monthly debt (40% DTI)
        dti = calculate_debt_to_income(6000, 2400)
        self.assertEqual(dti, 40.0)
        
        # Test case: $8,000 monthly income, $2,000 monthly debt (25% DTI)
        dti = calculate_debt_to_income(8000, 2000)
        self.assertEqual(dti, 25.0)
    
    def test_calculate_pmi(self):
        """Test PMI calculation."""
        # Test case: $240,000 loan, $300,000 property value (80% LTV, no PMI)
        pmi = calculate_pmi(240000, 300000)
        self.assertEqual(pmi, 0)
        
        # Test case: $270,000 loan, $300,000 property value (90% LTV, with PMI)
        pmi = calculate_pmi(270000, 300000)
        self.assertEqual(pmi, 270000 * 0.005)
    
    def test_calculate_affordability(self):
        """Test affordability calculation."""
        # Test case: $6,000 monthly income, $1,000 monthly debt, $60,000 down payment,
        # 4.5% interest, 30-year term
        max_price = calculate_affordability(6000, 1000, 60000, 4.5, 30)
        self.assertGreater(max_price, 300000)  # Should be able to afford > $300k


if __name__ == '__main__':
    unittest.main()
