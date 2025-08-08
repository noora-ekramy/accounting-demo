import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from setup_logic import (
    load_onboarding_data, 
    generate_chart_of_accounts_with_ai, 
    generate_customers_with_ai,
    generate_services_with_ai,
    generate_vendors_with_ai,
    generate_expenses_with_ai,
    save_to_csv
)

# Fixed asset depreciation table
ASSET_DEPRECIATION_YEARS = {
    "Office Furniture": 7,
    "Office Equipment": 5,
    "Computers & Peripherals": 5,
    "Software (Purchased)": 3,
    "Vehicles": 5,
    "Pharmacy Equipment": 7,
    "Manufacturing Equipment": 10,
    "Leasehold Improvements": 15,
    "Commercial Building": 39,
    "Residential Building": 27.5,
    "Land Improvements": 15,
    "Security Systems": 7,
    "Medical Equipment": 7,
    "Refrigeration Units": 7,
    "POS Systems": 5,
    "Signage (Exterior)": 10
}

def calculate_depreciation(cost, purchase_date, useful_life_years, reporting_date="2024-12-31"):
    """Calculate accumulated depreciation using straight-line method"""
    try:
        purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
        report = datetime.strptime(reporting_date, "%Y-%m-%d")
        
        # Calculate months used
        months_used = (report.year - purchase.year) * 12 + (report.month - purchase.month)
        if report.day >= purchase.day:
            months_used += 1
        
        # Calculate depreciation
        total_months = useful_life_years * 12
        monthly_depreciation = cost / total_months
        accumulated_depreciation = min(monthly_depreciation * months_used, cost)
        
        return round(accumulated_depreciation, 2)
    except:
        return 0.0

def count_completed_fields(financial_data):
    """Count completed fields in financial data"""
    count = 0
    
    # Count general_info fields (3 fields)
    general_info = financial_data.get("general_info", {})
    for value in general_info.values():
        if value and str(value).strip():
            count += 1
    
    # Count business_questions fields (3 fields)
    business_questions = financial_data.get("business_questions", {})
    for key, value in business_questions.items():
        if key != "locked" and value and str(value).strip():
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
    
    # Count equity fields (3 fields - removed preferred/treasury stock)
    equity = financial_data.get("equity", {})
    required_equity_fields = ["common_stock", "retained_earnings", "additional_paid_in_capital"]
    for field in required_equity_fields:
        if equity.get(field) and str(equity[field]).strip():
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
    
    # Upload Section - Enhanced
    st.subheader("Data Import Options")
    st.write("Skip manual entry by uploading existing financial data:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Trial Balance Upload**")
        st.write("Upload from QuickBooks, Xero, or Excel")
        trial_balance_file = st.file_uploader(
            "Choose CSV/Excel file",
            type=['csv', 'xlsx'],
            help="Required columns: Account Name, Type (Asset/Liability/Equity/Income/Expense), Debit, Credit",
            key="trial_balance"
        )
        if trial_balance_file:
            process_trial_balance_upload(trial_balance_file)
    
    with col2:
        st.markdown("**Bank Statement Upload**")
        st.write("Auto-extract cash and loan balances")
        bank_statement_file = st.file_uploader(
            "Choose CSV/PDF file",
            type=['csv', 'pdf'],
            help="We'll extract ending cash balance and loan information",
            key="bank_statement"
        )
        if bank_statement_file:
            process_bank_statement_upload(bank_statement_file)
    
    with col3:
        st.markdown("**Loan Documents Upload**")
        st.write("Extract rates, terms, balances")
        loan_docs_file = st.file_uploader(
            "Choose loan documents",
            type=['csv', 'xlsx', 'pdf'],
            help="Amortization schedules, promissory notes, loan statements",
            key="loan_docs"
        )
        if loan_docs_file:
            process_loan_documents_upload(loan_docs_file)
    
    st.markdown("---")
    
    # Fixed Asset Depreciation Helper - Enhanced
    st.subheader("Fixed Asset & Depreciation Helper")
    with st.expander("Add Fixed Assets with Auto-Depreciation", expanded=False):
        show_enhanced_fixed_asset_helper()
    
    st.markdown("---")
    
    # Check if onboarding is completed
    onboarding_file = "onboarding_responses.json"
    try:
        with open(onboarding_file, 'r') as f:
            saved_data = json.load(f)
        
        # Check if it's the new format with required fields
        if isinstance(saved_data, dict) and any(key in saved_data for key in ["general_info", "assets", "liabilities", "equity"]):
            completed_fields = count_completed_fields(saved_data)
            
            if completed_fields < 25:  # Updated to new field count
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

