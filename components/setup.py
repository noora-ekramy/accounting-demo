import streamlit as st
import pandas as pd
import os
import json
from setup_logic import (
    load_onboarding_data, 
    generate_chart_of_accounts_with_ai, 
    generate_customers_with_ai,
    generate_services_with_ai,
    generate_vendors_with_ai,
    generate_expenses_with_ai,
    save_to_csv
)

def count_completed_fields(financial_data):
    """Count completed fields in financial data"""
    count = 0
    
    # Count general_info fields (2 fields)
    general_info = financial_data.get("general_info", {})
    for value in general_info.values():
        if value and str(value).strip():
            count += 1
    
    # Count business_questions fields (3 fields)
    business_questions = financial_data.get("business_questions", {})
    for value in business_questions.values():
        if value and str(value).strip():
            count += 1
    
    # Count assets fields (8 fields)
    assets = financial_data.get("assets", {})
    for value in assets.values():
        if value and str(value).strip():
            count += 1
    
    # Count liabilities fields (7 fields)
    liabilities = financial_data.get("liabilities", {})
    for value in liabilities.values():
        if value and str(value).strip():
            count += 1
    
    # Count equity fields (5 fields)
    equity = financial_data.get("equity", {})
    for value in equity.values():
        if value and str(value).strip():
            count += 1
    
    return count

def display_collected_financial_data(saved_data):
    """Display comprehensive financial data from JSON"""
    with st.expander("📊 Your Collected Financial Information", expanded=True):
        
        # Check if it's new format or legacy
        if isinstance(saved_data, dict) and any(key in saved_data for key in ["general_info", "assets", "liabilities", "equity"]):
            # New comprehensive format
            col1, col2 = st.columns(2)
            
            with col1:
                # General Information
                st.subheader("General Information")
                general_info = saved_data.get("general_info", {})
                if any(general_info.values()):
                    for key, value in general_info.items():
                        if value:
                            display_name = key.replace("_", " ").title()
                            st.write(f"**{display_name}:** {value}")
                else:
                    st.write("No general information collected.")
                
                st.markdown("---")
                
                # Business Questions
                st.subheader("Business Overview")
                business_questions = saved_data.get("business_questions", {})
                if any(v for k, v in business_questions.items() if k != "locked" and v):
                    if business_questions.get("business_type"):
                        st.write(f"**Business Type:** {business_questions['business_type']}")
                    if business_questions.get("money_in"):
                        st.write(f"**Revenue Sources:** {business_questions['money_in']}")
                    if business_questions.get("money_out"):
                        st.write(f"**Main Expenses:** {business_questions['money_out']}")
                else:
                    st.write("No business overview collected.")
                
                st.markdown("---")
                
                # Assets
                st.subheader("Assets")
                assets = saved_data.get("assets", {})
                if any(assets.values()):
                    for key, value in assets.items():
                        if value:
                            display_name = key.replace("_", " ").title()
                            st.write(f"**{display_name}:** {value}")
                else:
                    st.write("No asset information collected.")
            
            with col2:
                # Liabilities
                st.subheader("Liabilities")
                liabilities = saved_data.get("liabilities", {})
                if any(liabilities.values()):
                    for key, value in liabilities.items():
                        if value:
                            display_name = key.replace("_", " ").title()
                            st.write(f"**{display_name}:** {value}")
                else:
                    st.write("No liability information collected.")
                
                st.markdown("---")
                
                # Equity
                st.subheader("Equity")
                equity = saved_data.get("equity", {})
                if any(equity.values()):
                    for key, value in equity.items():
                        if value:
                            display_name = key.replace("_", " ").title()
                            st.write(f"**{display_name}:** {value}")
                else:
                    st.write("No equity information collected.")
                
                st.markdown("---")
                
                # Metadata
                st.subheader("Collection Details")
                if saved_data.get("timestamp"):
                    st.write(f"**Created:** {saved_data['timestamp']}")
                if saved_data.get("last_updated"):
                    st.write(f"**Last Updated:** {saved_data['last_updated']}")
                
                completion_status = "Complete" if saved_data.get("completed", False) else "In Progress"
                st.write(f"**Status:** {completion_status}")
                
                # Field count
                completed_fields = count_completed_fields(saved_data)
                st.write(f"**Fields Completed:** {completed_fields}/25")
        
        else:
            # Legacy format
            st.subheader("Legacy Business Information")
            st.write(f"**Business Type:** {saved_data.get('business_type', 'N/A')}")
            st.write(f"**Revenue Sources:** {saved_data.get('money_in', 'N/A')}")
            st.write(f"**Main Expenses:** {saved_data.get('money_out', 'N/A')}")
            st.write(f"**Collected:** {saved_data.get('timestamp', 'Unknown')}")
            
            st.info("This is legacy format data. For complete setup, please update to the new comprehensive data collection.")

