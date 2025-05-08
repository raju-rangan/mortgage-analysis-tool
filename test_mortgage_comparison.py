"""
Test module for mortgage comparison functionality.
"""

import unittest
import os
import tempfile
import shutil
from mortgage_scenario import MortgageScenario
from mortgage_calculator import calculate_equity_buildup, calculate_break_even_point
from mortgage_comparison import compare_scenarios, generate_comparison_table


class TestMortgageScenario(unittest.TestCase):
    """Test cases for MortgageScenario class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_scenario_creation(self):
        """Test scenario creation."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000,
            property_value=360000
        )
        
        self.assertEqual(scenario.name, "Test Scenario")
        self.assertEqual(scenario.loan_amount, 300000)
        self.assertEqual(scenario.interest_rate, 4.5)
        self.assertEqual(scenario.term_years, 30)
        self.assertEqual(scenario.down_payment, 60000)
        self.assertEqual(scenario.property_value, 360000)
        self.assertEqual(scenario.points_paid, 0)
        self.assertIsNone(scenario.reduced_rate)
    
    def test_scenario_with_points(self):
        """Test scenario with points."""
        scenario = MortgageScenario(
            name="Points Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000,
            property_value=360000,
            points_paid=1.5,
            reduced_rate=4.0
        )
        
        self.assertEqual(scenario.points_paid, 1.5)
        self.assertEqual(scenario.reduced_rate, 4.0)
    
    def test_calculate_monthly_payment(self):
        """Test monthly payment calculation."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30
        )
        
        monthly_payment = scenario.calculate_monthly_payment()
        self.assertAlmostEqual(monthly_payment, 1520.06, places=2)
    
    def test_calculate_monthly_payment_with_points(self):
        """Test monthly payment calculation with points."""
        scenario = MortgageScenario(
            name="Points Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            points_paid=1.5,
            reduced_rate=4.0
        )
        
        monthly_payment = scenario.calculate_monthly_payment()
        self.assertAlmostEqual(monthly_payment, 1432.25, places=2)
    
    def test_calculate_total_interest(self):
        """Test total interest calculation."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30
        )
        
        total_interest = scenario.calculate_total_interest()
        self.assertAlmostEqual(total_interest, 247220.13, places=2)
    
    def test_calculate_total_cost(self):
        """Test total cost calculation."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30
        )
        
        total_cost = scenario.calculate_total_cost()
        self.assertAlmostEqual(total_cost, 547220.13, places=2)
    
    def test_calculate_total_cost_with_points(self):
        """Test total cost calculation with points."""
        scenario = MortgageScenario(
            name="Points Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            points_paid=1.5,
            reduced_rate=4.0
        )
        
        # Points cost: 1.5% of 300000 = 4500
        points_cost = 4500
        
        # Calculate total cost with reduced rate
        total_cost = scenario.calculate_total_cost()
        
        # Total cost should include points
        self.assertGreater(total_cost, 300000)
        self.assertAlmostEqual(total_cost, 300000 + scenario.calculate_total_interest() + points_cost, places=2)
    
    def test_calculate_equity_at_year(self):
        """Test equity calculation at specific years."""
        scenario = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000,
            property_value=360000
        )
        
        # At year 0, equity should be just the down payment
        equity_0 = scenario.calculate_equity_at_year(0)
        self.assertEqual(equity_0, 60000)
        
        # At year 5, equity should be down payment plus principal paid in 5 years
        equity_5 = scenario.calculate_equity_at_year(5)
        self.assertGreater(equity_5, 60000)
        
        # At year 30 (end of term), equity should be the full property value
        equity_30 = scenario.calculate_equity_at_year(30)
        self.assertEqual(equity_30, 360000)
    
    def test_calculate_break_even_point(self):
        """Test break-even point calculation."""
        scenario = MortgageScenario(
            name="Points Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            points_paid=1.5,
            reduced_rate=4.0
        )
        
        break_even = scenario.calculate_break_even_point()
        self.assertIsNotNone(break_even)
        self.assertGreater(break_even, 0)
    
    def test_scenario_serialization(self):
        """Test scenario serialization and deserialization."""
        original = MortgageScenario(
            name="Test Scenario",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000,
            property_value=360000,
            points_paid=1.5,
            reduced_rate=4.0
        )
        
        # Convert to dict
        scenario_dict = original.to_dict()
        
        # Create new scenario from dict
        loaded = MortgageScenario.from_dict(scenario_dict)
        
        # Check that all properties match
        self.assertEqual(loaded.name, original.name)
        self.assertEqual(loaded.loan_amount, original.loan_amount)
        self.assertEqual(loaded.interest_rate, original.interest_rate)
        self.assertEqual(loaded.term_years, original.term_years)
        self.assertEqual(loaded.down_payment, original.down_payment)
        self.assertEqual(loaded.property_value, original.property_value)
        self.assertEqual(loaded.points_paid, original.points_paid)
        self.assertEqual(loaded.reduced_rate, original.reduced_rate)
    
    def test_save_and_load(self):
        """Test saving and loading scenarios."""
        scenario = MortgageScenario(
            name="Save Test",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30
        )
        
        # Save to file
        file_path = scenario.save_to_file(directory=self.test_dir)
        self.assertTrue(os.path.exists(file_path))
        
        # Load from file
        loaded = MortgageScenario.load_from_file(file_path)
        
        # Check that properties match
        self.assertEqual(loaded.name, scenario.name)
        self.assertEqual(loaded.loan_amount, scenario.loan_amount)
        self.assertEqual(loaded.interest_rate, scenario.interest_rate)
        self.assertEqual(loaded.term_years, scenario.term_years)


class TestMortgageCalculator(unittest.TestCase):
    """Test cases for new mortgage calculator functions."""
    
    def test_calculate_equity_buildup(self):
        """Test equity buildup calculation."""
        # Test case: $300,000 loan, 4.5% interest, 30-year term, $60,000 down payment, $360,000 property value
        equity_5yr = calculate_equity_buildup(300000, 4.5, 30, 5, 360000, 60000)
        
        # After 5 years, equity should be more than down payment
        self.assertGreater(equity_5yr, 60000)
        
        # After 5 years, equity should be less than property value
        self.assertLess(equity_5yr, 360000)
    
    def test_calculate_break_even_point(self):
        """Test break-even point calculation."""
        # Test case: $4,500 points cost (1.5% of $300,000), $100 monthly savings
        break_even = calculate_break_even_point(4500, 100)
        
        # Break-even should be 45 months
        self.assertEqual(break_even, 45)
        
        # Test with no monthly savings
        break_even = calculate_break_even_point(4500, 0)
        self.assertIsNone(break_even)


class TestMortgageComparison(unittest.TestCase):
    """Test cases for mortgage comparison functionality."""
    
    def test_compare_scenarios(self):
        """Test scenario comparison."""
        # Create two test scenarios
        scenario1 = MortgageScenario(
            name="Scenario 1",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30,
            down_payment=60000
        )
        
        scenario2 = MortgageScenario(
            name="Scenario 2",
            loan_amount=300000,
            interest_rate=4.0,
            term_years=15,
            down_payment=60000
        )
        
        # Compare scenarios
        comparison = compare_scenarios([scenario1, scenario2])
        
        # Check that comparison contains expected keys
        self.assertIn("scenarios", comparison)
        self.assertIn("metrics", comparison)
        
        # Check that scenario names are correct
        self.assertEqual(comparison["scenarios"], ["Scenario 1", "Scenario 2"])
        
        # Check that metrics are present
        metrics = comparison["metrics"]
        self.assertIn("monthly_payment", metrics)
        self.assertIn("total_interest", metrics)
        self.assertIn("total_cost", metrics)
        self.assertIn("equity_5yr", metrics)
        self.assertIn("equity_10yr", metrics)
        self.assertIn("equity_15yr", metrics)
        self.assertIn("break_even_point", metrics)
        
        # Check that metrics have correct length
        self.assertEqual(len(metrics["monthly_payment"]), 2)
        
        # Check that monthly payment for 15-year loan is higher
        self.assertGreater(metrics["monthly_payment"][1], metrics["monthly_payment"][0])
        
        # Check that total interest for 15-year loan is lower
        self.assertLess(metrics["total_interest"][1], metrics["total_interest"][0])
    
    def test_generate_comparison_table(self):
        """Test comparison table generation."""
        # Create two test scenarios
        scenario1 = MortgageScenario(
            name="Scenario 1",
            loan_amount=300000,
            interest_rate=4.5,
            term_years=30
        )
        
        scenario2 = MortgageScenario(
            name="Scenario 2",
            loan_amount=300000,
            interest_rate=4.0,
            term_years=15
        )
        
        # Compare scenarios
        comparison = compare_scenarios([scenario1, scenario2])
        
        # Generate table
        table = generate_comparison_table(comparison)
        
        # Check that table is a list
        self.assertIsInstance(table, list)
        
        # Check that table has expected number of rows (header + 7 metrics)
        self.assertEqual(len(table), 8)
        
        # Check that header row has expected format
        self.assertEqual(table[0], ["Metric", "Scenario 1", "Scenario 2"])


if __name__ == '__main__':
    unittest.main()