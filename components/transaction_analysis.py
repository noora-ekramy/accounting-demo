import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration for wide layout
st.set_page_config(page_title="Transaction Analysis", layout="wide")

def show_transaction_analysis_page():
    """Display the transaction analysis page"""
    st.title("AI Transaction Analysis")
    st.markdown("---")
    
    # Check if we have transaction data from session state
    if "analysis_transaction" not in st.session_state:
        st.warning("No transaction selected for analysis.")
        st.info("Please go back to Bank Transactions page and select a transaction to analyze.")
        
        if st.button("Back to Bank Transactions"):
            st.session_state.bank_transactions_requested = True
            st.rerun()
        return
    
    transaction = st.session_state.analysis_transaction
    
    # Display transaction details
    st.subheader("Transaction Details")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Date:** {transaction.get('date', 'N/A')}")
        st.write(f"**Description:** {transaction.get('description', 'N/A')}")
        st.write(f"**Amount:** ${transaction.get('amount', 0):,.2f}")
    
    with col2:
        st.write(f"**Type:** {transaction.get('transaction_type', 'N/A')}")
        st.write(f"**Category:** {transaction.get('category', 'N/A')}")
        st.write(f"**Reference:** {transaction.get('reference', 'N/A')}")
    
    st.markdown("---")
    
    # AI Analysis Section
    st.subheader("AI Analysis & Suggestions")
    
    if st.button("Generate AI Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing transaction with AI..."):
            suggestions = get_ai_transaction_suggestions(transaction)
            
            if suggestions:
                st.session_state.ai_suggestions = suggestions
                st.success("AI analysis completed!")
            else:
                st.error("Failed to generate AI suggestions. Please try again.")
    
    # Display AI suggestions if available
    if "ai_suggestions" in st.session_state:
        display_ai_suggestions(st.session_state.ai_suggestions, transaction)
    
    # Navigation
    st.markdown("---")
    if st.button("Back to Bank Transactions"):
        # Clear session state
        if "analysis_transaction" in st.session_state:
            del st.session_state.analysis_transaction
        if "ai_suggestions" in st.session_state:
            del st.session_state.ai_suggestions
        st.session_state.bank_transactions_requested = True
        st.rerun()