def show_setup_page():
    """Display the setup page"""
    st.title("Setup")
    st.markdown("---")
    
    # Check if onboarding is completed
    onboarding_file = "onboarding_responses.json"
    try:
        with open(onboarding_file, 'r') as f:
            saved_data = json.load(f)
        
        # Check if it's the new format with required fields
        if isinstance(saved_data, dict) and any(key in saved_data for key in ["general_info", "assets", "liabilities", "equity"]):
            completed_fields = count_completed_fields(saved_data)
            
            if completed_fields < 25:
                st.error(f"Setup requires all 25 fields to be completed. You have {completed_fields}/25 fields.")
                st.warning("Please complete the onboarding process with all financial information before accessing setup.")
                
                # Show progress
                st.subheader("Completion Progress")
                st.progress(completed_fields / 25)
                st.write(f"**Progress:** {completed_fields}/25 fields completed ({(completed_fields/25)*100:.1f}%)")
                
                if st.button("Go to Onboarding"):
                    st.info("Navigate to the Onboarding page from the sidebar to complete your data collection.")
                return
            
            # All fields completed, show setup
            st.success(f"All required data completed! ({completed_fields}/25 fields)")
            st.write("Great! Now let's set up your accounting system based on your complete business information.")
        else:
            # Legacy format - require completion
            st.error("Setup requires complete financial data collection.")
            st.warning("Please complete the new onboarding process with detailed financial information.")
            if st.button("Go to Onboarding"):
                st.info("Navigate to the Onboarding page from the sidebar to complete your data collection.")
            return
        
        st.markdown("---")
        
        # Display comprehensive data from JSON
        display_collected_financial_data(saved_data)
        
        st.markdown("---")
        
        # Initial setup steps
        st.subheader("Setup Steps")
        st.write("Follow these steps to configure your accounting system:")
        
        st.markdown("---")
        
        # Step 1: Chart of Accounts
        show_step1_accounts()
        
        st.markdown("---")
        
        # Step 2: Sales, Customers and Services
        show_step2_sales()
        
        st.markdown("---")
        
        # Step 3: Vendors and Expenses
        show_step3_vendors_expenses()
            
    except FileNotFoundError:
        # Onboarding not completed
        st.warning("Please complete onboarding first")
        st.write("You need to complete the onboarding process before you can access the setup.")
        st.write("The onboarding helps us understand your business so we can customize the accounting system for your needs.")
        
        st.markdown("---")
        
        # Link to onboarding page
        st.info("Please go to the Onboarding page in the sidebar to get started.")
        
        # Optional: Add a button to navigate to onboarding (note: this won't actually navigate but provides UX)
        if st.button("Go to Onboarding", type="secondary"):
            st.info("Please use the sidebar navigation to go to the Onboarding page.")

