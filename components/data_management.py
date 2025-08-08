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
        
        # Convert to DataFrame and display
        if export_data:
            df = pd.DataFrame(export_data)
            st.dataframe(df)
            
            # Convert to CSV for download
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="financial_data_export.csv",
                mime="text/csv"
            )
            st.success("Financial data ready for download!")
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