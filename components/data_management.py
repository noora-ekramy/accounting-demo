import streamlit as st
import pandas as pd
import os
import json

def show_data_management_page():
    """Display the data management page"""
    st.title("Data Management")
    st.markdown("---")
    
    # Balance Sheet Verification Section
    st.subheader("Balance Sheet Verification")
    st.write("Check if your financial data balances and make adjustments:")
    
    if st.button("Check Balance Sheet", type="primary"):
        check_balance_sheet_from_file()
    
    st.markdown("---")
    
    # Helper Tools Data Section
    st.subheader("Quick Helper Tools Data")
    show_helper_tools_data()
    
    st.markdown("---")
    
    # Data Import/Export Section
    st.subheader("Data Import/Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Export Financial Data**")
        if st.button("Export to CSV"):
            export_financial_data()
    
    with col2:
        st.markdown("**Data Summary**")
        show_data_summary()
    
    st.markdown("---")
    
    st.write("Manage your accounting data and system settings.")
    
    # Clear All Data Section
    st.subheader("Clear All Data")
    st.warning("This action will permanently delete all your data and cannot be undone!")
    
    # Show what will be cleared
    with st.expander("What will be cleared?", expanded=False):
        st.write("The following data will be permanently deleted:")
        st.write("- **Onboarding responses** (onboarding_responses.json)")
        st.write("- **Chart of accounts** (anonymized_data/accounts.csv)")
        st.write("- **Customer data** (anonymized_data/customers.csv)")
        st.write("- **Vendor data** (anonymized_data/vendors.csv)")
        st.write("- **Service data** (anonymized_data/services.csv)")
        st.write("- **Invoice data** (anonymized_data/invoices.csv)")
        st.write("- **Bill data** (anonymized_data/bills.csv)")
        st.write("- **Expense data** (anonymized_data/expenses.csv)")
        st.write("- **Bank transaction data** (anonymized_data/bank_transactions.csv)")
        st.write("- **Fixed assets data** (anonymized_data/fixed_assets.csv)")
        st.write("- **All session data** and temporary files")
        st.write("- **Helper tools detailed data** (cash accounts, AR details, etc.)")
    
    st.markdown("---")
    
    # Confirmation checkbox
    confirm_clear = st.checkbox("I understand this action cannot be undone and will delete all my data")
    
    # Clear button (only enabled if confirmed)
    if st.button("Clear All Data", type="primary", disabled=not confirm_clear):
        if confirm_clear:
            # Clear all data
            files_to_clear = [
                "onboarding_responses.json",
                "anonymized_data/accounts.csv",
                "anonymized_data/customers.csv", 
                "anonymized_data/vendors.csv",
                "anonymized_data/services.csv",
                "anonymized_data/invoices.csv",
                "anonymized_data/bills.csv",
                "anonymized_data/expenses.csv",
                "anonymized_data/bank_transactions.csv",
                "anonymized_data/fixed_assets.csv"
            ]
            
            cleared_files = []
            errors = []
            
            # Clear each file
            for file_path in files_to_clear:
                try:
                    if os.path.exists(file_path):
                        # For CSV files, keep headers but remove data
                        if file_path.endswith('.csv'):
                            df = pd.read_csv(file_path)
                            # Keep only the header row (empty dataframe with columns)
                            empty_df = pd.DataFrame(columns=df.columns)
                            empty_df.to_csv(file_path, index=False)
                            cleared_files.append(f"Cleared data from {file_path}")
                        else:
                            # For JSON files, delete completely
                            os.remove(file_path)
                            cleared_files.append(f"Deleted {file_path}")
                    else:
                        cleared_files.append(f"{file_path} (file not found - already clear)")
                except Exception as e:
                    errors.append(f"Error clearing {file_path}: {str(e)}")
            
            # Clear session state
            session_keys_to_clear = [key for key in st.session_state.keys() if key not in ['session_active']]
            for key in session_keys_to_clear:
                del st.session_state[key]
            
            # Show results
            pass  # Data clearing completed
            
            if cleared_files:
                st.write("**Files processed:**")
                for message in cleared_files:
                    st.write(f"Processed: {message}")
            
            if errors:
                st.error("**Errors encountered:**")
                for error in errors:
                    st.write(f"Error: {error}")
        else:
            st.error("Please check the confirmation box to proceed.")
    
    st.markdown("---")
    
    # Data Reset Instructions
    st.subheader("After Clearing Data")
    st.write("Once you clear all data, you can:")
    st.write("1. **Start Over**: Go to Onboarding to set up your business again")
    st.write("2. **Fresh Setup**: Use Setup to create new chart of accounts")
    st.write("3. **Clean Slate**: All pages will be reset to their initial state")

