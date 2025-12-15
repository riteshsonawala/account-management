# Account Management

A web application for managing AWS accounts with a FastAPI backend and Streamlit UI.

## Setup

```bash
cd ~/Projects/account-management
pip install -r requirements.txt
```

## Running the Application

### 1. Start the API Server

```bash
cd ~/Projects/account-management/api
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

### 2. Start the Streamlit UI

In a separate terminal:

```bash
cd ~/Projects/account-management/ui
streamlit run app.py
```

The UI will be available at http://localhost:8501

## API Endpoints

- `GET /accounts` - List all accounts (with optional filters: tenant, status, environment)
- `GET /accounts/{account_number}` - Get detailed info for a specific account
- `GET /tenants` - List all unique tenant names
- `GET /stats` - Get account statistics

## Project Structure

```
account-management/
├── api/
│   ├── main.py      # FastAPI application
│   └── models.py    # Pydantic models
├── ui/
│   └── app.py       # Streamlit application
├── data/
│   └── accounts.json # Sample data
├── requirements.txt
└── README.md
```
