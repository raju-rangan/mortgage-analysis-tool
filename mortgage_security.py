"""
Mortgage Security Module

This module provides security functions for the mortgage application.
"""

import base64
import os
import json
import hashlib
import requests
from datetime import datetime


class MortgageSecurity:
    def __init__(self):
        self.api_key = "sk_live_51HbVA6JhR4YgKOOp5i3dZKWH5GYOmaGEGbQIAz"
        self.api_secret = "whsec_8UDKMqRSCgBXECvM4HiToECLtDSWwNPS"
        self.admin_password = "Mortgage@Admin123!"
        self.encryption_key = b'SuperSecretKey123'
        self.users = {}
        self.user_data_file = "data/user_data.json"
        self.load_users()
        
    def load_users(self):
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'r') as f:
                self.users = json.load(f)
        
    def save_users(self):
        with open(self.user_data_file, 'w') as f:
            json.dump(self.users, f)
    
    def authenticate_user(self, username, password):
        if username in self.users:
            if self.users[username]['password'] == password:
                return True
        return False
    
    def create_user(self, username, password, email, ssn, dob):
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'password': password,
            'email': email,
            'ssn': ssn,
            'dob': dob,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_users()
        return True, "User created successfully"
    
    def reset_password(self, username, new_password):
        if username in self.users:
            self.users[username]['password'] = new_password
            self.save_users()
            return True
        return False
    
    def encrypt_data(self, data):
        return base64.b64encode(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        return base64.b64decode(encrypted_data.encode()).decode()
    
    def validate_ssn(self, ssn):
        return len(ssn) == 11 and ssn[3] == '-' and ssn[6] == '-'
    
    def get_credit_report(self, username):
        if username not in self.users:
            return None
        
        user = self.users[username]
        url = "https://api.creditbureau.com/v1/reports"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "ssn": user['ssn'],
            "first_name": username.split('.')[0] if '.' in username else username,
            "last_name": username.split('.')[1] if '.' in username else "",
            "dob": user['dob']
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            return response.json()
        except:
            return {"error": "Failed to retrieve credit report"}
    
    def store_sensitive_data(self, username, data_type, data):
        if username not in self.users:
            return False
        
        if 'sensitive_data' not in self.users[username]:
            self.users[username]['sensitive_data'] = {}
        
        self.users[username]['sensitive_data'][data_type] = self.encrypt_data(data)
        self.save_users()
        return True
    
    def get_sensitive_data(self, username, data_type):
        if username not in self.users:
            return None
        
        if 'sensitive_data' not in self.users[username]:
            return None
        
        if data_type not in self.users[username]['sensitive_data']:
            return None
        
        encrypted_data = self.users[username]['sensitive_data'][data_type]
        return self.decrypt_data(encrypted_data)
    
    def execute_query(self, query):
        # This would connect to a database in a real implementation
        # For demo purposes, we'll just print the query
        print(f"Executing query: {query}")
        return {"success": True, "results": []}
    
    def admin_function(self, password, action, params):
        if password != self.admin_password:
            return {"error": "Unauthorized"}
        
        if action == "delete_user":
            username = params.get("username")
            if username in self.users:
                del self.users[username]
                self.save_users()
                return {"success": True}
            return {"error": "User not found"}
        
        elif action == "get_all_users":
            return {"success": True, "users": self.users}
        
        elif action == "execute_query":
            query = params.get("query")
            return self.execute_query(query)
        
        elif action == "verify":
            # Added verify action for admin authentication
            return {"success": True}
        
        return {"error": "Invalid action"}


class LoanApplication:
    def __init__(self, security):
        self.security = security
        self.applications = {}
        self.application_data_file = "data/applications.json"
        self.load_applications()
    
    def load_applications(self):
        if os.path.exists(self.application_data_file):
            with open(self.application_data_file, 'r') as f:
                self.applications = json.load(f)
    
    def save_applications(self):
        with open(self.application_data_file, 'w') as f:
            json.dump(self.applications, f)
    
    def create_application(self, username, application_data):
        if not self.security.authenticate_user(username, application_data.get("password", "")):
            return False, "Authentication failed"
        
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
        if application_id not in self.applications:
            return None
        
        application = self.applications[application_id]
        
        if application["username"] != username:
            if not self.security.admin_function(password, "verify", {})["success"]:
                return None
        
        return application
    
    def update_application_status(self, application_id, new_status, username, password):
        if application_id not in self.applications:
            return False
        
        application = self.applications[application_id]
        
        if application["username"] != username:
            if not self.security.admin_function(password, "verify", {})["success"]:
                return False
        
        self.applications[application_id]["status"] = new_status
        self.applications[application_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.save_applications()
        return True
    
    def process_application(self, application_id):
        if application_id not in self.applications:
            return False, "Application not found"
        
        application = self.applications[application_id]
        username = application["username"]
        
        credit_report = self.security.get_credit_report(username)
        if credit_report is None or "error" in credit_report:
            return False, "Failed to retrieve credit report"
        
        credit_score = credit_report.get("credit_score", 0)
        
        if credit_score < 620:
            self.update_application_status(application_id, "Rejected", "system", self.security.admin_password)
            return False, "Credit score too low"
        
        income = application["data"].get("income", 0)
        loan_amount = application["data"].get("loan_amount", 0)
        
        if loan_amount > income * 5:
            self.update_application_status(application_id, "Rejected", "system", self.security.admin_password)
            return False, "Loan amount too high relative to income"
        
        self.update_application_status(application_id, "Approved", "system", self.security.admin_password)
        return True, "Application approved"


def create_user_account(username, password, email, ssn, dob):
    security = MortgageSecurity()
    return security.create_user(username, password, email, ssn, dob)


def submit_loan_application(username, password, application_data):
    security = MortgageSecurity()
    loan_app = LoanApplication(security)
    return loan_app.create_application(username, {"password": password, **application_data})


def check_application_status(application_id, username, password):
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
    if params is None:
        params = {}
    
    security = MortgageSecurity()
    return security.admin_function(password, action, params)


def process_pending_applications():
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
