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

def load_invoices_data():
    """Load invoices data from CSV file"""
    invoices_file = os.path.join("anonymized_data", "invoices.csv")
    try:
        return pd.read_csv(invoices_file)
    except FileNotFoundError:
        # Create empty dataframe with proper columns
        return pd.DataFrame(columns=[
            'invoice_id', 'invoice_number', 'date', 'due_date', 
            'customer_id', 'customer_name', 'service_id', 'service_name',
            'total_amount', 'balance_due', 'tax_amount', 'payment_reference', 
            'status', 'notes'
        ])

def load_customers_data():
    """Load customers data from CSV file"""
    customers_file = os.path.join("anonymized_data", "customers.csv")
    try:
        return pd.read_csv(customers_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=['customer_id', 'name', 'company_name', 'email'])

def load_services_data():
    """Load services data from CSV file"""
    services_file = os.path.join("anonymized_data", "services.csv")
    try:
        return pd.read_csv(services_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=['name', 'description', 'type', 'unit_price', 'taxable'])

def save_invoice(invoice_data):
    """Save a new invoice to the CSV file"""
    invoices_file = os.path.join("anonymized_data", "invoices.csv")
    
    try:
        # Load existing data
        if os.path.exists(invoices_file):
            df = pd.read_csv(invoices_file)
        else:
            df = pd.DataFrame(columns=[
                'invoice_id', 'invoice_number', 'date', 'due_date',
                'customer_id', 'customer_name', 'service_id', 'service_name',
                'total_amount', 'balance_due', 'tax_amount', 'payment_reference',
                'status', 'notes', 'debit_account', 'debit_amount', 
                'credit_account', 'credit_amount', 'accounting_explanation'
            ])
        
        # Add new invoice
        new_row = pd.DataFrame([invoice_data])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to CSV
        os.makedirs("anonymized_data", exist_ok=True)
        df.to_csv(invoices_file, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving invoice: {str(e)}")
        return False

def generate_invoice_with_ai(description, customers_df, services_df):
    """Generate invoice details using AI"""
    try:
        model = get_gemini_model()
        if not model:
            return None
        
        # Prepare customer and service lists for AI
        customer_list = []
        for _, customer in customers_df.iterrows():
            customer_list.append(f"{customer['customer_id']}: {customer['name']} ({customer['company_name']})")
        
        service_list = []
        for _, service in services_df.iterrows():
            service_list.append(f"{service['name']}: {service['description']} - ${service['unit_price']}")
        
        prompt = f"""
        Based on this invoice description, select the most appropriate customer and service from the available options and create proper double-entry bookkeeping accounts:
        
        DESCRIPTION: {description}
        
        AVAILABLE CUSTOMERS:
        {chr(10).join(customer_list)}
        
        AVAILABLE SERVICES:
        {chr(10).join(service_list)}
        
        DOUBLE-ENTRY ACCOUNTING RULES:
        Every invoice MUST affect exactly TWO accounts following these principles:
        
        FOR SALES/REVENUE INVOICES:
        - DEBIT: Accounts Receivable (Asset account - increases when customer owes money)
        - CREDIT: Revenue/Sales (Revenue account - increases when earning income)
        
        FOR ASSET PURCHASES (if buying equipment/inventory):
        - DEBIT: Asset Account (Equipment, Inventory, etc. - increases asset value)
        - CREDIT: Accounts Payable or Cash (Liability decreases or Asset decreases)
        
        Select the most appropriate customer and service, calculate realistic amounts, and determine the correct accounts.
        
        Return ONLY a JSON object with this structure:
        {{
            "customer_id": "CUST001",
            "service_name": "Exact service name from list",
            "quantity": 1,
            "unit_price": 0.00,
            "subtotal": 0.00,
            "tax_amount": 0.00,
            "total_amount": 0.00,
            "notes": "Additional details about the service delivery",
            "accounting_entries": {{
                "debit_account": "Accounts Receivable",
                "debit_amount": 0.00,
                "credit_account": "Service Revenue",
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
        st.error(f"Error generating invoice with AI: {str(e)}")
        return None

def show_invoices_page():
    """Display the invoices page"""
    st.title("Invoices")
    st.markdown("---")
    
    # Load all required data
    invoices_df = load_invoices_data()
    customers_df = load_customers_data()
    services_df = load_services_data()
    
    # Check if we have customers and services
    if len(customers_df) == 0:
        st.error("❌ No customers found! You must add customers before creating invoices.")
        st.info("👥 Go to the **Customers** page to add customers first.")
        return
    
    if len(services_df) == 0:
        st.error("❌ No services found! You must add services before creating invoices.")
        st.info("🛠️ Go to the **Services** page to add services first.")
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 View Invoices", "➕ Create Invoice", "🤖 AI Assistant"])
    
    with tab1:
        st.subheader("Invoice List")
        
        if len(invoices_df) > 0:
            # Search functionality
            search_term = st.text_input("Search invoices:", placeholder="Search by invoice number, customer, service, or notes...")
            
            # Filter data based on search
            filtered_df = invoices_df.copy()
            if search_term:
                mask = (
                    invoices_df['invoice_number'].astype(str).str.contains(search_term, case=False, na=False) |
                    invoices_df['customer_name'].astype(str).str.contains(search_term, case=False, na=False) |
                    invoices_df['service_name'].astype(str).str.contains(search_term, case=False, na=False) |
                    invoices_df['notes'].astype(str).str.contains(search_term, case=False, na=False)
                )
                filtered_df = invoices_df[mask]
                st.write(f"Found {len(filtered_df)} matching invoices")
            
            # Status filter
            if 'status' in invoices_df.columns and not invoices_df['status'].isna().all():
                status_options = ['All'] + list(invoices_df['status'].dropna().unique())
                selected_status = st.selectbox("Filter by status:", status_options)
                
                if selected_status != 'All':
                    filtered_df = filtered_df[filtered_df['status'] == selected_status]
            
            # Display table
            st.dataframe(filtered_df, use_container_width=True)
            
            # Summary metrics
            if len(filtered_df) > 0:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Invoices", len(filtered_df))
                with col2:
                    total_amount = filtered_df['total_amount'].sum() if 'total_amount' in filtered_df.columns else 0
                    st.metric("Total Amount", f"${total_amount:,.2f}")
                with col3:
                    avg_amount = filtered_df['total_amount'].mean() if 'total_amount' in filtered_df.columns and len(filtered_df) > 0 else 0
                    st.metric("Average Amount", f"${avg_amount:,.2f}")
                with col4:
                    balance_due = filtered_df['balance_due'].sum() if 'balance_due' in filtered_df.columns else 0
                    st.metric("Outstanding", f"${balance_due:,.2f}")
        else:
            st.info("No invoices found. Create your first invoice using the tabs above!")
            
            # Show empty table structure
            st.subheader("Invoice Table Structure")
            empty_df = pd.DataFrame(columns=[
                'Invoice #', 'Date', 'Due Date', 'Customer', 'Service',
                'Amount', 'Balance Due', 'Status', 'Notes'
            ])
            st.dataframe(empty_df, use_container_width=True)
    
    with tab2:
        st.subheader("Create New Invoice")
        
        with st.form("create_invoice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Customer selection (mandatory)
                customer_options = [f"{row['customer_id']}: {row['name']} ({row['company_name']})" 
                                  for _, row in customers_df.iterrows()]
                selected_customer_idx = st.selectbox("Select Customer*", range(len(customer_options)), 
                                                   format_func=lambda x: customer_options[x])
                selected_customer = customers_df.iloc[selected_customer_idx]
                
                invoice_date = st.date_input("Invoice Date", value=datetime.now().date())
                due_date = st.date_input("Due Date", value=datetime.now().date() + timedelta(days=30))
                
            with col2:
                # Service selection (mandatory)
                service_options = [f"{row['name']}: {row['description'][:50]}... - ${row['unit_price']}" 
                                 for _, row in services_df.iterrows()]
                selected_service_idx = st.selectbox("Select Service*", range(len(service_options)), 
                                                  format_func=lambda x: service_options[x])
                selected_service = services_df.iloc[selected_service_idx]
                
                quantity = st.number_input("Quantity*", min_value=1, value=1, step=1)
                unit_price = st.number_input("Unit Price ($)", value=float(selected_service['unit_price']), step=0.01, format="%.2f")
            
            # Calculate amounts
            subtotal = quantity * unit_price
            is_taxable = str(selected_service.get('taxable', 'no')).lower() == 'yes'
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, 
                                     value=8.5 if is_taxable else 0.0, step=0.1)
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            st.write(f"**Subtotal: ${subtotal:.2f}**")
            st.write(f"**Tax Amount: ${tax_amount:.2f}**")
            st.write(f"**Total Amount: ${total_amount:.2f}**")
            
            # Double-Entry Accounting Display
            st.markdown("---")
            st.subheader("Double-Entry Bookkeeping")
            col3, col4 = st.columns(2)
            with col3:
                st.write("**DEBIT:**")
                st.write(f"Accounts Receivable: ${total_amount:.2f}")
                st.caption("Asset increases - Customer owes money")
            with col4:
                st.write("**CREDIT:**")
                st.write(f"Service Revenue: ${total_amount:.2f}")
                st.caption("Revenue increases - Earning income")
            
            notes = st.text_area("Additional Notes", placeholder="Any additional information about this invoice")
            
            submit_button = st.form_submit_button("Create Invoice", type="primary", use_container_width=True)
            
            if submit_button:
                # Generate invoice number
                invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{len(invoices_df) + 1:03d}"
                
                # Create invoice data with double-entry accounting
                invoice_data = {
                    'invoice_id': len(invoices_df) + 1,
                    'invoice_number': invoice_number,
                    'date': invoice_date.strftime('%Y-%m-%d'),
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'customer_id': selected_customer['customer_id'],
                    'customer_name': f"{selected_customer['name']} ({selected_customer['company_name']})",
                    'service_id': f"SRV-{selected_service_idx + 1:03d}",  # Generate service ID
                    'service_name': selected_service['name'],
                    'total_amount': total_amount,
                    'balance_due': total_amount,  # Initially, full amount is due
                    'tax_amount': tax_amount,
                    'payment_reference': '',
                    'status': 'Pending',
                    'notes': f"Service: {selected_service['name']} (Qty: {quantity} x ${unit_price:.2f}). {notes}".strip('. '),
                    'debit_account': 'Accounts Receivable',
                    'debit_amount': total_amount,
                    'credit_account': 'Service Revenue',
                    'credit_amount': total_amount,
                    'accounting_explanation': 'Invoice for services rendered - increases receivables and revenue'
                }
                
                if save_invoice(invoice_data):
                    st.success(f"Invoice {invoice_number} created successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create invoice. Please try again.")
    
    with tab3:
        st.subheader("AI Invoice Assistant")
        st.write("Describe your service delivery, and AI will help match it to existing customers and services.")
        
        with st.form("ai_invoice_form"):
            ai_description = st.text_area(
                "Describe the service delivered:",
                placeholder="Example: Completed website design project for Loo Technologies, delivered 3 pages with responsive design",
                height=100
            )
            
            generate_button = st.form_submit_button("Generate Invoice Details", type="primary", use_container_width=True)
            
            if generate_button:
                if not ai_description:
                    st.error("Please describe the service delivered")
                else:
                    with st.spinner("AI is matching your description to customers and services..."):
                        ai_invoice = generate_invoice_with_ai(ai_description, customers_df, services_df)
                        
                        if ai_invoice:
                            st.success("AI matched your description to existing customers and services!")
                            
                            # Find the matching customer and service
                            try:
                                matched_customer = customers_df[customers_df['customer_id'] == ai_invoice['customer_id']].iloc[0]
                                matched_service = services_df[services_df['name'] == ai_invoice['service_name']].iloc[0]
                                
                                # Show generated details in editable form
                                st.subheader("Review & Edit AI Suggestions")
                                
                                with st.form("ai_generated_invoice"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Show AI selected customer
                                        customer_options = [f"{row['customer_id']}: {row['name']} ({row['company_name']})" 
                                                          for _, row in customers_df.iterrows()]
                                        default_customer_idx = customers_df[customers_df['customer_id'] == ai_invoice['customer_id']].index[0]
                                        selected_customer_idx = st.selectbox("Customer (AI Selected)", range(len(customer_options)), 
                                                                           index=default_customer_idx,
                                                                           format_func=lambda x: customer_options[x])
                                        selected_customer = customers_df.iloc[selected_customer_idx]
                                        
                                        invoice_date = st.date_input("Invoice Date", value=datetime.now().date())
                                        due_date = st.date_input("Due Date", value=datetime.now().date() + timedelta(days=30))
                                    
                                    with col2:
                                        # Show AI selected service
                                        service_options = [f"{row['name']}: {row['description'][:50]}... - ${row['unit_price']}" 
                                                         for _, row in services_df.iterrows()]
                                        default_service_idx = services_df[services_df['name'] == ai_invoice['service_name']].index[0]
                                        selected_service_idx = st.selectbox("Service (AI Selected)", range(len(service_options)), 
                                                                          index=default_service_idx,
                                                                          format_func=lambda x: service_options[x])
                                        selected_service = services_df.iloc[selected_service_idx]
                                        
                                        quantity = st.number_input("Quantity", value=ai_invoice.get('quantity', 1), min_value=1, step=1)
                                        unit_price = st.number_input("Unit Price ($)", value=ai_invoice.get('unit_price', float(selected_service['unit_price'])), step=0.01, format="%.2f")
                                    
                                    # Calculate amounts
                                    subtotal = quantity * unit_price
                                    is_taxable = str(selected_service.get('taxable', 'no')).lower() == 'yes'
                                    tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, 
                                                             value=8.5 if is_taxable else 0.0, step=0.1)
                                    tax_amount = subtotal * (tax_rate / 100)
                                    total_amount = subtotal + tax_amount
                                    
                                    st.write(f"**Subtotal: ${subtotal:.2f}**")
                                    st.write(f"**Tax Amount: ${tax_amount:.2f}**")
                                    st.write(f"**Total Amount: ${total_amount:.2f}**")
                                    
                                    # Double-Entry Accounting Display
                                    st.markdown("---")
                                    st.subheader("Double-Entry Bookkeeping")
                                    col3, col4 = st.columns(2)
                                    with col3:
                                        st.write("**DEBIT:**")
                                        debit_account = ai_invoice.get('accounting_entries', {}).get('debit_account', 'Accounts Receivable')
                                        debit_amount = ai_invoice.get('accounting_entries', {}).get('debit_amount', total_amount)
                                        st.write(f"{debit_account}: ${debit_amount:.2f}")
                                        st.caption("Asset increases - Customer owes money")
                                    with col4:
                                        st.write("**CREDIT:**")
                                        credit_account = ai_invoice.get('accounting_entries', {}).get('credit_account', 'Service Revenue')
                                        credit_amount = ai_invoice.get('accounting_entries', {}).get('credit_amount', total_amount)
                                        st.write(f"{credit_account}: ${credit_amount:.2f}")
                                        st.caption("Revenue increases - Earning income")
                                    
                                    if 'accounting_entries' in ai_invoice and 'explanation' in ai_invoice['accounting_entries']:
                                        st.info(f"**AI Explanation:** {ai_invoice['accounting_entries']['explanation']}")
                                    
                                    notes = st.text_area("Additional Notes", value=ai_invoice.get('notes', ''))
                                    
                                    create_ai_invoice = st.form_submit_button("Create Invoice", type="primary", use_container_width=True)
                                    
                                    if create_ai_invoice:
                                        # Generate invoice number
                                        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{len(invoices_df) + 1:03d}"
                                        
                                        # Create invoice data with double-entry accounting
                                        debit_account = ai_invoice.get('accounting_entries', {}).get('debit_account', 'Accounts Receivable')
                                        credit_account = ai_invoice.get('accounting_entries', {}).get('credit_account', 'Service Revenue')
                                        accounting_explanation = ai_invoice.get('accounting_entries', {}).get('explanation', 'Invoice for services rendered - increases receivables and revenue')
                                        
                                        invoice_data = {
                                            'invoice_id': len(invoices_df) + 1,
                                            'invoice_number': invoice_number,
                                            'date': invoice_date.strftime('%Y-%m-%d'),
                                            'due_date': due_date.strftime('%Y-%m-%d'),
                                            'customer_id': selected_customer['customer_id'],
                                            'customer_name': f"{selected_customer['name']} ({selected_customer['company_name']})",
                                            'service_id': f"SRV-{selected_service_idx + 1:03d}",
                                            'service_name': selected_service['name'],
                                            'total_amount': total_amount,
                                            'balance_due': total_amount,
                                            'tax_amount': tax_amount,
                                            'payment_reference': '',
                                            'status': 'Pending',
                                            'notes': f"Service: {selected_service['name']} (Qty: {quantity} x ${unit_price:.2f}). {notes}".strip('. '),
                                            'debit_account': debit_account,
                                            'debit_amount': total_amount,
                                            'credit_account': credit_account,
                                            'credit_amount': total_amount,
                                            'accounting_explanation': accounting_explanation
                                        }
                                        
                                        if save_invoice(invoice_data):
                                            st.success(f"AI-generated invoice {invoice_number} created successfully!")
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error("Failed to create invoice. Please try again.")
                            
                            except (IndexError, KeyError):
                                st.error("AI couldn't find matching customer or service. Please check your description or create manually.")
                        else:
                            st.error("Failed to generate invoice details. Please try again or create manually.")
        
        # AI Tips
        st.markdown("---")
        st.subheader("💡 AI Assistant Tips")
        st.markdown(f"""
        **Available Customers:** {len(customers_df)} customers
        **Available Services:** {len(services_df)} services
        
        **For best results, mention:**
        - **Customer name or company** (e.g., "Loo Technologies", "Alice Smith")
        - **Service type** that matches your existing services
        - **What was delivered** or completed
        
        **Example descriptions:**
        - "Completed agile development sprint for Loo Technologies"
        - "Delivered hardware chips to Kero company"
        - "Finished consulting project for Bob Johnson at Poo Industries"
        """) 