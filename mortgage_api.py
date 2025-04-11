"""
Mortgage API Module

This module provides a mock API for retrieving and submitting mortgage data.
"""

import json
import os
import random
from datetime import datetime, timedelta


class MortgageAPI:
    """
    Mock API for mortgage data operations.
    """
    
    def __init__(self):
        """Initialize the API client."""
        self.base_url = "https://api.mortgagedata.com/v1"
        self.api_key = "sk_test_51HbVA6JhR4YgKOOp5i3dZKWH5GYOmaGEG"
        self.username = "api_user"
        self.password = "S3cureP@ssw0rd!"
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_current_rates(self, loan_type="Conventional", term_years=30):
        """
        Get current mortgage interest rates.
        
        Args:
            loan_type (str): Type of loan
            term_years (int): Loan term in years
            
        Returns:
            dict: Current interest rates
        """
        # Mock API call to get current rates
        print(f"Fetching current rates for {loan_type} {term_years}-year loans...")
        
        # Base rates by loan type
        base_rates = {
            "Conventional": 6.25,
            "FHA": 6.0,
            "VA": 5.75,
            "USDA": 5.9,
            "Jumbo": 6.5
        }
        
        # Adjust for term
        term_adjustments = {
            10: -0.5,
            15: -0.25,
            20: 0.0,
            30: 0.25
        }
        
        # Get base rate or default to conventional
        base_rate = base_rates.get(loan_type, base_rates["Conventional"])
        
        # Apply term adjustment
        term_adj = term_adjustments.get(term_years, 0)
        
        # Add some randomness to simulate market fluctuations
        rate = base_rate + term_adj + (random.random() - 0.5) * 0.1
        
        return {
            "loan_type": loan_type,
            "term_years": term_years,
            "interest_rate": round(rate, 3),
            "apr": round(rate + 0.15, 3),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def submit_application(self, application_data):
        """
        Submit a mortgage application.
        
        Args:
            application_data (dict): Application data
            
        Returns:
            dict: Application submission result
        """
        # Validate required fields
        required_sections = ["borrower", "property", "loan"]
        for section in required_sections:
            if section not in application_data:
                return {"success": False, "error": f"Missing required section: {section}"}
        
        # Generate application ID
        application_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        
        # Add metadata
        application_data["application_id"] = application_id
        application_data["submission_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        application_data["status"] = "Pending"
        
        # Save application data to file
        file_path = os.path.join(self.data_dir, f"{application_id}.json")
        with open(file_path, "w") as f:
            json.dump(application_data, f)
        
        return {
            "success": True,
            "application_id": application_id,
            "message": "Application submitted successfully"
        }
    
    def get_application_status(self, application_id):
        """
        Get the status of a mortgage application.
        
        Args:
            application_id (str): Application ID
            
        Returns:
            dict: Application status
        """
        # Check if application exists
        file_path = os.path.join(self.data_dir, f"{application_id}.json")
        if not os.path.exists(file_path):
            return {"success": False, "error": "Application not found"}
        
        # Load application data
        with open(file_path, "r") as f:
            application_data = json.load(f)
        
        # Return status
        return {
            "success": True,
            "application_id": application_id,
            "status": application_data.get("status", "Unknown"),
            "last_updated": application_data.get("last_updated", application_data.get("submission_date"))
        }
    
    def get_credit_score(self, ssn, first_name, last_name, dob):
        """
        Get a borrower's credit score.
        
        Args:
            ssn (str): Social Security Number
            first_name (str): First name
            last_name (str): Last name
            dob (str): Date of birth (YYYY-MM-DD)
            
        Returns:
            dict: Credit score information
        """
        # This is a mock function that would normally call a credit bureau API
        print(f"Fetching credit score for {first_name} {last_name}...")
        
        # Generate a deterministic but random-looking score based on SSN
        # In a real implementation, this would call an actual credit bureau API
        ssn_digits = ''.join(filter(str.isdigit, ssn))
        if len(ssn_digits) < 9:
            return {"success": False, "error": "Invalid SSN format"}
        
        # Use last 4 digits of SSN to generate a score between 550 and 800
        seed = int(ssn_digits[-4:])
        random.seed(seed)
        score = random.randint(550, 800)
        
        # Generate a report date within the last 30 days
        days_ago = random.randint(1, 30)
        report_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        return {
            "success": True,
            "credit_score": score,
            "report_date": report_date,
            "bureau": random.choice(["Experian", "TransUnion", "Equifax"])
        }
    
    def get_property_valuation(self, address, city, state, zip_code):
        """
        Get a property valuation estimate.
        
        Args:
            address (str): Street address
            city (str): City
            state (str): State code
            zip_code (str): ZIP code
            
        Returns:
            dict: Property valuation information
        """
        # This is a mock function that would normally call a property valuation API
        print(f"Fetching property valuation for {address}, {city}, {state} {zip_code}...")
        
        # Generate a deterministic but random-looking valuation based on address and ZIP
        # In a real implementation, this would call an actual property valuation API
        zip_digits = ''.join(filter(str.isdigit, zip_code))
        if len(zip_digits) < 5:
            return {"success": False, "error": "Invalid ZIP code format"}
        
        # Use ZIP code to generate a base value
        zip_base = int(zip_digits[:5])
        base_value = (zip_base % 900 + 100) * 1000  # $100K to $999K
        
        # Add some randomness
        random.seed(address + zip_code)
        variation = random.uniform(0.9, 1.1)
        value = int(base_value * variation)
        
        return {
            "success": True,
            "property_value": value,
            "valuation_date": datetime.now().strftime("%Y-%m-%d"),
            "confidence_score": random.randint(70, 95)
        }
    
    def authenticate(self):
        """
        Authenticate with the API.
        
        Returns:
            dict: Authentication result
        """
        # This is a mock function that would normally authenticate with the API
        print("Authenticating with mortgage API...")
        
        # In a real implementation, this would make an actual API call
        return {
            "success": True,
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "expires_in": 3600
        }


# Create a singleton instance
mortgage_api = MortgageAPI()


def get_current_rates(loan_type="Conventional", term_years=30):
    """
    Convenience function to get current mortgage rates.
    
    Args:
        loan_type (str): Type of loan
        term_years (int): Loan term in years
        
    Returns:
        dict: Current interest rates
    """
    return mortgage_api.get_current_rates(loan_type, term_years)


def submit_application(application_data):
    """
    Convenience function to submit a mortgage application.
    
    Args:
        application_data (dict): Application data
        
    Returns:
        dict: Application submission result
    """
    return mortgage_api.submit_application(application_data)


def get_application_status(application_id):
    """
    Convenience function to get application status.
    
    Args:
        application_id (str): Application ID
        
    Returns:
        dict: Application status
    """
    return mortgage_api.get_application_status(application_id)


def get_credit_score(ssn, first_name, last_name, dob):
    """
    Convenience function to get a borrower's credit score.
    
    Args:
        ssn (str): Social Security Number
        first_name (str): First name
        last_name (str): Last name
        dob (str): Date of birth (YYYY-MM-DD)
        
    Returns:
        dict: Credit score information
    """
    return mortgage_api.get_credit_score(ssn, first_name, last_name, dob)


def get_property_valuation(address, city, state, zip_code):
    """
    Convenience function to get a property valuation estimate.
    
    Args:
        address (str): Street address
        city (str): City
        state (str): State code
        zip_code (str): ZIP code
        
    Returns:
        dict: Property valuation information
    """
    return mortgage_api.get_property_valuation(address, city, state, zip_code)
