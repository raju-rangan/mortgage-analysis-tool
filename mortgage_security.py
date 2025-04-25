"""
Mortgage Security Module

This module provides security functions for the mortgage application.
"""

import base64
import os
import json
import hashlib
import requests
import bcrypt
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import getpass

# Load environment variables
load_dotenv()

class MortgageSecurity:
    def __init__(self):
        # Load credentials from environment variables
        self.api_key = os.getenv('API_KEY', '')
        self.api_secret = os.getenv('API_SECRET', '')
        self.admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH', '')
        
        # If admin password hash is not set, create one from the environment variable
        if not self.admin_password_hash and os.getenv('ADMIN_PASSWORD'):
            self.admin_password_hash = self._hash_password(os.getenv('ADMIN_PASSWORD')).decode('utf-8')
        
        # Set up encryption
        encryption_key = os.getenv('ENCRYPTION_KEY', '')
        if not encryption_key:
            # Generate a key if not provided
            self.encryption_key = Fernet.generate_key()
            print("Warning: No encryption key found in environment. Generated temporary key.")
        else:
            # Use the provided key
            try:
                # Ensure the key is valid for Fernet
                if len(base64.b64decode(encryption_key)) != 32:
                    raise ValueError("Invalid key length")
                self.encryption_key = encryption_key.encode()
            except:
                # Generate a key if the provided one is invalid
                self.encryption_key = Fernet.generate_key()
                print("Warning: Invalid encryption key in environment. Generated temporary key.")
        
        self.cipher = Fernet(self.encryption_key)
        self.users = {}
        self.user_data_file = "data/user_data.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.user_data_file), exist_ok=True)
        
        self.load_users()
        
    def load_users(self):
        """Load user data from file."""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r') as f:
                    self.users = json.load(f)
        except Exception as e:
            print(f"Error loading user data: {e}")
            self.users = {}
        
    def save_users(self):
        """Save user data to file."""
        try:
            with open(self.user_data_file, 'w') as f:
                json.dump(self.users, f)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def _hash_password(self, password):
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def _verify_password(self, password, hashed):
        """Verify a password against a hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8') if isinstance(hashed, str) else hashed)
        except Exception:
            return False
    
    def authenticate_user(self, username, password):
        """Authenticate a user with username and password."""
        if username in self.users:
            if 'password_hash' in self.users[username]:
                # Use the new hashed password
                return self._verify_password(password, self.users[username]['password_hash'])
            elif 'password' in self.users[username]:
                # Legacy support for plaintext passwords - upgrade to hash
                if self.users[username]['password'] == password:
                    # Upgrade to hashed password
                    self.users[username]['password_hash'] = self._hash_password(password).decode('utf-8')
                    del self.users[username]['password']
                    self.save_users()
                    return True
        return False
    
    def create_user(self, username, password, email, ssn, dob):
        """Create a new user account."""
        if username in self.users:
            return False, "Username already exists"
        
        # Validate inputs
        if not self._validate_password(password):
            return False, "Password does not meet security requirements"
        
        if not self._validate_email(email):
            return False, "Invalid email format"
        
        if not self.validate_ssn(ssn):
            return False, "Invalid SSN format (must be XXX-XX-XXXX)"
        
        # Hash the password
        password_hash = self._hash_password(password).decode('utf-8')
        
        # Encrypt sensitive data
        encrypted_ssn = self.encrypt_data(ssn)
        
        self.users[username] = {
            'password_hash': password_hash,
            'email': email,
            'ssn': encrypted_ssn,
            'dob': dob,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_users()
        return True, "User created successfully"
    
    def reset_password(self, username, new_password):
        """Reset a user's password."""
        if username in self.users:
            if not self._validate_password(new_password):
                return False
            
            # Hash the new password
            password_hash = self._hash_password(new_password).decode('utf-8')
            self.users[username]['password_hash'] = password_hash
            
            # Remove plaintext password if it exists
            if 'password' in self.users[username]:
                del self.users[username]['password']
                
            self.save_users()
            return True
        return False
    
    def _validate_password(self, password):
        """Validate password strength."""
        # At least 8 characters, with at least one uppercase, one lowercase, one digit, and one special character
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def _validate_email(self, email):
        """Validate email format."""
        # Basic email validation
        return '@' in email and '.' in email.split('@')[1]
    
    def encrypt_data(self, data):
        """Encrypt data using Fernet symmetric encryption."""
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return ""
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data using Fernet symmetric encryption."""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def validate_ssn(self, ssn):
        """Validate SSN format."""
        return len(ssn) == 11 and ssn[3] == '-' and ssn[6] == '-' and all(c.isdigit() for c in ssn.replace('-', ''))
    
    def get_credit_report(self, username):
        """Get a user's credit report."""
        if username not in self.users:
            return None
        
        user = self.users[username]
        
        # Check if API key is available
        if not self.api_key:
            return {"error": "API key not configured"}
        
        url = "https://api.creditbureau.com/v1/reports"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Decrypt SSN
        try:
            ssn = self.decrypt_data(user['ssn'])
        except:
            # Handle legacy unencrypted SSNs
            ssn = user['ssn']
        
        data = {
            "ssn": ssn,
            "first_name": username.split('.')[0] if '.' in username else username,
            "last_name": username.split('.')[1] if '.' in username else "",
            "dob": user['dob']
        }
        
        try:
            # In a real implementation, we would make the API call
            # For demo purposes, we'll return mock data
            # response = requests.post(url, headers=headers, json=data)
            # return response.json()
            
            # Mock response
            return {
                "credit_score": 720,
                "report_date": datetime.now().strftime("%Y-%m-%d"),
                "inquiries": 2,
                "accounts": 5,
                "derogatory_marks": 0
            }
        except Exception as e:
            return {"error": f"Failed to retrieve credit report: {str(e)}"}
    
    def store_sensitive_data(self, username, data_type, data):
        """Store encrypted sensitive data for a user."""
        if username not in self.users:
            return False
        
        if 'sensitive_data' not in self.users[username]:
            self.users[username]['sensitive_data'] = {}
        
        self.users[username]['sensitive_data'][data_type] = self.encrypt_data(data)
        self.save_users()
        return True
    
    def get_sensitive_data(self, username, data_type):
        """Retrieve and decrypt sensitive data for a user."""
        if username not in self.users:
            return None
        
        if 'sensitive_data' not in self.users[username]:
            return None
        
        if data_type not in self.users[username]['sensitive_data']:
            return None
        
        encrypted_data = self.users[username]['sensitive_data'][data_type]
        return self.decrypt_data(encrypted_data)
    
    def execute_query(self, query, params=None):
        """Execute a parameterized query."""
        # This would connect to a database in a real implementation
        # For demo purposes, we'll just print the query
        
        # SECURITY: Use parameterized queries instead of string concatenation
        if params:
            print(f"Executing query: {query} with parameters: {params}")
        else:
            print(f"Executing query: {query}")
            
        return {"success": True, "results": []}
    
    def admin_function(self, password, action, params):
        """Execute admin functions with proper authentication."""
        # Check if admin password is configured
        if not self.admin_password_hash:
            return {"error": "Admin password not configured"}
        
        # Verify admin password
        if not self._verify_password(password, self.admin_password_hash):
            return {"error": "Unauthorized"}
        
        if action == "delete_user":
            username = params.get("username")
            if username in self.users:
                del self.users[username]
                self.save_users()
                return {"success": True}
            return {"error": "User not found"}
        
        elif action == "get_all_users":
            # Return user data with sensitive information masked
            masked_users = {}
            for username, user_data in self.users.items():
                masked_user = user_data.copy()
                # Mask SSN
                if 'ssn' in masked_user:
                    try:
                        # Try to decrypt if it's encrypted
                        ssn = self.decrypt_data(masked_user['ssn'])
                        masked_user['ssn'] = f"XXX-XX-{ssn.split('-')[2]}" if '-' in ssn else "XXX-XX-XXXX"
                    except:
                        masked_user['ssn'] = "XXX-XX-XXXX"
                
                # Remove password hash
                if 'password_hash' in masked_user:
                    del masked_user['password_hash']
                if 'password' in masked_user:
                    del masked_user['password']
                
                masked_users[username] = masked_user
            
            return {"success": True, "users": masked_users}
        
        elif action == "execute_query":
            query = params.get("query")
            query_params = params.get("params", {})
            return self.execute_query(query, query_params)
        
        elif action == "verify":
            # Added verify action for admin authentication
            return {"success": True}
        
        return {"error": "Invalid action"}