def check_balance_sheet_from_file():
    """Check balance sheet using data from onboarding file"""
    try:
        if not os.path.exists("onboarding_responses.json"):
            st.error("No financial data found. Please complete onboarding first.")
            return
        
        with open("onboarding_responses.json", 'r') as f:
            financial_data = json.load(f)
        
        # Calculate totals
        assets_total = 0
        liabilities_total = 0
        equity_total = 0
        
        # Sum assets
        for value in financial_data.get("assets", {}).values():
            if value and str(value).strip():
                try:
                    clean_value = str(value).replace("$", "").replace(",", "").strip()
                    if clean_value:
                        assets_total += float(clean_value)
                except:
                    pass
        
        # Sum liabilities
        for value in financial_data.get("liabilities", {}).values():
            if value and str(value).strip():
                try:
                    clean_value = str(value).replace("$", "").replace(",", "").strip()
                    if clean_value:
                        liabilities_total += float(clean_value)
                except:
                    pass
        
        # Sum equity (only required fields)
        equity_data = financial_data.get("equity", {})
        required_equity_fields = ["common_stock", "retained_earnings", "additional_paid_in_capital"]
        for field in required_equity_fields:
            value = equity_data.get(field)
            if value and str(value).strip():
                try:
                    clean_value = str(value).replace("$", "").replace(",", "").strip()
                    if clean_value:
                        equity_total += float(clean_value)
                except:
                    pass
        
        # Check balance
        liab_plus_equity = liabilities_total + equity_total
        difference = assets_total - liab_plus_equity
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Assets", f"${assets_total:,.2f}")
        with col2:
            st.metric("Total Liabilities", f"${liabilities_total:,.2f}")
        with col3:
            st.metric("Total Equity", f"${equity_total:,.2f}")
        
        st.metric("Liabilities + Equity", f"${liab_plus_equity:,.2f}")
        
        if abs(difference) < 0.01:  # Balanced (allow for rounding)
            st.success(f"Balance Sheet is balanced! Assets = Liabilities + Equity")
        else:
            st.warning(f"Balance Sheet is out of balance by ${abs(difference):,.2f}")
            
            if difference > 0:
                st.write(f"Assets exceed Liabilities + Equity by ${difference:,.2f}")
                st.info("Consider increasing Retained Earnings or adding missing liabilities.")
            else:
                st.write(f"Liabilities + Equity exceed Assets by ${abs(difference):,.2f}")
                st.info("Consider increasing assets or reducing equity/liabilities.")
                
    except Exception as e:
        st.error(f"Error checking balance sheet: {e}")

