"""
Mortgage Analysis Tool - Command Line Interface

This module provides a simple command-line interface for the mortgage analysis tool.
"""

import sys
import json
from datetime import datetime

from mortgage_calculator import (
    calculate_monthly_payment,
    calculate_total_interest,
    calculate_loan_to_value,
    calculate_debt_to_income,
    calculate_pmi,
    calculate_affordability,
    generate_amortization_schedule
)
from mortgage_validator import validate_loan_application
from mortgage_api import get_current_rates, get_property_valuation


def print_header():
    """Print application header."""
    print("\n" + "=" * 60)
    print("MORTGAGE ANALYSIS TOOL".center(60))
    print("=" * 60 + "\n")


def print_menu():
    """Print main menu options."""
    print("\nPlease select an option:")
    print("1. Calculate Monthly Payment")
    print("2. Generate Amortization Schedule")
    print("3. Calculate Loan-to-Value Ratio")
    print("4. Calculate Debt-to-Income Ratio")
    print("5. Calculate PMI")
    print("6. Calculate Affordability")
    print("7. Get Current Mortgage Rates")
    print("8. Get Property Valuation")
    print("9. Exit")
    print()


def get_float_input(prompt, min_value=0):
    """Get float input from user with validation."""
    while True:
        try:
            value = float(input(prompt))
            if value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def get_int_input(prompt, min_value=0):
    """Get integer input from user with validation."""
    while True:
        try:
            value = int(input(prompt))
            if value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


def calculate_payment():
    """Calculate and display monthly mortgage payment."""
    print("\n--- Calculate Monthly Payment ---")
    
    principal = get_float_input("Loan amount ($): ")
    interest_rate = get_float_input("Annual interest rate (%): ")
    term_years = get_int_input("Loan term (years): ")
    
    monthly_payment = calculate_monthly_payment(principal, interest_rate, term_years)
    total_interest = calculate_total_interest(principal, interest_rate, term_years)
    total_cost = principal + total_interest
    
    print("\nResults:")
    print(f"Monthly payment: ${monthly_payment:.2f}")
    print(f"Total interest: ${total_interest:.2f}")
    print(f"Total cost: ${total_cost:.2f}")


def generate_schedule():
    """Generate and display amortization schedule."""
    print("\n--- Generate Amortization Schedule ---")
    
    principal = get_float_input("Loan amount ($): ")
    interest_rate = get_float_input("Annual interest rate (%): ")
    term_years = get_int_input("Loan term (years): ")
    
    schedule = generate_amortization_schedule(principal, interest_rate, term_years)
    
    print("\nAmortization Schedule (first 12 months):")
    print(f"{'Payment #':<10}{'Payment':<15}{'Principal':<15}{'Interest':<15}{'Balance':<15}")
    print("-" * 70)
    
    for payment in schedule[:12]:
        print(f"{payment['payment_num']:<10}${payment['payment']:<14.2f}${payment['principal']:<14.2f}${payment['interest']:<14.2f}${payment['remaining_balance']:<14.2f}")
    
    print("\nSchedule summary:")
    print(f"Total payments: {len(schedule)}")
    print(f"Total interest: ${sum(payment['interest'] for payment in schedule):.2f}")


def calculate_ltv():
    """Calculate and display loan-to-value ratio."""
    print("\n--- Calculate Loan-to-Value Ratio ---")
    
    loan_amount = get_float_input("Loan amount ($): ")
    property_value = get_float_input("Property value ($): ")
    
    ltv = calculate_loan_to_value(loan_amount, property_value)
    
    print("\nResults:")
    print(f"Loan-to-Value Ratio: {ltv:.1f}%")
    
    if ltv > 80:
        print("Note: LTV > 80% typically requires Private Mortgage Insurance (PMI).")