class LoanApplication:
    def __init__(self, security):
        self.security = security
        self.applications = {}
        self.application_data_file = "data/applications.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.application_data_file), exist_ok=True)
        
        self.load_applications()
    
    def load_applications(self):
        """Load application data from file."""
        try:
            if os.path.exists(self.application_data_file):
                with open(self.application_data_file, 'r') as f:
                    self.applications = json.load(f)
        except Exception as e:
            print(f"Error loading application data: {e}")
            self.applications = {}
    
    def save_applications(self):
        """Save application data to file."""
        try:
            with open(self.application_data_file, 'w') as f:
                json.dump(self.applications, f)
        except Exception as e:
            print(f"Error saving application data: {e}")
    
    def create_application(self, username, application_data):
        """Create a new loan application."""
        if not self.security.authenticate_user(username, application_data.get("password", "")):
            return False, "Authentication failed"
        
        # Remove password from application data
        if "password" in application_data:
            del application_data["password"]
        
        application_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{len(self.applications) + 1}"
        
        self.applications[application_id] = {
            "username": username,
            "data": application_data,
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_applications()
        return True, application_id
    
    def get_application(self, application_id, username, password):
        """Get application details with proper authentication."""
        if application_id not in self.applications:
            return None
        
        application = self.applications[application_id]
        
        # Only allow access to the application owner or an admin
        if application["username"] != username:
            # Verify admin credentials
            admin_result = self.security.admin_function(password, "verify", {})
            if "error" in admin_result:
                return None
        else:
            # Verify user credentials
            if not self.security.authenticate_user(username, password):
                return None
        
        return application
    
    def update_application_status(self, application_id, new_status, username, password):
        """Update application status with proper authentication."""
        if application_id not in self.applications:
            return False
        
        application = self.applications[application_id]
        
        # Only allow the application owner or an admin to update status
        if application["username"] != username:
            # Verify admin credentials
            admin_result = self.security.admin_function(password, "verify", {})
            if "error" in admin_result:
                return False
        else:
            # Verify user credentials
            if not self.security.authenticate_user(username, password):
                return False
        
        self.applications[application_id]["status"] = new_status
        self.applications[application_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.save_applications()
        return True
    
    def process_application(self, application_id):
        """Process a loan application."""
        if application_id not in self.applications:
            return False, "Application not found"
        
        application = self.applications[application_id]
        username = application["username"]
        
        credit_report = self.security.get_credit_report(username)
        if credit_report is None or "error" in credit_report:
            return False, "Failed to retrieve credit report"
        
        credit_score = credit_report.get("credit_score", 0)
        
        if credit_score < 620:
            self.update_application_status(application_id, "Rejected", "system", os.getenv('ADMIN_PASSWORD', ''))
            return False, "Credit score too low"
        
        income = application["data"].get("income", 0)
        loan_amount = application["data"].get("loan_amount", 0)
        
        if loan_amount > income * 5:
            self.update_application_status(application_id, "Rejected", "system", os.getenv('ADMIN_PASSWORD', ''))
            return False, "Loan amount too high relative to income"
        
        self.update_application_status(application_id, "Approved", "system", os.getenv('ADMIN_PASSWORD', ''))
        return True, "Application approved"


def create_user_account(username, password, email, ssn, dob):
    """Create a new user account."""
    security = MortgageSecurity()
    return security.create_user(username, password, email, ssn, dob)


def submit_loan_application(username, password, application_data):
    """Submit a new loan application."""
    security = MortgageSecurity()
    loan_app = LoanApplication(security)
    return loan_app.create_application(username, {"password": password, **application_data})


def check_application_status(application_id, username, password):
    """Check the status of a loan application."""
    security = MortgageSecurity()
    loan_app = LoanApplication(security)
    application = loan_app.get_application(application_id, username, password)
    
    if application is None:
        return {"error": "Application not found or access denied"}
    
    return {
        "application_id": application_id,
        "status": application["status"],
        "created_at": application["created_at"],
        "updated_at": application.get("updated_at", application["created_at"])
    }


def admin_dashboard(password, action, params=None):
    """Access admin dashboard functions."""
    if params is None:
        params = {}
    
    security = MortgageSecurity()
    return security.admin_function(password, action, params)


def process_pending_applications():
    """Process all pending loan applications."""
    security = MortgageSecurity()
    loan_app = LoanApplication(security)
    
    results = []
    for application_id, application in loan_app.applications.items():
        if application["status"] == "Pending":
            success, message = loan_app.process_application(application_id)
            results.append({
                "application_id": application_id,
                "success": success,
                "message": message
            })
    
    return results
