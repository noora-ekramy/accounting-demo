import streamlit as st
import pandas as pd
import os

def show_expenses_page():
    """Display the expenses page"""
    st.title("Expenses")
    st.markdown("---")
    
    # Load expenses data
    expenses_file = os.path.join("anonymized_data", "expenses.csv")
    
    try:
        expenses_df = pd.read_csv(expenses_file)
        
        if len(expenses_df) > 0:
            st.subheader(f"Expense Categories ({len(expenses_df)} categories)")
            
            # Search functionality
            search_term = st.text_input("Search expenses:", placeholder="Search by category, description, or account...")
            
            # Filter data based on search
            if search_term:
                # Search across all text columns
                search_columns = []
                if 'category' in expenses_df.columns:
                    search_columns.append(expenses_df['category'].str.contains(search_term, case=False, na=False))
                if 'description' in expenses_df.columns:
                    search_columns.append(expenses_df['description'].str.contains(search_term, case=False, na=False))
                if 'account_name' in expenses_df.columns:
                    search_columns.append(expenses_df['account_name'].str.contains(search_term, case=False, na=False))
                
                if search_columns:
                    mask = search_columns[0]
                    for col_mask in search_columns[1:]:
                        mask = mask | col_mask
                    filtered_df = expenses_df[mask]
                    st.write(f"Found {len(filtered_df)} matching expense categories")
                else:
                    filtered_df = expenses_df
            else:
                filtered_df = expenses_df
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Categories", len(expenses_df))
            with col2:
                # Average estimated amount
                if 'estimated_monthly_amount' in expenses_df.columns:
                    avg_amount = expenses_df['estimated_monthly_amount'].mean()
                    st.metric("Avg Monthly Est.", f"${avg_amount:,.2f}")
                else:
                    st.metric("Avg Monthly Est.", "$0.00")
            with col3:
                # Total estimated monthly expenses
                if 'estimated_monthly_amount' in expenses_df.columns:
                    total_monthly = expenses_df['estimated_monthly_amount'].sum()
                    st.metric("Total Monthly Est.", f"${total_monthly:,.2f}")
                else:
                    st.metric("Total Monthly Est.", "$0.00")
            
            # Category breakdown by type (if available)
            if 'expense_type' in expenses_df.columns:
                st.markdown("---")
                st.subheader("Expense Types")
                type_counts = expenses_df['expense_type'].value_counts()
                
                cols = st.columns(min(len(type_counts), 4))
                for i, (expense_type, count) in enumerate(type_counts.items()):
                    with cols[i]:
                        st.metric(f"{expense_type}", count)
            
            # Monthly expense analysis
            if 'estimated_monthly_amount' in expenses_df.columns:
                st.markdown("---")
                st.subheader("Monthly Expense Analysis")
                
                # Top expense categories
                top_expenses = expenses_df.nlargest(5, 'estimated_monthly_amount')[['category', 'estimated_monthly_amount']]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Top 5 Expense Categories:**")
                    for _, row in top_expenses.iterrows():
                        st.write(f"• {row['category']}: ${row['estimated_monthly_amount']:,.2f}")
                
                with col2:
                    # Annual projection
                    total_monthly = expenses_df['estimated_monthly_amount'].sum()
                    annual_projection = total_monthly * 12
                    st.metric("Annual Projection", f"${annual_projection:,.2f}")
                    
                    # Expense range
                    min_expense = expenses_df['estimated_monthly_amount'].min()
                    max_expense = expenses_df['estimated_monthly_amount'].max()
                    st.metric("Expense Range", f"${min_expense:,.2f} - ${max_expense:,.2f}")
            
            # Frequency analysis (if available)
            if 'frequency' in expenses_df.columns:
                st.markdown("---")
                st.subheader("Expense Frequency")
                frequency_counts = expenses_df['frequency'].value_counts()
                
                cols = st.columns(min(len(frequency_counts), 4))
                for i, (frequency, count) in enumerate(frequency_counts.items()):
                    with cols[i]:
                        st.metric(f"{frequency}", count)
            
            # Account mapping (if available)
            if 'account_name' in expenses_df.columns:
                st.markdown("---")
                st.subheader("Account Mapping")
                st.info("Expense categories are mapped to chart of accounts for proper tracking.")
                account_counts = expenses_df['account_name'].value_counts().head(5)
                
                if len(account_counts) > 0:
                    st.write("**Most Used Accounts:**")
                    for account, count in account_counts.items():
                        st.write(f"• {account}: {count} categories")
            
        else:
            st.info("No expense categories found. Go to Setup to create your expense structure.")
            
    except FileNotFoundError:
        st.warning("No expense categories found.")
        st.info("Please go to the Setup page to generate your expense categories first.")
        
    except Exception as e:
        st.error(f"Error loading expenses: {str(e)}")
    
    st.markdown("---")
    st.subheader("Add New Expense Categories")
    
    # Tab selection for manual vs AI generation
    tab1, tab2 = st.tabs(["➕ Manual Entry", "🤖 AI Generation"])
    
    with tab1:
        st.write("**Add a new expense category manually:**")
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_category = st.text_input("Category Name*")
                new_expense_type = st.selectbox("Expense Type", ["Fixed", "Variable", "One-time", "Recurring"])
                new_frequency = st.selectbox("Frequency", ["Monthly", "Quarterly", "Annually", "As Needed", "Daily", "Weekly"])
            with col2:
                new_estimated_amount = st.number_input("Estimated Monthly Amount*", min_value=0.0, format="%.2f")
                new_account_name = st.text_input("Account Name", placeholder="Link to chart of accounts")
                new_description = st.text_area("Description*", height=80)
            
            submitted = st.form_submit_button("Add Expense Category", type="primary")
            if submitted:
                if new_category and new_estimated_amount >= 0 and new_description:
                    new_expense = {
                        "category": new_category,
                        "expense_type": new_expense_type,
                        "frequency": new_frequency,
                        "estimated_monthly_amount": new_estimated_amount,
                        "account_name": new_account_name,
                        "description": new_description
                    }
                    
                    # Load existing expenses
                    try:
                        existing_expenses = pd.read_csv(expenses_file)
                        # Add new expense
                        new_df = pd.concat([existing_expenses, pd.DataFrame([new_expense])], ignore_index=True)
                        new_df.to_csv(expenses_file, index=False)
                        pass  # Expense category added
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding expense category: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.write("**Generate expense categories using AI:**")
        prompt_text = st.text_area(
            "Describe what expense categories you need:",
            placeholder="Example: I need expense categories for a retail store including inventory costs, store rent, employee wages, utilities, and marketing expenses",
            height=100
        )
        
        if st.button("Generate Expense Categories with AI", type="primary"):
            if prompt_text.strip():
                with st.spinner("Generating expense categories using AI..."):
                    try:
                        from setup_logic import generate_expenses_with_ai
                        
                        # Create a custom context for this specific request
                        custom_context = {
                            "business_type": prompt_text,
                            "money_in": "Various revenue sources",
                            "money_out": prompt_text
                        }
                        
                        # Load chart of accounts for context
                        accounts_file = os.path.join("anonymized_data", "accounts.csv")
                        chart_of_accounts = []
                        if os.path.exists(accounts_file):
                            accounts_df = pd.read_csv(accounts_file)
                            chart_of_accounts = accounts_df.to_dict('records')
                        
                        # Generate expenses
                        generated_expenses = generate_expenses_with_ai(custom_context, chart_of_accounts)
                        
                        if generated_expenses:
                            # Show preview
                            st.write("**Generated Expense Categories Preview:**")
                            preview_df = pd.DataFrame(generated_expenses)
                            st.dataframe(preview_df, use_container_width=True)
                            
                            # Add to existing expenses
                            try:
                                existing_expenses = pd.read_csv(expenses_file)
                                combined_df = pd.concat([existing_expenses, preview_df], ignore_index=True)
                                combined_df.to_csv(expenses_file, index=False)
                                pass  # Expense categories generated
                                st.rerun()
                            except FileNotFoundError:
                                # Create new file if doesn't exist
                                preview_df.to_csv(expenses_file, index=False)
                                pass  # File created with expense categories
                                st.rerun()
                        else:
                            st.error("No expense categories were generated. Please try a different prompt.")
                            
                    except Exception as e:
                        st.error(f"Error generating expense categories: {str(e)}")
            else:
                st.warning("Please enter a description of what expense categories you need.")
    
    st.info("💡 Tip: These are expense categories. Actual expense transactions would be recorded separately and linked to these categories.") 