"""
Mortgage Analysis Tool - Command Line Interface

This module provides a simple command-line interface for the mortgage analysis tool.
"""

import sys
import json
import os
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
from mortgage_comparison import MortgageScenario, MortgageComparison


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
    print("9. Compare Mortgage Scenarios")
    print("0. Exit")
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


def compare_mortgages(mortgage_comparison):
    """Compare multiple mortgage scenarios."""
    print("\n--- Mortgage Comparison Tool ---")
    
    while True:
        print("\nMortgage Comparison Menu:")
        print("1. Create New Scenario")
        print("2. View All Scenarios")
        print("3. Remove Scenario")
        print("4. Compare Scenarios")
        print("5. Generate Payment Breakdown Chart")
        print("6. Export Comparison to CSV")
        print("7. Save Scenarios")
        print("8. Load Scenarios")
        print("9. Return to Main Menu")
        
        choice = input("\nEnter your choice (1-9): ")
        
        if choice == '1':
            create_scenario(mortgage_comparison)
        elif choice == '2':
            view_scenarios(mortgage_comparison)
        elif choice == '3':
            remove_scenario(mortgage_comparison)
        elif choice == '4':
            display_comparison(mortgage_comparison)
        elif choice == '5':
            generate_chart(mortgage_comparison)
        elif choice == '6':
            export_comparison(mortgage_comparison)
        elif choice == '7':
            save_scenarios(mortgage_comparison)
        elif choice == '8':
            load_scenarios(mortgage_comparison)
        elif choice == '9':
            return
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


def create_scenario(mortgage_comparison):
    """Create a new mortgage scenario."""
    print("\n--- Create New Mortgage Scenario ---")
    
    name = input("Scenario name: ")
    
    # Check if scenario with this name already exists
    if mortgage_comparison.get_scenario(name):
        print(f"\nA scenario with the name '{name}' already exists.")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            return
    
    loan_amount = get_float_input("Loan amount ($): ")
    interest_rate = get_float_input("Annual interest rate (%): ")
    term_years = get_int_input("Loan term (years): ")
    down_payment = get_float_input("Down payment ($): ")
    points = get_float_input("Points paid (%): ")
    
    property_value_input = input("Property value ($, leave blank to use loan + down payment): ")
    property_value = float(property_value_input) if property_value_input else None
    
    annual_appreciation = get_float_input("Annual property appreciation rate (%, default 2.0): ", min_value=-10)
    
    # Create scenario
    scenario = MortgageScenario(
        name=name,
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        term_years=term_years,
        down_payment=down_payment,
        points=points,
        property_value=property_value,
        annual_appreciation=annual_appreciation
    )
    
    # Add to comparison
    mortgage_comparison.add_scenario(scenario)
    
    print(f"\nScenario '{name}' created successfully.")
    print(f"Monthly payment: ${scenario.monthly_payment:.2f}")
    print(f"Total interest: ${scenario.total_interest:.2f}")
    print(f"Total cost: ${scenario.total_cost:.2f}")


def view_scenarios(mortgage_comparison):
    """View all mortgage scenarios."""
    print("\n--- All Mortgage Scenarios ---")
    
    scenarios = mortgage_comparison.get_all_scenarios()
    
    if not scenarios:
        print("No scenarios have been created yet.")
        return
    
    print(f"\nTotal scenarios: {len(scenarios)}")
    print(f"{'Name':<20}{'Loan Amount':<15}{'Interest Rate':<15}{'Term':<10}{'Monthly Payment':<20}")
    print("-" * 80)
    
    for name, scenario in scenarios.items():
        print(f"{name:<20}${scenario.loan_amount:<14,.2f}{scenario.interest_rate:<15.2f}{scenario.term_years:<10}${scenario.monthly_payment:<19,.2f}")


def remove_scenario(mortgage_comparison):
    """Remove a mortgage scenario."""
    print("\n--- Remove Mortgage Scenario ---")
    
    scenarios = mortgage_comparison.get_all_scenarios()
    
    if not scenarios:
        print("No scenarios have been created yet.")
        return
    
    print("\nAvailable scenarios:")
    for i, name in enumerate(scenarios.keys(), 1):
        print(f"{i}. {name}")
    
    choice = input("\nEnter the number of the scenario to remove (or 'c' to cancel): ")
    
    if choice.lower() == 'c':
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(scenarios):
            scenario_name = list(scenarios.keys())[index]
            confirm = input(f"Are you sure you want to remove '{scenario_name}'? (y/n): ").lower()
            
            if confirm == 'y':
                mortgage_comparison.remove_scenario(scenario_name)
                print(f"\nScenario '{scenario_name}' removed successfully.")
            else:
                print("\nRemoval cancelled.")
        else:
            print("\nInvalid selection.")
    except ValueError:
        print("\nInvalid input. Please enter a number.")


