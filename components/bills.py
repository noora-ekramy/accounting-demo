import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_gemini_model():
    """Initialize and return Gemini model"""
    try:
        # Try different environment variable names and Streamlit secrets
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
            except:
                pass
        
        if not api_key:
            st.error("Google/Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in environment variables.")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini model: {str(e)}")
        return None

def load_bills_data():
    """Load bills data from CSV file"""
    bills_file = os.path.join("anonymized_data", "bills.csv")
    try:
        return pd.read_csv(bills_file)
    except FileNotFoundError:
        # Create empty dataframe with proper columns
        return pd.DataFrame(columns=[
            'bill_id', 'bill_number', 'date', 'due_date', 
            'vendor_id', 'vendor_name', 'expense_id', 'expense_category',
            'total_amount', 'balance_due', 'currency', 'status', 'notes'
        ])

def load_vendors_data():
    """Load vendors data from CSV file"""
    vendors_file = os.path.join("anonymized_data", "vendors.csv")
    try:
        return pd.read_csv(vendors_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=['vendor_id', 'name', 'company_name', 'email'])

def load_expenses_data():
    """Load expenses data from CSV file"""
    expenses_file = os.path.join("anonymized_data", "expenses.csv")
    try:
        return pd.read_csv(expenses_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=['expense_id', 'vendor_or_entity', 'account_used', 'total_amount'])