def export_financial_data():
    """Export financial data to CSV format"""
    try:
        if not os.path.exists("onboarding_responses.json"):
            st.error("No financial data found to export.")
            return
        
        with open("onboarding_responses.json", 'r') as f:
            financial_data = json.load(f)
        
        # Create export data
        export_data = []
        
        # Add general info
        for key, value in financial_data.get("general_info", {}).items():
            if value:
                export_data.append({"Category": "General Info", "Field": key.replace("_", " ").title(), "Value": value})
        
        # Add business questions
        business_q = financial_data.get("business_questions", {})
        for key, value in business_q.items():
            if key != "locked" and value:
                export_data.append({"Category": "Business Questions", "Field": key.replace("_", " ").title(), "Value": value})
        
        # Add assets
        for key, value in financial_data.get("assets", {}).items():
            if value:
                export_data.append({"Category": "Assets", "Field": key.replace("_", " ").title(), "Value": value})
        
        # Add liabilities
        for key, value in financial_data.get("liabilities", {}).items():
            if value:
                export_data.append({"Category": "Liabilities", "Field": key.replace("_", " ").title(), "Value": value})
        
        # Add equity
        for key, value in financial_data.get("equity", {}).items():
            if value:
                export_data.append({"Category": "Equity", "Field": key.replace("_", " ").title(), "Value": value})
        
        # Add detailed helper tools data
        if "cash_accounts_details" in financial_data:
            for i, account in enumerate(financial_data["cash_accounts_details"]):
                export_data.append({
                    "Category": "Cash Accounts", 
                    "Field": f"Account {i+1}: {account['name']}", 
                    "Value": f"${account['balance']:,.2f} (Added: {account.get('date_added', 'N/A')})"
                })
        
        if "ar_estimation_details" in financial_data:
            ar_details = financial_data["ar_estimation_details"]
            export_data.append({
                "Category": "AR Estimation", 
                "Field": "Method", 
                "Value": ar_details.get('method', 'N/A')
            })
            export_data.append({
                "Category": "AR Estimation", 
                "Field": "Amount", 
                "Value": f"${ar_details.get('amount', ar_details.get('total_amount', 0)):,.2f}"
            })
            if ar_details.get('january_payments'):
                export_data.append({
                    "Category": "AR Estimation", 
                    "Field": "January Payments", 
                    "Value": f"${ar_details['january_payments']:,.2f}"
                })
        
        if "inventory_details" in financial_data:
            inv_details = financial_data["inventory_details"]
            export_data.append({
                "Category": "Inventory Details", 
                "Field": "Type", 
                "Value": inv_details.get('type', 'N/A')
            })
            export_data.append({
                "Category": "Inventory Details", 
                "Field": "Cost Method", 
                "Value": inv_details.get('cost_method', 'N/A')
            })
            export_data.append({
                "Category": "Inventory Details", 
                "Field": "Value", 
                "Value": f"${inv_details.get('value', 0):,.2f}"
            })
        
        if "owner_transactions" in financial_data:
            owner_data = financial_data["owner_transactions"]
            for key, value in owner_data.items():
                if key != "loan_details" and value is not None:
                    export_data.append({
                        "Category": "Owner Transactions", 
                        "Field": key.replace("_", " ").title(), 
                        "Value": f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
                    })
        
        if "accrual_details" in financial_data:
            accrual_data = financial_data["accrual_details"]
            for key, value in accrual_data.items():
                if key not in ["description", "date_set", "reporting_date"] and value:
                    export_data.append({
                        "Category": "Accruals", 
                        "Field": key.replace("_", " ").title(), 
                        "Value": f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
                    })
        
        # Convert to DataFrame and display
        if export_data:
            df = pd.DataFrame(export_data)
            st.dataframe(df)
            
            # Convert to CSV for download
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Complete Financial Data CSV",
                data=csv,
                file_name="complete_financial_data_export.csv",
                mime="text/csv"
            )
            st.success("Complete financial data with helper tools details ready for download!")
        else:
            st.warning("No data available to export.")
            
    except Exception as e:
        st.error(f"Error exporting data: {e}")

def show_data_summary():
    """Show summary of current data"""
    try:
        if not os.path.exists("onboarding_responses.json"):
            st.write("No financial data found")
            return
        
        with open("onboarding_responses.json", 'r') as f:
            financial_data = json.load(f)
        
        # Count completed fields
        total_fields = 0
        completed_fields = 0
        
        categories = ["general_info", "business_questions", "assets", "liabilities", "equity"]
        
        for category in categories:
            category_data = financial_data.get(category, {})
            for key, value in category_data.items():
                if key != "locked":  # Skip metadata
                    total_fields += 1
                    if value and str(value).strip():
                        completed_fields += 1
        
        completion_rate = (completed_fields / total_fields * 100) if total_fields > 0 else 0
        
        st.metric("Completion", f"{completed_fields}/{total_fields}")
        st.metric("Progress", f"{completion_rate:.1f}%")
        
        if financial_data.get("completed", False):
            st.success("Data collection complete!")
        else:
            st.info("Data collection in progress")
            
    except Exception as e:
        st.error(f"Error loading data summary: {e}") 

