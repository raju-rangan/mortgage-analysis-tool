"""
Mortgage Analysis Tool - Command Line Interface

This module provides a simple command-line interface for the mortgage analysis tool.
"""

import sys
import json
import getpass
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
from mortgage_security import (
    create_user_account,
    submit_loan_application,
    check_application_status,
    admin_dashboard,
    process_pending_applications,
    MortgageSecurity
)


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
    print("9. User Account Management")
    print("10. Loan Application")
    print("11. Admin Functions")
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


def manage_user_account():
    """Manage user account functions."""
    print("\n--- User Account Management ---")
    
    print("\nPlease select an option:")
    print("1. Create New Account")
    print("2. Login")
    print("3. Back to Main Menu")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        create_account()
    elif choice == '2':
        login_account()
    elif choice == '3':
        return
    else:
        print("\nInvalid choice. Returning to main menu.")


def create_account():
    """Create a new user account."""
    print("\n--- Create New Account ---")
    
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    email = input("Email: ")
    ssn = input("SSN (XXX-XX-XXXX): ")
    dob = input("Date of Birth (YYYY-MM-DD): ")
    
    success, message = create_user_account(username, password, email, ssn, dob)
    
    if success:
        print(f"\nSuccess: {message}")
    else:
        print(f"\nError: {message}")


def login_account():
    """Login to an existing account."""
    print("\n--- Login ---")
    
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    security = MortgageSecurity()
    if security.authenticate_user(username, password):
        print("\nLogin successful!")
        user_dashboard(username, password)
    else:
        print("\nLogin failed. Invalid username or password.")


def user_dashboard(username, password):
    """User dashboard after login."""
    print(f"\n--- User Dashboard: {username} ---")
    
    print("\nPlease select an option:")
    print("1. View Profile")
    print("2. Update Profile")
    print("3. Back to Main Menu")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        view_profile(username)
    elif choice == '2':
        update_profile(username, password)
    elif choice == '3':
        return
    else:
        print("\nInvalid choice. Returning to main menu.")


def view_profile(username):
    """View user profile."""
    print("\n--- User Profile ---")
    
    security = MortgageSecurity()
    if username in security.users:
        user = security.users[username]
        print(f"Username: {username}")
        print(f"Email: {user['email']}")
        print(f"SSN: {user['ssn']}")
        print(f"Date of Birth: {user['dob']}")
        print(f"Account Created: {user['created_at']}")
    else:
        print("\nError: User not found.")


def update_profile(username, password):
    """Update user profile."""
    print("\n--- Update Profile ---")
    
    security = MortgageSecurity()
    if not security.authenticate_user(username, password):
        print("\nAuthentication failed.")
        return
    
    new_password = getpass.getpass("New Password (leave blank to keep current): ")
    
    if new_password:
        if security.reset_password(username, new_password):
            print("\nPassword updated successfully.")
        else:
            print("\nFailed to update password.")


def manage_loan_application():
    """Manage loan application functions."""
    print("\n--- Loan Application ---")
    
    print("\nPlease select an option:")
    print("1. Submit New Application")
    print("2. Check Application Status")
    print("3. Back to Main Menu")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        submit_application()
    elif choice == '2':
        check_status()
    elif choice == '3':
        return
    else:
        print("\nInvalid choice. Returning to main menu.")


def submit_application():
    """Submit a new loan application."""
    print("\n--- Submit New Application ---")
    
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    security = MortgageSecurity()
    if not security.authenticate_user(username, password):
        print("\nAuthentication failed.")
        return
    
    print("\nPlease provide loan application details:")
    loan_amount = get_float_input("Loan Amount ($): ")
    property_value = get_float_input("Property Value ($): ")
    income = get_float_input("Annual Income ($): ")
    loan_type = input("Loan Type (Conventional, FHA, VA, USDA, Jumbo): ")
    term_years = get_int_input("Loan Term (years): ")
    
    application_data = {
        "loan_amount": loan_amount,
        "property_value": property_value,
        "income": income,
        "loan_type": loan_type,
        "term_years": term_years
    }
    
    success, result = submit_loan_application(username, password, application_data)
    
    if success:
        print(f"\nApplication submitted successfully!")
        print(f"Application ID: {result}")
        print("\nPlease save this ID to check your application status later.")
    else:
        print(f"\nError: {result}")