def display_comparison(mortgage_comparison):
    """Display comparison of mortgage scenarios."""
    print("\n--- Mortgage Comparison Results ---")
    
    scenarios = mortgage_comparison.get_all_scenarios()
    
    if not scenarios:
        print("No scenarios have been created yet.")
        return
    
    if len(scenarios) < 2:
        print("You need at least 2 scenarios to compare. Please create another scenario.")
        return
    
    comparison = mortgage_comparison.generate_comparison_table()
    
    # Display comparison table
    print("\nComparison Table:")
    print(f"{'Metric':<20}", end="")
    
    for name in comparison['scenarios']:
        print(f"{name:<15}", end="")
    print()
    
    print("-" * (20 + 15 * len(comparison['scenarios'])))
    
    print(f"{'Monthly Payment':<20}", end="")
    for payment in comparison['monthly_payment']:
        print(f"${payment:<14,.2f}", end="")
    print()
    
    print(f"{'Total Interest':<20}", end="")
    for interest in comparison['total_interest']:
        print(f"${interest:<14,.2f}", end="")
    print()
    
    print(f"{'Total Cost':<20}", end="")
    for cost in comparison['total_cost']:
        print(f"${cost:<14,.2f}", end="")
    print()
    
    print(f"{'Equity (5 years)':<20}", end="")
    for equity in comparison['equity_5yr']:
        print(f"${equity:<14,.2f}", end="")
    print()
    
    print(f"{'Equity (10 years)':<20}", end="")
    for equity in comparison['equity_10yr']:
        print(f"${equity:<14,.2f}", end="")
    print()
    
    print(f"{'Equity (15 years)':<20}", end="")
    for equity in comparison['equity_15yr']:
        print(f"${equity:<14,.2f}", end="")
    print()


def generate_chart(mortgage_comparison):
    """Generate and display payment breakdown chart."""
    print("\n--- Generate Payment Breakdown Chart ---")
    
    scenarios = mortgage_comparison.get_all_scenarios()
    
    if not scenarios:
        print("No scenarios have been created yet.")
        return
    
    if len(scenarios) < 1:
        print("You need at least 1 scenario to generate a chart.")
        return
    
    print("\nGenerating payment breakdown chart...")
    
    # Create scenarios directory if it doesn't exist
    chart_dir = os.path.join(os.path.dirname(__file__), "charts")
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    
    # Generate chart
    chart_path = os.path.join(chart_dir, f"payment_breakdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    mortgage_comparison.generate_payment_breakdown_chart(chart_path)
    
    print(f"\nChart generated and saved to: {chart_path}")
    print("Note: In a GUI application, this chart would be displayed directly.")


def export_comparison(mortgage_comparison):
    """Export comparison results to CSV."""
    print("\n--- Export Comparison Results ---")
    
    scenarios = mortgage_comparison.get_all_scenarios()
    
    if not scenarios:
        print("No scenarios have been created yet.")
        return
    
    if len(scenarios) < 2:
        print("You need at least 2 scenarios to compare and export.")
        return
    
    print("\nExporting comparison results...")
    
    # Export to CSV
    csv_path = mortgage_comparison.export_to_csv()
    
    print(f"\nComparison exported to CSV: {csv_path}")
    print("Note: PDF export would require additional libraries in a real implementation.")


def save_scenarios(mortgage_comparison):
    """Save mortgage scenarios to a file."""
    print("\n--- Save Mortgage Scenarios ---")
    
    scenarios = mortgage_comparison.get_all_scenarios()
    
    if not scenarios:
        print("No scenarios have been created yet.")
        return
    
    filename = input("Enter filename (leave blank for auto-generated name): ")
    
    if not filename:
        filename = None
    
    file_path = mortgage_comparison.save_scenarios(filename)
    
    print(f"\nScenarios saved to: {file_path}")


def load_scenarios(mortgage_comparison):
    """Load mortgage scenarios from a file."""
    print("\n--- Load Mortgage Scenarios ---")
    
    # Get list of saved scenario files
    scenarios_dir = os.path.join(os.path.dirname(__file__), "scenarios")
    
    if not os.path.exists(scenarios_dir):
        print("No saved scenarios found.")
        return
    
    scenario_files = [f for f in os.listdir(scenarios_dir) if f.endswith('.json')]
    
    if not scenario_files:
        print("No saved scenarios found.")
        return
    
    print("\nAvailable scenario files:")
    for i, filename in enumerate(scenario_files, 1):
        print(f"{i}. {filename}")
    
    choice = input("\nEnter the number of the file to load (or 'c' to cancel): ")
    
    if choice.lower() == 'c':
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(scenario_files):
            filename = scenario_files[index]
            
            # Confirm if there are existing scenarios
            if mortgage_comparison.get_all_scenarios():
                confirm = input("This will replace all current scenarios. Continue? (y/n): ").lower()
                if confirm != 'y':
                    return
            
            success = mortgage_comparison.load_scenarios(filename)
            
            if success:
                print(f"\nScenarios loaded successfully from: {filename}")
            else:
                print(f"\nError loading scenarios from: {filename}")
        else:
            print("\nInvalid selection.")
    except ValueError:
        print("\nInvalid input. Please enter a number.")


def main():
    """Main application function."""
    print_header()
    
    # Initialize mortgage comparison
    mortgage_comparison = MortgageComparison()
    
    while True:
        print_menu()
        
        choice = input("Enter your choice (0-9): ")
        
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
            compare_mortgages(mortgage_comparison)
        elif choice == '0':
            print("\nThank you for using the Mortgage Analysis Tool. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
