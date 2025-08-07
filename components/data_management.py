import streamlit as st
import pandas as pd
import os

def show_data_management_page():
    """Display the data management page"""
    st.title("Data Management")
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
                "anonymized_data/bank_transactions.csv"
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
                    st.write(f"✅ {message}")
            
            if errors:
                st.error("**Errors encountered:**")
                for error in errors:
                    st.write(f"❌ {error}")
        else:
            st.error("Please check the confirmation box to proceed.")
    
    st.markdown("---")
    
    # Data Reset Instructions
    st.subheader("After Clearing Data")
    st.write("Once you clear all data, you can:")
    st.write("1. **Start Over**: Go to Onboarding to set up your business again")
    st.write("2. **Fresh Setup**: Use Setup to create new chart of accounts")
    st.write("3. **Clean Slate**: All pages will be reset to their initial state") 