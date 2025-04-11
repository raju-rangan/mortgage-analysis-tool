# Mortgage Analysis Tool

A simple Python application for analyzing mortgage data and performing common mortgage-related calculations.

## Features

- Calculate monthly mortgage payments
- Generate amortization schedules
- Calculate loan-to-value ratios
- Calculate debt-to-income ratios
- Estimate PMI costs
- Calculate maximum affordable home price
- Fetch current mortgage rates
- Get property valuations

## Project Structure

```
mortgage_analysis_tool/
├── app.py                  # Command-line interface
├── mortgage_calculator.py  # Core calculation functions
├── mortgage_validator.py   # Input validation
├── mortgage_api.py         # Mock API for mortgage data
└── test_mortgage.py        # Unit tests
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mortgage-analysis-tool.git
cd mortgage-analysis-tool

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the command-line interface:

```bash
python app.py
```

Or import the modules in your own code:

```python
from mortgage_calculator import calculate_monthly_payment

# Calculate a monthly mortgage payment
payment = calculate_monthly_payment(
    principal=300000,
    annual_interest_rate=4.5,
    term_years=30
)
print(f"Monthly payment: ${payment:.2f}")
```

## Demo Purpose

This project is designed to demonstrate AI-powered code review capabilities on GitHub. It contains intentional code issues across various categories:
- Security vulnerabilities
- Performance inefficiencies
- Code style inconsistencies
- Error handling gaps
- Documentation issues

These issues are distributed across different files to showcase how AI agents can identify and suggest fixes for various code quality concerns.

## Feature to Add During Demo

During the demo, we'll add a "Refinance Analysis" feature that:
- Takes an existing mortgage and calculates potential savings from refinancing
- Shows monthly payment differences and lifetime interest savings
- Includes a break-even analysis (how long until refinance costs are recovered)

This feature will demonstrate how AI can assist with code implementation and review in real-time.