def display_ai_suggestions(suggestions, transaction):
    """Display AI suggestions in organized tabs"""
    
    tab1, tab2, tab3, tab4 = st.tabs(["Account Mapping", "Double-Entry Bookkeeping", "Entity Matching", "Document Creation"])
    
    with tab1:
        st.subheader("Affected Accounts")
        account_suggestions = suggestions.get("account_suggestions", [])
        
        if len(account_suggestions) >= 2:
            st.write("**Two accounts will be affected by this transaction:**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**First Account**")
                first_account = account_suggestions[0]
                st.write(f"**Name:** {first_account.get('account_name', 'N/A')}")
                st.write(f"**Type:** {first_account.get('account_type', 'N/A')}")
                st.write(f"**Confidence:** {first_account.get('confidence', 'Low')}")
                st.caption(f"Reason: {first_account.get('reason', 'No reason provided')}")
                
            with col2:
                st.write("**Second Account**")
                second_account = account_suggestions[1]
                st.write(f"**Name:** {second_account.get('account_name', 'N/A')}")
                st.write(f"**Type:** {second_account.get('account_type', 'N/A')}")
                st.write(f"**Confidence:** {second_account.get('confidence', 'Low')}")
                st.caption(f"Reason: {second_account.get('reason', 'No reason provided')}")
            
            if st.button("Apply These Account Mappings"):
                st.success("Account mappings applied successfully!")
                st.info("Both accounts have been assigned to this transaction.")
        else:
            # Fallback for single account suggestion
            for i, account in enumerate(account_suggestions):
                with st.expander(f"Account Option {i+1}: {account.get('account_name', 'Unknown')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Account Name:** {account.get('account_name', 'N/A')}")
                        st.write(f"**Account Type:** {account.get('account_type', 'N/A')}")
                    with col2:
                        confidence = account.get('confidence', 'Low')
                        st.write(f"**Confidence:** {confidence}")
                    
                    st.write(f"**Reason:** {account.get('reason', 'No reason provided')}")
                    
                    if st.button(f"Apply This Account Mapping", key=f"account_{i}"):
                        apply_account_mapping(transaction, account)
    
    with tab2:
        st.subheader("Double-Entry Bookkeeping")
        double_entry = suggestions.get("double_entry_mapping", {})
        
        if double_entry:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**DEBIT:**")
                debit_account = double_entry.get("debit_account", "N/A")
                debit_amount = double_entry.get("debit_amount", 0)
                st.write(f"{debit_account}: ${debit_amount:,.2f}")
                st.caption("Account balance increases")
            with col2:
                st.write("**CREDIT:**")
                credit_account = double_entry.get("credit_account", "N/A")
                credit_amount = double_entry.get("credit_amount", 0)
                st.write(f"{credit_account}: ${credit_amount:,.2f}")
                st.caption("Account balance increases")
            
            explanation = double_entry.get("explanation", "No explanation provided")
            st.info(f"**Explanation:** {explanation}")
            
            # Verify accounting equation balance
            if abs(debit_amount - credit_amount) < 0.01:
                st.success("✅ Accounting equation balanced: Debits = Credits")
            else:
                st.error("❌ Accounting equation unbalanced!")
            
            if st.button("Apply Double-Entry Mapping"):
                st.success("Double-entry mapping applied successfully!")
        else:
            st.warning("No double-entry mapping provided by AI. Please try generating suggestions again.")
    
    with tab3:
        st.subheader("Entity Matching")
        entity_suggestion = suggestions.get("entity_suggestion", {})
        
        entity_type = entity_suggestion.get("type", "new")
        entity_name = entity_suggestion.get("name", "")
        confidence = entity_suggestion.get("confidence", "Low")
        reason = entity_suggestion.get("reason", "No reason provided")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Entity Type:** {entity_type.title()}")
            st.write(f"**Entity Name:** {entity_name if entity_name else 'New Entity'}")
        with col2:
            st.write(f"**Confidence:** {confidence}")
        
        st.write(f"**Reason:** {reason}")
        
        if entity_type in ['customer', 'vendor'] and entity_name:
            if st.button(f"Link to {entity_type.title()}: {entity_name}"):
                link_to_entity(transaction, entity_type, entity_name)
        elif entity_type == 'new':
            if st.button("Create New Entity"):
                create_new_entity(transaction, suggestions)
    
    with tab4:
        st.subheader("Document Creation")
        doc_suggestion = suggestions.get("document_suggestion", {})
        
        doc_type = doc_suggestion.get("type", "none")
        service_or_expense = doc_suggestion.get("service_or_expense", "")
        amount = doc_suggestion.get("amount", 0)
        confidence = doc_suggestion.get("confidence", "Low")
        reason = doc_suggestion.get("reason", "No reason provided")
        
        if doc_type != "none":
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Document Type:** {doc_type.title()}")
                st.write(f"**Service/Expense:** {service_or_expense}")
            with col2:
                st.write(f"**Amount:** ${amount:,.2f}")
                st.write(f"**Confidence:** {confidence}")
            
            st.write(f"**Reason:** {reason}")
            
            if st.button(f"Create {doc_type.title()}"):
                create_document(transaction, doc_suggestion)
        else:
            st.info("No document creation suggested for this transaction.")
    
    # Additional notes
    st.markdown("---")
    st.subheader("Additional AI Insights")
    additional_notes = suggestions.get("additional_notes", "No additional notes available.")
    st.write(additional_notes)