def show_step1_accounts():
    """Display Step 1: Chart of Accounts"""
    st.markdown("## Step 1: Chart of Accounts")
    
    # Check if accounts already exist
    accounts_file = os.path.join("anonymized_data", "accounts.csv")
    accounts_exist = False
    
    try:
        existing_accounts = pd.read_csv(accounts_file)
        if len(existing_accounts) > 0:
            accounts_exist = True
            st.success("Chart of accounts already exists!")
            st.dataframe(existing_accounts)
    except:
        pass
    
    # Generate Chart of Accounts button
    if st.button("Generate Chart of Accounts", type="primary", disabled=accounts_exist):
        with st.spinner("Generating chart of accounts using AI..."):
            try:
                # Get comprehensive financial data
                onboarding_data = load_onboarding_data()
                if not onboarding_data:
                    st.error("Financial data not found. Please complete onboarding first.")
                else:
                    # Show what data is being used
                    st.info("Using your complete financial data including all amounts, assets, liabilities, and equity for accurate chart generation...")
                    
                    # Generate accounts using AI with comprehensive data
                    generated_accounts = generate_chart_of_accounts_with_ai(onboarding_data)
                    
                    # Store in session state for editing
                    st.session_state.generated_accounts = generated_accounts
                    st.success(f"Generated {len(generated_accounts)} accounts based on your business profile!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error generating accounts: {str(e)}")
    
    # Show editable table if accounts are generated
    if "generated_accounts" in st.session_state and st.session_state.generated_accounts:
        st.markdown("### Edit Your Chart of Accounts")
        st.write("Review and modify the generated accounts before saving:")
        
        # Convert to DataFrame for editing
        accounts_df = pd.DataFrame(st.session_state.generated_accounts)
        
        # Create editable data editor
        edited_accounts = st.data_editor(
            accounts_df,
            column_config={
                "name": st.column_config.TextColumn("Account Name", required=True),
                "account_type": st.column_config.SelectboxColumn(
                    "Account Type",
                    options=["Asset", "Liability", "Equity", "Income", "Expense"],
                    required=True
                ),
                "account_sub_type": st.column_config.TextColumn("Sub Type", required=True),
                "description": st.column_config.TextColumn("Description", required=True, help="Brief description of what this account tracks"),
                "current_balance": st.column_config.NumberColumn("Current Balance", format="%.2f")
            },
            num_rows="dynamic",
            use_container_width=True,
            key="accounts_editor"
        )
        
        # Save button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Chart of Accounts", type="primary"):
                try:
                    # Convert DataFrame back to list of dicts
                    accounts_to_save = edited_accounts.to_dict('records')
                    
                    # Save to CSV
                    if save_to_csv(accounts_to_save, "accounts.csv"):
                        st.success("Chart of accounts saved successfully to anonymized_data/accounts.csv!")
                        st.info(f"Saved {len(accounts_to_save)} accounts to the file.")
                        # Clear the session state
                        del st.session_state.generated_accounts
                        st.rerun()
                    else:
                        st.error("Failed to save chart of accounts.")
                except Exception as e:
                    st.error(f"Error saving accounts: {str(e)}")
        
        with col2:
            if st.button("Cancel", type="secondary"):
                # Clear the session state without saving
                del st.session_state.generated_accounts
                st.rerun()

