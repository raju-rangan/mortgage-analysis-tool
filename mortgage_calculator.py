"""
Mortgage Calculator Module

This module provides functions for calculating mortgage payments,
amortization schedules, and other mortgage-related metrics.
"""

import math
from datetime import datetime


def calculate_monthly_payment(principal, annual_interest_rate, term_years):
    """
    Calculate the monthly payment for a fixed-rate mortgage.
    
    Args:
        principal (float): Loan principal amount
        annual_interest_rate (float): Annual interest rate (percentage)
        term_years (int): Loan term in years
        
    Returns:
        float: Monthly payment amount
    """
    # Convert annual interest rate to monthly decimal rate
    monthly_rate = annual_interest_rate / 100 / 12
    
    # Calculate number of payments
    num_payments = term_years * 12
    
    # Calculate monthly payment using the mortgage payment formula
    if monthly_rate == 0:
        # Handle edge case of 0% interest
        return principal / num_payments
    
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    return monthly_payment


def generate_amortization_schedule(principal, annual_interest_rate, term_years):
    """
    Generate a complete amortization schedule for a mortgage.
    
    Args:
        principal (float): Loan principal amount
        annual_interest_rate (float): Annual interest rate (percentage)
        term_years (int): Loan term in years
        
    Returns:
        list: List of dictionaries containing payment details for each period
    """
    # Convert annual interest rate to monthly decimal rate
    monthly_rate = annual_interest_rate / 100 / 12
    
    # Calculate number of payments
    num_payments = term_years * 12
    
    # Calculate monthly payment
    monthly_payment = calculate_monthly_payment(principal, annual_interest_rate, term_years)
    
    # Initialize schedule
    schedule = []
    remaining_balance = principal
    
    for payment_num in range(1, num_payments + 1):
        # Calculate interest for this period
        interest_payment = remaining_balance * monthly_rate
        
        # Calculate principal for this period
        principal_payment = monthly_payment - interest_payment
        
        # Update remaining balance
        remaining_balance -= principal_payment
        
        # Handle potential floating point errors in final payment
        if payment_num == num_payments:
            principal_payment += remaining_balance
            remaining_balance = 0
        
        # Add payment details to schedule
        schedule.append({
            'payment_num': payment_num,
            'payment': monthly_payment,
            'principal': principal_payment,
            'interest': interest_payment,
            'remaining_balance': remaining_balance
        })
    
    return schedule


def calculate_total_interest(principal, annual_interest_rate, term_years):
    """
    Calculate the total interest paid over the life of the loan.
    
    Args:
        principal (float): Loan principal amount
        annual_interest_rate (float): Annual interest rate (percentage)
        term_years (int): Loan term in years
        
    Returns:
        float: Total interest paid
    """
    monthly_payment = calculate_monthly_payment(principal, annual_interest_rate, term_years)
    total_payments = monthly_payment * term_years * 12
    total_interest = total_payments - principal
    
    return total_interest


def calculate_loan_to_value(loan_amount, property_value):
    """
    Calculate the Loan-to-Value (LTV) ratio.
    
    Args:
        loan_amount (float): Loan principal amount
        property_value (float): Appraised property value
        
    Returns:
        float: LTV ratio as a percentage
    """
    return (loan_amount / property_value) * 100


def calculate_debt_to_income(monthly_income, monthly_debt):
    """
    Calculate Debt-to-Income ratio.
    
    Args:
        monthly_income (float): Monthly gross income
        monthly_debt (float): Monthly debt payments
        
    Returns:
        float: DTI ratio as a percentage
    """
    return (monthly_debt / monthly_income) * 100


default_pmi_rate = 0.005

def calculate_pmi(loan_amount, property_value):
    """
    Calculate Private Mortgage Insurance (PMI) for loans with LTV > 80%.
    
    Args:
        loan_amount (float): Loan principal amount
        property_value (float): Appraised property value
        
    Returns:
        float: Annual PMI cost, or 0 if LTV <= 80%
    """
    ltv = calculate_loan_to_value(loan_amount, property_value)
    
    # PMI typically required if LTV > 80%
    if ltv <= 80:
        return 0
    
    annual_pmi = loan_amount * default_pmi_rate
    
    return annual_pmi


def calculate_affordability(monthly_income, monthly_debts, down_payment, annual_interest_rate, term_years, property_tax_rate=0.0125, insurance_rate=0.0035):
    """
    Calculate the maximum affordable home price based on income and debts.
    
    Args:
        monthly_income (float): Gross monthly income
        monthly_debts (float): Monthly debt payments
        down_payment (float): Available down payment
        annual_interest_rate (float): Annual interest rate (percentage)
        term_years (int): Loan term in years
        property_tax_rate (float, optional): Annual property tax rate
        insurance_rate (float, optional): Annual insurance rate
        
    Returns:
        float: Maximum affordable home price
    """
    # Maximum recommended DTI ratio (43%)
    max_dti = 0.43
    
    # Maximum monthly payment available for PITI
    # (Principal, Interest, Taxes, Insurance)
    max_piti = monthly_income * max_dti - monthly_debts
    
    # Monthly tax and insurance rates
    monthly_tax_rate = property_tax_rate / 12
    monthly_insurance_rate = insurance_rate / 12
    
    # Maximum amount available for principal and interest
    max_pi = max_piti / (1 + monthly_tax_rate + monthly_insurance_rate)
    
    # Convert annual interest rate to monthly decimal rate
    monthly_rate = annual_interest_rate / 100 / 12
    
    # Calculate number of payments
    num_payments = term_years * 12
    
    if monthly_rate == 0:
        max_loan = max_pi * num_payments
    else:
        max_loan = max_pi * ((1 - (1 + monthly_rate) ** -num_payments) / monthly_rate)
    
    # Add down payment to get maximum affordable home price
    max_price = max_loan + down_payment
    
    return max_price


# Feature to be added during demo: Refinance Analysis
def calculate_refinance_savings(current_principal, current_rate, current_term_remaining, 
                               new_rate, new_term, closing_costs):
    """
    Calculate potential savings from refinancing a mortgage.
    
    Args:
        current_principal (float): Remaining loan balance
        current_rate (float): Current annual interest rate (percentage)
        current_term_remaining (int): Remaining term in years
        new_rate (float): New annual interest rate (percentage)
        new_term (int): New loan term in years
        closing_costs (float): Refinance closing costs
        
    Returns:
        dict: Refinance analysis results
    """
    # Calculate current monthly payment
    current_payment = calculate_monthly_payment(
        current_principal, current_rate, current_term_remaining)
    
    # Calculate new monthly payment
    new_payment = calculate_monthly_payment(
        current_principal, new_rate, new_term)
    
    # Calculate total payments under current loan
    current_total = current_payment * current_term_remaining * 12
    
    # Calculate total payments under new loan
    new_total = new_payment * new_term * 12
    
    # Calculate monthly savings
    monthly_savings = current_payment - new_payment
    
    # Calculate lifetime savings (including closing costs)
    lifetime_savings = current_total - new_total - closing_costs
    
    # Calculate break-even point in months
    if monthly_savings > 0:
        break_even_months = closing_costs / monthly_savings
    else:
        break_even_months = float('inf')  # No break-even if no monthly savings
    
    return {
        'current_payment': current_payment,
        'new_payment': new_payment,
        'monthly_savings': monthly_savings,
        'lifetime_savings': lifetime_savings,
        'break_even_months': break_even_months
    }