def calculate_dti():
    """Calculate and display debt-to-income ratio."""
    print("\n--- Calculate Debt-to-Income Ratio ---")
    
    monthly_income = get_float_input("Monthly gross income ($): ")
    monthly_debt = get_float_input("Monthly debt payments ($): ")
    
    dti = calculate_debt_to_income(monthly_income, monthly_debt)
    
    print("\nResults:")
    print(f"Debt-to-Income Ratio: {dti:.1f}%")
    
    if dti <= 36:
        print("DTI is good (≤ 36%).")
    elif dti <= 43:
        print("DTI is acceptable (≤ 43%).")
    else:
        print("DTI is high (> 43%). May have difficulty qualifying for a mortgage.")


def calculate_pmi_cost():
    """Calculate and display PMI cost."""
    print("\n--- Calculate PMI ---")
    
    loan_amount = get_float_input("Loan amount ($): ")
    property_value = get_float_input("Property value ($): ")
    
    annual_pmi = calculate_pmi(loan_amount, property_value)
    monthly_pmi = annual_pmi / 12
    
    print("\nResults:")
    if annual_pmi > 0:
        print(f"Annual PMI: ${annual_pmi:.2f}")
        print(f"Monthly PMI: ${monthly_pmi:.2f}")
    else:
        print("No PMI required (LTV ≤ 80%).")


def calculate_max_affordability():
    """Calculate and display maximum affordable home price."""
    print("\n--- Calculate Affordability ---")
    
    monthly_income = get_float_input("Monthly gross income ($): ")
    monthly_debts = get_float_input("Monthly debt payments ($): ")
    down_payment = get_float_input("Available down payment ($): ")
    interest_rate = get_float_input("Expected interest rate (%): ")
    term_years = get_int_input("Loan term (years): ", 1)
    
    max_price = calculate_affordability(
        monthly_income, monthly_debts, down_payment, interest_rate, term_years
    )
    
    print("\nResults:")
    print(f"Maximum affordable home price: ${max_price:.2f}")
    print(f"With down payment: ${down_payment:.2f}")
    print(f"Maximum loan amount: ${max_price - down_payment:.2f}")


def fetch_current_rates():
    """Fetch and display current mortgage rates."""
    print("\n--- Current Mortgage Rates ---")
    
    print("Fetching current rates...")
    
    loan_types = ["Conventional", "FHA", "VA", "USDA", "Jumbo"]
    term_years = [15, 30]
    
    print("\nCurrent Rates:")
    print(f"{'Loan Type':<15}{'Term':<10}{'Rate':<10}{'APR':<10}")
    print("-" * 45)
    
    for loan_type in loan_types:
        for term in term_years:
            rates = get_current_rates(loan_type, term)
            print(f"{loan_type:<15}{term} years{rates['interest_rate']:<10.3f}%{rates['apr']:<10.3f}%")
    
    print(f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def fetch_property_valuation():
    """Fetch and display property valuation."""
    print("\n--- Property Valuation ---")
    
    address = input("Street address: ")
    city = input("City: ")
    state = input("State (2-letter code): ")
    zip_code = input("ZIP code: ")
    
    print("\nFetching property valuation...")
    
    valuation = get_property_valuation(address, city, state, zip_code)
    
    if valuation["success"]:
        print("\nValuation Results:")
        print(f"Estimated value: ${valuation['property_value']:,.2f}")
        print(f"Valuation date: {valuation['valuation_date']}")
        print(f"Confidence score: {valuation['confidence_score']}%")
    else:
        print(f"\nError: {valuation['error']}")


def main():
    """Main application function."""
    print_header()
    
    while True:
        print_menu()
        
        choice = input("Enter your choice (1-9): ")
        
        if choice == '1':
            calculate_payment()
        elif choice == '2':
            generate_schedule()
        elif choice == '3':
            calculate_ltv()
        elif choice == '4':
            calculate_dti()
        elif choice == '5':
            calculate_pmi_cost()
        elif choice == '6':
            calculate_max_affordability()
        elif choice == '7':
            fetch_current_rates()
        elif choice == '8':
            fetch_property_valuation()
        elif choice == '9':
            print("\nThank you for using the Mortgage Analysis Tool. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
