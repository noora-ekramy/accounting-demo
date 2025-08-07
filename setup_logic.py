"""
Setup Logic for Accounting Demo
This module contains functions to handle the setup process for the accounting system.
"""

import json
import pandas as pd
import os
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def get_gemini_model():
    """
    Initialize and return Gemini model.
    
    Returns:
        GenerativeModel: Configured Gemini model
    """
    # Try different environment variable names and Streamlit secrets
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
        except:
            pass
    
    if not api_key:
        raise ValueError("Google/Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in environment variables.")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def load_onboarding_data() -> Optional[Dict]:
    """
    Load onboarding data from JSON file.
    
    Returns:
        Dict: Onboarding data if file exists, None otherwise
    """
    try:
        with open("onboarding_responses.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def generate_chart_of_accounts_with_ai(onboarding_data: Dict) -> List[Dict]:
    """
    Generate chart of accounts using Gemini AI based on onboarding data.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        
    Returns:
        List[Dict]: Generated chart of accounts
    """
    try:
        model = get_gemini_model()
        
        # Convert onboarding data to JSON string
        onboarding_json = json.dumps(onboarding_data, indent=2)
        
        # Log the data being used for chart generation
        print("="*50)
        print("CHART OF ACCOUNTS GENERATION")
        print("="*50)
        print("Using comprehensive financial data:")
        print(onboarding_json)
        print("="*50)
        
        prompt = f"""
        You are an expert accountant. Based on the comprehensive business financial information provided in JSON format, create a detailed chart of accounts with actual starting balances.

        COMPLETE BUSINESS FINANCIAL DATA (JSON):
        {onboarding_json}

        INSTRUCTIONS:
        Analyze ALL the provided financial data including:
        - General company information (name, reporting date)
        - Business questions (business type, revenue sources, expenses)
        - Assets with amounts (cash, accounts receivable, inventory, etc.)
        - Liabilities with amounts (accounts payable, loans, accrued expenses, etc.)
        - Equity with amounts (stock, retained earnings, etc.)

        Create a comprehensive chart of accounts that includes:
        1. ALL Asset accounts mentioned in the data with their actual amounts
        2. ALL Liability accounts mentioned in the data with their actual amounts
        3. ALL Equity accounts mentioned in the data with their actual amounts
        4. Income accounts based on the revenue sources described
        5. Expense accounts based on the business expenses described

        BALANCE INSTRUCTIONS:
        - Use the ACTUAL amounts provided in the financial data for current_balance
        - If an amount is provided (like "Cash: $25,000"), set current_balance to 25000.0
        - If no amount is provided, set current_balance to 0.0
        - Convert all dollar amounts to numbers (remove $ and commas)
        - For expense and income accounts, start with 0.0 balance

        DESCRIPTION REQUIREMENTS:
        For each account description, include:
        - What transactions go into this account
        - When this account is used and why
        - How it affects financial statements
        - Specific examples relevant to this business
        - The starting balance and what it represents
        - Accounting rules and considerations
        - How this account helps track business performance

        REQUIRED FORMAT:
        Return ONLY a valid JSON array with this exact structure:

        [
          {{
            "name": "Account Name",
            "account_type": "Asset|Liability|Equity|Income|Expense",
            "account_sub_type": "Specific category",
            "description": "COMPREHENSIVE description including what this account tracks, when it's used, the starting balance meaning, specific business examples, accounting impact, and performance tracking benefits",
            "current_balance": actual_amount_from_data_or_0.0
          }}
        ]

        CRITICAL REQUIREMENTS:
        - Use ACTUAL financial amounts from the provided data
        - Include ALL accounts that have values in the financial data
        - Make accounts highly specific to this business type and situation
        - Reference the actual business name and specific revenue/expense sources
        - Write detailed descriptions that incorporate the real financial data
        - Ensure all dollar amounts are converted to decimal numbers

        Generate the comprehensive chart of accounts with actual balances now:
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            accounts = json.loads(response_text)
            
            # Validate the structure
            for account in accounts:
                if not all(key in account for key in ['name', 'account_type', 'account_sub_type', 'description', 'current_balance']):
                    raise ValueError("Invalid account structure")
            
            return accounts
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            # Return default accounts if AI parsing fails
            return create_sample_accounts()
            
    except Exception as e:
        print(f"Error generating accounts with AI: {e}")
        # Return default accounts if AI fails
        return create_sample_accounts()


def setup_chart_of_accounts(onboarding_data: Dict) -> bool:
    """
    Set up the chart of accounts based on onboarding data.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        accounts = generate_chart_of_accounts_with_ai(onboarding_data)
        return save_to_csv(accounts, "accounts.csv")
    except Exception as e:
        print(f"Error setting up chart of accounts: {e}")
        return False


def generate_customers_with_ai(onboarding_data: Dict, chart_of_accounts: List[Dict]) -> List[Dict]:
    """
    Generate customers using Gemini AI based on onboarding data and chart of accounts.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        chart_of_accounts: List of account dictionaries for context
        
    Returns:
        List[Dict]: Generated customer data
    """
    try:
        model = get_gemini_model()
        
        # Convert data to JSON strings
        onboarding_json = json.dumps(onboarding_data, indent=2)
        accounts_json = json.dumps(chart_of_accounts, indent=2)
        
        prompt = f"""
        You are an expert business consultant. Based on the business information and chart of accounts, create realistic customer data.

        BUSINESS INFORMATION (JSON):
        {onboarding_json}

        CHART OF ACCOUNTS (JSON):
        {accounts_json}

        INSTRUCTIONS:
        Create realistic customers that match this business type and revenue sources. Include:
        1. 5-8 diverse customers that would realistically buy from this business
        2. Mix of individual and business customers as appropriate
        3. Realistic contact information and addresses
        4. Varied account balances reflecting different customer relationships
        5. Detailed notes explaining the customer relationship

        CUSTOMER REQUIREMENTS:
        For each customer, write detailed descriptions in notes that include:
        - How they found your business
        - What products/services they typically buy
        - Their payment patterns and preferences
        - Any special requirements or considerations
        - History of relationship with your business
        - Potential for future growth

        REQUIRED FORMAT:
        Return ONLY a valid JSON array with this exact structure:

        [
          {{
            "customer_id": "CUST001",
            "name": "Full Customer Name",
            "company_name": "Company Name or empty string if individual",
            "email": "realistic.email@domain.com",
            "phone": "(555) 123-4567",
            "billing_address": "Street Address",
            "city": "City Name",
            "country": "Country",
            "balance": 0.0,
            "notes": "DETAILED description of this customer including how they found the business, what they buy, payment patterns, special requirements, relationship history, and growth potential"
          }}
        ]

        REQUIREMENTS:
        - Make customers specific to the business type described
        - Use realistic names, emails, and addresses
        - Write extremely detailed, comprehensive notes (minimum 3-4 sentences per customer)
        - Include practical examples relevant to the specific business
        - All balances should start at 0.0
        - Return valid JSON only, no additional text

        Generate realistic customers now with very detailed notes:
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            customers = json.loads(response_text)
            
            # Validate the structure
            for customer in customers:
                if not all(key in customer for key in ['customer_id', 'name', 'company_name', 'email', 'phone', 'billing_address', 'city', 'country', 'balance', 'notes']):
                    raise ValueError("Invalid customer structure")
            
            return customers
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            # Return default customers if AI parsing fails
            return create_sample_customers()
            
    except Exception as e:
        print(f"Error generating customers with AI: {e}")
        # Return default customers if AI fails
        return create_sample_customers()


def generate_services_with_ai(onboarding_data: Dict, chart_of_accounts: List[Dict]) -> List[Dict]:
    """
    Generate services using Gemini AI based on onboarding data and chart of accounts.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        chart_of_accounts: List of account dictionaries for context
        
    Returns:
        List[Dict]: Generated service data
    """
    try:
        model = get_gemini_model()
        
        # Convert data to JSON strings
        onboarding_json = json.dumps(onboarding_data, indent=2)
        accounts_json = json.dumps(chart_of_accounts, indent=2)
        
        prompt = f"""
        You are an expert business consultant. Based on the business information and chart of accounts, create realistic services/products offered.

        BUSINESS INFORMATION (JSON):
        {onboarding_json}

        CHART OF ACCOUNTS (JSON):
        {accounts_json}

        INSTRUCTIONS:
        Create realistic services/products that match this business type and revenue sources. Include:
        1. 4-6 main services/products this business would offer
        2. Appropriate pricing for the business type and market
        3. Mix of different service types as relevant
        4. Proper income account linkage from the chart of accounts
        5. Detailed descriptions explaining the service value

        SERVICE REQUIREMENTS:
        For each service, write detailed descriptions that include:
        - What exactly is included in this service/product
        - Who the target customer is for this offering
        - How this service is delivered or provided
        - What makes this service valuable to customers
        - Any special features or benefits
        - How this fits into the overall business model

        REQUIRED FORMAT:
        Return ONLY a valid JSON array with this exact structure:

        [
          {{
            "name": "Service/Product Name",
            "description": "DETAILED description of what this service includes, who it's for, how it's delivered, its value proposition, special features, and how it fits the business model",
            "type": "Service or Product",
            "unit_price": 99.99,
            "taxable": "yes or no",
            "income_account_name": "Exact name from chart of accounts that matches income"
          }}
        ]

        REQUIREMENTS:
        - Make services specific to the business type described
        - Use realistic pricing for the industry and market
        - Write extremely detailed, comprehensive descriptions (minimum 3-4 sentences per service)
        - Link to actual income account names from the provided chart of accounts
        - Include practical examples relevant to the specific business
        - Return valid JSON only, no additional text

        Generate realistic services now with very detailed descriptions:
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            services = json.loads(response_text)
            
            # Validate the structure
            for service in services:
                if not all(key in service for key in ['name', 'description', 'type', 'unit_price', 'taxable', 'income_account_name']):
                    raise ValueError("Invalid service structure")
            
            return services
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            # Return default services if AI parsing fails
            return create_sample_services()
            
    except Exception as e:
        print(f"Error generating services with AI: {e}")
        # Return default services if AI fails
        return create_sample_services()


def setup_sales_customers_services(onboarding_data: Dict) -> bool:
    """
    Set up sales, customers, and services based on onboarding data.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load existing chart of accounts for context
        accounts_file = os.path.join("anonymized_data", "accounts.csv")
        chart_of_accounts = []
        
        if os.path.exists(accounts_file):
            accounts_df = pd.read_csv(accounts_file)
            chart_of_accounts = accounts_df.to_dict('records')
        
        # Generate customers and services
        customers = generate_customers_with_ai(onboarding_data, chart_of_accounts)
        services = generate_services_with_ai(onboarding_data, chart_of_accounts)
        
        # Save both
        customers_saved = save_to_csv(customers, "customers.csv")
        services_saved = save_to_csv(services, "services.csv")
        
        return customers_saved and services_saved
    except Exception as e:
        print(f"Error setting up sales customers and services: {e}")
        return False


def setup_vendors_expenses(onboarding_data: Dict) -> bool:
    """
    Set up vendors and expenses based on onboarding data.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load existing chart of accounts for context
        accounts_file = os.path.join("anonymized_data", "accounts.csv")
        chart_of_accounts = []
        
        if os.path.exists(accounts_file):
            accounts_df = pd.read_csv(accounts_file)
            chart_of_accounts = accounts_df.to_dict('records')
        
        # Generate vendors and expenses
        vendors = generate_vendors_with_ai(onboarding_data, chart_of_accounts)
        expenses = generate_expenses_with_ai(onboarding_data, chart_of_accounts)
        
        # Save both
        vendors_saved = save_to_csv(vendors, "vendors.csv")
        expenses_saved = save_to_csv(expenses, "expenses.csv")
        
        return vendors_saved and expenses_saved
    except Exception as e:
        print(f"Error setting up vendors and expenses: {e}")
        return False


def generate_vendors_with_ai(onboarding_data: Dict, chart_of_accounts: List[Dict]) -> List[Dict]:
    """
    Generate vendors using Gemini AI based on onboarding data and chart of accounts.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        chart_of_accounts: List of account dictionaries for context
        
    Returns:
        List[Dict]: Generated vendor data
    """
    try:
        model = get_gemini_model()
        
        # Convert data to JSON strings
        onboarding_json = json.dumps(onboarding_data, indent=2)
        accounts_json = json.dumps(chart_of_accounts, indent=2)
        
        prompt = f"""
        You are an expert business consultant. Based on the business information and chart of accounts, create realistic vendor data.

        BUSINESS INFORMATION (JSON):
        {onboarding_json}

        CHART OF ACCOUNTS (JSON):
        {accounts_json}

        INSTRUCTIONS:
        Create realistic vendors that match this business type and expense patterns. Include:
        1. 5-8 diverse vendors that would realistically supply this business
        2. Mix of suppliers, service providers, and utility companies as appropriate
        3. Realistic contact information and addresses
        4. Varied account balances reflecting different vendor relationships
        5. Detailed notes explaining the vendor relationship

        VENDOR REQUIREMENTS:
        For each vendor, write detailed descriptions in notes that include:
        - What products/services they provide to your business
        - How often you work with them (frequency of orders/services)
        - Their payment terms and preferences
        - Quality of their products/services and reliability
        - History of relationship with your business
        - Any special agreements or considerations

        REQUIRED FORMAT:
        Return ONLY a valid JSON array with this exact structure:

        [
          {{
            "vendor_id": "VEND001",
            "name": "Vendor Company Name",
            "company_name": "Full Company Name",
            "email": "realistic.email@vendorcompany.com",
            "phone": "(555) 123-4567",
            "address": "Street Address",
            "city": "City Name",
            "country": "Country",
            "balance": 0.0,
            "currency": "USD",
            "notes": "DETAILED description of this vendor including what they provide, frequency of work, payment terms, quality and reliability, relationship history, and special agreements"
          }}
        ]

        REQUIREMENTS:
        - Make vendors specific to the business type and expenses described
        - Use realistic company names and contact information
        - Write extremely detailed, comprehensive notes (minimum 3-4 sentences per vendor)
        - Include practical examples relevant to the specific business
        - All balances should start at 0.0
        - Return valid JSON only, no additional text

        Generate realistic vendors now with very detailed notes:
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            vendors = json.loads(response_text)
            
            # Validate the structure
            for vendor in vendors:
                if not all(key in vendor for key in ['vendor_id', 'name', 'company_name', 'email', 'phone', 'address', 'city', 'country', 'balance', 'currency', 'notes']):
                    raise ValueError("Invalid vendor structure")
            
            return vendors
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            # Return default vendors if AI parsing fails
            return create_sample_vendors()
            
    except Exception as e:
        print(f"Error generating vendors with AI: {e}")
        # Return default vendors if AI fails
        return create_sample_vendors()


def generate_expenses_with_ai(onboarding_data: Dict, chart_of_accounts: List[Dict]) -> List[Dict]:
    """
    Generate expense categories using Gemini AI based on onboarding data and chart of accounts.
    
    Args:
        onboarding_data: Dictionary containing user's onboarding responses
        chart_of_accounts: List of account dictionaries for context
        
    Returns:
        List[Dict]: Generated expense data
    """
    try:
        model = get_gemini_model()
        
        # Convert data to JSON strings
        onboarding_json = json.dumps(onboarding_data, indent=2)
        accounts_json = json.dumps(chart_of_accounts, indent=2)
        
        prompt = f"""
        You are an expert business consultant. Based on the business information and chart of accounts, create realistic expense categories/templates.

        BUSINESS INFORMATION (JSON):
        {onboarding_json}

        CHART OF ACCOUNTS (JSON):
        {accounts_json}

        INSTRUCTIONS:
        Create realistic expense categories that match this business type and spending patterns. Include:
        1. 6-10 common expense types this business would incur
        2. Appropriate expense accounts from the chart of accounts
        3. Realistic amounts for typical transactions
        4. Mix of different payment methods as relevant
        5. Detailed notes explaining when and why these expenses occur

        EXPENSE REQUIREMENTS:
        For each expense category, write detailed descriptions in notes that include:
        - What this expense covers and why it's necessary for the business
        - How frequently this expense typically occurs
        - Factors that might cause this expense to vary
        - Best practices for managing this type of expense
        - How this expense impacts business operations
        - Any tax considerations or accounting rules

        REQUIRED FORMAT:
        Return ONLY a valid JSON array with this exact structure:

        [
          {{
            "expense_id": "EXP001",
            "date": "2024-01-15",
            "payment_type": "credit or cash or bank or check",
            "vendor_or_entity": "Vendor/Entity Name",
            "total_amount": 99.99,
            "account_used": "Exact expense account name from chart of accounts",
            "project": "General or specific project name",
            "notes": "DETAILED description of this expense category including what it covers, frequency, variation factors, management best practices, operational impact, and tax considerations"
          }}
        ]

        REQUIREMENTS:
        - Make expenses specific to the business type and spending patterns described
        - Link to actual expense account names from the provided chart of accounts
        - Use realistic amounts for the business type and expense category
        - Write extremely detailed, comprehensive notes (minimum 3-4 sentences per expense)
        - Include practical examples relevant to the specific business
        - Use recent dates (2024)
        - Return valid JSON only, no additional text

        Generate realistic expense categories now with very detailed notes:
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            expenses = json.loads(response_text)
            
            # Validate the structure
            for expense in expenses:
                if not all(key in expense for key in ['expense_id', 'date', 'payment_type', 'vendor_or_entity', 'total_amount', 'account_used', 'project', 'notes']):
                    raise ValueError("Invalid expense structure")
            
            return expenses
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            # Return default expenses if AI parsing fails
            return create_sample_expenses()
            
    except Exception as e:
        print(f"Error generating expenses with AI: {e}")
        # Return default expenses if AI fails
        return create_sample_expenses()


def create_sample_accounts() -> List[Dict]:
    """
    Create sample chart of accounts entries.
    
    Returns:
        List[Dict]: Sample account data
    """
    sample_accounts = [
        {"name": "Checking Account", "account_type": "Asset", "account_sub_type": "Current Asset", "description": "Primary business checking account", "current_balance": 0.0},
        {"name": "Accounts Receivable", "account_type": "Asset", "account_sub_type": "Current Asset", "description": "Money owed by customers for goods or services", "current_balance": 0.0},
        {"name": "Sales Revenue", "account_type": "Income", "account_sub_type": "Operating Income", "description": "Revenue from primary business operations", "current_balance": 0.0},
        {"name": "Office Expenses", "account_type": "Expense", "account_sub_type": "Operating Expense", "description": "General office supplies and expenses", "current_balance": 0.0},
        {"name": "Accounts Payable", "account_type": "Liability", "account_sub_type": "Current Liability", "description": "Money owed to vendors and suppliers", "current_balance": 0.0},
    ]
    return sample_accounts


def create_sample_customers() -> List[Dict]:
    """
    Create sample customer entries.
    
    Returns:
        List[Dict]: Sample customer data
    """
    sample_customers = [
        {
            "customer_id": "CUST001",
            "name": "Sarah Johnson",
            "company_name": "ABC Company",
            "email": "sarah.johnson@abccompany.com",
            "phone": "(555) 123-4567",
            "billing_address": "123 Main St",
            "city": "Anytown",
            "country": "USA",
            "balance": 0.0,
            "notes": "Sarah is the procurement manager at ABC Company and found our business through a Google search for professional services. She typically orders monthly consulting packages and prefers to pay via ACH transfer within 30 days. ABC Company has been growing rapidly and may need additional services in the future. Sarah values detailed reporting and quick response times, making her an excellent long-term customer prospect."
        },
        {
            "customer_id": "CUST002", 
            "name": "Mike Chen",
            "company_name": "",
            "email": "mike.chen.business@gmail.com",
            "phone": "(555) 987-6543",
            "billing_address": "456 Oak Ave",
            "city": "Business City",
            "country": "USA",
            "balance": 0.0,
            "notes": "Mike is a small business owner who was referred to us by another satisfied customer. He typically purchases our basic service packages and always pays immediately via credit card. Mike runs a seasonal business and tends to need more services during his busy periods from March to September. He appreciates straightforward pricing and minimal paperwork, and has potential to upgrade to premium services as his business grows."
        }
    ]
    return sample_customers


def create_sample_services() -> List[Dict]:
    """
    Create sample service entries.
    
    Returns:
        List[Dict]: Sample service data
    """
    sample_services = [
        {
            "name": "Basic Consulting Package",
            "description": "Our foundational consulting service designed for small to medium businesses looking to improve their operations and profitability. This package includes a comprehensive business analysis, strategic planning session, and detailed recommendations report. Perfect for business owners who need expert guidance but want to maintain control over implementation. The service is delivered through a combination of on-site visits, virtual meetings, and written deliverables over a 4-week period. This offering provides exceptional value by giving businesses access to senior-level expertise at an affordable price point.",
            "type": "Service",
            "unit_price": 1500.0,
            "taxable": "yes",
            "income_account_name": "Consulting Revenue"
        },
        {
            "name": "Premium Advisory Service",
            "description": "Our comprehensive advisory service for established businesses seeking ongoing strategic support and operational excellence. This premium offering includes monthly strategy sessions, quarterly business reviews, unlimited email and phone consultations, and priority access to our team of specialists. Designed for companies ready to scale and optimize their operations with continuous expert guidance. The service is delivered through regular face-to-face meetings, detailed progress reports, and immediate access to our expertise whenever critical business decisions arise. This service represents our highest value offering and typically results in significant ROI improvements for our clients.",
            "type": "Service", 
            "unit_price": 5000.0,
            "taxable": "yes",
            "income_account_name": "Advisory Revenue"
        }
    ]
    return sample_services


def create_sample_vendors() -> List[Dict]:
    """
    Create sample vendor entries.
    
    Returns:
        List[Dict]: Sample vendor data
    """
    sample_vendors = [
        {
            "vendor_id": "VEND001",
            "name": "TechSource Solutions",
            "company_name": "TechSource Solutions Inc",
            "email": "billing@techsource.com",
            "phone": "(555) 987-6543",
            "address": "456 Business Ave",
            "city": "Commerce City",
            "country": "USA",
            "balance": 0.0,
            "currency": "USD",
            "notes": "TechSource Solutions provides all our technology equipment and IT support services including computers, software licensing, and network maintenance. We work with them monthly for equipment purchases and have a quarterly service contract for ongoing IT support. They offer NET 30 payment terms and have consistently delivered quality products with excellent technical support. Their relationship with our business spans over three years, and they provide priority service due to our regular volume. They also offer competitive pricing on bulk orders and emergency support when needed."
        },
        {
            "vendor_id": "VEND002",
            "name": "Premier Office Supplies",
            "company_name": "Premier Office Supplies LLC",
            "email": "orders@premieroffice.com", 
            "phone": "(555) 456-7890",
            "address": "789 Supply Street",
            "city": "Business Park",
            "country": "USA",
            "balance": 0.0,
            "currency": "USD",
            "notes": "Premier Office Supplies is our primary vendor for all office supplies, stationery, and general business materials. We place orders with them bi-weekly and they provide same-day delivery for orders over $100. Payment terms are NET 15 with a 2% discount for early payment. They have been extremely reliable over our two-year relationship and maintain consistent inventory levels. Their customer service is exceptional, often suggesting cost-saving alternatives or bulk purchase options that help manage our operating expenses more effectively."
        }
    ]
    return sample_vendors


def create_sample_expenses() -> List[Dict]:
    """
    Create sample expense entries.
    
    Returns:
        List[Dict]: Sample expense data
    """
    sample_expenses = [
        {
            "expense_id": "EXP001",
            "date": "2024-01-15",
            "payment_type": "credit",
            "vendor_or_entity": "Office Supply Plus",
            "total_amount": 250.00,
            "account_used": "Office Supplies",
            "project": "General",
            "notes": "Monthly office supplies purchase including paper, pens, folders, and basic office equipment. This is a recurring monthly expense that varies based on business activity and staffing levels. Proper management involves bulk purchasing to reduce per-unit costs while avoiding over-stocking. These supplies are essential for daily operations and directly impact employee productivity and professional presentation to clients."
        },
        {
            "expense_id": "EXP002",
            "date": "2024-01-20",
            "payment_type": "bank",
            "vendor_or_entity": "Professional Services Inc",
            "total_amount": 500.00,
            "account_used": "Professional Services",
            "project": "General",
            "notes": "Quarterly legal and accounting consultation fees for business compliance and tax preparation. This expense occurs regularly each quarter and is essential for maintaining legal compliance and optimizing tax strategies. The amount may vary based on business complexity and special projects requiring professional guidance. These services help prevent costly legal issues and ensure proper financial management, making them a critical investment in business sustainability."
        }
    ]
    return sample_expenses


def save_to_csv(data: List[Dict], filename: str) -> bool:
    """
    Save data to CSV file in anonymized_data directory.
    
    Args:
        data: List of dictionaries to save
        filename: Name of the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        df = pd.DataFrame(data)
        filepath = os.path.join("anonymized_data", filename)
        df.to_csv(filepath, index=False)
        print(f"Successfully saved {len(data)} records to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {str(e)}")
        return False


def check_setup_status() -> Dict[str, bool]:
    """
    Check which setup steps have been completed.
    
    Returns:
        Dict[str, bool]: Status of each setup step
    """
    status = {
        "accounts": False,
        "customers_services": False,
        "vendors_expenses": False
    }
    
    # Check if CSV files have data (more than just headers)
    csv_files = {
        "accounts": "accounts.csv",
        "customers_services": ["customers.csv", "services.csv"],
        "vendors_expenses": ["vendors.csv", "expenses.csv"]
    }
    
    for step, files in csv_files.items():
        if isinstance(files, str):
            files = [files]
        
        step_complete = True
        for file in files:
            filepath = os.path.join("anonymized_data", file)
            try:
                df = pd.read_csv(filepath)
                if len(df) == 0:  # Only headers, no data
                    step_complete = False
                    break
            except:
                step_complete = False
                break
        
        status[step] = step_complete
    
    return status


def get_setup_progress() -> float:
    """
    Calculate setup progress as a percentage.
    
    Returns:
        float: Progress percentage (0.0 to 1.0)
    """
    status = check_setup_status()
    completed_steps = sum(status.values())
    total_steps = len(status)
    return completed_steps / total_steps if total_steps > 0 else 0.0 