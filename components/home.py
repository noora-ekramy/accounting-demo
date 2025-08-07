import streamlit as st
import time
from setup_logic import load_onboarding_data
import os
from openai import OpenAI

def upload_files_to_openai():
    """Upload CSV files to OpenAI and create assistant with code interpreter"""
    try:
        # Get API key from environment or Streamlit secrets
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not found. Please add it to your .env file or Streamlit secrets.")
            return None, []
        
        client = OpenAI(api_key=api_key)
        
        file_ids = []
        csv_files = ["accounts.csv", "invoices.csv", "bills.csv", "expenses.csv"]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Upload files
        for i, filename in enumerate(csv_files):
            filepath = os.path.join("anonymized_data", filename)
            if os.path.exists(filepath):
                status_text.text(f"Uploading {filename}...")
                
                with open(filepath, "rb") as file:
                    uploaded_file = client.files.create(
                        file=file,
                        purpose="assistants"
                    )
                    file_ids.append(uploaded_file.id)
                
                progress_bar.progress((i + 1) / len(csv_files))
        
        # Create assistant with code interpreter
        status_text.text("Creating AI assistant with code interpreter...")
        assistant = client.beta.assistants.create(
            name="Accounting Test Data Analyst",
            instructions="You are an expert accounting data analyst. Analyze accounting data and provide insights.",
            model="gpt-4-turbo-preview",
            tools=[{"type": "code_interpreter"}],
            file_ids=file_ids
        )
        
        status_text.text("Setup complete!")
        progress_bar.progress(1.0)
        
        return assistant, file_ids
        
    except Exception as e:
        st.error(f"Error setting up OpenAI: {str(e)}")
        return None, []

def start_session():
    """Start Session function - Upload files to OpenAI and create assistant"""
    try:
        assistant, file_ids = upload_files_to_openai()
        if assistant and file_ids:
            st.session_state.assistant = assistant
            st.session_state.file_ids = file_ids
            return f"Session started successfully! Created AI assistant with {len(file_ids)} files for code interpreter analysis."
        else:
            return "Session started but failed to create assistant or upload files."
    except Exception as e:
        return f"Error starting session: {str(e)}"

def show_home_page():
    """Display the home page"""
    st.title("Accounting Test System")
    st.markdown("---")
    st.write("Welcome to your comprehensive accounting test system.")
    
    # Session Management
    st.subheader("Session Management")
    
    # Initialize session state
    if "session_active" not in st.session_state:
        st.session_state.session_active = False
    
    # Start Session button
    if not st.session_state.session_active:
        if st.button("Start Session", type="primary"):
            result = start_session()
            st.success(result)
            st.rerun()
    else:
        st.success("Session is active")
        if st.button("End Session"):
            st.session_state.session_active = False
            st.rerun()
    
    # Analysis tool (only show if session is active)
    if st.session_state.session_active:
        st.markdown("---")
        st.subheader("AI Analysis Tool")
        
        analysis_input = st.text_area("Enter text for analysis:", placeholder="Type your analysis request here...")
        
        if st.button("Analyze"):
            if analysis_input:
                st.info("Analysis functionality will be implemented here.")
            else:
                st.warning("Please enter some text to analyze.")
    else:
        st.warning("Please start a session to use the analysis tool.")
        st.text_area("Enter text for analysis:", placeholder="Type your text here...", disabled=True)
        st.button("Analyze", disabled=True)
    
 