def show_step2_sales():
    """Display Step 2: Sales, Customers and Services"""
    st.markdown("## Step 2: Sales, Customers and Services")
    
    # Check if customers and services already exist
    customers_file = os.path.join("anonymized_data", "customers.csv")
    services_file = os.path.join("anonymized_data", "services.csv")
    
    customers_exist = False
    services_exist = False
    
    try:
        existing_customers = pd.read_csv(customers_file)
        if len(existing_customers) > 0:
            customers_exist = True
            st.success("Customers already exist!")
            st.write("**Current Customers:**")
            st.dataframe(existing_customers, use_container_width=True)
    except:
        pass
        
    try:
        existing_services = pd.read_csv(services_file)
        if len(existing_services) > 0:
            services_exist = True
            st.success("Services already exist!")
            st.write("**Current Services:**")
            st.dataframe(existing_services, use_container_width=True)
    except:
        pass
    
    if not customers_exist or not services_exist:
        st.markdown("---")
        st.subheader("Generate Customers and Services")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Customers", type="primary", disabled=customers_exist):
                with st.spinner("Generating customers using AI..."):
                    try:
                        onboarding_data = load_onboarding_data()
                        if not onboarding_data:
                            st.error("Onboarding data not found. Please complete onboarding first.")
                        else:
                            # Load chart of accounts for context
                            accounts_file = os.path.join("anonymized_data", "accounts.csv")
                            chart_of_accounts = []
                            if os.path.exists(accounts_file):
                                accounts_df = pd.read_csv(accounts_file)
                                chart_of_accounts = accounts_df.to_dict('records')
                            
                            generated_customers = generate_customers_with_ai(onboarding_data, chart_of_accounts)
                            st.session_state.generated_customers = generated_customers
                            st.success(f"Generated {len(generated_customers)} customers!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating customers: {str(e)}")
        
        with col2:
            if st.button("Generate Services", type="primary", disabled=services_exist):
                with st.spinner("Generating services using AI..."):
                    try:
                        onboarding_data = load_onboarding_data()
                        if not onboarding_data:
                            st.error("Onboarding data not found. Please complete onboarding first.")
                        else:
                            # Load chart of accounts for context
                            accounts_file = os.path.join("anonymized_data", "accounts.csv")
                            chart_of_accounts = []
                            if os.path.exists(accounts_file):
                                accounts_df = pd.read_csv(accounts_file)
                                chart_of_accounts = accounts_df.to_dict('records')
                            
                            generated_services = generate_services_with_ai(onboarding_data, chart_of_accounts)
                            st.session_state.generated_services = generated_services
                            st.success(f"Generated {len(generated_services)} services!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating services: {str(e)}")
    
    # Show editing tables (customers and services)
    show_customer_editing()
    show_service_editing()

def show_step3_vendors_expenses():
    """Display Step 3: Vendors and Expenses"""
    st.markdown("## Step 3: Vendors and Expenses")
    
    # Check if vendors and expenses already exist
    vendors_file = os.path.join("anonymized_data", "vendors.csv")
    expenses_file = os.path.join("anonymized_data", "expenses.csv")
    
    vendors_exist = False
    expenses_exist = False
    
    try:
        existing_vendors = pd.read_csv(vendors_file)
        if len(existing_vendors) > 0:
            vendors_exist = True
            st.success("Vendors already exist!")
            st.write("**Current Vendors:**")
            st.dataframe(existing_vendors, use_container_width=True)
    except:
        pass
        
    try:
        existing_expenses = pd.read_csv(expenses_file)
        if len(existing_expenses) > 0:
            expenses_exist = True
            st.success("Expenses already exist!")
            st.write("**Current Expenses:**")
            st.dataframe(existing_expenses, use_container_width=True)
    except:
        pass
    
    if not vendors_exist or not expenses_exist:
        st.markdown("---")
        st.subheader("Generate Vendors and Expenses")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Vendors", type="primary", disabled=vendors_exist):
                with st.spinner("Generating vendors using AI..."):
                    try:
                        onboarding_data = load_onboarding_data()
                        if not onboarding_data:
                            st.error("Onboarding data not found. Please complete onboarding first.")
                        else:
                            # Load chart of accounts for context
                            accounts_file = os.path.join("anonymized_data", "accounts.csv")
                            chart_of_accounts = []
                            if os.path.exists(accounts_file):
                                accounts_df = pd.read_csv(accounts_file)
                                chart_of_accounts = accounts_df.to_dict('records')
                            
                            generated_vendors = generate_vendors_with_ai(onboarding_data, chart_of_accounts)
                            st.session_state.generated_vendors = generated_vendors
                            st.success(f"Generated {len(generated_vendors)} vendors!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating vendors: {str(e)}")
        
        with col2:
            if st.button("Generate Expenses", type="primary", disabled=expenses_exist):
                with st.spinner("Generating expenses using AI..."):
                    try:
                        onboarding_data = load_onboarding_data()
                        if not onboarding_data:
                            st.error("Onboarding data not found. Please complete onboarding first.")
                        else:
                            # Load chart of accounts for context
                            accounts_file = os.path.join("anonymized_data", "accounts.csv")
                            chart_of_accounts = []
                            if os.path.exists(accounts_file):
                                accounts_df = pd.read_csv(accounts_file)
                                chart_of_accounts = accounts_df.to_dict('records')
                            
                            generated_expenses = generate_expenses_with_ai(onboarding_data, chart_of_accounts)
                            st.session_state.generated_expenses = generated_expenses
                            st.success(f"Generated {len(generated_expenses)} expense categories!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating expenses: {str(e)}")
    
    # Show editing tables (vendors and expenses)
    show_vendor_editing()
    show_expense_editing()