def check_status():
    """Check status of an existing application."""
    print("\n--- Check Application Status ---")
    
    application_id = input("Application ID: ")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    result = check_application_status(application_id, username, password)
    
    if "error" in result:
        print(f"\nError: {result['error']}")
    else:
        print("\nApplication Status:")
        print(f"Application ID: {result['application_id']}")
        print(f"Status: {result['status']}")
        print(f"Created: {result['created_at']}")
        print(f"Last Updated: {result['updated_at']}")


def access_admin_functions():
    """Access admin functions."""
    print("\n--- Admin Functions ---")
    
    password = getpass.getpass("Admin Password: ")
    
    print("\nPlease select an option:")
    print("1. View All Users")
    print("2. View All Applications")
    print("3. Process Pending Applications")
    print("4. Execute Custom Query")
    print("5. Back to Main Menu")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == '1':
        view_all_users(password)
    elif choice == '2':
        view_all_applications(password)
    elif choice == '3':
        process_applications(password)
    elif choice == '4':
        execute_query(password)
    elif choice == '5':
        return
    else:
        print("\nInvalid choice. Returning to main menu.")


def view_all_users(password):
    """View all users (admin function)."""
    print("\n--- All Users ---")
    
    result = admin_dashboard(password, "get_all_users")
    
    if "error" in result:
        print(f"\nError: {result['error']}")
    else:
        users = result["users"]
        print(f"\nTotal Users: {len(users)}")
        
        for username, user in users.items():
            print(f"\nUsername: {username}")
            print(f"Email: {user['email']}")
            print(f"SSN: {user['ssn']}")
            print(f"Date of Birth: {user['dob']}")
            print(f"Account Created: {user['created_at']}")
            print("-" * 40)


def view_all_applications(password):
    """View all applications (admin function)."""
    print("\n--- All Applications ---")
    
    result = admin_dashboard(password, "execute_query", {"query": "SELECT * FROM applications", "params": {}})
    
    if "error" in result:
        print(f"\nError: {result['error']}")
    else:
        print("\nQuery executed successfully.")


def process_applications(password):
    """Process pending applications (admin function)."""
    print("\n--- Process Pending Applications ---")
    
    security = MortgageSecurity()
    if password != security.admin_password:
        print("\nError: Unauthorized")
        return
    
    results = process_pending_applications()
    
    print(f"\nProcessed {len(results)} applications:")
    
    for result in results:
        status = "Approved" if result["success"] else "Rejected"
        print(f"Application {result['application_id']}: {status} - {result['message']}")


def execute_query(password):
    """Execute custom query (admin function)."""
    print("\n--- Execute Custom Query ---")
    
    query = input("Enter SQL Query: ")
    params = input("Enter query parameters as JSON (optional, leave blank for none): ")
    
    query_params = {}
    if params:
        try:
            query_params = json.loads(params)
        except json.JSONDecodeError:
            print("\nError: Invalid JSON format for parameters")
            return
    
    result = admin_dashboard(password, "execute_query", {"query": query, "params": query_params})
    
    if "error" in result:
        print(f"\nError: {result['error']}")
    else:
        print("\nQuery executed successfully.")


def main():
    """Main application function."""
    print_header()
    
    while True:
        print_menu()
        
        choice = input("Enter your choice (0-11): ")
        
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
            manage_user_account()
        elif choice == '10':
            manage_loan_application()
        elif choice == '11':
            access_admin_functions()
        elif choice == '0':
            print("\nThank you for using the Mortgage Analysis Tool. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