def get_ai_transaction_suggestions(transaction_row):
    """Get AI suggestions for transaction mapping"""
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("Google/Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in environment variables.")
            return None
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Load relevant data for context
        accounts_data = load_csv_data("accounts.csv")
        customers_data = load_csv_data("customers.csv")
        vendors_data = load_csv_data("vendors.csv")
        services_data = load_csv_data("services.csv")
        expenses_data = load_csv_data("expenses.csv")
        
        # Create comprehensive prompt
        amount = transaction_row.get('amount', 0)
        is_income = amount > 0
        transaction_type = "Income/Revenue" if is_income else "Expense/Payment"
        
        prompt = f"""
        Analyze this bank transaction and provide structured suggestions:

        TRANSACTION DETAILS:
        Date: {transaction_row.get('date', '')}
        Description: {transaction_row.get('description', '')}
        Amount: ${amount:,.2f}
        Category: {transaction_row.get('category', '')}
        Type: {transaction_type}

        AVAILABLE DATA:
        Chart of Accounts: {str(accounts_data)[:1000]}...
        Customers: {str(customers_data)[:500]}...
        Vendors: {str(vendors_data)[:500]}...
        Services: {str(services_data)[:500]}...
        Expense Categories: {str(expenses_data)[:500]}...

        DOUBLE-ENTRY ACCOUNTING RULES:
        Every transaction MUST affect exactly TWO accounts from the chart of accounts.
        Select TWO specific accounts from the available chart of accounts that will be affected.

        DEBIT/CREDIT RULES:
        - ASSETS: Debit increases, Credit decreases
        - LIABILITIES: Credit increases, Debit decreases  
        - EQUITY: Credit increases, Debit decreases
        - REVENUE: Credit increases, Debit decreases
        - EXPENSES: Debit increases, Credit decreases

        TRANSACTION ANALYSIS:
        1. Look at the transaction amount and description
        2. Choose the FIRST account from the chart of accounts that should be affected
        3. Choose the SECOND account from the chart of accounts for the offsetting entry
        4. Determine which account gets debited and which gets credited
        5. Both amounts must be equal to maintain balance

        ANALYSIS INSTRUCTIONS:
        1. Select TWO specific accounts from the provided chart of accounts
        2. Determine debit/credit for each account based on account type and transaction
        3. Match with existing customers (for income) or vendors (for expenses)
        4. Suggest appropriate document creation (invoice/bill)
        5. Confidence levels: High, Medium, or Low

        Return ONLY a JSON object with this structure:
        {{
            "account_suggestions": [
                {{
                    "account_name": "First account from chart of accounts",
                    "account_type": "Asset|Liability|Equity|Income|Expense",
                    "confidence": "High|Medium|Low",
                    "reason": "Why this account is affected"
                }},
                {{
                    "account_name": "Second account from chart of accounts",
                    "account_type": "Asset|Liability|Equity|Income|Expense", 
                    "confidence": "High|Medium|Low",
                    "reason": "Why this account is affected"
                }}
            ],
            "double_entry_mapping": {{
                "debit_account": "Account name from chart of accounts to debit",
                "debit_amount": {abs(amount)},
                "credit_account": "Account name from chart of accounts to credit", 
                "credit_amount": {abs(amount)},
                "explanation": "Why these two accounts are affected and debit/credit logic"
            }},
            "entity_suggestion": {{
                "type": "customer|vendor|new",
                "name": "Matching entity name or empty if new",
                "confidence": "High|Medium|Low",
                "reason": "Brief explanation"
            }},
            "document_suggestion": {{
                "type": "invoice|bill|none",
                "service_or_expense": "Matching service or expense category",
                "amount": {abs(amount)},
                "confidence": "High|Medium|Low",
                "reason": "Brief explanation"
            }},
            "additional_notes": "Any other relevant insights about the transaction and accounting treatment"
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse JSON response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        suggestions = json.loads(response_text)
        return suggestions
        
    except Exception as e:
        st.error(f"Error in AI analysis: {str(e)}")
        return create_fallback_suggestions(transaction_row)

def load_csv_data(filename):
    """Load CSV data for AI context"""
    try:
        file_path = os.path.join("anonymized_data", filename)
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except:
        return []

def create_fallback_suggestions(transaction):
    """Create basic suggestions if AI fails"""
    amount = transaction.get('amount', 0)
    is_income = amount > 0
    abs_amount = abs(amount)
    
    # Load chart of accounts to get real account names
    accounts_data = load_csv_data("accounts.csv")
    
    # Find appropriate accounts from chart of accounts
    if accounts_data:
        if is_income:
            # Look for cash/bank account and revenue account
            cash_accounts = [acc for acc in accounts_data if 'cash' in acc.get('account_name', '').lower() or 'bank' in acc.get('account_name', '').lower()]
            revenue_accounts = [acc for acc in accounts_data if acc.get('account_type', '').lower() == 'revenue' or 'revenue' in acc.get('account_name', '').lower()]
            
            debit_account = cash_accounts[0]['account_name'] if cash_accounts else "Cash"
            credit_account = revenue_accounts[0]['account_name'] if revenue_accounts else "Service Revenue"
            explanation = f"Money received increases {debit_account} (asset) and {credit_account} (revenue)"
        else:
            # Look for expense account and cash/bank account
            expense_accounts = [acc for acc in accounts_data if acc.get('account_type', '').lower() == 'expense' or 'expense' in acc.get('account_name', '').lower()]
            cash_accounts = [acc for acc in accounts_data if 'cash' in acc.get('account_name', '').lower() or 'bank' in acc.get('account_name', '').lower()]
            
            debit_account = expense_accounts[0]['account_name'] if expense_accounts else "General Expenses"
            credit_account = cash_accounts[0]['account_name'] if cash_accounts else "Cash"
            explanation = f"Money spent increases {debit_account} (expense) and decreases {credit_account} (asset)"
    else:
        # Fallback if no chart of accounts available
        if is_income:
            debit_account = "Cash"
            credit_account = "Service Revenue"
            explanation = "Money received increases cash asset and revenue"
        else:
            debit_account = "General Expenses"
            credit_account = "Cash"
            explanation = "Money spent increases expenses and decreases cash"
    
    return {
        "account_suggestions": [
            {
                "account_name": credit_account if is_income else debit_account,
                "account_type": "Revenue" if is_income else "Expense",
                "confidence": "Medium",
                "reason": "Selected from chart of accounts based on transaction type"
            },
            {
                "account_name": debit_account if is_income else credit_account,
                "account_type": "Asset" if is_income else "Asset",
                "confidence": "Medium", 
                "reason": "Cash/bank account from chart of accounts"
            }
        ],
        "double_entry_mapping": {
            "debit_account": debit_account,
            "debit_amount": abs_amount,
            "credit_account": credit_account,
            "credit_amount": abs_amount,
            "explanation": explanation
        },
        "entity_suggestion": {
            "type": "new",
            "name": "",
            "confidence": "Low",
            "reason": "No existing entities matched"
        },
        "document_suggestion": {
            "type": "none",
            "service_or_expense": "",
            "amount": abs_amount,
            "confidence": "Low",
            "reason": "Insufficient data for document creation"
        },
        "additional_notes": "Basic double-entry analysis using chart of accounts. Manual review recommended for accurate account selection."
    }

def apply_account_mapping(transaction, account):
    """Apply the selected account mapping"""
    st.success(f"Account mapping applied: {account.get('account_name', 'Unknown')}")
    st.info("In a full system, this would update the transaction's account assignment.")

def link_to_entity(transaction, entity_type, entity_name):
    """Link transaction to existing entity"""
    st.success(f"Transaction linked to {entity_type}: {entity_name}")
    st.info("In a full system, this would create the association in your database.")

def create_new_entity(transaction, suggestions):
    """Create a new customer or vendor"""
    st.success("New entity creation initiated.")
    st.info("In a full system, this would open a form to create a new customer or vendor.")

def create_document(transaction, doc_suggestion):
    """Create invoice or bill from transaction"""
    doc_type = doc_suggestion.get("type", "document")
    amount = doc_suggestion.get("amount", 0)
    
    st.success(f"{doc_type.title()} creation initiated for ${amount:,.2f}")
    st.info(f"In a full system, this would open the {doc_type} creation form with pre-filled data.") 