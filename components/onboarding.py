import streamlit as st
import json
import time
import os
import logging
from setup_logic import get_gemini_model

# Set up logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_chat_session():
    """Initialize the chat session state"""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "chat_stage" not in st.session_state:
        st.session_state.chat_stage = "welcome"
    
    if "financial_data" not in st.session_state:
        st.session_state.financial_data = {
            "general_info": {},
            "business_questions": {
                "business_type": "",
                "money_in": "",
                "money_out": ""
            },
            "assets": {},
            "liabilities": {},
            "equity": {},
            "completed": False
        }
    
    if "current_category" not in st.session_state:
        st.session_state.current_category = "general_info"

def get_welcome_message():
    """Get the initial welcome message from the AI"""
    return """Hello! I'm your AI accounting assistant. I'll help you set up your company's financial information through a friendly conversation.

I need to collect information about:
**General Company Information**
**Assets** (Cash, Accounts Receivable, Inventory, etc.)
**Liabilities** (Accounts Payable, Loans, etc.)
**Equity** (Stock, Retained Earnings, etc.)

Let's start with some basic information about your company. What's your company name?"""

def get_ai_response(user_message, chat_history, current_stage, financial_data):
    """Get AI response based on current conversation stage"""
    try:
        model = get_gemini_model()
        
        # Build context based on current stage and collected data
        context = f"""
You are an expert accounting assistant helping to collect comprehensive financial information for a company's balance sheet setup.

Current collection stage: {current_stage}
Data collected so far: {json.dumps(financial_data, indent=2)}

INFORMATION TO COLLECT:

1. GENERAL INFO:
   - Company Name
   - Reporting Date

2. ASSETS:
   - Cash
   - Accounts Receivable
   - Inventory
   - Prepaid Expenses
   - Investments
   - Property, Plant & Equipment (PP&E)
   - Intangible Assets (Patents, Trademarks)
   - Other Assets

3. LIABILITIES:
   - Accounts Payable
   - Short-term Loans
   - Accrued Expenses
   - Taxes Payable
   - Long-term Debt
   - Lease Obligations
   - Other Liabilities

4. EQUITY:
   - Common Stock
   - Preferred Stock
   - Retained Earnings
   - Additional Paid-in Capital
   - Treasury Stock

INSTRUCTIONS:
- Ask ONE question at a time
- Be conversational and friendly
- Guide the user through each category systematically
- Ask for specific dollar amounts when appropriate
- Clarify if user says "none" or "zero" for any item
- Move to next category when current one is complete
- When ALL information is collected, say "COLLECTION_COMPLETE" and provide a summary
- DO NOT use emojis in your responses - keep all text clean and professional

USER MESSAGE: {user_message}

CONVERSATION HISTORY:
{chat_history}

Respond naturally and ask the next appropriate question:
"""

        response = model.generate_content(context)
        return response.text

    except Exception as e:
        return f"I apologize, but I'm having trouble connecting right now. Error: {str(e)}. Please try asking your question again."

