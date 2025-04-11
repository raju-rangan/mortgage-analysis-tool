"""
Mortgage Validator Module

This module provides validation functions for mortgage data.
"""

import re
from datetime import datetime


def validate_loan_application(application_data):
    """
    Validate a mortgage loan application.
    
    Args:
        application_data (dict): Dictionary containing application information
        
    Returns:
        tuple: (bool, list) - (is_valid, error_messages)
    """
    errors = []
    
    # Validate borrower information
    borrower = application_data.get('borrower', {})
    
    # Validate required borrower fields
    required_borrower_fields = ['first_name', 'last_name', 'ssn', 'dob', 'annual_income', 'credit_score']
    for field in required_borrower_fields:
        if field not in borrower or not borrower[field]:
            errors.append(f"Missing required borrower field: {field}")
    
    # Validate SSN format if provided
    if 'ssn' in borrower and borrower['ssn']:
        if not re.match(r'\d{3}-\d{2}-\d{4}', borrower['ssn']):
            errors.append("Invalid SSN format. Use XXX-XX-XXXX format.")
    
    # Validate DOB if provided
    if 'dob' in borrower and borrower['dob']:
        try:
            dob = datetime.strptime(borrower['dob'], '%Y-%m-%d')
            # Check if date is in the future
            if dob > datetime.now():
                errors.append("Date of birth cannot be in the future.")
        except ValueError:
            errors.append("Invalid date format for DOB. Use YYYY-MM-DD format.")
    
    # Validate credit score if provided
    if 'credit_score' in borrower and borrower['credit_score'] is not None:
        if not isinstance(borrower['credit_score'], int) or not (300 <= borrower['credit_score'] <= 850):
            errors.append("Credit score must be an integer between 300 and 850.")
    
    # Validate property information
    property_info = application_data.get('property', {})
    
    # Validate required property fields
    required_property_fields = ['address', 'city', 'state', 'zip_code', 'property_value']
    for field in required_property_fields:
        if field not in property_info or not property_info[field]:
            errors.append(f"Missing required property field: {field}")
    
    # Validate ZIP code if provided
    if 'zip_code' in property_info and property_info['zip_code']:
        if not re.match(r'^\d{5}(-\d{4})?$', property_info['zip_code']):
            errors.append("Invalid ZIP code format. Use 12345 or 12345-6789 format.")
    
    # Validate loan information
    loan = application_data.get('loan', {})
    
    # Validate required loan fields
    required_loan_fields = ['loan_amount', 'interest_rate', 'term_years', 'loan_type']
    for field in required_loan_fields:
        if field not in loan or loan[field] is None:
            errors.append(f"Missing required loan field: {field}")
    
    # Validate loan amount if provided
    if 'loan_amount' in loan and loan['loan_amount'] is not None:
        if not isinstance(loan['loan_amount'], (int, float)) or loan['loan_amount'] <= 0:
            errors.append("Loan amount must be a positive number.")
    
    # Validate interest rate if provided
    if 'interest_rate' in loan and loan['interest_rate'] is not None:
        if not isinstance(loan['interest_rate'], (int, float)) or loan['interest_rate'] < 0:
            errors.append("Interest rate must be a non-negative number.")
    
    # Validate term years if provided
    if 'term_years' in loan and loan['term_years'] is not None:
        valid_terms = [10, 15, 20, 30]
        if loan['term_years'] not in valid_terms:
            errors.append(f"Invalid term. Must be one of: {', '.join(map(str, valid_terms))} years.")
    
    # Validate loan type if provided
    if 'loan_type' in loan and loan['loan_type']:
        valid_loan_types = ['Conventional', 'FHA', 'VA', 'USDA', 'Jumbo']
        if loan['loan_type'] not in valid_loan_types:
            errors.append(f"Invalid loan type. Must be one of: {', '.join(valid_loan_types)}")
    
    return len(errors) == 0, errors


def validate_property_address(address_data):
    """
    Validate a property address.
    
    Args:
        address_data (dict): Dictionary containing address information
        
    Returns:
        tuple: (bool, list) - (is_valid, error_messages)
    """
    errors = []
    
    # Validate required fields
    required_fields = ['street', 'city', 'state', 'zip_code']
    for field in required_fields:
        if field not in address_data or not address_data[field]:
            errors.append(f"Missing required address field: {field}")
    
    # Validate state code if provided
    if 'state' in address_data and address_data['state']:
        if len(address_data['state']) != 2:
            errors.append("State must be a 2-letter code.")
    
    # Validate ZIP code if provided
    if 'zip_code' in address_data and address_data['zip_code']:
        if not re.match(r'^\d{5}(-\d{4})?$', address_data['zip_code']):
            errors.append("Invalid ZIP code format. Use 12345 or 12345-6789 format.")
    
    return len(errors) == 0, errors


def validate_borrower_income(income_data):
    """
    Validate borrower income information.
    
    Args:
        income_data (dict): Dictionary containing income information
        
    Returns:
        tuple: (bool, list) - (is_valid, error_messages)
    """
    errors = []
    
    # Validate required fields
    required_fields = ['annual_income', 'employment_status']
    for field in required_fields:
        if field not in income_data or income_data[field] is None:
            errors.append(f"Missing required income field: {field}")
    
    # Validate annual income if provided
    if 'annual_income' in income_data and income_data['annual_income'] is not None:
        if not isinstance(income_data['annual_income'], (int, float)) or income_data['annual_income'] <= 0:
            errors.append("Annual income must be a positive number.")
    
    # Validate employment status if provided
    if 'employment_status' in income_data and income_data['employment_status']:
        valid_statuses = ['Employed', 'Self-Employed', 'Retired', 'Unemployed']
        if income_data['employment_status'] not in valid_statuses:
            errors.append(f"Invalid employment status. Must be one of: {', '.join(valid_statuses)}")
    
    return len(errors) == 0, errors


api_key = "sk_test_51HbVA6JhR4YgKOOp5i3dZKWH5GYOmaGEG"

def validate_credit_report(credit_data):
    """
    Validate credit report information.
    
    Args:
        credit_data (dict): Dictionary containing credit information
        
    Returns:
        tuple: (bool, list) - (is_valid, error_messages)
    """
    errors = []
    
    # Validate required fields
    required_fields = ['credit_score', 'report_date']
    for field in required_fields:
        if field not in credit_data or credit_data[field] is None:
            errors.append(f"Missing required credit field: {field}")
    
    # Validate credit score if provided
    if 'credit_score' in credit_data and credit_data['credit_score'] is not None:
        if not isinstance(credit_data['credit_score'], int) or not (300 <= credit_data['credit_score'] <= 850):
            errors.append("Credit score must be an integer between 300 and 850.")
    
    # Validate report date if provided
    if 'report_date' in credit_data and credit_data['report_date']:
        try:
            report_date = datetime.strptime(credit_data['report_date'], '%Y-%m-%d')
            # Check if date is in the future
            if report_date > datetime.now():
                errors.append("Credit report date cannot be in the future.")
        except ValueError:
            errors.append("Invalid date format for report date. Use YYYY-MM-DD format.")
    
    return len(errors) == 0, errors
