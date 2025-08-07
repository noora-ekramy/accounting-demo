import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

def load_financial_data():
    """Load financial data from onboarding_responses.json file"""
    try:
        if os.path.exists("onboarding_responses.json"):
            with open("onboarding_responses.json", 'r') as f:
                data = json.load(f)
                # Check if it's the new format (has general_info, assets, etc.)
                if isinstance(data, dict) and any(key in data for key in ["general_info", "assets", "liabilities", "equity"]):
                    return data
                else:
                    # Legacy format - return None to show legacy view
                    return None
        else:
            return None
    except Exception as e:
        st.error(f"Error loading financial data: {str(e)}")
        return None

def load_onboarding_data():
    """Load legacy onboarding data from JSON file"""
    try:
        if os.path.exists("onboarding_responses.json"):
            with open("onboarding_responses.json", 'r') as f:
                data = json.load(f)
                # Check if it's the legacy format
                if isinstance(data, dict) and not any(key in data for key in ["general_info", "assets", "liabilities", "equity"]):
                    return data
                else:
                    return None
        else:
            return None
    except Exception as e:
        st.error(f"Error loading onboarding data: {str(e)}")
        return None

def export_to_csv(financial_data):
    """Export financial data to CSV format"""
    try:
        # Create a flattened structure for CSV export
        export_data = []
        
        # General Information
        general_info = financial_data.get("general_info", {})
        for key, value in general_info.items():
            if value:
                export_data.append({
                    "Category": "General Information",
                    "Item": key.replace("_", " ").title(),
                    "Value": value
                })
        
        # Business Questions
        business_questions = financial_data.get("business_questions", {})
        question_labels = {
            "business_type": "Business Type & Offerings",
            "money_in": "Revenue Sources",
            "money_out": "Main Expenses"
        }
        for key, value in business_questions.items():
            if value:
                export_data.append({
                    "Category": "Business Overview",
                    "Item": question_labels.get(key, key.replace("_", " ").title()),
                    "Value": value
                })
        
        # Assets
        assets = financial_data.get("assets", {})
        for key, value in assets.items():
            if value:
                export_data.append({
                    "Category": "Assets",
                    "Item": key.replace("_", " ").title(),
                    "Value": value
                })
        
        # Liabilities
        liabilities = financial_data.get("liabilities", {})
        for key, value in liabilities.items():
            if value:
                export_data.append({
                    "Category": "Liabilities",
                    "Item": key.replace("_", " ").title(),
                    "Value": value
                })
        
        # Equity
        equity = financial_data.get("equity", {})
        for key, value in equity.items():
            if value:
                export_data.append({
                    "Category": "Equity",
                    "Item": key.replace("_", " ").title(),
                    "Value": value
                })
        
        # Add metadata
        export_data.append({
            "Category": "Metadata",
            "Item": "Last Updated",
            "Value": financial_data.get("last_updated", "Unknown")
        })
        
        export_data.append({
            "Category": "Metadata",
            "Item": "Completion Status",
            "Value": "Complete" if financial_data.get("completed", False) else "In Progress"
        })
        
        return pd.DataFrame(export_data)
        
    except Exception as e:
        st.error(f"Error creating CSV export: {str(e)}")
        return None

def display_financial_summary(financial_data):
    """Display a summary of financial data"""
    st.subheader("Financial Data Summary")
    
    # Count completed fields
    total_fields = 0
    completed_fields = 0
    
    for category in ["general_info", "assets", "liabilities", "equity"]:
        category_data = financial_data.get(category, {})
        for key, value in category_data.items():
            total_fields += 1
            if value and str(value).strip():
                completed_fields += 1
    
    completion_rate = (completed_fields / total_fields * 100) if total_fields > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Fields", total_fields)
    with col2:
        st.metric("Completed Fields", completed_fields)
    with col3:
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    with col4:
        status = "Complete" if financial_data.get("completed", False) else "In Progress"
        st.metric("Status", status)

