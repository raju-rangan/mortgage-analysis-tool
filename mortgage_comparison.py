"""
Mortgage Comparison Module

This module provides functionality for comparing multiple mortgage scenarios.
"""

import csv
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO

from mortgage_calculator import (
    calculate_monthly_payment,
    calculate_total_interest,
    generate_amortization_schedule
)


class MortgageScenario:
    """
    Class representing a single mortgage scenario with its parameters and calculated metrics.
    """
    
    def __init__(self, name, loan_amount, interest_rate, term_years, down_payment=0, points=0, 
                 property_value=None, annual_appreciation=2.0):
        """
        Initialize a mortgage scenario.
        
        Args:
            name (str): Name of the scenario
            loan_amount (float): Loan principal amount
            interest_rate (float): Annual interest rate (percentage)
            term_years (int): Loan term in years
            down_payment (float, optional): Down payment amount
            points (float, optional): Mortgage points paid (percentage)
            property_value (float, optional): Total property value (loan_amount + down_payment if None)
            annual_appreciation (float, optional): Annual property appreciation rate (percentage)
        """
        self.name = name
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate
        self.term_years = term_years
        self.down_payment = down_payment
        self.points = points
        self.property_value = property_value if property_value is not None else (loan_amount + down_payment)
        self.annual_appreciation = annual_appreciation
        
        # Calculate derived metrics
        self.monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, term_years)
        self.total_interest = calculate_total_interest(loan_amount, interest_rate, term_years)
        self.total_cost = loan_amount + self.total_interest
        self.amortization_schedule = None  # Lazy-loaded when needed
    
    def get_amortization_schedule(self):
        """
        Get the amortization schedule for this scenario.
        
        Returns:
            list: Amortization schedule
        """
        if self.amortization_schedule is None:
            self.amortization_schedule = generate_amortization_schedule(
                self.loan_amount, self.interest_rate, self.term_years
            )
        return self.amortization_schedule
    
    def calculate_equity_at_year(self, year):
        """
        Calculate equity buildup at a specific year.
        
        Args:
            year (int): Year to calculate equity for
            
        Returns:
            dict: Equity breakdown including principal paid, property value, and total equity
        """
        if year > self.term_years:
            year = self.term_years
            
        # Get amortization schedule
        schedule = self.get_amortization_schedule()
        
        # Calculate payment number for the given year
        payment_num = year * 12
        
        # If payment_num exceeds the length of the schedule, use the last payment
        if payment_num >= len(schedule):
            payment_num = len(schedule) - 1
        
        # Calculate principal paid (original loan amount - remaining balance)
        principal_paid = self.loan_amount - schedule[payment_num]['remaining_balance']
        
        # Calculate property value with appreciation
        appreciated_value = self.property_value * ((1 + self.annual_appreciation / 100) ** year)
        
        # Calculate total equity (principal paid + down payment + appreciation)
        total_equity = principal_paid + self.down_payment + (appreciated_value - self.property_value)
        
        return {
            'year': year,
            'principal_paid': principal_paid,
            'property_value': appreciated_value,
            'total_equity': total_equity,
            'equity_percentage': (total_equity / appreciated_value) * 100
        }
    
    def calculate_break_even_point(self, points_cost, reduced_interest_rate):
        """
        Calculate break-even point for paying points to reduce interest rate.
        
        Args:
            points_cost (float): Cost of points as percentage of loan amount
            reduced_interest_rate (float): Reduced interest rate after paying points
            
        Returns:
            dict: Break-even analysis including monthly savings, break-even months, and total savings
        """
        # Calculate cost of points
        points_dollar_cost = self.loan_amount * (points_cost / 100)
        
        # Calculate monthly payment with original rate
        original_payment = self.monthly_payment
        
        # Calculate monthly payment with reduced rate
        reduced_payment = calculate_monthly_payment(self.loan_amount, reduced_interest_rate, self.term_years)
        
        # Calculate monthly savings
        monthly_savings = original_payment - reduced_payment
        
        # Calculate break-even point in months
        if monthly_savings > 0:
            break_even_months = points_dollar_cost / monthly_savings
            break_even_years = break_even_months / 12
        else:
            break_even_months = float('inf')
            break_even_years = float('inf')
        
        # Calculate total savings over the life of the loan
        total_payment_savings = monthly_savings * self.term_years * 12
        net_savings = total_payment_savings - points_dollar_cost
        
        return {
            'points_cost': points_dollar_cost,
            'original_payment': original_payment,
            'reduced_payment': reduced_payment,
            'monthly_savings': monthly_savings,
            'break_even_months': break_even_months,
            'break_even_years': break_even_years,
            'total_payment_savings': total_payment_savings,
            'net_savings': net_savings
        }
    
    def to_dict(self):
        """
        Convert scenario to dictionary for serialization.
        
        Returns:
            dict: Scenario data as dictionary
        """
        return {
            'name': self.name,
            'loan_amount': self.loan_amount,
            'interest_rate': self.interest_rate,
            'term_years': self.term_years,
            'down_payment': self.down_payment,
            'points': self.points,
            'property_value': self.property_value,
            'annual_appreciation': self.annual_appreciation,
            'monthly_payment': self.monthly_payment,
            'total_interest': self.total_interest,
            'total_cost': self.total_cost
        }