def process_trial_balance_upload(uploaded_file):
    """Process uploaded trial balance file"""
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write("**Preview of uploaded trial balance:**")
        st.dataframe(df.head())
        
        # Check required columns
        required_cols = ['Account Name', 'Type', 'Debit', 'Credit']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            st.write("Required columns: Account Name, Type (Asset/Liability/Equity/Income/Expense), Debit, Credit")
        else:
            if st.button("Import Trial Balance"):
                # Convert to chart of accounts format
                accounts_data = []
                for _, row in df.iterrows():
                    balance = float(row.get('Debit', 0) or 0) - float(row.get('Credit', 0) or 0)
                    accounts_data.append({
                        'name': row['Account Name'],
                        'account_type': row['Type'],
                        'account_sub_type': f"{row['Type']} Account",
                        'description': f"Imported from trial balance - {row['Account Name']}",
                        'current_balance': balance
                    })
                
                # Save to CSV
                if save_to_csv(accounts_data, "accounts.csv"):
                    st.success(f"Successfully imported {len(accounts_data)} accounts from trial balance!")
                else:
                    st.error("Failed to save imported accounts.")
                    
    except Exception as e:
        st.error(f"Error processing trial balance: {e}")

def process_bank_statement_upload(uploaded_file):
    """Process uploaded bank statement file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.write("**Bank statement preview:**")
            st.dataframe(df.head())
            
            # Try to find ending balance
            balance_keywords = ['balance', 'ending', 'total', 'amount']
            ending_balance = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in balance_keywords):
                    try:
                        ending_balance = df[col].iloc[-1]  # Last row
                        break
                    except:
                        continue
            
            if ending_balance:
                st.success(f"Found ending balance: ${ending_balance:,.2f}")
                if st.button("Import Cash Balance"):
                    # Update cash in session state if exists
                    if "financial_data" in st.session_state:
                        st.session_state.financial_data.setdefault("assets", {})["cash"] = str(int(ending_balance))
                        st.success("Cash balance updated in your financial data!")
            else:
                st.warning("Could not automatically detect ending balance. Please enter manually.")
        else:
            st.info("PDF processing requires additional setup. Please convert to CSV for now.")
            
    except Exception as e:
        st.error(f"Error processing bank statement: {e}")

def process_loan_documents_upload(uploaded_file):
    """Process uploaded loan documents"""
    try:
        if uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.xlsx'):
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("**Loan document preview:**")
            st.dataframe(df.head())
            
            # Try to extract loan information
            loan_info = extract_loan_info_from_data(df)
            if loan_info:
                st.success("Extracted loan information:")
                for key, value in loan_info.items():
                    st.write(f"**{key}:** {value}")
                
                if st.button("Import Loan Data"):
                    # Add to financial data
                    liabilities = st.session_state.get('financial_data', {}).get('liabilities', {})
                    
                    # Split current vs long-term based on maturity
                    if loan_info.get('remaining_term_months', 12) <= 12:
                        liabilities['short_term_loans'] = str(int(loan_info.get('current_balance', 0)))
                    else:
                        current_portion = loan_info.get('current_balance', 0) * 0.1  # Estimate 10% current
                        liabilities['short_term_loans'] = str(int(current_portion))
                        liabilities['long_term_debt'] = str(int(loan_info.get('current_balance', 0) - current_portion))
                    
                    st.success("Loan data imported successfully!")
        else:
            st.info("PDF loan document processing requires OCR. Please convert to CSV/Excel or enter manually.")
            
    except Exception as e:
        st.error(f"Error processing loan documents: {e}")

def extract_loan_info_from_data(df):
    """Extract loan information from uploaded data"""
    loan_info = {}
    
    try:
        # Look for common loan data patterns
        balance_keywords = ['balance', 'principal', 'outstanding', 'amount']
        rate_keywords = ['rate', 'interest', 'apr']
        term_keywords = ['term', 'months', 'maturity', 'years']
        payment_keywords = ['payment', 'monthly', 'pmt']
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Extract balance
            if any(keyword in col_lower for keyword in balance_keywords):
                try:
                    loan_info['current_balance'] = float(df[col].iloc[-1])  # Last row (most recent)
                except:
                    pass
            
            # Extract interest rate
            if any(keyword in col_lower for keyword in rate_keywords):
                try:
                    rate = float(df[col].iloc[0])  # First row (rate usually constant)
                    loan_info['interest_rate'] = f"{rate}%" if rate < 1 else f"{rate/100}%"
                except:
                    pass
            
            # Extract term
            if any(keyword in col_lower for keyword in term_keywords):
                try:
                    loan_info['remaining_term_months'] = int(df[col].iloc[-1])
                except:
                    pass
            
            # Extract payment
            if any(keyword in col_lower for keyword in payment_keywords):
                try:
                    loan_info['monthly_payment'] = float(df[col].iloc[-1])
                except:
                    pass
        
        return loan_info if loan_info else None
        
    except Exception as e:
        print(f"Error extracting loan info: {e}")
        return None

def show_enhanced_fixed_asset_helper():
    """Enhanced fixed asset helper with depreciation overrides"""
    st.markdown("**Add Fixed Assets with Customizable Depreciation**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        asset_name = st.text_input("Asset Name:", placeholder="e.g., Dell Laptop", key="enhanced_asset_name")
        asset_type = st.selectbox("Asset Type:", list(ASSET_DEPRECIATION_YEARS.keys()), key="enhanced_asset_type")
        purchase_cost = st.number_input("Purchase Cost ($):", min_value=0.0, format="%.2f", key="enhanced_purchase_cost")
        purchase_date = st.date_input("Purchase Date:", key="enhanced_purchase_date")
        
        # Get reporting date dynamically
        reporting_date = "2024-12-31"  # Default, can be made dynamic
        if os.path.exists("onboarding_responses.json"):
            try:
                with open("onboarding_responses.json", 'r') as f:
                    data = json.load(f)
                    reporting_date = data.get("general_info", {}).get("reporting_date", "2024-12-31")
                    if "/" in reporting_date:  # Convert MM/DD/YYYY to YYYY-MM-DD
                        parts = reporting_date.split("/")
                        if len(parts) == 3:
                            reporting_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            except:
                pass
    
    with col2:
        # AI suggested values with override capability
        suggested_life = ASSET_DEPRECIATION_YEARS.get(asset_type, 5)
        useful_life = st.number_input("Useful Life (years):", value=suggested_life, min_value=1, key="enhanced_useful_life")
        
        dep_method = st.selectbox("Depreciation Method:", 
                                 ["Straight-Line", "MACRS", "Double-Declining", "Units of Production"], 
                                 key="enhanced_dep_method")
        
        financed_amount = st.number_input("Amount Financed ($):", min_value=0.0, format="%.2f", key="enhanced_financed")
        current_loan_balance = st.number_input("Outstanding Loan Balance ($):", min_value=0.0, format="%.2f", key="enhanced_loan_balance")
        
        # Calculate and show depreciation with override option
        if purchase_cost > 0 and purchase_date:
            if dep_method == "Straight-Line":
                auto_accumulated_dep = calculate_depreciation(purchase_cost, purchase_date.strftime("%Y-%m-%d"), useful_life, reporting_date)
            else:
                # For other methods, use straight-line as default calculation
                auto_accumulated_dep = calculate_depreciation(purchase_cost, purchase_date.strftime("%Y-%m-%d"), useful_life, reporting_date)
            
            st.markdown("**AI Calculated Values:**")
            st.info(f"Suggested Accumulated Depreciation: ${auto_accumulated_dep:,.2f}")
            
            # Allow override
            override_depreciation = st.checkbox("Override depreciation calculation", key="override_dep")
            if override_depreciation:
                accumulated_dep = st.number_input("Custom Accumulated Depreciation ($):", 
                                                value=auto_accumulated_dep, 
                                                min_value=0.0, 
                                                max_value=purchase_cost,
                                                format="%.2f", 
                                                key="custom_accumulated_dep")
            else:
                accumulated_dep = auto_accumulated_dep
            
            net_book_value = purchase_cost - accumulated_dep
            st.metric("Net Book Value", f"${net_book_value:,.2f}")
    
    # Asset notes/description
    asset_notes = st.text_area("Asset Notes/Description:", 
                              placeholder="Additional details about the asset...", 
                              key="enhanced_asset_notes")
    
    if st.button("Add Enhanced Fixed Asset", key="add_enhanced_asset") and asset_name and purchase_cost > 0:
        # Create comprehensive asset entry
        asset_entry = {
            "name": asset_name,
            "type": asset_type,
            "purchase_cost": purchase_cost,
            "purchase_date": purchase_date.strftime("%Y-%m-%d"),
            "useful_life_years": useful_life,
            "depreciation_method": dep_method,
            "accumulated_depreciation": accumulated_dep,
            "net_book_value": net_book_value,
            "financed_amount": financed_amount,
            "current_loan_balance": current_loan_balance,
            "notes": asset_notes,
            "reporting_date": reporting_date,
            "depreciation_overridden": override_depreciation if 'override_depreciation' in locals() else False
        }
        
        # Save to session state
        if "enhanced_fixed_assets" not in st.session_state:
            st.session_state.enhanced_fixed_assets = []
        st.session_state.enhanced_fixed_assets.append(asset_entry)
        
        st.success(f"Added {asset_name} with ${accumulated_dep:,.2f} accumulated depreciation ({dep_method})")
        
        # Show loan liability suggestion if applicable
        if current_loan_balance > 0:
            if current_loan_balance <= purchase_cost * 0.1:  # If loan is small, suggest short-term
                st.info(f"Consider adding ${current_loan_balance:,.2f} as Short-term Loans (current portion)")
            else:
                current_portion = current_loan_balance * 0.1  # Estimate 10% current
                long_term_portion = current_loan_balance - current_portion
                st.info(f"Consider splitting the loan: ${current_portion:,.2f} Short-term, ${long_term_portion:,.2f} Long-term")
    
    # Show existing enhanced assets with edit capability
    if "enhanced_fixed_assets" in st.session_state and st.session_state.enhanced_fixed_assets:
        st.markdown("---")
        st.markdown("**Your Fixed Assets:**")
        
        # Create editable dataframe
        assets_df = pd.DataFrame(st.session_state.enhanced_fixed_assets)
        
        # Show key columns in a nice format
        display_cols = ['name', 'type', 'purchase_cost', 'accumulated_depreciation', 'net_book_value', 'depreciation_method']
        if not assets_df.empty:
            st.dataframe(assets_df[display_cols], use_container_width=True)
            
            # Edit mode
            if st.checkbox("Edit Mode", key="edit_assets_mode"):
                asset_to_edit = st.selectbox("Select asset to edit:", 
                                           [f"{i}: {asset['name']}" for i, asset in enumerate(st.session_state.enhanced_fixed_assets)],
                                           key="select_asset_edit")
                
                if asset_to_edit:
                    asset_index = int(asset_to_edit.split(":")[0])
                    asset = st.session_state.enhanced_fixed_assets[asset_index]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_accumulated_dep = st.number_input("Edit Accumulated Depreciation:", 
                                                            value=asset['accumulated_depreciation'],
                                                            min_value=0.0,
                                                            max_value=asset['purchase_cost'],
                                                            format="%.2f",
                                                            key="edit_accum_dep")
                    with col2:
                        new_useful_life = st.number_input("Edit Useful Life (years):", 
                                                        value=asset['useful_life_years'],
                                                        min_value=1,
                                                        key="edit_useful_life")
                    
                    if st.button("Update Asset", key="update_asset"):
                        st.session_state.enhanced_fixed_assets[asset_index]['accumulated_depreciation'] = new_accumulated_dep
                        st.session_state.enhanced_fixed_assets[asset_index]['useful_life_years'] = new_useful_life
                        st.session_state.enhanced_fixed_assets[asset_index]['net_book_value'] = asset['purchase_cost'] - new_accumulated_dep
                        st.session_state.enhanced_fixed_assets[asset_index]['depreciation_overridden'] = True
                        st.success("Asset updated successfully!")
                        st.rerun()
        
        if st.button("Save All Fixed Assets to CSV", key="save_enhanced_assets"):
            if save_to_csv(st.session_state.enhanced_fixed_assets, "fixed_assets.csv"):
                st.success("Enhanced fixed assets saved successfully!")

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