def show_helper_tools_data():
    """Display detailed data from helper tools"""
    if not os.path.exists("onboarding_responses.json"):
        st.info("No helper tools data found. Complete onboarding to see detailed data.")
        return
    
    try:
        with open("onboarding_responses.json", 'r') as f:
            financial_data = json.load(f)
        
        # Show cash accounts details
        if "cash_accounts_details" in financial_data and financial_data["cash_accounts_details"]:
            st.markdown("**Cash Accounts Breakdown:**")
            cash_df = pd.DataFrame(financial_data["cash_accounts_details"])
            st.dataframe(cash_df, use_container_width=True)
            
            total_cash = sum(acc["balance"] for acc in financial_data["cash_accounts_details"])
            st.metric("Total Cash from Accounts", f"${total_cash:,.2f}")
        
        # Show AR estimation details
        if "ar_estimation_details" in financial_data:
            st.markdown("**Accounts Receivable Estimation Details:**")
            ar_details = financial_data["ar_estimation_details"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Method Used:** {ar_details.get('method', 'N/A')}")
                st.write(f"**Date Set:** {ar_details.get('date_set', 'N/A')}")
            with col2:
                if ar_details.get('method') == 'January Payments Estimate':
                    st.write(f"**January Payments:** ${ar_details.get('january_payments', 0):,.2f}")
                elif ar_details.get('method') == 'Software/Invoice Upload':
                    st.write(f"**File:** {ar_details.get('filename', 'N/A')}")
                    st.write(f"**Records:** {ar_details.get('records_count', 0)}")
                st.write(f"**Amount:** ${ar_details.get('amount', ar_details.get('total_amount', 0)):,.2f}")
        
        # Show inventory details
        if "inventory_details" in financial_data:
            st.markdown("**Inventory Details:**")
            inv_details = financial_data["inventory_details"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {inv_details.get('type', 'N/A')}")
                st.write(f"**Cost Method:** {inv_details.get('cost_method', 'N/A')}")
            with col2:
                st.write(f"**Value:** ${inv_details.get('value', 0):,.2f}")
                st.write(f"**Date Set:** {inv_details.get('date_set', 'N/A')}")
            
            if inv_details.get('description'):
                st.write(f"**Description:** {inv_details['description']}")
        
        # Show owner transactions
        if "owner_transactions" in financial_data:
            st.markdown("**Owner Transactions:**")
            owner_data = financial_data["owner_transactions"]
            
            if "net_income_2024" in owner_data:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Net Income 2024", f"${owner_data.get('net_income_2024', 0):,.2f}")
                with col2:
                    st.metric("Distributions", f"${owner_data.get('distributions_taken', 0):,.2f}")
                with col3:
                    st.metric("Retained Earnings", f"${owner_data.get('calculated_retained_earnings', 0):,.2f}")
            
            if "loan_details" in owner_data:
                loan_info = owner_data["loan_details"]
                st.write(f"**Loan Direction:** {loan_info.get('direction', 'N/A')}")
                st.write(f"**Loan Amount:** ${loan_info.get('amount', 0):,.2f}")
                if loan_info.get('notes'):
                    st.write(f"**Notes:** {loan_info['notes']}")
        
        # Show accrual details
        if "accrual_details" in financial_data:
            st.markdown("**Year-End Accruals:**")
            accrual_data = financial_data["accrual_details"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Unpaid Wages", f"${accrual_data.get('unpaid_wages', 0):,.2f}")
            with col2:
                st.metric("Unpaid Payroll Tax", f"${accrual_data.get('unpaid_payroll_tax', 0):,.2f}")
            with col3:
                st.metric("Other Unpaid", f"${accrual_data.get('unpaid_other', 0):,.2f}")
            
            st.metric("Total Accruals", f"${accrual_data.get('total_accruals', 0):,.2f}")
            
            if accrual_data.get('description'):
                st.write(f"**Description:** {accrual_data['description']}")
        
        if not any(key in financial_data for key in ['cash_accounts_details', 'ar_estimation_details', 'inventory_details', 'owner_transactions', 'accrual_details']):
            st.info("No detailed helper tools data found. Use the Quick Helper Tools in onboarding to generate detailed data.")
    
    except Exception as e:
        st.error(f"Error loading helper tools data: {e}") 