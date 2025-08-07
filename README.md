# Accounting Demo System

A comprehensive AI-powered accounting management system built with Streamlit that helps businesses manage their financial data with intelligent automation.

## Features

- **AI-Powered Onboarding**: Conversational setup process for business information
- **Smart Chart of Accounts**: Auto-generated based on business type and financial data
- **Transaction Analysis**: AI categorization and double-entry bookkeeping suggestions
- **Customer & Vendor Management**: Integrated relationship tracking
- **Invoice & Bill Management**: Professional document creation
- **Expense Tracking**: Category-based expense management with AI insights

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd accounting-demo
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Setup
1. Copy the template file:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` and add your actual API keys:
   ```bash
   # OpenAI API Key (for GPT analysis features)
   OPENAI_API_KEY="your-actual-openai-api-key"
   
   # Google/Gemini API Key (for AI chart generation)
   GOOGLE_API_KEY="your-actual-google-api-key"
   GEMINI_API_KEY="your-actual-gemini-api-key"
   ```

### 4. Run the Application
```bash
streamlit run app.py
```

## API Keys Required

- **OpenAI API Key**: Used for advanced transaction analysis and AI insights
- **Google/Gemini API Key**: Used for generating customized chart of accounts and business data

## Project Structure

```
accounting-demo/
├── app.py                      # Main Streamlit application
├── setup_logic.py             # AI setup and data generation logic
├── components/                 # Page components
│   ├── onboarding.py          # AI-powered onboarding
│   ├── accounts.py            # Chart of accounts management
│   ├── bank_transactions.py   # Transaction processing
│   ├── transaction_analysis.py # AI transaction analysis
│   ├── customers.py           # Customer management
│   ├── vendors.py             # Vendor management
│   ├── invoices.py            # Invoice creation
│   ├── bills.py               # Bill management
│   └── expenses.py            # Expense tracking
├── anonymized_data/           # Sample financial data
└── requirements.txt           # Python dependencies
```

## Usage

1. **Start with Onboarding**: Complete the AI-guided setup process
2. **Review Generated Accounts**: Check the AI-created chart of accounts
3. **Import Transactions**: Add bank transactions for analysis
4. **Use AI Analysis**: Get intelligent categorization suggestions
5. **Manage Relationships**: Track customers and vendors
6. **Create Documents**: Generate invoices and bills

## Security Note

- Never commit API keys to version control
- Use the `.env.template` file as a reference
- Keep your actual `.env` file local and private

## Demo Data

The system includes sample data for "X Software", a software/hardware company, demonstrating:
- Complete chart of accounts with realistic balances
- Customer profiles with detailed relationship information
- Vendor management with supplier details
- Expense categories with AI-generated insights 