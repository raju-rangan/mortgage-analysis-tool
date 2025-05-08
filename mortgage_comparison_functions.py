def mortgage_comparison_tool():
    """Mortgage comparison tool interface."""
    scenarios = []
    
    while True:
        print("\n--- Mortgage Comparison Tool ---")
        print("\nCurrent scenarios:")
        
        if not scenarios:
            print("No scenarios added yet.")
        else:
            for i, scenario in enumerate(scenarios, 1):
                print(f"{i}. {scenario.name} - ${scenario.loan_amount:,.2f} at {scenario.interest_rate:.2f}% for {scenario.term_years} years")
        
        print("\nOptions:")
        print("1. Add a new scenario")
        print("2. Load a saved scenario")
        print("3. Compare scenarios")
        print("4. Generate payment chart")
        print("5. Export comparison to CSV")
        print("6. Export comparison to PDF")
        print("7. Return to main menu")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            scenario = create_new_scenario()
            if scenario:
                scenarios.append(scenario)
                print(f"\nScenario '{scenario.name}' added successfully.")
        
        elif choice == '2':
            scenario = load_saved_scenario()
            if scenario:
                scenarios.append(scenario)
                print(f"\nScenario '{scenario.name}' loaded successfully.")
        
        elif choice == '3':
            if len(scenarios) < 2:
                print("\nYou need at least 2 scenarios to compare. Please add more scenarios.")
            else:
                compare_mortgage_scenarios(scenarios)
        
        elif choice == '4':
            if not scenarios:
                print("\nNo scenarios to visualize. Please add at least one scenario.")
            else:
                visualize_scenarios(scenarios)
        
        elif choice == '5':
            if len(scenarios) < 2:
                print("\nYou need at least 2 scenarios to export. Please add more scenarios.")
            else:
                export_comparison_to_csv(scenarios)
        
        elif choice == '6':
            if len(scenarios) < 2:
                print("\nYou need at least 2 scenarios to export. Please add more scenarios.")
            else:
                export_comparison_to_pdf(scenarios)
        
        elif choice == '7':
            break
        
        else:
            print("\nInvalid choice. Please try again.")


def create_new_scenario():
    """Create a new mortgage scenario."""
    print("\n--- Create New Mortgage Scenario ---")
    
    try:
        name = input("Scenario name: ")
        if not name:
            print("Scenario name cannot be empty.")
            return None
        
        loan_amount = get_float_input("Loan amount ($): ")
        interest_rate = get_float_input("Annual interest rate (%): ")
        term_years = get_int_input("Loan term (years): ")
        down_payment = get_float_input("Down payment ($): ")
        
        property_value = get_float_input("Property value ($, or 0 to use loan + down payment): ")
        if property_value == 0:
            property_value = None
        
        # Ask about points
        has_points = input("Are you paying points to reduce the interest rate? (y/n): ").lower() == 'y'
        points_paid = 0
        reduced_rate = None
        
        if has_points:
            points_paid = get_float_input("Points paid (%): ")
            reduced_rate = get_float_input("Reduced interest rate (%): ")
        
        # Create the scenario
        scenario = MortgageScenario(
            name=name,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            term_years=term_years,
            down_payment=down_payment,
            property_value=property_value,
            points_paid=points_paid,
            reduced_rate=reduced_rate
        )
        
        # Ask if user wants to save the scenario
        if input("\nDo you want to save this scenario? (y/n): ").lower() == 'y':
            file_path = scenario.save_to_file()
            print(f"Scenario saved to {file_path}")
        
        return scenario
    
    except Exception as e:
        print(f"\nError creating scenario: {e}")
        return None


def load_saved_scenario():
    """Load a saved mortgage scenario."""
    print("\n--- Load Saved Mortgage Scenario ---")
    
    # Get list of saved scenarios
    scenarios = MortgageScenario.list_saved_scenarios()
    
    if not scenarios:
        print("No saved scenarios found.")
        return None
    
    print("\nAvailable scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']} (created: {scenario['date']})")
    
    try:
        choice = get_int_input("\nEnter scenario number to load (0 to cancel): ", min_value=0)
        
        if choice == 0:
            return None
        
        if 1 <= choice <= len(scenarios):
            file_path = scenarios[choice - 1]['path']
            return MortgageScenario.load_from_file(file_path)
        else:
            print("Invalid choice.")
            return None
    
    except Exception as e:
        print(f"\nError loading scenario: {e}")
        return None


def compare_mortgage_scenarios(scenarios):
    """Compare multiple mortgage scenarios."""
    print("\n--- Compare Mortgage Scenarios ---")
    
    # Generate comparison data
    comparison_data = compare_scenarios(scenarios)
    
    # Generate and display comparison table
    table = generate_comparison_table(comparison_data)
    
    # Print the table
    print("\nComparison Results:")
    for row in table:
        print("  ".join(str(cell).ljust(20) for cell in row))


def visualize_scenarios(scenarios):
    """Visualize payment breakdown for scenarios."""
    print("\n--- Visualize Payment Breakdown ---")
    
    print("Generating chart...")
    
    # Generate chart (this will display the chart)
    generate_payment_chart(scenarios)
    
    print("\nChart displayed. Close the chart window to continue.")


def export_comparison_to_csv(scenarios):
    """Export comparison data to CSV."""
    print("\n--- Export Comparison to CSV ---")
    
    # Generate comparison data
    comparison_data = compare_scenarios(scenarios)
    
    # Ask for filename
    default_filename = f"mortgage_comparison_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    filename = input(f"Enter filename (default: {default_filename}): ")
    
    if not filename:
        filename = default_filename
    
    # Ensure the filename has .csv extension
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    try:
        # Export to CSV
        file_path = export_to_csv(comparison_data, filename)
        print(f"\nComparison exported to {file_path}")
    
    except Exception as e:
        print(f"\nError exporting to CSV: {e}")


def export_comparison_to_pdf(scenarios):
    """Export comparison data to PDF."""
    print("\n--- Export Comparison to PDF ---")
    
    # Generate comparison data
    comparison_data = compare_scenarios(scenarios)
    
    # Ask for filename
    default_filename = f"mortgage_comparison_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filename = input(f"Enter filename (default: {default_filename}): ")
    
    if not filename:
        filename = default_filename
    
    # Ensure the filename has .pdf extension
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    try:
        # Export to PDF
        file_path = export_to_pdf(comparison_data, scenarios, filename)
        print(f"\nComparison exported to {file_path}")
    
    except Exception as e:
        print(f"\nError exporting to PDF: {e}")


# Import these functions at the top of the file
from datetime import datetime
from mortgage_scenario import MortgageScenario
from mortgage_comparison import (
    compare_scenarios,
    generate_comparison_table,
    generate_payment_chart,
    export_to_csv,
    export_to_pdf
)

# These functions are imported from app.py
# get_float_input
# get_int_input