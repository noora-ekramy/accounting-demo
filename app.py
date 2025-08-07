import streamlit as st
import pandas as pd
import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Import page modules
from components.home import show_home_page
from components.onboarding import show_onboarding_page
from components.setup import show_setup_page
from components.data_management import show_data_management_page
from components.accounts import show_accounts_page
from components.services import show_services_page
from components.customers import show_customers_page
from components.invoices import show_invoices_page
from components.vendors import show_vendors_page
from components.bills import show_bills_page
from components.expenses import show_expenses_page
from components.bank_transactions import show_bank_transactions_page
from components.transaction_analysis import show_transaction_analysis_page
from components.company_data import show_company_data_page


# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Accounting Test",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_startup_page():
    """Display the startup welcome page"""
    # Hide sidebar on startup page
    st.markdown("""
        <style>
        .css-1d391kg {display: none}
        .css-1dp5vir {display: none}
        </style>
        """, unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
        
        # Title
        st.markdown("# Welcome to Accounting Test")
        
        st.markdown("---")
        
        # Welcome message
        st.markdown("""
        ### Your Comprehensive Accounting Management System
        
        Welcome to the complete accounting solution designed to help you manage your business finances efficiently.
        
        **What you can do:**
        - **Get Started** with personalized onboarding
        - **Manage Accounts** with AI-generated chart of accounts
        - **Track Transactions** with smart categorization
        - **Handle Customers & Vendors** seamlessly
        - **Analyze Data** with AI-powered insights
        - **Create Invoices & Bills** professionally
        
        Ready to streamline your accounting workflow?
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Start button
        if st.button("Start Accounting System", type="primary", use_container_width=True):
            st.session_state.app_started = True
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
        Powered by Streamlit - Enhanced with AI
        </div>
        """, unsafe_allow_html=True)

# Initialize session state for app startup
if "app_started" not in st.session_state:
    st.session_state.app_started = False

# Show startup page or main app
if not st.session_state.app_started:
    show_startup_page()
else:
    # Check if transaction analysis was requested
    if st.session_state.get("analysis_page_requested", False):
        page = "Transaction Analysis"
        st.session_state.analysis_page_requested = False
    elif st.session_state.get("bank_transactions_requested", False):
        page = "Bank Transactions"
        st.session_state.bank_transactions_requested = False
    else:
        # Sidebar navigation (only show when app is started)
        st.sidebar.title("Accounting Test")
        st.sidebar.markdown("---")

        # Main navigation
        page = st.sidebar.radio(
            "Navigate to:",
            [
                "Home",
                "Onboarding",
                "Company Data",
                "Setup",
                "Data Management",
                "Accounts", 
                "Services",
                "Customers",
                "Invoices",
                "Vendors",
                "Bills", 
                "Expenses",
                "Bank Transactions",
                "Transaction Analysis"
            ]
        )

    # Page routing
    if page == "Home":
        show_home_page()
    elif page == "Onboarding":
        show_onboarding_page()
    elif page == "Company Data":
        show_company_data_page()
    elif page == "Setup":
        show_setup_page()
    elif page == "Data Management":
        show_data_management_page()
    elif page == "Accounts":
        show_accounts_page()
    elif page == "Services":
        show_services_page()
    elif page == "Customers":
        show_customers_page()
    elif page == "Invoices":
        show_invoices_page()
    elif page == "Vendors":
        show_vendors_page()
    elif page == "Bills":
        show_bills_page()
    elif page == "Expenses":
        show_expenses_page()
    elif page == "Bank Transactions":
        show_bank_transactions_page()
    elif page == "Transaction Analysis":
        show_transaction_analysis_page()

    # Sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built with Streamlit")
    
    # Add a "Back to Welcome" button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("Back to Welcome"):
        st.session_state.app_started = False
        st.rerun() 