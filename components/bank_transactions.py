import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

def show_bank_transactions_page():
    """Display the bank transactions page"""
    st.title("Bank Transactions")
    st.markdown("---")
    
    # Load bank transactions data
    transactions_file = os.path.join("anonymized_data", "bank_transactions.csv")
    
    try:
        transactions_df = pd.read_csv(transactions_file)
        
        if len(transactions_df) > 0:
            st.subheader(f"Bank Transactions ({len(transactions_df)} transactions)")
            
            # Search functionality
            search_term = st.text_input("Search transactions:", placeholder="Search by description, category, or reference...")
            
            # Filter controls
            col1, col2, col3 = st.columns(3)
            with col1:
                # Transaction type filter
                if 'transaction_type' in transactions_df.columns:
                    type_options = ['All'] + list(transactions_df['transaction_type'].unique())
                    selected_type = st.selectbox("Filter by type:", type_options)
                else:
                    selected_type = 'All'
            
            with col2:
                # Category filter
                if 'category' in transactions_df.columns:
                    category_options = ['All'] + list(transactions_df['category'].unique())
                    selected_category = st.selectbox("Filter by category:", category_options)
                else:
                    selected_category = 'All'
            
            with col3:
                # Amount range filter
                if 'amount' in transactions_df.columns:
                    amount_filter = st.selectbox("Amount filter:", ["All", "Income (> 0)", "Expenses (< 0)", "Large (> $1000)", "Small (< $100)"])
                else:
                    amount_filter = 'All'
            
            # Apply filters
            filtered_df = transactions_df.copy()
            
            if search_term:
                # Search across text columns
                search_columns = []
                if 'description' in filtered_df.columns:
                    search_columns.append(filtered_df['description'].str.contains(search_term, case=False, na=False))
                if 'category' in filtered_df.columns:
                    search_columns.append(filtered_df['category'].str.contains(search_term, case=False, na=False))
                if 'reference' in filtered_df.columns:
                    search_columns.append(filtered_df['reference'].str.contains(search_term, case=False, na=False))
                
                if search_columns:
                    mask = search_columns[0]
                    for col_mask in search_columns[1:]:
                        mask = mask | col_mask
                    filtered_df = filtered_df[mask]
            
            if selected_type != 'All' and 'transaction_type' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['transaction_type'] == selected_type]
            
            if selected_category != 'All' and 'category' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['category'] == selected_category]
            
            if amount_filter != 'All' and 'amount' in filtered_df.columns:
                if amount_filter == "Income (> 0)":
                    filtered_df = filtered_df[filtered_df['amount'] > 0]
                elif amount_filter == "Expenses (< 0)":
                    filtered_df = filtered_df[filtered_df['amount'] < 0]
                elif amount_filter == "Large (> $1000)":
                    filtered_df = filtered_df[abs(filtered_df['amount']) > 1000]
                elif amount_filter == "Small (< $100)":
                    filtered_df = filtered_df[abs(filtered_df['amount']) < 100]
            
            if len(filtered_df) != len(transactions_df):
                st.write(f"Showing {len(filtered_df)} of {len(transactions_df)} transactions")
            
            # Display data with action buttons
            display_transactions_with_actions(filtered_df)
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Transactions", len(transactions_df))
            with col2:
                # Total income
                if 'amount' in transactions_df.columns:
                    total_income = transactions_df[transactions_df['amount'] > 0]['amount'].sum()
                    st.metric("Total Income", f"${total_income:,.2f}")
                else:
                    st.metric("Total Income", "$0.00")
            with col3:
                # Total expenses
                if 'amount' in transactions_df.columns:
                    total_expenses = transactions_df[transactions_df['amount'] < 0]['amount'].sum()
                    st.metric("Total Expenses", f"${total_expenses:,.2f}")
                else:
                    st.metric("Total Expenses", "$0.00")
            with col4:
                # Net balance
                if 'amount' in transactions_df.columns:
                    net_balance = transactions_df['amount'].sum()
                    st.metric("Net Balance", f"${net_balance:,.2f}")
                else:
                    st.metric("Net Balance", "$0.00")
            
            # Transaction type breakdown
            if 'transaction_type' in transactions_df.columns:
                st.markdown("---")
                st.subheader("Transaction Types")
                type_counts = transactions_df['transaction_type'].value_counts()
                
                cols = st.columns(min(len(type_counts), 4))
                for i, (trans_type, count) in enumerate(type_counts.items()):
                    with cols[i]:
                        st.metric(f"{trans_type}", count)
            
            # Category analysis
            if 'category' in transactions_df.columns and 'amount' in transactions_df.columns:
                st.markdown("---")
                st.subheader("Category Analysis")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Top spending categories
                    expense_categories = transactions_df[transactions_df['amount'] < 0].groupby('category')['amount'].sum().abs().nlargest(5)
                    if len(expense_categories) > 0:
                        st.write("**Top 5 Expense Categories:**")
                        for category, amount in expense_categories.items():
                            st.write(f"• {category}: ${amount:,.2f}")
                
                with col2:
                    # Top income categories
                    income_categories = transactions_df[transactions_df['amount'] > 0].groupby('category')['amount'].sum().nlargest(5)
                    if len(income_categories) > 0:
                        st.write("**Top 5 Income Categories:**")
                        for category, amount in income_categories.items():
                            st.write(f"• {category}: ${amount:,.2f}")
            
            # Date analysis (if date columns exist)
            date_columns = [col for col in transactions_df.columns if 'date' in col.lower()]
            if date_columns:
                st.markdown("---")
                st.subheader("Timeline Analysis")
                st.info("Date-based analysis can be implemented when transaction dates are processed.")
            
        else:
            st.info("No bank transactions found. Add some transactions below to get started.")
            
    except FileNotFoundError:
        st.warning("No bank transactions found.")
        st.info("No bank transaction data file exists yet. Add your first transaction below.")
        
    except Exception as e:
        st.error(f"Error loading bank transactions: {str(e)}")
    
    st.markdown("---")
    st.subheader("Add New Bank Transactions")
    
    # Tab selection for manual vs AI generation
    tab1, tab2 = st.tabs(["Manual Entry", "AI Generation"])
    
    with tab1:
        st.write("**Add a new bank transaction manually:**")
        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("Transaction Date*", value=date.today())
                new_description = st.text_input("Description*", placeholder="e.g., Payment from Client ABC")
                new_amount = st.number_input("Amount*", help="Positive for income, negative for expenses", format="%.2f")
                new_type = st.selectbox("Transaction Type*", ["Deposit", "Withdrawal", "Transfer", "Fee", "Interest", "Other"])
            with col2:
                new_category = st.text_input("Category*", placeholder="e.g., Revenue, Office Expenses, Bank Fees")
                new_reference = st.text_input("Reference/Check #", placeholder="Optional reference number")
                new_account = st.text_input("Account", placeholder="e.g., Business Checking")
                new_notes = st.text_area("Notes", height=60, placeholder="Additional notes or details")
            
            submitted = st.form_submit_button("Add Transaction", type="primary")
            if submitted:
                if new_description and new_amount != 0 and new_category:
                    new_transaction = {
                        "date": new_date.strftime("%Y-%m-%d"),
                        "description": new_description,
                        "amount": new_amount,
                        "transaction_type": new_type,
                        "category": new_category,
                        "reference": new_reference,
                        "account": new_account,
                        "notes": new_notes
                    }
                    
                    # Load existing transactions
                    try:
                        existing_transactions = pd.read_csv(transactions_file)
                        # Add new transaction
                        new_df = pd.concat([existing_transactions, pd.DataFrame([new_transaction])], ignore_index=True)
                        new_df.to_csv(transactions_file, index=False)
                        pass  # Transaction added
                        st.rerun()
                    except FileNotFoundError:
                        # Create new file if doesn't exist
                        new_df = pd.DataFrame([new_transaction])
                        new_df.to_csv(transactions_file, index=False)
                        pass  # File created
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding transaction: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.write("**Generate bank transactions using AI:**")
        
        # Generation options
        generation_type = st.radio(
            "What type of transactions do you want to generate?",
            ["Business Operations", "Monthly Recurring", "Custom Scenario"]
        )
        
        if generation_type == "Business Operations":
            prompt_text = st.text_area(
                "Describe your business operations:",
                placeholder="Example: I run a consulting business. Generate typical transactions including client payments, office expenses, software subscriptions, and business meals",
                height=100
            )
        elif generation_type == "Monthly Recurring":
            prompt_text = st.text_area(
                "Describe your recurring transactions:",
                placeholder="Example: Generate monthly recurring transactions for a small business including rent, utilities, insurance, payroll, and subscription services",
                height=100
            )
        else:  # Custom Scenario
            prompt_text = st.text_area(
                "Describe the specific scenario:",
                placeholder="Example: Generate transactions for a busy month including equipment purchase, large client payment, tax payment, and various operational expenses",
                height=100
            )
        
        # Additional parameters
        col1, col2 = st.columns(2)
        with col1:
            num_transactions = st.slider("Number of transactions to generate:", 5, 50, 15)
        with col2:
            time_period = st.selectbox("Time period:", ["Last month", "Current month", "Next month", "Last 3 months"])
        
        if st.button("Generate Bank Transactions with AI", type="primary"):
            if prompt_text.strip():
                with st.spinner("Generating bank transactions using AI..."):
                    try:
                        # Generate transactions using AI
                        generated_transactions = generate_bank_transactions_with_ai(
                            prompt_text, 
                            num_transactions, 
                            time_period,
                            generation_type
                        )
                        
                        if generated_transactions:
                            # Show preview
                            st.write("**Generated Bank Transactions Preview:**")
                            preview_df = pd.DataFrame(generated_transactions)
                            st.dataframe(preview_df, use_container_width=True)
                            
                            # Add to existing transactions
                            try:
                                existing_transactions = pd.read_csv(transactions_file)
                                combined_df = pd.concat([existing_transactions, preview_df], ignore_index=True)
                                combined_df.to_csv(transactions_file, index=False)
                                pass  # Transactions generated
                                st.rerun()
                            except FileNotFoundError:
                                # Create new file if doesn't exist
                                preview_df.to_csv(transactions_file, index=False)
                                pass  # File created with transactions
                                st.rerun()
                        else:
                            st.error("No bank transactions were generated. Please try a different prompt.")
                            
                    except Exception as e:
                        st.error(f"Error generating bank transactions: {str(e)}")
            else:
                st.warning("Please enter a description of what bank transactions you need.")
    
    st.markdown("---")
    st.info("Tip: Bank transactions help you track cash flow, reconcile accounts, and understand your business financial patterns.")

