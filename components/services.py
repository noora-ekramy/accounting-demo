import streamlit as st
import pandas as pd
import os

def show_services_page():
    """Display the services page"""
    st.title("Services")
    st.markdown("---")
    
    # Load services data
    services_file = os.path.join("anonymized_data", "services.csv")
    
    try:
        services_df = pd.read_csv(services_file)
        
        if len(services_df) > 0:
            st.subheader(f"Services ({len(services_df)} services)")
            
            # Search functionality
            search_term = st.text_input("Search services:", placeholder="Search by name, category, or description...")
            
            # Filter data based on search
            if search_term:
                # Search across all text columns
                mask = (
                    services_df['name'].str.contains(search_term, case=False, na=False) |
                    services_df['category'].str.contains(search_term, case=False, na=False) |
                    services_df['description'].str.contains(search_term, case=False, na=False)
                )
                filtered_df = services_df[mask]
                st.write(f"Found {len(filtered_df)} matching services")
            else:
                filtered_df = services_df
            
            # Display data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Services", len(services_df))
            with col2:
                # Average price
                if 'price' in services_df.columns:
                    avg_price = services_df['price'].mean()
                    st.metric("Average Price", f"${avg_price:,.2f}")
                else:
                    st.metric("Average Price", "$0.00")
            with col3:
                # Total revenue potential
                if 'price' in services_df.columns:
                    total_value = services_df['price'].sum()
                    st.metric("Total Service Value", f"${total_value:,.2f}")
                else:
                    st.metric("Total Service Value", "$0.00")
            
            # Category breakdown
            if 'category' in services_df.columns:
                st.markdown("---")
                st.subheader("Service Categories")
                category_counts = services_df['category'].value_counts()
                
                # Display as columns
                if len(category_counts) > 0:
                    cols = st.columns(min(len(category_counts), 4))
                    for i, (category, count) in enumerate(category_counts.items()):
                        with cols[i % 4]:
                            st.metric(f"{category}", count)
            
            # Price analysis
            if 'price' in services_df.columns:
                st.markdown("---")
                st.subheader("Price Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    min_price = services_df['price'].min()
                    max_price = services_df['price'].max()
                    st.metric("Price Range", f"${min_price:,.2f} - ${max_price:,.2f}")
                with col2:
                    median_price = services_df['price'].median()
                    st.metric("Median Price", f"${median_price:,.2f}")
            
        else:
            st.info("No services found. Go to Setup to create your services.")
            
    except FileNotFoundError:
        st.warning("No services found.")
        st.info("Please go to the Setup page to generate your services first.")
        
    except Exception as e:
        st.error(f"Error loading services: {str(e)}")
    
    st.markdown("---")
    st.subheader("Add New Services")
    
    # Tab selection for manual vs AI generation
    tab1, tab2 = st.tabs(["➕ Manual Entry", "🤖 AI Generation"])
    
    with tab1:
        st.write("**Add a new service manually:**")
        with st.form("add_service_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Service Name*")
                new_category = st.text_input("Category*", placeholder="e.g., Consulting, Design, Development")
                new_price = st.number_input("Price*", min_value=0.0, format="%.2f")
            with col2:
                new_duration = st.text_input("Duration", placeholder="e.g., 2 hours, 1 week")
                new_unit = st.selectbox("Pricing Unit", ["Per Hour", "Per Project", "Per Day", "Per Month", "Per Year", "Other"])
                new_description = st.text_area("Description*", height=80)
            
            submitted = st.form_submit_button("Add Service", type="primary")
            if submitted:
                if new_name and new_category and new_price >= 0 and new_description:
                    new_service = {
                        "name": new_name,
                        "category": new_category,
                        "price": new_price,
                        "duration": new_duration,
                        "pricing_unit": new_unit,
                        "description": new_description
                    }
                    
                    # Load existing services
                    try:
                        existing_services = pd.read_csv(services_file)
                        # Add new service
                        new_df = pd.concat([existing_services, pd.DataFrame([new_service])], ignore_index=True)
                        new_df.to_csv(services_file, index=False)
                        pass  # Service added
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding service: {str(e)}")
                else:
                    st.error("Please fill in all required fields marked with *")
    
    with tab2:
        st.write("**Generate services using AI:**")
        prompt_text = st.text_area(
            "Describe what services you need:",
            placeholder="Example: I need professional services for a digital marketing agency including SEO, social media management, content creation, and PPC advertising",
            height=100
        )
        
        if st.button("Generate Services with AI", type="primary"):
            if prompt_text.strip():
                with st.spinner("Generating services using AI..."):
                    try:
                        from setup_logic import generate_services_with_ai
                        
                        # Create a custom context for this specific request
                        custom_context = {
                            "business_type": prompt_text,
                            "money_in": "Service revenue",
                            "money_out": "Service delivery costs"
                        }
                        
                        # Load chart of accounts for context
                        accounts_file = os.path.join("anonymized_data", "accounts.csv")
                        chart_of_accounts = []
                        if os.path.exists(accounts_file):
                            accounts_df = pd.read_csv(accounts_file)
                            chart_of_accounts = accounts_df.to_dict('records')
                        
                        # Generate services
                        generated_services = generate_services_with_ai(custom_context, chart_of_accounts)
                        
                        if generated_services:
                            # Show preview
                            st.write("**Generated Services Preview:**")
                            preview_df = pd.DataFrame(generated_services)
                            st.dataframe(preview_df, use_container_width=True)
                            
                            # Add to existing services
                            try:
                                existing_services = pd.read_csv(services_file)
                                combined_df = pd.concat([existing_services, preview_df], ignore_index=True)
                                combined_df.to_csv(services_file, index=False)
                                pass  # Services generated
                                st.rerun()
                            except FileNotFoundError:
                                # Create new file if doesn't exist
                                preview_df.to_csv(services_file, index=False)
                                pass  # File created with services
                                st.rerun()
                        else:
                            st.error("No services were generated. Please try a different prompt.")
                            
                    except Exception as e:
                        st.error(f"Error generating services: {str(e)}")
            else:
                st.warning("Please enter a description of what services you need.") 