def show_company_data_page():
    """Display the company data page"""
    st.title("Company Data")
    st.markdown("---")
    st.write("View and manage your collected company financial information.")
    
    # Load data
    financial_data = load_financial_data()
    onboarding_data = load_onboarding_data()
    
    if not financial_data and not onboarding_data:
        st.warning("No company data found. Please complete the onboarding process first.")
        if st.button("Go to Onboarding"):
            # This would switch to onboarding page in a real app
            st.info("Navigate to the Onboarding page from the sidebar to collect your data.")
        return
    
    # Display data based on what's available
    if financial_data:
        # Display financial summary
        display_financial_summary(financial_data)
        st.markdown("---")
        
        # Main data display
        col1, col2 = st.columns(2)
        
        with col1:
            # General Information
            st.subheader("General Information")
            general_info = financial_data.get("general_info", {})
            if any(general_info.values()):
                for key, value in general_info.items():
                    if value:
                        display_name = key.replace("_", " ").title()
                        st.write(f"**{display_name}:** {value}")
            else:
                st.write("No general information collected yet.")
            
            st.markdown("---")
            
            # Business Questions
            st.subheader("Business Overview")
            business_questions = financial_data.get("business_questions", {})
            if any(business_questions.values()):
                if business_questions.get("business_type"):
                    st.write(f"**Business Type:** {business_questions['business_type']}")
                if business_questions.get("money_in"):
                    st.write(f"**Revenue Sources:** {business_questions['money_in']}")
                if business_questions.get("money_out"):
                    st.write(f"**Main Expenses:** {business_questions['money_out']}")
            else:
                st.write("No business overview collected yet.")
            
            st.markdown("---")
            
            # Assets
            st.subheader("Assets")
            assets = financial_data.get("assets", {})
            if any(assets.values()):
                for key, value in assets.items():
                    if value:
                        display_name = key.replace("_", " ").title()
                        st.write(f"**{display_name}:** {value}")
            else:
                st.write("No asset information collected yet.")
        
        with col2:
            # Liabilities
            st.subheader("Liabilities")
            liabilities = financial_data.get("liabilities", {})
            if any(liabilities.values()):
                for key, value in liabilities.items():
                    if value:
                        display_name = key.replace("_", " ").title()
                        st.write(f"**{display_name}:** {value}")
            else:
                st.write("No liability information collected yet.")
            
            st.markdown("---")
            
            # Equity
            st.subheader("Equity")
            equity = financial_data.get("equity", {})
            if any(equity.values()):
                for key, value in equity.items():
                    if value:
                        display_name = key.replace("_", " ").title()
                        st.write(f"**{display_name}:** {value}")
            else:
                st.write("No equity information collected yet.")
        
        st.markdown("---")
        
        # Metadata
        st.subheader("Data Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Created:** {financial_data.get('timestamp', 'Unknown')}")
        with col2:
            st.write(f"**Last Updated:** {financial_data.get('last_updated', 'Unknown')}")
        with col3:
            status = "Complete" if financial_data.get("completed", False) else "In Progress"
            st.write(f"**Status:** {status}")
        
        st.markdown("---")
        
        # Actions
        st.subheader("Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Refresh Data"):
                st.rerun()
        
        with col2:
            # Export to CSV
            csv_data = export_to_csv(financial_data)
            if csv_data is not None:
                csv_string = csv_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_string,
                    file_name=f"company_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            # Export JSON
            json_string = json.dumps(financial_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_string,
                file_name=f"financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col4:
            if st.button("Clear All Data", type="secondary"):
                if st.button("Confirm Clear", type="secondary"):
                    try:
                        if os.path.exists("onboarding_responses.json"):
                            os.remove("onboarding_responses.json")
                        st.success("All data cleared successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing data: {str(e)}")
        
        # Raw JSON Display (expandable)
        with st.expander("View Raw JSON Data"):
            st.json(financial_data)
    
    elif onboarding_data:
        # Display legacy onboarding data
        st.subheader("Legacy Onboarding Data")
        st.write("**Business Type:** " + onboarding_data.get("business_type", "Not provided"))
        st.write("**Money In:** " + onboarding_data.get("money_in", "Not provided"))
        st.write("**Money Out:** " + onboarding_data.get("money_out", "Not provided"))
        st.write("**Timestamp:** " + onboarding_data.get("timestamp", "Unknown"))
        
        if onboarding_data.get("chat_status") == "in_progress":
            st.info("It looks like you have an onboarding session in progress. Continue the chat to collect detailed financial information.")
        
        with st.expander("View Raw JSON Data"):
            st.json(onboarding_data) 