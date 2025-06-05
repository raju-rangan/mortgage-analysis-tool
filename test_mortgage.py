"""
Test module for mortgage calculator functions.
"""

import unittest
import os
import shutil
from mortgage_calculator import (
    calculate_monthly_payment,
    calculate_total_interest,
    calculate_loan_to_value,
    calculate_debt_to_income,
    calculate_pmi,
    calculate_affordability
)
from mortgage_comparison import MortgageScenario, MortgageComparison


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


class TestMortgageScenario(unittest.TestCase):
    """Test cases for MortgageScenario class."""
    
    def test_mortgage_scenario_creation(self):
        """Test creating a mortgage scenario."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000,
            points=1.0,
            property_value=360000,
            annual_appreciation=3.0
        )
        
        # Test basic properties
        self.assertEqual(scenario.name, "Test Scenario")
        self.assertEqual(scenario.loan_amount, 300000)
        self.assertEqual(scenario.interest_rate, 4.5)
        self.assertEqual(scenario.term_years, 30)
        self.assertEqual(scenario.down_payment, 60000)
        self.assertEqual(scenario.points, 1.0)
        self.assertEqual(scenario.property_value, 360000)
        self.assertEqual(scenario.annual_appreciation, 3.0)
        
        # Test calculated metrics
        self.assertAlmostEqual(scenario.monthly_payment, 1520.06, places=2)
        self.assertAlmostEqual(scenario.total_interest, 247220.13, places=2)
        self.assertAlmostEqual(scenario.total_cost, 547220.13, places=2)
    
    def test_property_value_default(self):
        """Test default property value calculation."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000
        )
        
        # Property value should default to loan_amount + down_payment
        self.assertEqual(scenario.property_value, 360000)
    
    def test_calculate_equity_at_year(self):
        """Test equity calculation at specific years."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000,
            property_value=360000,
            annual_appreciation=3.0
        )
        
        # Test equity at year 5
        equity_5yr = scenario.calculate_equity_at_year(5)
        self.assertGreater(equity_5yr['principal_paid'], 0)
        self.assertGreater(equity_5yr['property_value'], 360000)  # Should have appreciated
        self.assertGreater(equity_5yr['total_equity'], 60000)  # Should be more than down payment
        
        # Test equity at year beyond term
        equity_40yr = scenario.calculate_equity_at_year(40)
        self.assertEqual(equity_40yr['year'], 30)  # Should be capped at term_years
    
    def test_calculate_break_even_point(self):
        """Test break-even point calculation."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000
        )
        
        # Test break-even calculation
        break_even = scenario.calculate_break_even_point(1.0, 4.0)
        
        # Cost of points should be 1% of loan amount
        self.assertEqual(break_even['points_cost'], 3000)
        
        # Reduced payment should be less than original
        self.assertLess(break_even['reduced_payment'], break_even['original_payment'])
        
        # Monthly savings should be positive
        self.assertGreater(break_even['monthly_savings'], 0)
        
        # Break-even months should be positive
        self.assertGreater(break_even['break_even_months'], 0)
        
        # Net savings should be positive for this scenario
        self.assertGreater(break_even['net_savings'], 0)


class TestMortgageComparison(unittest.TestCase):
    """Test cases for MortgageComparison class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.comparison = MortgageComparison()
        
        # Create test scenarios
        self.scenario1 = MortgageScenario(
            name="Scenario 1",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000
        )
        
        self.scenario2 = MortgageScenario(
            name="Scenario 2",
            loan_amount=300000,
            interest_rate=4.0,
            term_years=15,
            down_payment=60000
        )
        
        # Add scenarios to comparison
        self.comparison.add_scenario(self.scenario1)
        self.comparison.add_scenario(self.scenario2)
        
        # Create test directory for saving/loading
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_scenarios")
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        
        # Override data directory for testing
        self.comparison.data_dir = self.test_dir
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_add_and_get_scenario(self):
        """Test adding and retrieving scenarios."""
        # Test getting existing scenario
        scenario = self.comparison.get_scenario("Scenario 1")
        self.assertEqual(scenario.name, "Scenario 1")
        self.assertEqual(scenario.loan_amount, 300000)
        
        # Test getting non-existent scenario
        scenario = self.comparison.get_scenario("Non-existent")
        self.assertIsNone(scenario)
        
        # Test getting all scenarios
        scenarios = self.comparison.get_all_scenarios()
        self.assertEqual(len(scenarios), 2)
        self.assertIn("Scenario 1", scenarios)
        self.assertIn("Scenario 2", scenarios)
    
    def test_remove_scenario(self):
        """Test removing scenarios."""
        # Test removing existing scenario
        result = self.comparison.remove_scenario("Scenario 1")
        self.assertTrue(result)
        
        # Verify scenario was removed
        scenarios = self.comparison.get_all_scenarios()
        self.assertEqual(len(scenarios), 1)
        self.assertNotIn("Scenario 1", scenarios)
        
        # Test removing non-existent scenario
        result = self.comparison.remove_scenario("Non-existent")
        self.assertFalse(result)
    
    def test_generate_comparison_table(self):
        """Test generating comparison table."""
        comparison_table = self.comparison.generate_comparison_table()
        
        # Check table structure
        self.assertIn('scenarios', comparison_table)
        self.assertIn('monthly_payment', comparison_table)
        self.assertIn('total_interest', comparison_table)
        self.assertIn('total_cost', comparison_table)
        self.assertIn('equity_5yr', comparison_table)
        self.assertIn('equity_10yr', comparison_table)
        self.assertIn('equity_15yr', comparison_table)
        
        # Check scenario names
        self.assertEqual(comparison_table['scenarios'], ["Scenario 1", "Scenario 2"])
        
        # Check data lengths
        self.assertEqual(len(comparison_table['monthly_payment']), 2)
        self.assertEqual(len(comparison_table['total_interest']), 2)
        
        # Check that 15-year loan has less total interest than 30-year loan
        self.assertLess(comparison_table['total_interest'][1], comparison_table['total_interest'][0])
    
    def test_save_and_load_scenarios(self):
        """Test saving and loading scenarios."""
        # Save scenarios
        file_path = self.comparison.save_scenarios("test_save.json")
        self.assertTrue(os.path.exists(file_path))
        
        # Create a new comparison object
        new_comparison = MortgageComparison()
        new_comparison.data_dir = self.test_dir
        
        # Load scenarios
        result = new_comparison.load_scenarios("test_save.json")
        self.assertTrue(result)
        
        # Verify loaded scenarios
        scenarios = new_comparison.get_all_scenarios()
        self.assertEqual(len(scenarios), 2)
        self.assertIn("Scenario 1", scenarios)
        self.assertIn("Scenario 2", scenarios)
        
        # Verify scenario properties
        scenario1 = new_comparison.get_scenario("Scenario 1")
        self.assertEqual(scenario1.loan_amount, 300000)
        self.assertEqual(scenario1.interest_rate, 4.5)
    
    def test_export_to_csv(self):
        """Test exporting comparison to CSV."""
        # Export to CSV
        csv_path = self.comparison.export_to_csv(os.path.join(self.test_dir, "test_export.csv"))
        self.assertTrue(os.path.exists(csv_path))
        
        # Verify file is not empty
        self.assertGreater(os.path.getsize(csv_path), 0)