def extract_financial_info(conversation_text, financial_data):
    """Extract and structure financial information from conversation"""
    try:
        logger.info("Starting financial info extraction...")
        model = get_gemini_model()
        logger.info("Gemini model loaded successfully")
        
        prompt = f"""
        You are extracting financial information from a conversation. Look for company name, financial amounts, and dates.

        CONVERSATION:
        {conversation_text}

        Find any of these and update the JSON structure:
        - Company name (look for business names)
        - Cash amounts (look for dollar amounts, cash mentions)
        - Any financial figures mentioned
        - Dates mentioned for reporting

        IMPORTANT: Do NOT modify business_questions if they are marked as locked.

        Current data: {json.dumps(financial_data, indent=2)}

        Return ONLY this JSON structure with any new information filled in:
        {{
            "general_info": {{
                "company_name": "",
                "reporting_date": ""
            }},
            "business_questions": {{
                "business_type": "",
                "money_in": "",
                "money_out": ""
            }},
            "assets": {{
        "cash": "",
        "accounts_receivable": "",
        "inventory": "",
        "prepaid_expenses": "",
        "investments": "",
        "property_plant_equipment": "",
        "intangible_assets": "",
        "other_assets": ""
    }},
    "liabilities": {{
        "accounts_payable": "",
        "short_term_loans": "",
        "accrued_expenses": "",
        "taxes_payable": "",
        "long_term_debt": "",
        "lease_obligations": "",
        "other_liabilities": ""
    }},
    "equity": {{
        "common_stock": "",
        "preferred_stock": "",
        "retained_earnings": "",
        "additional_paid_in_capital": "",
        "treasury_stock": ""
    }}
}}
        """
        
        logger.info(f"Sending prompt to Gemini API (length: {len(prompt)})")
        response = model.generate_content(prompt)
        logger.info(f"Received response from Gemini API")
        
        # Log successful extraction to terminal
        logger.info("="*50)
        logger.info("EXTRACTION SUCCESS:")
        logger.info(f"AI Response: {response.text[:200]}...")
        logger.info(f"Conversation length: {len(conversation_text)}")
        
        # Clean the response text to remove markdown code blocks
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove ```
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        logger.info(f"Extracted data: {result}")
        logger.info("="*50)
        
        return result
        
    except Exception as e:
        # Log to terminal/console
        error_msg = f"Error extracting financial info: {str(e)}"
        if 'response' in locals() and hasattr(response, 'text'):
            ai_response_msg = f"AI Response was: {response.text}"
        elif 'response' in locals():
            ai_response_msg = f"AI Response object: {response}"
        else:
            ai_response_msg = "No response received - API call failed"
        
        logger.error("="*50)
        logger.error("EXTRACTION ERROR:")
        logger.error(error_msg)
        logger.error(ai_response_msg)
        logger.error(f"Conversation text length: {len(conversation_text)}")
        logger.error(f"Financial data: {financial_data}")
        logger.error("="*50)
        
        # Also store in session state
        if "extraction_errors" not in st.session_state:
            st.session_state.extraction_errors = []
        st.session_state.extraction_errors.append(f"{error_msg} | {ai_response_msg}")
        
        st.error(error_msg)
        st.error(ai_response_msg)
        
        # Try simple text parsing as fallback
        logger.info("Attempting fallback text extraction...")
        fallback_data = simple_text_extraction(conversation_text, financial_data)
        return fallback_data

def simple_text_extraction(conversation_text, financial_data):
    """Simple text-based extraction as fallback when AI fails"""
    try:
        updated_data = financial_data.copy()
        text = conversation_text.lower()
        
        # Extract company name
        if not updated_data.get("general_info", {}).get("company_name"):
            # Look for common patterns
            import re
            company_patterns = [
                r"company name is ([^.!?\n]+)",
                r"my company is ([^.!?\n]+)",
                r"business is ([^.!?\n]+)",
                r"called ([^.!?\n]+)",
                r"company ([^.!?\n]+)"
            ]
            for pattern in company_patterns:
                match = re.search(pattern, text)
                if match:
                    company_name = match.group(1).strip().title()
                    if len(company_name) > 1 and len(company_name) < 50:
                        updated_data.setdefault("general_info", {})["company_name"] = company_name
                        logger.info(f"Fallback extracted company name: {company_name}")
                        break
        
        # Extract business questions answers only if not locked
        business_questions = updated_data.setdefault("business_questions", {})
        
        # Skip business questions extraction if they are locked
        if not business_questions.get("locked", False):
            # Look for business type descriptions
            if not business_questions.get("business_type"):
                business_patterns = [
                    r"(?:business|company).*?(?:is|does|offers?|provides?|sells?)\s+([^.!?\n]{10,200})",
                    r"we (?:run|operate|have)\s+(?:a|an)?\s*([^.!?\n]{10,200})",
                    r"(?:type|kind) of business.*?(?:is|:)\s*([^.!?\n]{10,200})"
                ]
                for pattern in business_patterns:
                    match = re.search(pattern, text)
                    if match:
                        business_type = match.group(1).strip()
                        if len(business_type) > 10:
                            business_questions["business_type"] = business_type
                            logger.info(f"Fallback extracted business type: {business_type}")
                            break
            
            # Look for money in descriptions
            if not business_questions.get("money_in"):
                money_in_patterns = [
                    r"money comes? in.*?(?:from|through|via)\s+([^.!?\n]{5,200})",
                    r"(?:revenue|income|payments?).*?(?:from|through|via)\s+([^.!?\n]{5,200})",
                    r"get paid.*?(?:from|through|via)\s+([^.!?\n]{5,200})"
                ]
                for pattern in money_in_patterns:
                    match = re.search(pattern, text)
                    if match:
                        money_in = match.group(1).strip()
                        if len(money_in) > 5:
                            business_questions["money_in"] = money_in
                            logger.info(f"Fallback extracted money in: {money_in}")
                            break
            
            # Look for money out descriptions
            if not business_questions.get("money_out"):
                money_out_patterns = [
                    r"money goes?.*?(?:to|on|for)\s+([^.!?\n]{5,200})",
                    r"(?:expenses?|costs?|spend).*?(?:on|for)\s+([^.!?\n]{5,200})",
                    r"usually spend.*?(?:on|for)\s+([^.!?\n]{5,200})"
                ]
                for pattern in money_out_patterns:
                    match = re.search(pattern, text)
                    if match:
                        money_out = match.group(1).strip()
                        if len(money_out) > 5:
                            business_questions["money_out"] = money_out
                            logger.info(f"Fallback extracted money out: {money_out}")
                            break
        else:
            logger.info("Business questions are locked - skipping extraction")
        
        # Extract cash amounts
        cash_patterns = [
            r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:in\s+)?cash",
            r"cash.*?\$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?\s+cash"
        ]
        for pattern in cash_patterns:
            match = re.search(pattern, text)
            if match:
                cash_amount = match.group(1)
                updated_data.setdefault("assets", {})["cash"] = f"${cash_amount}"
                logger.info(f"Fallback extracted cash: ${cash_amount}")
                break
        
        return updated_data
        
    except Exception as e:
        logger.error(f"Fallback extraction failed: {e}")
        return financial_data

def display_chat_interface(completed_fields=0, business_questions_complete=False):
    """Display the chat interface"""
    st.title("Financial Information Chat")
    st.markdown("---")
    
    # Display progress information
    st.subheader("Collection Progress")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completed Fields", f"{completed_fields}/25")
    with col2:
        completion_rate = (completed_fields / 25) * 100
        st.metric("Progress", f"{completion_rate:.1f}%")
    with col3:
        status = "Complete" if business_questions_complete else "Required"
        st.metric("Business Questions", status)
    
    st.progress(completed_fields / 25)
    
    # Always show business questions form (sticky)
    st.subheader("Required Business Questions")
    
    # Get current business questions data
    business_questions = st.session_state.financial_data.get("business_questions", {})
    
    if business_questions_complete:
        # Show static (read-only) version when complete
        st.success("All business questions completed and locked!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**1. What type of business do you have, and what do you offer?**")
            st.info(business_questions.get("business_type", ""))
        
        with col2:
            st.markdown("**2. How does money come in?**")
            st.info(business_questions.get("money_in", ""))
        
        with col3:
            st.markdown("**3. Where does your money usually go?**")
            st.info(business_questions.get("money_out", ""))
            
        st.markdown("**Status:** ✅ Locked - Questions cannot be modified once saved")
    
    else:
        # Show editable form when incomplete
        st.warning("Please complete all 3 business questions to enable AI chat.")
        
        with st.form("business_questions_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**1. What type of business do you have, and what do you offer?**")
                business_type = st.text_area(
                    "Business Type & Offerings:",
                    value=business_questions.get("business_type", ""),
                    height=120,
                    help="Tell us about your business type, products, or services you provide.",
                    key="business_type_direct"
                )
            
            with col2:
                st.markdown("**2. How does money come in?**")
                money_in = st.text_area(
                    "Revenue Sources:",
                    value=business_questions.get("money_in", ""),
                    height=120,
                    help="Describe your revenue sources, how customers pay you, and income streams.",
                    key="money_in_direct"
                )
            
            with col3:
                st.markdown("**3. Where does your money usually go?**")
                money_out = st.text_area(
                    "Main Expenses:",
                    value=business_questions.get("money_out", ""),
                    height=120,
                    help="List your main expenses, costs, and where you spend business money.",
                    key="money_out_direct"
                )
            
            # Submit button for the form
            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submitted = st.form_submit_button("Save Business Information", type="primary", use_container_width=True)
            
            if submitted:
                # Validate all fields are filled
                if not (business_type.strip() and money_in.strip() and money_out.strip()):
                    st.error("Please fill in all 3 fields before saving.")
                    return
                
                # Update the business questions in session state
                st.session_state.financial_data.setdefault("business_questions", {})
                st.session_state.financial_data["business_questions"]["business_type"] = business_type.strip()
                st.session_state.financial_data["business_questions"]["money_in"] = money_in.strip()
                st.session_state.financial_data["business_questions"]["money_out"] = money_out.strip()
                
                # Mark as locked
                st.session_state.financial_data["business_questions"]["locked"] = True
                
                # Save the data
                save_financial_data_incremental()
                
                # Show success message
                st.success("All business questions saved and locked! AI chat is now enabled.")
                
                # Refresh the page to show static version
                st.rerun()
    
    st.markdown("---")
    
    # AI Chat section - only enabled if business questions are complete
    if business_questions_complete:
        st.subheader("AI-Guided Financial Data Collection")
        st.write("Now that your business questions are complete, you can start detailed data collection with AI assistance.")
        
        # Show start session button
        if "chat_session_started" not in st.session_state:
            st.session_state.chat_session_started = False
        
        if not st.session_state.chat_session_started:
            if st.button("Start AI Chat Session", type="primary"):
                st.session_state.chat_session_started = True
                welcome_msg = get_welcome_message()
                st.session_state.chat_messages.append({"role": "assistant", "content": welcome_msg})
                save_financial_data_incremental()
                st.rerun()
        else:
            # Show the chat interface
            display_chat_messages()
    else:
        st.subheader("AI Chat (Disabled)")
        st.info("Complete all 3 business questions above to enable AI-guided data collection.")
        st.text_area("AI Chat will appear here...", disabled=True, height=100)
    
    # Custom CSS for better chat layout
    st.markdown("""
    <style>
    /* Remove avatars/icons */
    .stChatMessage .stChatMessageAvatar {
        display: none !important;
    }
    
    /* User messages on the right */
    .stChatMessage[data-testid="user-message"] {
        flex-direction: row-reverse;
        text-align: right;
        margin-left: 20%;
        margin-right: 0;
    }
    
    /* Assistant messages on the left */
    .stChatMessage[data-testid="assistant-message"] {
        text-align: left;
        margin-left: 0;
        margin-right: 20%;
    }
    
    /* Style the message content */
    .stChatMessage[data-testid="user-message"] .stMarkdown {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stMarkdown {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
def display_chat_messages():
    """Display the actual chat interface"""
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.chat_messages:
            if message["role"] == "assistant":
                # AI messages on the left
                with st.chat_message("assistant"):
                    st.write(message["content"])
            else:
                # User messages on the right
                with st.chat_message("user"):
                    st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your response here..."):
        # Immediately show user message on the right
        with st.chat_message("user"):
            st.write(prompt)
        
        # Add user message to session state
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get conversation history for context
        chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_messages[-10:]])
        
        # Get AI response with streaming on the left
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Show typing indicator
            message_placeholder.markdown("Thinking...")
            
            # Get AI response
            ai_response = get_ai_response(
                prompt, 
                chat_history, 
                st.session_state.chat_stage,
                st.session_state.financial_data
            )
            
            # Simulate streaming by showing response progressively
            words = ai_response.split()
            for i, word in enumerate(words):
                full_response += word + " "
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.02)  # Small delay for streaming effect
            
            # Final response without cursor
            message_placeholder.markdown(full_response)
        
        # Check if collection is complete
        if "COLLECTION_COMPLETE" in ai_response:
            st.session_state.chat_stage = "complete"
            ai_response = ai_response.replace("COLLECTION_COMPLETE", "").strip()
            
            # Extract final financial information
            full_conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_messages])
            st.session_state.financial_data = extract_financial_info(full_conversation, st.session_state.financial_data)
            st.session_state.financial_data["completed"] = True
            
            # Save to file
            save_financial_data()
        
        # Add AI response
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
        
        # Extract and update financial info from conversation after every message
        full_conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_messages])
        
        # Preserve locked business questions before extraction
        locked_business_questions = None
        if st.session_state.financial_data.get("business_questions", {}).get("locked", False):
            locked_business_questions = st.session_state.financial_data["business_questions"].copy()
        
        # Extract new data
        st.session_state.financial_data = extract_financial_info(full_conversation, st.session_state.financial_data)
        
        # Restore locked business questions if they were overwritten
        if locked_business_questions:
            st.session_state.financial_data["business_questions"] = locked_business_questions
        
        # Save data after each message
        save_financial_data_incremental()
        logger.info(f"CHAT UPDATE: Message count: {len(st.session_state.chat_messages)}, Last message: {st.session_state.chat_messages[-1]['content'][:100] if st.session_state.chat_messages else 'None'}...")
        
        st.rerun()

def save_financial_data():
    """Save collected financial data to JSON file"""
    try:
        financial_data = st.session_state.financial_data
        financial_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Save all data in onboarding_responses.json
        with open("onboarding_responses.json", 'w') as f:
            json.dump(financial_data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

def save_financial_data_incremental():
    """Save financial data incrementally after each user interaction"""
    try:
        financial_data = st.session_state.financial_data.copy()
        financial_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        financial_data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Save all data in onboarding_responses.json
        with open("onboarding_responses.json", 'w') as f:
            json.dump(financial_data, f, indent=2)
            
    except Exception as e:
        # Log to terminal/console
        save_error_msg = f"Error in incremental save: {str(e)}"
        data_msg = f"Financial data: {st.session_state.financial_data}"
        
        logger.error("="*50)
        logger.error("SAVE ERROR:")
        logger.error(save_error_msg)
        logger.error(data_msg)
        logger.error("="*50)
        
        # Also store in session state
        if "save_errors" not in st.session_state:
            st.session_state.save_errors = []
        st.session_state.save_errors.append(f"{save_error_msg} | {data_msg}")
        
        st.error(save_error_msg)
        st.error(data_msg)
        pass

def display_collected_data():
    """Display the collected financial information"""
    st.title("Financial Information Collected")
    st.markdown("---")
    
    financial_data = st.session_state.financial_data
    
    # General Information
    st.subheader("General Information")
    general_info = financial_data.get("general_info", {})
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Company Name:** {general_info.get('company_name', 'Not provided')}")
    with col2:
        st.write(f"**Reporting Date:** {general_info.get('reporting_date', 'Not provided')}")
    
    # Assets
    st.subheader("Assets")
    assets = financial_data.get("assets", {})
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Cash:** {assets.get('cash', 'Not provided')}")
        st.write(f"**Accounts Receivable:** {assets.get('accounts_receivable', 'Not provided')}")
        st.write(f"**Inventory:** {assets.get('inventory', 'Not provided')}")
        st.write(f"**Prepaid Expenses:** {assets.get('prepaid_expenses', 'Not provided')}")
    with col2:
        st.write(f"**Investments:** {assets.get('investments', 'Not provided')}")
        st.write(f"**Property, Plant & Equipment:** {assets.get('property_plant_equipment', 'Not provided')}")
        st.write(f"**Intangible Assets:** {assets.get('intangible_assets', 'Not provided')}")
        st.write(f"**Other Assets:** {assets.get('other_assets', 'Not provided')}")
    
    # Liabilities
    st.subheader("Liabilities")
    liabilities = financial_data.get("liabilities", {})
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Accounts Payable:** {liabilities.get('accounts_payable', 'Not provided')}")
        st.write(f"**Short-term Loans:** {liabilities.get('short_term_loans', 'Not provided')}")
        st.write(f"**Accrued Expenses:** {liabilities.get('accrued_expenses', 'Not provided')}")
        st.write(f"**Taxes Payable:** {liabilities.get('taxes_payable', 'Not provided')}")
    with col2:
        st.write(f"**Long-term Debt:** {liabilities.get('long_term_debt', 'Not provided')}")
        st.write(f"**Lease Obligations:** {liabilities.get('lease_obligations', 'Not provided')}")
        st.write(f"**Other Liabilities:** {liabilities.get('other_liabilities', 'Not provided')}")
    
    # Equity
    st.subheader("Equity")
    equity = financial_data.get("equity", {})
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Common Stock:** {equity.get('common_stock', 'Not provided')}")
        st.write(f"**Preferred Stock:** {equity.get('preferred_stock', 'Not provided')}")
        st.write(f"**Retained Earnings:** {equity.get('retained_earnings', 'Not provided')}")
    with col2:
        st.write(f"**Additional Paid-in Capital:** {equity.get('additional_paid_in_capital', 'Not provided')}")
        st.write(f"**Treasury Stock:** {equity.get('treasury_stock', 'Not provided')}")
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start New Chat", type="secondary"):
            # Clear chat session
            for key in ["chat_messages", "chat_stage", "financial_data", "current_category"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("Continue to Setup", type="primary"):
            st.success("Financial data saved! You can now proceed to the Setup page to generate your chart of accounts.")

def count_completed_fields(financial_data):
    """Count completed fields in financial data"""
    count = 0
    
    # Count general_info fields (2 fields)
    general_info = financial_data.get("general_info", {})
    for value in general_info.values():
        if value and str(value).strip():
            count += 1
    
    # Count business_questions fields (3 fields, exclude "locked" metadata)
    business_questions = financial_data.get("business_questions", {})
    for key, value in business_questions.items():
        if key != "locked" and value and str(value).strip():
            count += 1
    
    # Count assets fields (8 fields)
    assets = financial_data.get("assets", {})
    for value in assets.values():
        if value and str(value).strip():
            count += 1
    
    # Count liabilities fields (7 fields)
    liabilities = financial_data.get("liabilities", {})
    for value in liabilities.values():
        if value and str(value).strip():
            count += 1
    
    # Count equity fields (5 fields)
    equity = financial_data.get("equity", {})
    for value in equity.values():
        if value and str(value).strip():
            count += 1
    
    return count

def check_business_questions_complete(financial_data):
    """Check if all 3 business questions are completed and locked"""
    business_questions = financial_data.get("business_questions", {})
    required_questions = ["business_type", "money_in", "money_out"]
    
    # Check if all questions are answered
    for question in required_questions:
        if not business_questions.get(question, "").strip():
            return False
    
    # Check if they are locked (saved)
    return business_questions.get("locked", False)

def show_onboarding_page():
    """Main onboarding page function"""
    # Check if financial data already exists
    if os.path.exists("onboarding_responses.json"):
        try:
            with open("onboarding_responses.json", 'r') as f:
                saved_data = json.load(f)
            
            # Check if it's the new format and completed
            if isinstance(saved_data, dict) and any(key in saved_data for key in ["general_info", "assets", "liabilities", "equity"]):
                if saved_data.get("completed", False):
                    st.session_state.financial_data = saved_data
                    st.session_state.chat_stage = "complete"
                    display_collected_data()
                    return
                else:
                    # Load in-progress data
                    st.session_state.financial_data = saved_data
        except:
            pass
    
    # Initialize chat session
    initialize_chat_session()
    
    # Check completion status
    completed_fields = count_completed_fields(st.session_state.financial_data)
    business_questions_complete = check_business_questions_complete(st.session_state.financial_data)
    all_complete = completed_fields >= 25
    
    # Display appropriate interface
    if all_complete:
        st.session_state.financial_data["completed"] = True
        save_financial_data_incremental()
        st.session_state.chat_stage = "complete"
        display_collected_data()
    else:
        display_chat_interface(completed_fields, business_questions_complete)
        
        # Show sidebar information
        with st.sidebar:
            # Show persistent errors
            if "extraction_errors" in st.session_state and st.session_state.extraction_errors:
                st.markdown("---")
                st.subheader("Extraction Errors")
                for error in st.session_state.extraction_errors[-3:]:  # Show last 3 errors
                    st.error(error)
                    
            if "save_errors" in st.session_state and st.session_state.save_errors:
                st.markdown("---")
                st.subheader("Save Errors")
                for error in st.session_state.save_errors[-3:]:  # Show last 3 errors
                    st.error(error)
                    
            # Debug info
            st.markdown("---")
            st.subheader("Debug Info")
            st.write(f"Messages: {len(st.session_state.chat_messages) if 'chat_messages' in st.session_state else 0}")
            if st.button("Clear Error Log"):
                if "extraction_errors" in st.session_state:
                    st.session_state.extraction_errors = []
                if "save_errors" in st.session_state:
                    st.session_state.save_errors = []
                st.rerun() 