def show_customer_editing():
    """Show customer editing table if data exists"""
    if "generated_customers" in st.session_state and st.session_state.generated_customers:
        st.markdown("### Edit Your Customers")
        customers_df = pd.DataFrame(st.session_state.generated_customers)
        edited_customers = st.data_editor(customers_df, num_rows="dynamic", use_container_width=True, key="customers_editor")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Customers", type="primary"):
                try:
                    customers_to_save = edited_customers.to_dict('records')
                    if save_to_csv(customers_to_save, "customers.csv"):
                        st.success("Customers saved successfully!")
                        del st.session_state.generated_customers
                        st.rerun()
                    else:
                        st.error("Failed to save customers.")
                except Exception as e:
                    st.error(f"Error saving customers: {str(e)}")
        with col2:
            if st.button("Cancel Customers", type="secondary"):
                del st.session_state.generated_customers
                st.rerun()

def show_service_editing():
    """Show service editing table if data exists"""
    if "generated_services" in st.session_state and st.session_state.generated_services:
        st.markdown("### Edit Your Services")
        services_df = pd.DataFrame(st.session_state.generated_services)
        edited_services = st.data_editor(services_df, num_rows="dynamic", use_container_width=True, key="services_editor")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Services", type="primary"):
                try:
                    services_to_save = edited_services.to_dict('records')
                    if save_to_csv(services_to_save, "services.csv"):
                        st.success("Services saved successfully!")
                        del st.session_state.generated_services
                        st.rerun()
                    else:
                        st.error("Failed to save services.")
                except Exception as e:
                    st.error(f"Error saving services: {str(e)}")
        with col2:
            if st.button("Cancel Services", type="secondary"):
                del st.session_state.generated_services
                st.rerun()

def show_vendor_editing():
    """Show vendor editing table if data exists"""
    if "generated_vendors" in st.session_state and st.session_state.generated_vendors:
        st.markdown("### Edit Your Vendors")
        vendors_df = pd.DataFrame(st.session_state.generated_vendors)
        edited_vendors = st.data_editor(vendors_df, num_rows="dynamic", use_container_width=True, key="vendors_editor")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Vendors", type="primary"):
                try:
                    vendors_to_save = edited_vendors.to_dict('records')
                    if save_to_csv(vendors_to_save, "vendors.csv"):
                        st.success("Vendors saved successfully!")
                        del st.session_state.generated_vendors
                        st.rerun()
                    else:
                        st.error("Failed to save vendors.")
                except Exception as e:
                    st.error(f"Error saving vendors: {str(e)}")
        with col2:
            if st.button("Cancel Vendors", type="secondary"):
                del st.session_state.generated_vendors
                st.rerun()

def show_expense_editing():
    """Show expense editing table if data exists"""
    if "generated_expenses" in st.session_state and st.session_state.generated_expenses:
        st.markdown("### Edit Your Expenses")
        expenses_df = pd.DataFrame(st.session_state.generated_expenses)
        edited_expenses = st.data_editor(expenses_df, num_rows="dynamic", use_container_width=True, key="expenses_editor")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Expenses", type="primary"):
                try:
                    expenses_to_save = edited_expenses.to_dict('records')
                    if save_to_csv(expenses_to_save, "expenses.csv"):
                        st.success("Expenses saved successfully!")
                        del st.session_state.generated_expenses
                        st.rerun()
                    else:
                        st.error("Failed to save expenses.")
                except Exception as e:
                    st.error(f"Error saving expenses: {str(e)}")
        with col2:
            if st.button("Cancel Expenses", type="secondary"):
                del st.session_state.generated_expenses
                st.rerun() 