def generate_bank_transactions_with_ai(prompt, num_transactions, time_period, generation_type):
    """Generate bank transactions using AI"""
    try:
        import os
        from langchain.output_parsers import ResponseSchema, StructuredOutputParser
        from langchain_core.prompts import PromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI
        from datetime import datetime, timedelta
        import random
        
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise Exception("Google API key not found. Please check your .env file.")
        
        # Initialize the model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=api_key,
            temperature=0.7
        )
        
        # Define response schemas for bank transactions
        response_schemas = [
            ResponseSchema(name="date", description="Transaction date in YYYY-MM-DD format"),
            ResponseSchema(name="description", description="Clear description of the transaction"),
            ResponseSchema(name="amount", description="Transaction amount (positive for income, negative for expenses)"),
            ResponseSchema(name="transaction_type", description="Type: Deposit, Withdrawal, Transfer, Fee, Interest, or Other"),
            ResponseSchema(name="category", description="Transaction category (e.g., Revenue, Office Expenses, Bank Fees)"),
            ResponseSchema(name="reference", description="Reference number or check number (optional)"),
            ResponseSchema(name="account", description="Bank account name (e.g., Business Checking)"),
            ResponseSchema(name="notes", description="Additional notes or details")
        ]
        
        # Create output parser
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Calculate date range based on time period
        today = datetime.now()
        if time_period == "Last month":
            start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
        elif time_period == "Current month":
            start_date = today.replace(day=1)
            end_date = today
        elif time_period == "Next month":
            if today.month == 12:
                start_date = today.replace(year=today.year + 1, month=1, day=1)
                end_date = today.replace(year=today.year + 1, month=1, day=28)
            else:
                start_date = today.replace(month=today.month + 1, day=1)
                end_date = today.replace(month=today.month + 1, day=28)
        else:  # Last 3 months
            start_date = (today - timedelta(days=90))
            end_date = today
        
        # Create the prompt template
        prompt_template = PromptTemplate(
            template="""
You are an expert financial data generator for bank transactions. Generate realistic bank transactions for a business.

Business Context: {business_context}
Generation Type: {generation_type}
Number of Transactions: {num_transactions}
Date Range: {start_date} to {end_date}

Guidelines:
1. Generate exactly {num_transactions} realistic bank transactions
2. Include a mix of income (positive amounts) and expenses (negative amounts)
3. Use realistic amounts appropriate for a business
4. Include various transaction types: Deposits, Withdrawals, Transfers, Fees, Interest
5. Create relevant categories like: Revenue, Office Expenses, Utilities, Bank Fees, Payroll, etc.
6. Distribute dates realistically across the specified time period
7. Make descriptions specific and business-relevant
8. Use positive amounts for income/deposits and negative amounts for expenses/withdrawals
9. Include reference numbers for checks and transfers where appropriate
10. Add helpful notes for complex transactions

For {generation_type} focus on:
- Business Operations: Daily business activities, client payments, vendor payments, operational expenses
- Monthly Recurring: Regular monthly expenses like rent, utilities, subscriptions, salaries
- Custom Scenario: Follow the specific scenario described in the business context

{format_instructions}

Generate the bank transactions as a JSON array:
            """,
            input_variables=["business_context", "generation_type", "num_transactions", "start_date", "end_date"],
            partial_variables={"format_instructions": format_instructions}
        )
        
        # Create the prompt
        formatted_prompt = prompt_template.format(
            business_context=prompt,
            generation_type=generation_type,
            num_transactions=num_transactions,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Get the response
        response = llm.invoke(formatted_prompt)
        
        # Parse the response
        import json
        import re
        
        # Extract JSON from the response
        response_text = response.content
        
        # Try to find JSON array in the response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                transactions_data = json.loads(json_str)
                
                # Convert to list of dictionaries if needed
                if isinstance(transactions_data, list) and all(isinstance(item, dict) for item in transactions_data):
                    return transactions_data
                else:
                    # Try to parse as individual objects
                    if isinstance(transactions_data, dict):
                        return [transactions_data]
                    
            except json.JSONDecodeError:
                pass
        
        # Fallback: create sample transactions if AI fails
        return create_sample_bank_transactions(num_transactions, start_date, end_date, generation_type)
        
    except Exception as e:
        print(f"Error in AI generation: {str(e)}")
        # Fallback to sample data
        from datetime import datetime, timedelta
        today = datetime.now()
        start_date = today - timedelta(days=30)
        end_date = today
        return create_sample_bank_transactions(num_transactions, start_date, end_date, generation_type)

def create_sample_bank_transactions(num_transactions, start_date, end_date, generation_type):
    """Create sample bank transactions as fallback"""
    import random
    from datetime import timedelta
    
    sample_transactions = []
    date_range = (end_date - start_date).days
    
    # Sample data based on generation type
    if generation_type == "Business Operations":
        templates = [
            {"description": "Client payment - Project ABC", "amount": 2500, "type": "Deposit", "category": "Revenue"},
            {"description": "Office supplies purchase", "amount": -150, "type": "Withdrawal", "category": "Office Expenses"},
            {"description": "Software subscription renewal", "amount": -99, "type": "Withdrawal", "category": "Software"},
            {"description": "Business lunch with client", "amount": -85, "type": "Withdrawal", "category": "Meals & Entertainment"},
            {"description": "Invoice payment from Client XYZ", "amount": 1800, "type": "Deposit", "category": "Revenue"},
        ]
    elif generation_type == "Monthly Recurring":
        templates = [
            {"description": "Office rent payment", "amount": -2000, "type": "Withdrawal", "category": "Rent"},
            {"description": "Electricity bill", "amount": -120, "type": "Withdrawal", "category": "Utilities"},
            {"description": "Internet service", "amount": -80, "type": "Withdrawal", "category": "Utilities"},
            {"description": "Insurance premium", "amount": -250, "type": "Withdrawal", "category": "Insurance"},
            {"description": "Employee salary", "amount": -3500, "type": "Withdrawal", "category": "Payroll"},
        ]
    else:  # Custom Scenario
        templates = [
            {"description": "Equipment purchase", "amount": -5000, "type": "Withdrawal", "category": "Equipment"},
            {"description": "Large client payment", "amount": 8000, "type": "Deposit", "category": "Revenue"},
            {"description": "Tax payment", "amount": -1500, "type": "Withdrawal", "category": "Taxes"},
            {"description": "Marketing campaign", "amount": -800, "type": "Withdrawal", "category": "Marketing"},
            {"description": "Consulting fee received", "amount": 1200, "type": "Deposit", "category": "Revenue"},
        ]
    
    for i in range(num_transactions):
        template = random.choice(templates)
        transaction_date = start_date + timedelta(days=random.randint(0, date_range))
        
        # Add some variation to amounts
        amount_variation = random.uniform(0.8, 1.2)
        varied_amount = int(template["amount"] * amount_variation)
        
        transaction = {
            "date": transaction_date.strftime("%Y-%m-%d"),
            "description": template["description"],
            "amount": varied_amount,
            "transaction_type": template["type"],
            "category": template["category"],
            "reference": f"REF{random.randint(1000, 9999)}" if random.choice([True, False]) else "",
            "account": "Business Checking",
            "notes": f"Generated transaction {i+1}"
        }
        sample_transactions.append(transaction)
    
    return sample_transactions

def display_transactions_with_actions(transactions_df):
    """Display transactions with AI analysis action buttons"""
    import streamlit as st
    
    # Create a copy for display
    display_df = transactions_df.copy()
    
    # Add action column indicator
    if len(display_df) > 0:
        display_df['Action'] = 'AI Analyze'
    
    # Display the dataframe
    st.dataframe(display_df, use_container_width=True)
    
    # Add analyze buttons to dataframe display
    if len(transactions_df) > 0:
        st.markdown("### Transaction Actions")
        st.write("Select a transaction to analyze with AI:")
        
        # Show select buttons for each transaction (limit to first 10 for performance)
        display_limit = min(10, len(transactions_df))
        for idx in range(display_limit):
            row = transactions_df.iloc[idx]
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{row.get('date', 'N/A')}** - {row.get('description', 'N/A')} - ${row.get('amount', 0):,.2f}")
            with col2:
                if st.button(f"Analyze", key=f"analyze_{idx}"):
                    analyze_transaction_with_ai(row, idx)
        
        if len(transactions_df) > display_limit:
            st.info(f"Showing action buttons for first {display_limit} transactions. Scroll up to see all data.")

def analyze_transaction_with_ai(transaction_row, row_index):
    """Navigate to analysis page"""
    
    # Store transaction data in session state for analysis
    st.session_state.analysis_transaction = transaction_row
    st.session_state.analysis_source = "bank_transactions"
    
    # Set the page to Transaction Analysis
    st.session_state.analysis_page_requested = True
    st.rerun()



def get_ai_transaction_suggestions(transaction_row):
    """Get AI suggestions for transaction mapping"""
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        import json
        
        # Load environment variables
        load_dotenv()
        
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return create_fallback_suggestions(transaction_row)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Load relevant data for context
        accounts_data = load_csv_data("accounts.csv")
        customers_data = load_csv_data("customers.csv") 
        vendors_data = load_csv_data("vendors.csv")
        
        # Create simple prompt
        amount = transaction_row.get('amount', 0)
        is_income = amount > 0
        
        prompt = f"""
        Analyze this bank transaction with double-entry bookkeeping principles:
        
        Date: {transaction_row.get('date', '')}
        Description: {transaction_row.get('description', '')}
        Amount: ${amount:,.2f}
        Category: {transaction_row.get('category', '')}
        
        Available Accounts: {str(accounts_data)[:500]}...
        Available Customers: {str(customers_data)[:300]}...
        Available Vendors: {str(vendors_data)[:300]}...
        
        DOUBLE-ENTRY RULES:
        - Every transaction affects exactly TWO accounts from the chart of accounts
        - Select TWO specific accounts from the available chart of accounts
        - ASSETS: Debit increases, Credit decreases
        - LIABILITIES: Credit increases, Debit decreases
        - EQUITY: Credit increases, Debit decreases
        - REVENUE: Credit increases, Debit decreases  
        - EXPENSES: Debit increases, Credit decreases
        
        Return ONLY a JSON object:
        {{
            "account_suggestions": [
                {{
                    "account_name": "Account from chart of accounts",
                    "account_type": "Income|Expense|Asset|Liability|Equity",
                    "confidence": "High|Medium|Low",
                    "reason": "Why this account"
                }}
            ],
                         "double_entry_mapping": {{
                 "debit_account": "Account name from chart of accounts to debit",
                 "debit_amount": {abs(amount)},
                 "credit_account": "Account name from chart of accounts to credit",
                 "credit_amount": {abs(amount)},
                 "explanation": "Why these two accounts are affected"
             }},
            "entity_suggestion": {{
                "type": "customer|vendor|new",
                "name": "Entity name or empty",
                "confidence": "High|Medium|Low",
                "reason": "Why this entity"
            }},
            "document_suggestion": {{
                "type": "{'invoice' if is_income else 'bill'}|none",
                "amount": {abs(amount)},
                "confidence": "High|Medium|Low",
                "reason": "Why create document"
            }},
            "additional_notes": "Brief insights about accounting treatment"
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
        print(f"Error in AI analysis: {str(e)}")
        return create_fallback_suggestions(transaction_row)

def load_csv_data(filename):
    """Load CSV data for AI context"""
    try:
        file_path = os.path.join("anonymized_data", filename)
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except:
        return []

def create_structured_analysis_prompt(transaction, accounts, customers, vendors, services, expenses, format_instructions):
    """Create structured prompt for AI analysis using LangChain template"""
    from langchain_core.prompts import PromptTemplate
    
    amount = transaction.get('amount', 0)
    is_income = amount > 0
    transaction_type = "Income/Revenue" if is_income else "Expense/Payment"
    
    prompt_template = PromptTemplate(
        template="""You are an expert accounting AI assistant. Analyze this bank transaction and provide structured analysis.

TRANSACTION DETAILS:
Date: {transaction_date}
Description: {transaction_description}
Amount: ${transaction_amount}
Category: {transaction_category}
Type: {transaction_type}

AVAILABLE DATA:
Chart of Accounts: {accounts_data}
Customers: {customers_data}
Vendors: {vendors_data}
Services: {services_data}
Expense Categories: {expenses_data}

ANALYSIS INSTRUCTIONS:
1. For account mapping: Select the best matching account from the chart of accounts
2. For entity identification: Match with existing customers (for income) or vendors (for expenses)
3. For document creation: Suggest invoice creation for income or bill creation for expenses
4. For service/expense matching: Match with appropriate service or expense category
5. Confidence levels must be exactly: High, Medium, or Low

{format_instructions}

Make sure all fields are filled with appropriate values based on the transaction analysis.""",
        input_variables=[
            "transaction_date", "transaction_description", "transaction_amount", 
            "transaction_category", "transaction_type", "accounts_data", "customers_data", 
            "vendors_data", "services_data", "expenses_data"
        ],
        partial_variables={"format_instructions": format_instructions}
    )
    
    return prompt_template

def format_structured_response(structured_output, transaction_row):
    """Convert structured output to expected format"""
    amount = transaction_row.get('amount', 0)
    
    formatted_response = {
        "account_suggestions": [
            {
                "account_name": structured_output.get("account_name", "Unknown Account"),
                "account_type": structured_output.get("account_type", "Unknown"),
                "confidence": structured_output.get("account_confidence", "Low"),
                "reason": structured_output.get("account_reason", "No reason provided")
            }
        ],
        "entity_suggestion": {
            "type": structured_output.get("entity_type", "new"),
            "name": structured_output.get("entity_name", ""),
            "confidence": structured_output.get("entity_confidence", "Low"),
            "reason": structured_output.get("entity_reason", "No reason provided")
        },
        "document_suggestion": {
            "type": structured_output.get("document_type", "none"),
            "service_or_expense": structured_output.get("service_or_expense", ""),
            "amount": abs(float(structured_output.get("document_amount", amount))),
            "confidence": structured_output.get("document_confidence", "Low"),
            "reason": structured_output.get("document_reason", "No reason provided")
        },
        "additional_notes": structured_output.get("additional_notes", "No additional notes")
    }
    
    return formatted_response

def parse_ai_suggestions(response_text):
    """Parse AI response into structured suggestions with improved JSON handling"""
    try:
        import json
        import re
        
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Try multiple JSON extraction methods
        json_data = None
        
        # Method 1: Try direct JSON parsing (if response is clean JSON)
        try:
            json_data = json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass
        
        # Method 2: Extract JSON object with regex
        if not json_data:
            json_patterns = [
                r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested object
                r'\{.*?\}(?=\s*$)',  # JSON at end of text
                r'\{.*\}',  # Any JSON-like structure
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, cleaned_text, re.DOTALL)
                if json_match:
                    try:
                        json_str = json_match.group()
                        json_data = json.loads(json_str)
                        break
                    except json.JSONDecodeError:
                        continue
        
        # Method 3: Extract JSON between code blocks
        if not json_data:
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_text, re.DOTALL)
            if code_block_match:
                try:
                    json_str = code_block_match.group(1)
                    json_data = json.loads(json_str)
                except json.JSONDecodeError:
                    pass
        
        # Validate the JSON structure
        if json_data and validate_suggestion_structure(json_data):
            return json_data
        else:
            print(f"Invalid JSON structure received: {json_data}")
            return create_fallback_suggestions(response_text)
            
    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
        return create_fallback_suggestions(response_text)

def validate_suggestion_structure(data):
    """Validate that the AI response has the required structure"""
    try:
        required_keys = ['account_suggestions', 'entity_suggestion', 'document_suggestion', 'additional_notes']
        
        if not isinstance(data, dict):
            return False
        
        # Check if all required keys exist
        for key in required_keys:
            if key not in data:
                return False
        
        # Validate account_suggestions structure
        if not isinstance(data['account_suggestions'], list):
            return False
        
        # Validate entity_suggestion structure
        entity_sug = data['entity_suggestion']
        if not isinstance(entity_sug, dict) or 'type' not in entity_sug:
            return False
        
        # Validate document_suggestion structure
        doc_sug = data['document_suggestion']
        if not isinstance(doc_sug, dict) or 'type' not in doc_sug:
            return False
        
        return True
        
    except Exception:
        return False

def create_fallback_suggestions(transaction_row):
    """Create basic suggestions if AI analysis fails"""
    amount = transaction_row.get('amount', 0)
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
            "amount": abs_amount,
            "confidence": "Low",
            "reason": "Insufficient data for document creation"
        },
        "additional_notes": "Basic double-entry analysis using chart of accounts. Manual review recommended for accurate account selection."
    }

# Transaction analysis functions integrated above 