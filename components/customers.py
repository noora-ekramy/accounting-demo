import streamlit as st
import pandas as pd
import os

def show_customers_page():
    """Display the customers page"""
    st.title("Customers")
    st.markdown("---")
    
    # Load customers data
    customers_file = os.path.join("anonymized_data", "customers.csv")
    
    try:
        customers_df = pd.read_csv(customers_file)
        
        if len(customers_df) > 0:
            st.subheader(f"Customers ({len(customers_df)} customers)")
            
            # Search functionality
            search_term = st.text_input("Search customers:", placeholder="Search by name, email, company, or location...")
            
            # Filter data based on search
            if search_term:
                # Search across all text columns
                mask = (
                    customers_df['name'].str.contains(search_term, case=False, na=False) |
                    customers_df['email'].str.contains(search_term, case=False, na=False) |
                    customers_df['company'].str.contains(search_term, case=False, na=False) |
                    customers_df['location'].str.contains(search_term, case=False, na=False)
                )
                filtered_df = customers_df[mask]
                st.write(f"Found {len(filtered_df)} matching customers")
            else:
                filtered_df = customers_df
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Customers", len(customers_df))
            with col2:
                # Unique locations
                if 'location' in customers_df.columns:
                    unique_locations = customers_df['location'].nunique()
                    st.metric("Locations", unique_locations)
                else:
                    st.metric("Locations", 0)
            with col3:
                # Customer types breakdown
                if 'customer_type' in customers_df.columns:
                    business_customers = len(customers_df[customers_df['customer_type'] == 'Business'])
                    st.metric("Business Customers", business_customers)
                else:
                    st.metric("Business Customers", 0)
            
            # Location breakdown
            if 'location' in customers_df.columns:
                st.markdown("---")
                st.subheader("Customer Locations")
                location_counts = customers_df['location'].value_counts().head(8)
                
                # Display as columns (max 4 per row)
                if len(location_counts) > 0:
                    for i in range(0, len(location_counts), 4):
                        cols = st.columns(4)
                        for j, (location, count) in enumerate(location_counts.iloc[i:i+4].items()):
                            with cols[j]:
                                st.metric(f"{location}", count)
            
            # Customer type analysis
            if 'customer_type' in customers_df.columns:
                st.markdown("---")
                st.subheader("Customer Types")
                type_counts = customers_df['customer_type'].value_counts()
                
                cols = st.columns(len(type_counts))
                for i, (customer_type, count) in enumerate(type_counts.items()):
                    with cols[i]:
                        st.metric(f"{customer_type}", count)
            
            # Recent activity (if date columns exist)
            date_columns = [col for col in customers_df.columns if 'date' in col.lower()]
            if date_columns:
                st.markdown("---")
                st.subheader("Customer Activity")
                st.info("Customer activity tracking can be implemented based on invoice data.")
            
        else:
            st.info("No customers found. Go to Setup to create your customer database.")
            
    except FileNotFoundError:
        st.warning("No customers found.")
        st.info("Please go to the Setup page to generate your customers first.")
        
    except Exception as e:
        st.error(f"Error loading customers: {str(e)}")
    
    st.markdown("---")
    st.subheader("Add New Customers")
    
    # Tab selection for manual vs AI generation
    tab1, tab2 = st.tabs(["➕ Manual Entry", "🤖 AI Generation"])
    
    with tab1:
        st.write("**Add a new customer manually:**")
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Customer Name*")
                new_email = st.text_input("Email*")
                new_company = st.text_input("Company")
                new_phone = st.text_input("Phone Number")
            with col2:
                new_location = st.text_input("Location*")
                new_customer_type = st.selectbox("Customer Type", ["Individual", "Business", "Government", "Non-Profit"])
                new_status = st.selectbox("Status", ["Active", "Inactive", "Prospect"])
                new_notes = st.text_area("Notes", height=60)
            
            submitted = st.form_submit_button("Add Customer", type="primary")
            if submitted:
                if new_name and new_email and new_location:
                    new_customer = {
                        "name": new_name,
                        "email": new_email,
                        "company": new_company,
                        "phone": new_phone,
                        "location": new_location,
                        "customer_type": new_customer_type,
                        "status": new_status,
                        "notes": new_notes
                    }
                    
                    # Load existing customers
                    try:
                        existing_customers = pd.read_csv(customers_file)
                        # Add new customer
                        new_df = pd.concat([existing_customers, pd.DataFrame([new_customer])], ignore_index=True)
                        new_df.to_csv(customers_file, index=False)
                        pass  # Customer added
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding customer: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.write("**Generate customers using AI:**")
        prompt_text = st.text_area(
            "Describe what customers you need:",
            placeholder="Example: I need customers for a B2B software company including tech startups, small businesses, and enterprise clients in various industries",
            height=100
        )
        
        if st.button("Generate Customers with AI", type="primary"):
            if prompt_text.strip():
                with st.spinner("Generating customers using AI..."):
                    try:
                        from setup_logic import generate_customers_with_ai
                        
                        # Create a custom context for this specific request
                        custom_context = {
                            "business_type": prompt_text,
                            "money_in": "Customer payments",
                            "money_out": "Customer service costs"
                        }
                        
                        # Load chart of accounts for context
                        accounts_file = os.path.join("anonymized_data", "accounts.csv")
                        chart_of_accounts = []
                        if os.path.exists(accounts_file):
                            accounts_df = pd.read_csv(accounts_file)
                            chart_of_accounts = accounts_df.to_dict('records')
                        
                        # Generate customers
                        generated_customers = generate_customers_with_ai(custom_context, chart_of_accounts)
                        
                        if generated_customers:
                            # Show preview
                            st.write("**Generated Customers Preview:**")
                            preview_df = pd.DataFrame(generated_customers)
                            st.dataframe(preview_df, use_container_width=True)
                            
                            # Add to existing customers
                            try:
                                existing_customers = pd.read_csv(customers_file)
                                combined_df = pd.concat([existing_customers, preview_df], ignore_index=True)
                                combined_df.to_csv(customers_file, index=False)
                                pass  # Customers generated
                                st.rerun()
                            except FileNotFoundError:
                                # Create new file if doesn't exist
                                preview_df.to_csv(customers_file, index=False)
                                pass  # File created with customers
                                st.rerun()
                        else:
                            st.error("No customers were generated. Please try a different prompt.")
                            
                    except Exception as e:
                        st.error(f"Error generating customers: {str(e)}")
            else:
                st.warning("Please enter a description of what customers you need.") 