def save_bill(bill_data):
    """Save a new bill to the CSV file"""
    bills_file = os.path.join("anonymized_data", "bills.csv")
    
    try:
        # Load existing data
        if os.path.exists(bills_file):
            df = pd.read_csv(bills_file)
        else:
            df = pd.DataFrame(columns=[
                'bill_id', 'bill_number', 'date', 'due_date',
                'vendor_id', 'vendor_name', 'expense_id', 'expense_category',
                'total_amount', 'balance_due', 'currency', 'status', 'notes',
                'debit_account', 'debit_amount', 'credit_account', 'credit_amount', 'accounting_explanation'
            ])
        
        # Add new bill
        new_row = pd.DataFrame([bill_data])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to CSV
        os.makedirs("anonymized_data", exist_ok=True)
        df.to_csv(bills_file, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving bill: {str(e)}")
        return False

def generate_bill_with_ai(description, vendors_df, expenses_df):
    """Generate bill details using AI"""
    try:
        model = get_gemini_model()
        if not model:
            return None
        
        # Prepare vendor and expense lists for AI
        vendor_list = []
        for _, vendor in vendors_df.iterrows():
            vendor_list.append(f"{vendor['vendor_id']}: {vendor['name']} ({vendor['company_name']})")
        
        expense_list = []
        for _, expense in expenses_df.iterrows():
            expense_list.append(f"{expense['expense_id']}: {expense['account_used']} - {expense['vendor_or_entity']}")
        
        prompt = f"""
        Based on this bill description, select the most appropriate vendor and expense category from the available options and create proper double-entry bookkeeping accounts:
        
        DESCRIPTION: {description}
        
        AVAILABLE VENDORS:
        {chr(10).join(vendor_list)}
        
        AVAILABLE EXPENSE CATEGORIES:
        {chr(10).join(expense_list)}
        
        DOUBLE-ENTRY ACCOUNTING RULES:
        Every bill MUST affect exactly TWO accounts following these principles:
        
        FOR EXPENSE BILLS (office supplies, utilities, rent, etc.):
        - DEBIT: Expense Account (Office Supplies, Utilities, Rent - increases expense)
        - CREDIT: Accounts Payable or Cash (Liability increases or Asset decreases)
        
        FOR ASSET PURCHASES (equipment, vehicles, inventory):
        - DEBIT: Asset Account (Equipment, Vehicles, Inventory - increases asset value)
        - CREDIT: Accounts Payable or Cash (Liability increases or Asset decreases)
        
        FOR LIABILITY PAYMENTS (loan payments):
        - DEBIT: Loan Payable (Liability account - decreases debt)
        - CREDIT: Cash (Asset account - decreases cash)
        
        Select the most appropriate vendor and expense, calculate realistic amounts, and determine the correct accounts.
        
        Return ONLY a JSON object with this structure:
        {{
            "vendor_id": "VEND001",
            "expense_id": "EXP001",
            "expense_category": "Account name from expense list",
            "total_amount": 0.00,
            "description": "Detailed description of what was purchased",
            "notes": "Additional details about the purchase",
            "accounting_entries": {{
                "debit_account": "Office Supplies Expense",
                "debit_amount": 0.00,
                "credit_account": "Accounts Payable",
                "credit_amount": 0.00,
                "explanation": "Brief explanation of the double-entry logic"
            }}
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse JSON response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        return json.loads(response_text)
        
    except Exception as e:
        st.error(f"Error generating bill with AI: {str(e)}")
        return None

def show_bills_page():
    """Display the bills page"""
    st.title("Bills")
    st.markdown("---")
    
    # Load all required data
    bills_df = load_bills_data()
    vendors_df = load_vendors_data()
    expenses_df = load_expenses_data()
    
    # Check if we have vendors and expenses
    if len(vendors_df) == 0:
        st.error("❌ No vendors found! You must add vendors before creating bills.")
        st.info("🏪 Go to the **Vendors** page to add vendors first.")
        return
    
    if len(expenses_df) == 0:
        st.error("❌ No expense categories found! You must add expenses before creating bills.")
        st.info("💰 Go to the **Expenses** page to add expense categories first.")
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 View Bills", "➕ Create Bill", "🤖 AI Assistant"])
    
    with tab1:
        st.subheader("Bills List")
        
        if len(bills_df) > 0:
            # Search functionality
            search_term = st.text_input("Search bills:", placeholder="Search by bill number, vendor, expense category, or notes...")
            
            # Filter data based on search
            filtered_df = bills_df.copy()
            if search_term:
                mask = (
                    bills_df['bill_number'].astype(str).str.contains(search_term, case=False, na=False) |
                    bills_df['vendor_name'].astype(str).str.contains(search_term, case=False, na=False) |
                    bills_df['notes'].astype(str).str.contains(search_term, case=False, na=False) |
                    bills_df['expense_category'].astype(str).str.contains(search_term, case=False, na=False)
                )
                filtered_df = bills_df[mask]
                st.write(f"Found {len(filtered_df)} matching bills")
            
            # Status filter
            if 'status' in bills_df.columns and not bills_df['status'].isna().all():
                status_options = ['All'] + list(bills_df['status'].dropna().unique())
                selected_status = st.selectbox("Filter by status:", status_options)
                
                if selected_status != 'All':
                    filtered_df = filtered_df[filtered_df['status'] == selected_status]
            
            # Category filter
            if 'expense_category' in bills_df.columns and not bills_df['expense_category'].isna().all():
                category_options = ['All Categories'] + list(bills_df['expense_category'].dropna().unique())
                selected_category = st.selectbox("Filter by category:", category_options)
                
                if selected_category != 'All Categories':
                    filtered_df = filtered_df[filtered_df['expense_category'] == selected_category]
            
            # Display table
            st.dataframe(filtered_df, use_container_width=True)
            
            # Summary metrics
            if len(filtered_df) > 0:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Bills", len(filtered_df))
                with col2:
                    total_amount = filtered_df['total_amount'].sum() if 'total_amount' in filtered_df.columns else 0
                    st.metric("Total Amount", f"${total_amount:,.2f}")
                with col3:
                    avg_amount = filtered_df['total_amount'].mean() if 'total_amount' in filtered_df.columns and len(filtered_df) > 0 else 0
                    st.metric("Average Amount", f"${avg_amount:,.2f}")
                with col4:
                    balance_due = filtered_df['balance_due'].sum() if 'balance_due' in filtered_df.columns else 0
                    st.metric("Outstanding", f"${balance_due:,.2f}")
                
                # Category breakdown
                if 'expense_category' in filtered_df.columns and len(filtered_df) > 0:
                    st.markdown("---")
                    st.subheader("Expense Categories")
                    category_amounts = filtered_df.groupby('expense_category')['total_amount'].sum().sort_values(ascending=False)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Spending by Category:**")
                        for category, amount in category_amounts.head(5).items():
                            st.write(f"• {category}: ${amount:,.2f}")
                    
                    with col2:
                        category_counts = filtered_df['expense_category'].value_counts()
                        st.write("**Bills by Category:**")
                        for category, count in category_counts.head(5).items():
                            st.write(f"• {category}: {count} bills")
        else:
            st.info("No bills found. Create your first bill using the tabs above!")
            
            # Show empty table structure
            st.subheader("Bills Table Structure")
            empty_df = pd.DataFrame(columns=[
                'Bill #', 'Date', 'Due Date', 'Vendor', 'Expense Category',
                'Amount', 'Balance Due', 'Status', 'Notes'
            ])
            st.dataframe(empty_df, use_container_width=True)
    
    with tab2:
        st.subheader("Create New Bill")
        
        with st.form("create_bill_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Vendor selection (mandatory)
                vendor_options = [f"{row['vendor_id']}: {row['name']} ({row['company_name']})" 
                                for _, row in vendors_df.iterrows()]
                selected_vendor_idx = st.selectbox("Select Vendor*", range(len(vendor_options)), 
                                                 format_func=lambda x: vendor_options[x])
                selected_vendor = vendors_df.iloc[selected_vendor_idx]
                
                bill_date = st.date_input("Bill Date", value=datetime.now().date())
                due_date = st.date_input("Due Date", value=datetime.now().date() + timedelta(days=30))
                
            with col2:
                # Expense category selection (mandatory)
                expense_options = [f"{row['expense_id']}: {row['account_used']} (Related: {row['vendor_or_entity']})" 
                                 for _, row in expenses_df.iterrows()]
                selected_expense_idx = st.selectbox("Select Expense Category*", range(len(expense_options)), 
                                                  format_func=lambda x: expense_options[x])
                selected_expense = expenses_df.iloc[selected_expense_idx]
                
                total_amount = st.number_input("Total Amount ($)*", min_value=0.01, step=0.01, format="%.2f")
            
            # Double-Entry Accounting Display
            if total_amount > 0:
                st.markdown("---")
                st.subheader("Double-Entry Bookkeeping")
                col3, col4 = st.columns(2)
                with col3:
                    st.write("**DEBIT:**")
                    st.write(f"{selected_expense['account_used']}: ${total_amount:.2f}")
                    st.caption("Expense increases - Money spent on business")
                with col4:
                    st.write("**CREDIT:**")
                    st.write(f"Accounts Payable: ${total_amount:.2f}")
                    st.caption("Liability increases - Amount owed to vendor")
            
            description = st.text_area("Description*", placeholder="Describe what was purchased or services received")
            notes = st.text_area("Additional Notes", placeholder="Any additional information about this bill")
            
            submit_button = st.form_submit_button("Create Bill", type="primary", use_container_width=True)
            
            if submit_button:
                if not description or total_amount <= 0:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    # Generate bill number
                    bill_number = f"BILL-{datetime.now().strftime('%Y%m%d')}-{len(bills_df) + 1:03d}"
                    
                    # Create bill data with double-entry accounting
                    bill_data = {
                        'bill_id': len(bills_df) + 1,
                        'bill_number': bill_number,
                        'date': bill_date.strftime('%Y-%m-%d'),
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'vendor_id': selected_vendor['vendor_id'],
                        'vendor_name': f"{selected_vendor['name']} ({selected_vendor['company_name']})",
                        'expense_id': selected_expense['expense_id'],
                        'expense_category': selected_expense['account_used'],
                        'total_amount': total_amount,
                        'balance_due': total_amount,  # Initially, full amount is due
                        'currency': 'USD',
                        'status': 'Pending',
                        'notes': f"{description}. {notes}".strip('. '),
                        'debit_account': selected_expense['account_used'],
                        'debit_amount': total_amount,
                        'credit_account': 'Accounts Payable',
                        'credit_amount': total_amount,
                        'accounting_explanation': f'Bill from {selected_vendor["name"]} - increases expenses and payables'
                    }
                    
                    if save_bill(bill_data):
                        st.success(f"Bill {bill_number} created successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to create bill. Please try again.")
    
    with tab3:
        st.subheader("AI Bill Assistant")
        st.write("Describe your expense or purchase, and AI will help match it to existing vendors and expense categories.")
        
        with st.form("ai_bill_form"):
            ai_description = st.text_area(
                "Describe what you purchased or need to pay for:",
                placeholder="Example: Received monthly bill from Ram Electronics for hardware chips, need to pay Dell for new laptops",
                height=100
            )
            
            generate_button = st.form_submit_button("Generate Bill Details", type="primary", use_container_width=True)
            
            if generate_button:
                if not ai_description:
                    st.error("Please describe the expense or purchase")
                else:
                    with st.spinner("AI is matching your description to vendors and expenses..."):
                        ai_bill = generate_bill_with_ai(ai_description, vendors_df, expenses_df)
                        
                        if ai_bill:
                            st.success("AI matched your description to existing vendors and expenses!")
                            
                            # Find the matching vendor and expense
                            try:
                                matched_vendor = vendors_df[vendors_df['vendor_id'] == ai_bill['vendor_id']].iloc[0]
                                matched_expense = expenses_df[expenses_df['expense_id'] == ai_bill['expense_id']].iloc[0]
                                
                                # Show generated details in editable form
                                st.subheader("Review & Edit AI Suggestions")
                                
                                with st.form("ai_generated_bill"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Show AI selected vendor
                                        vendor_options = [f"{row['vendor_id']}: {row['name']} ({row['company_name']})" 
                                                        for _, row in vendors_df.iterrows()]
                                        default_vendor_idx = vendors_df[vendors_df['vendor_id'] == ai_bill['vendor_id']].index[0]
                                        selected_vendor_idx = st.selectbox("Vendor (AI Selected)", range(len(vendor_options)), 
                                                                         index=default_vendor_idx,
                                                                         format_func=lambda x: vendor_options[x])
                                        selected_vendor = vendors_df.iloc[selected_vendor_idx]
                                        
                                        bill_date = st.date_input("Bill Date", value=datetime.now().date())
                                        due_date = st.date_input("Due Date", value=datetime.now().date() + timedelta(days=30))
                                    
                                    with col2:
                                        # Show AI selected expense
                                        expense_options = [f"{row['expense_id']}: {row['account_used']} (Related: {row['vendor_or_entity']})" 
                                                         for _, row in expenses_df.iterrows()]
                                        default_expense_idx = expenses_df[expenses_df['expense_id'] == ai_bill['expense_id']].index[0]
                                        selected_expense_idx = st.selectbox("Expense Category (AI Selected)", range(len(expense_options)), 
                                                                          index=default_expense_idx,
                                                                          format_func=lambda x: expense_options[x])
                                        selected_expense = expenses_df.iloc[selected_expense_idx]
                                        
                                        total_amount = st.number_input("Total Amount ($)", value=ai_bill.get('total_amount', 0.0), min_value=0.01, step=0.01, format="%.2f")
                                    
                                    description = st.text_area("Description", value=ai_bill.get('description', ''))
                                    notes = st.text_area("Additional Notes", value=ai_bill.get('notes', ''))
                                    
                                    create_ai_bill = st.form_submit_button("Create Bill", type="primary", use_container_width=True)
                                    
                                    if create_ai_bill:
                                        if not description or total_amount <= 0:
                                            st.error("Please fill in all required fields")
                                        else:
                                            # Generate bill number
                                            bill_number = f"BILL-{datetime.now().strftime('%Y%m%d')}-{len(bills_df) + 1:03d}"
                                            
                                            # Create bill data
                                            bill_data = {
                                                'bill_id': len(bills_df) + 1,
                                                'bill_number': bill_number,
                                                'date': bill_date.strftime('%Y-%m-%d'),
                                                'due_date': due_date.strftime('%Y-%m-%d'),
                                                'vendor_id': selected_vendor['vendor_id'],
                                                'vendor_name': f"{selected_vendor['name']} ({selected_vendor['company_name']})",
                                                'expense_id': selected_expense['expense_id'],
                                                'expense_category': selected_expense['account_used'],
                                                'total_amount': total_amount,
                                                'balance_due': total_amount,
                                                'currency': 'USD',
                                                'status': 'Pending',
                                                'notes': f"{description}. {notes}".strip('. ')
                                            }
                                            
                                            if save_bill(bill_data):
                                                st.success(f"AI-generated bill {bill_number} created successfully!")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error("Failed to create bill. Please try again.")
                            
                            except (IndexError, KeyError):
                                st.error("AI couldn't find matching vendor or expense. Please check your description or create manually.")
                        else:
                            st.error("Failed to generate bill details. Please try again or create manually.")
        
        # AI Tips
        st.markdown("---")
        st.subheader("💡 AI Assistant Tips")
        st.markdown(f"""
        **Available Vendors:** {len(vendors_df)} vendors
        **Available Expense Categories:** {len(expenses_df)} expense types
        
        **For best results, mention:**
        - **Vendor name or company** (e.g., "Ram Electronics", "Dell Technologies")
        - **Type of expense** that matches your existing expense categories
        - **What was purchased** or the service received
        
        **Example descriptions:**
        - "Monthly payment to Ram Electronics for hardware chips"
        - "Received bill from Dell for new development laptops"
        - "Payment due to vendor for office equipment purchase"
        """) 