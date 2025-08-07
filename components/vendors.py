import streamlit as st
import pandas as pd
import os

def show_vendors_page():
    """Display the vendors page"""
    st.title("Vendors")
    st.markdown("---")
    
    # Load vendors data
    vendors_file = os.path.join("anonymized_data", "vendors.csv")
    
    try:
        vendors_df = pd.read_csv(vendors_file)
        
        if len(vendors_df) > 0:
            st.subheader(f"Vendors ({len(vendors_df)} vendors)")
            
            # Search functionality
            search_term = st.text_input("Search vendors:", placeholder="Search by name, category, contact, or location...")
            
            # Filter data based on search
            if search_term:
                # Search across all text columns
                search_columns = []
                if 'name' in vendors_df.columns:
                    search_columns.append(vendors_df['name'].str.contains(search_term, case=False, na=False))
                if 'category' in vendors_df.columns:
                    search_columns.append(vendors_df['category'].str.contains(search_term, case=False, na=False))
                if 'contact_email' in vendors_df.columns:
                    search_columns.append(vendors_df['contact_email'].str.contains(search_term, case=False, na=False))
                if 'location' in vendors_df.columns:
                    search_columns.append(vendors_df['location'].str.contains(search_term, case=False, na=False))
                
                if search_columns:
                    mask = search_columns[0]
                    for col_mask in search_columns[1:]:
                        mask = mask | col_mask
                    filtered_df = vendors_df[mask]
                    st.write(f"Found {len(filtered_df)} matching vendors")
                else:
                    filtered_df = vendors_df
            else:
                filtered_df = vendors_df
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Vendors", len(vendors_df))
            with col2:
                # Unique categories
                if 'category' in vendors_df.columns:
                    unique_categories = vendors_df['category'].nunique()
                    st.metric("Categories", unique_categories)
                else:
                    st.metric("Categories", 0)
            with col3:
                # Active vendors (if status column exists)
                if 'status' in vendors_df.columns:
                    active_vendors = len(vendors_df[vendors_df['status'] == 'Active'])
                    st.metric("Active Vendors", active_vendors)
                else:
                    st.metric("Active Vendors", len(vendors_df))
            
            # Category breakdown
            if 'category' in vendors_df.columns:
                st.markdown("---")
                st.subheader("Vendor Categories")
                category_counts = vendors_df['category'].value_counts()
                
                # Display as columns (max 4 per row)
                if len(category_counts) > 0:
                    for i in range(0, len(category_counts), 4):
                        cols = st.columns(4)
                        for j, (category, count) in enumerate(category_counts.iloc[i:i+4].items()):
                            with cols[j]:
                                st.metric(f"{category}", count)
            
            # Location breakdown
            if 'location' in vendors_df.columns:
                st.markdown("---")
                st.subheader("Vendor Locations")
                location_counts = vendors_df['location'].value_counts().head(8)
                
                if len(location_counts) > 0:
                    for i in range(0, len(location_counts), 4):
                        cols = st.columns(4)
                        for j, (location, count) in enumerate(location_counts.iloc[i:i+4].items()):
                            with cols[j]:
                                st.metric(f"{location}", count)
            
            # Payment terms analysis (if available)
            if 'payment_terms' in vendors_df.columns:
                st.markdown("---")
                st.subheader("Payment Terms")
                payment_counts = vendors_df['payment_terms'].value_counts()
                
                cols = st.columns(min(len(payment_counts), 4))
                for i, (terms, count) in enumerate(payment_counts.items()):
                    with cols[i]:
                        st.metric(f"{terms}", count)
            
        else:
            st.info("No vendors found. Go to Setup to create your vendor database.")
            
    except FileNotFoundError:
        st.warning("No vendors found.")
        st.info("Please go to the Setup page to generate your vendors first.")
        
    except Exception as e:
        st.error(f"Error loading vendors: {str(e)}")
    
    st.markdown("---")
    st.subheader("Add New Vendors")
    
    # Tab selection for manual vs AI generation
    tab1, tab2 = st.tabs(["➕ Manual Entry", "🤖 AI Generation"])
    
    with tab1:
        st.write("**Add a new vendor manually:**")
        with st.form("add_vendor_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Vendor Name*")
                new_category = st.text_input("Category*", placeholder="e.g., Office Supplies, IT Services")
                new_email = st.text_input("Contact Email")
                new_phone = st.text_input("Phone Number")
            with col2:
                new_location = st.text_input("Location*")
                new_payment_terms = st.selectbox("Payment Terms", ["Net 30", "Net 15", "Due on Receipt", "Net 60", "Other"])
                new_status = st.selectbox("Status", ["Active", "Inactive", "Pending"])
                new_description = st.text_area("Description", height=60)
            
            submitted = st.form_submit_button("Add Vendor", type="primary")
            if submitted:
                if new_name and new_category and new_location:
                    new_vendor = {
                        "name": new_name,
                        "category": new_category,
                        "contact_email": new_email,
                        "phone": new_phone,
                        "location": new_location,
                        "payment_terms": new_payment_terms,
                        "status": new_status,
                        "description": new_description
                    }
                    
                    # Load existing vendors
                    try:
                        existing_vendors = pd.read_csv(vendors_file)
                        # Add new vendor
                        new_df = pd.concat([existing_vendors, pd.DataFrame([new_vendor])], ignore_index=True)
                        new_df.to_csv(vendors_file, index=False)
                        pass  # Vendor added
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding vendor: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.write("**Generate vendors using AI:**")
        prompt_text = st.text_area(
            "Describe what vendors you need:",
            placeholder="Example: I need vendors for a tech startup including office supplies, cloud services, legal services, and equipment rental",
            height=100
        )
        
        if st.button("Generate Vendors with AI", type="primary"):
            if prompt_text.strip():
                with st.spinner("Generating vendors using AI..."):
                    try:
                        from setup_logic import generate_vendors_with_ai
                        
                        # Create a custom context for this specific request
                        custom_context = {
                            "business_type": prompt_text,
                            "money_in": "Various revenue sources",
                            "money_out": "Various business expenses"
                        }
                        
                        # Load chart of accounts for context
                        accounts_file = os.path.join("anonymized_data", "accounts.csv")
                        chart_of_accounts = []
                        if os.path.exists(accounts_file):
                            accounts_df = pd.read_csv(accounts_file)
                            chart_of_accounts = accounts_df.to_dict('records')
                        
                        # Generate vendors
                        generated_vendors = generate_vendors_with_ai(custom_context, chart_of_accounts)
                        
                        if generated_vendors:
                            # Show preview
                            st.write("**Generated Vendors Preview:**")
                            preview_df = pd.DataFrame(generated_vendors)
                            st.dataframe(preview_df, use_container_width=True)
                            
                            # Add to existing vendors
                            try:
                                existing_vendors = pd.read_csv(vendors_file)
                                combined_df = pd.concat([existing_vendors, preview_df], ignore_index=True)
                                combined_df.to_csv(vendors_file, index=False)
                                pass  # Vendors generated
                                st.rerun()
                            except FileNotFoundError:
                                # Create new file if doesn't exist
                                preview_df.to_csv(vendors_file, index=False)
                                pass  # File created with vendors
                                st.rerun()
                        else:
                            st.error("No vendors were generated. Please try a different prompt.")
                            
                    except Exception as e:
                        st.error(f"Error generating vendors: {str(e)}")
            else:
                st.warning("Please enter a description of what vendors you need.") 