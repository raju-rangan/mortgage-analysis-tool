"""
Mortgage Scenario Module

This module provides a class for representing and managing mortgage scenarios.
"""

import json
import os
from datetime import datetime
from mortgage_calculator import (
    calculate_monthly_payment,
    calculate_total_interest,
    generate_amortization_schedule
)


class MortgageScenario:
    """
    Class representing a mortgage scenario with all relevant parameters and calculations.
    """
    
    def __init__(self, name, loan_amount, interest_rate, term_years, down_payment=0, 
                 property_value=None, points_paid=0, reduced_rate=None):
        """
        Initialize a mortgage scenario.
        
        Args:
            name (str): Name of the scenario
            loan_amount (float): Loan principal amount
            interest_rate (float): Annual interest rate (percentage)
            term_years (int): Loan term in years
            down_payment (float, optional): Down payment amount
            property_value (float, optional): Property value (if None, assumed to be loan_amount + down_payment)
            points_paid (float, optional): Mortgage points paid (percentage of loan amount)
            reduced_rate (float, optional): Reduced interest rate if points are paid
        """
        self.name = name
        self.loan_amount = float(loan_amount)
        self.interest_rate = float(interest_rate)
        self.term_years = int(term_years)
        self.down_payment = float(down_payment)
        
        # If property value is not provided, assume it's the loan amount plus down payment
        if property_value is None:
            self.property_value = self.loan_amount + self.down_payment
        else:
            self.property_value = float(property_value)
        
        self.points_paid = float(points_paid)
        self.reduced_rate = float(reduced_rate) if reduced_rate is not None else None
        self.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def calculate_monthly_payment(self):
        """
        Calculate the monthly payment for this scenario.
        
        Returns:
            float: Monthly payment amount
        """
        # Use the reduced rate if points were paid, otherwise use the standard rate
        rate = self.reduced_rate if self.reduced_rate is not None else self.interest_rate
        return calculate_monthly_payment(self.loan_amount, rate, self.term_years)
    
    def calculate_total_interest(self):
        """
        Calculate the total interest paid over the life of the loan.
        
        Returns:
            float: Total interest paid
        """
        # Use the reduced rate if points were paid, otherwise use the standard rate
        rate = self.reduced_rate if self.reduced_rate is not None else self.interest_rate
        return calculate_total_interest(self.loan_amount, rate, self.term_years)
    
    def calculate_total_cost(self):
        """
        Calculate the total cost of the loan including principal, interest, and points.
        
        Returns:
            float: Total cost of the loan
        """
        total_interest = self.calculate_total_interest()
        points_cost = (self.points_paid / 100) * self.loan_amount
        return self.loan_amount + total_interest + points_cost
    
    def calculate_equity_at_year(self, year):
        """
        Calculate the equity built up after a specific number of years.
        
        Args:
            year (int): Number of years
            
        Returns:
            float: Equity amount
        """
        if year <= 0:
            return self.down_payment
        
        if year > self.term_years:
            return self.property_value
        
        # Use the reduced rate if points were paid, otherwise use the standard rate
        rate = self.reduced_rate if self.reduced_rate is not None else self.interest_rate
        
        # Generate amortization schedule up to the specified year
        schedule = generate_amortization_schedule(self.loan_amount, rate, self.term_years)
        payments_per_year = 12
        payment_index = min(year * payments_per_year, len(schedule)) - 1
        
        # Calculate principal paid so far
        principal_paid = self.loan_amount - schedule[payment_index]['remaining_balance']
        
        # Equity is down payment plus principal paid
        return self.down_payment + principal_paid
    
    def calculate_break_even_point(self):
        """
        Calculate the break-even point in months if points were paid to reduce the interest rate.
        
        Returns:
            float or None: Break-even point in months, or None if no points were paid
        """
        if self.points_paid == 0 or self.reduced_rate is None or self.reduced_rate >= self.interest_rate:
            return None
        
        # Calculate monthly payments with and without points
        monthly_payment_with_points = calculate_monthly_payment(
            self.loan_amount, self.reduced_rate, self.term_years)
        monthly_payment_without_points = calculate_monthly_payment(
            self.loan_amount, self.interest_rate, self.term_years)
        
        # Calculate monthly savings
        monthly_savings = monthly_payment_without_points - monthly_payment_with_points
        
        if monthly_savings <= 0:
            return None
        
        # Calculate points cost
        points_cost = (self.points_paid / 100) * self.loan_amount
        
        # Calculate break-even point in months
        break_even_months = points_cost / monthly_savings
        
        return break_even_months
    
    def to_dict(self):
        """
        Convert the scenario to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the scenario
        """
        return {
            'name': self.name,
            'loan_amount': self.loan_amount,
            'interest_rate': self.interest_rate,
            'term_years': self.term_years,
            'down_payment': self.down_payment,
            'property_value': self.property_value,
            'points_paid': self.points_paid,
            'reduced_rate': self.reduced_rate,
            'creation_date': self.creation_date
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a scenario from a dictionary.
        
        Args:
            data (dict): Dictionary containing scenario data
            
        Returns:
            MortgageScenario: New scenario instance
        """
        scenario = cls(
            name=data['name'],
            loan_amount=data['loan_amount'],
            interest_rate=data['interest_rate'],
            term_years=data['term_years'],
            down_payment=data.get('down_payment', 0),
            property_value=data.get('property_value'),
            points_paid=data.get('points_paid', 0),
            reduced_rate=data.get('reduced_rate')
        )
        
        if 'creation_date' in data:
            scenario.creation_date = data['creation_date']
        
        return scenario
    
    def save_to_file(self, directory='scenarios'):
        """
        Save the scenario to a JSON file.
        
        Args:
            directory (str, optional): Directory to save the file in
            
        Returns:
            str: Path to the saved file
        """
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create filename based on scenario name
        safe_name = self.name.replace(' ', '_').lower()
        filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        file_path = os.path.join(directory, filename)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
        
        return file_path
    
    @classmethod
    def load_from_file(cls, file_path):
        """
        Load a scenario from a JSON file.
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            MortgageScenario: Loaded scenario
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @staticmethod
    def list_saved_scenarios(directory='scenarios'):
        """
        List all saved scenarios in the specified directory.
        
        Args:
            directory (str, optional): Directory to look for scenario files
            
        Returns:
            list: List of dictionaries with file info (path, name, date)
        """
        if not os.path.exists(directory):
            return []
        
        scenarios = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    scenarios.append({
                        'path': file_path,
                        'name': data.get('name', 'Unknown'),
                        'date': data.get('creation_date', 'Unknown')
                    })
                except (json.JSONDecodeError, KeyError):
                    # Skip invalid files
                    pass
        
        return scenarios