class MortgageComparison:
    """
    Class for comparing multiple mortgage scenarios.
    """
    
    def __init__(self):
        """Initialize an empty mortgage comparison."""
        self.scenarios = {}
        self.data_dir = os.path.join(os.path.dirname(__file__), "scenarios")
        
        # Create scenarios directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def add_scenario(self, scenario):
        """
        Add a scenario to the comparison.
        
        Args:
            scenario (MortgageScenario): Scenario to add
        """
        self.scenarios[scenario.name] = scenario
    
    def remove_scenario(self, scenario_name):
        """
        Remove a scenario from the comparison.
        
        Args:
            scenario_name (str): Name of scenario to remove
            
        Returns:
            bool: True if scenario was removed, False if not found
        """
        if scenario_name in self.scenarios:
            del self.scenarios[scenario_name]
            return True
        return False
    
    def get_scenario(self, scenario_name):
        """
        Get a scenario by name.
        
        Args:
            scenario_name (str): Name of scenario to get
            
        Returns:
            MortgageScenario or None: The scenario if found, None otherwise
        """
        return self.scenarios.get(scenario_name)
    
    def get_all_scenarios(self):
        """
        Get all scenarios.
        
        Returns:
            dict: All scenarios
        """
        return self.scenarios
    
    def save_scenarios(self, filename=None):
        """
        Save all scenarios to a file.
        
        Args:
            filename (str, optional): Filename to save to. If None, uses current timestamp.
            
        Returns:
            str: Path to saved file
        """
        if filename is None:
            filename = f"mortgage_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        file_path = os.path.join(self.data_dir, filename)
        
        # Convert scenarios to dictionaries
        scenarios_dict = {name: scenario.to_dict() for name, scenario in self.scenarios.items()}
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(scenarios_dict, f, indent=2)
        
        return file_path
    
    def load_scenarios(self, filename):
        """
        Load scenarios from a file.
        
        Args:
            filename (str): Filename to load from
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        file_path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                scenarios_dict = json.load(f)
            
            # Clear existing scenarios
            self.scenarios = {}
            
            # Create scenario objects from dictionaries
            for name, scenario_data in scenarios_dict.items():
                scenario = MortgageScenario(
                    name=scenario_data['name'],
                    loan_amount=scenario_data['loan_amount'],
                    interest_rate=scenario_data['interest_rate'],
                    term_years=scenario_data['term_years'],
                    down_payment=scenario_data['down_payment'],
                    points=scenario_data['points'],
                    property_value=scenario_data['property_value'],
                    annual_appreciation=scenario_data['annual_appreciation']
                )
                self.scenarios[name] = scenario
            
            return True
        except Exception as e:
            print(f"Error loading scenarios: {e}")
            return False
    
    def generate_comparison_table(self):
        """
        Generate a comparison table of all scenarios.
        
        Returns:
            dict: Comparison data
        """
        if not self.scenarios:
            return None
        
        comparison = {
            'scenarios': [],
            'monthly_payment': [],
            'total_interest': [],
            'total_cost': [],
            'equity_5yr': [],
            'equity_10yr': [],
            'equity_15yr': []
        }
        
        for name, scenario in self.scenarios.items():
            comparison['scenarios'].append(name)
            comparison['monthly_payment'].append(scenario.monthly_payment)
            comparison['total_interest'].append(scenario.total_interest)
            comparison['total_cost'].append(scenario.total_cost)
            
            # Calculate equity at 5, 10, and 15 years
            equity_5yr = scenario.calculate_equity_at_year(5)['total_equity']
            equity_10yr = scenario.calculate_equity_at_year(10)['total_equity']
            equity_15yr = scenario.calculate_equity_at_year(15)['total_equity']
            
            comparison['equity_5yr'].append(equity_5yr)
            comparison['equity_10yr'].append(equity_10yr)
            comparison['equity_15yr'].append(equity_15yr)
        
        return comparison
    
    def generate_payment_breakdown_chart(self, output_path=None):
        """
        Generate a chart showing payment breakdown over time for each scenario.
        
        Args:
            output_path (str, optional): Path to save the chart. If None, returns BytesIO object.
            
        Returns:
            str or BytesIO: Path to saved chart or BytesIO object containing the chart
        """
        if not self.scenarios:
            return None
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot each scenario
        for name, scenario in self.scenarios.items():
            schedule = scenario.get_amortization_schedule()
            
            # Extract data for plotting
            payments = [payment['payment_num'] for payment in schedule]
            principal_payments = [payment['principal'] for payment in schedule]
            interest_payments = [payment['interest'] for payment in schedule]
            
            # Plot principal and interest over time
            ax.plot(payments, principal_payments, label=f"{name} - Principal")
            ax.plot(payments, interest_payments, label=f"{name} - Interest", linestyle='--')
        
        # Add labels and legend
        ax.set_xlabel('Payment Number')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Payment Breakdown Over Time')
        ax.legend()
        ax.grid(True)
        
        # Save or return the chart
        if output_path:
            plt.savefig(output_path)
            plt.close(fig)
            return output_path
        else:
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            return buf
    
    def export_to_csv(self, output_path=None):
        """
        Export comparison results to CSV.
        
        Args:
            output_path (str, optional): Path to save the CSV. If None, uses current timestamp.
            
        Returns:
            str: Path to saved CSV
        """
        if not self.scenarios:
            return None
        
        if output_path is None:
            output_path = os.path.join(
                self.data_dir, 
                f"mortgage_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        
        comparison = self.generate_comparison_table()
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Metric'] + comparison['scenarios'])
            
            # Write data rows
            writer.writerow(['Monthly Payment'] + [f"${payment:.2f}" for payment in comparison['monthly_payment']])
            writer.writerow(['Total Interest'] + [f"${interest:.2f}" for interest in comparison['total_interest']])
            writer.writerow(['Total Cost'] + [f"${cost:.2f}" for cost in comparison['total_cost']])
            writer.writerow(['Equity (5 years)'] + [f"${equity:.2f}" for equity in comparison['equity_5yr']])
            writer.writerow(['Equity (10 years)'] + [f"${equity:.2f}" for equity in comparison['equity_10yr']])
            writer.writerow(['Equity (15 years)'] + [f"${equity:.2f}" for equity in comparison['equity_15yr']])
        
        return output_path
    
    def export_to_pdf(self, output_path=None):
        """
        Export comparison results to PDF.
        
        Args:
            output_path (str, optional): Path to save the PDF. If None, uses current timestamp.
            
        Returns:
            str: Path to saved PDF
        """
        # Note: This is a placeholder. In a real implementation, we would use a library like reportlab
        # to generate a PDF. For this example, we'll just return a message.
        if not self.scenarios:
            return None
        
        if output_path is None:
            output_path = os.path.join(
                self.data_dir, 
                f"mortgage_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        
        # Generate chart
        chart_path = os.path.join(self.data_dir, "temp_chart.png")
        self.generate_payment_breakdown_chart(chart_path)
        
        # In a real implementation, we would use reportlab to create a PDF with the comparison table
        # and the chart. For this example, we'll just return the path.
        
        return output_path