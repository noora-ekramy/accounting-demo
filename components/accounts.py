import streamlit as st 
import pandas as pd
import os

def show_accounts_page():
    """Display the accounts page"""
    st.title("Accounts")
    st.markdown("---")
    
    # Load accounts data
    accounts_file = os.path.join("anonymized_data", "accounts.csv")
    
    try:
        accounts_df = pd.read_csv(accounts_file)
        
        if len(accounts_df) > 0:
            st.subheader(f"Chart of Accounts ({len(accounts_df)} accounts)")
            
            # Search functionality
            search_term = st.text_input("Search accounts:", placeholder="Search by name, type, or description...")
            
            # Filter data based on search
            if search_term:
                # Search across all text columns
                mask = (
                    accounts_df['name'].str.contains(search_term, case=False, na=False) |
                    accounts_df['account_type'].str.contains(search_term, case=False, na=False) |
                    accounts_df['account_sub_type'].str.contains(search_term, case=False, na=False) |
                    accounts_df['description'].str.contains(search_term, case=False, na=False)
                )
                filtered_df = accounts_df[mask]
                st.write(f"Found {len(filtered_df)} matching accounts")
            else:
                filtered_df = accounts_df
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Accounts", len(accounts_df))
            with col2:
                # Count by account type
                if 'account_type' in accounts_df.columns:
                    asset_count = len(accounts_df[accounts_df['account_type'] == 'Asset'])
                    st.metric("Asset Accounts", asset_count)
                else:
                    st.metric("Asset Accounts", 0)
            with col3:
                # Total balance
                if 'current_balance' in accounts_df.columns:
                    total_balance = accounts_df['current_balance'].sum()
                    st.metric("Total Balance", f"${total_balance:,.2f}")
                else:
                    st.metric("Total Balance", "$0.00")
            
            # Account type breakdown
            if 'account_type' in accounts_df.columns:
                st.markdown("---")
                st.subheader("Account Type Breakdown")
                type_counts = accounts_df['account_type'].value_counts()
                
                # Display as columns
                cols = st.columns(len(type_counts))
                for i, (account_type, count) in enumerate(type_counts.items()):
                    with cols[i]:
                        st.metric(f"{account_type} Accounts", count)
            
        else:
            st.info("No accounts found. Go to Setup to create your chart of accounts.")
            
    except FileNotFoundError:
        st.warning("No chart of accounts found.")
        st.info("Please go to the Setup page to create your chart of accounts first.")
        
    except Exception as e:
        st.error(f"Error loading accounts: {str(e)}")
    
    st.markdown("---")
    st.subheader("Add New Accounts")
    
    # Tab selection for manual vs AI generation
    tab1, tab2 = st.tabs(["➕ Manual Entry", "🤖 AI Generation"])
    
    with tab1:
        st.write("**Add a new account manually:**")
        with st.form("add_account_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Account Name*")
                new_type = st.selectbox("Account Type*", ["Asset", "Liability", "Equity", "Income", "Expense"])
                new_subtype = st.text_input("Sub Type*")
            with col2:
                new_description = st.text_area("Description*", height=100)
                new_balance = st.number_input("Current Balance", value=0.0, format="%.2f")
            
            submitted = st.form_submit_button("Add Account", type="primary")
            if submitted:
                if new_name and new_type and new_subtype and new_description:
                    new_account = {
                        "name": new_name,
                        "account_type": new_type,
                        "account_sub_type": new_subtype,
                        "description": new_description,
                        "current_balance": new_balance
                    }
                    
                    # Load existing accounts
                    try:
                        existing_accounts = pd.read_csv(accounts_file)
                        # Add new account
                        new_df = pd.concat([existing_accounts, pd.DataFrame([new_account])], ignore_index=True)
                        new_df.to_csv(accounts_file, index=False)
                        pass  # Account added
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding account: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.write("**Generate accounts using AI:**")
        prompt_text = st.text_area(
            "Describe what accounts you need:",
            placeholder="Example: I need expense accounts for a restaurant business including food costs, utilities, rent, and staff wages",
            height=100
        )
        
        if st.button("Generate Accounts with AI", type="primary"):
            if prompt_text.strip():
                with st.spinner("Generating accounts using AI..."):
                    try:
                        from setup_logic import generate_chart_of_accounts_with_ai, save_to_csv
                        
                        # Create a custom context for this specific request
                        custom_context = {
                            "business_type": prompt_text,
                            "money_in": "Various revenue sources",
                            "money_out": "Various business expenses"
                        }
                        
                        # Generate accounts
                        generated_accounts = generate_chart_of_accounts_with_ai(custom_context)
                        
                        if generated_accounts:
                            # Show preview
                            st.write("**Generated Accounts Preview:**")
                            preview_df = pd.DataFrame(generated_accounts)
                            st.dataframe(preview_df, use_container_width=True)
                            
                            # Add to existing accounts
                            try:
                                existing_accounts = pd.read_csv(accounts_file)
                                combined_df = pd.concat([existing_accounts, preview_df], ignore_index=True)
                                combined_df.to_csv(accounts_file, index=False)
                                pass  # Accounts generated
                                st.rerun()
                            except FileNotFoundError:
                                # Create new file if doesn't exist
                                preview_df.to_csv(accounts_file, index=False)
                                pass  # File created with accounts
                                st.rerun()
                        else:
                            st.error("No accounts were generated. Please try a different prompt.")
                            
                    except Exception as e:
                        st.error(f"Error generating accounts: {str(e)}")
            else:
                st.warning("Please enter a description of what accounts you need.") 