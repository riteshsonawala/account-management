import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from models import Account, AccountSummary

app = FastAPI(
    title="Account Management API",
    description="API for managing AWS accounts",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).parent.parent / "data" / "accounts.json"


def load_accounts() -> list[dict]:
    with open(DATA_FILE) as f:
        return json.load(f)


@app.get("/")
def root():
    return {"message": "Account Management API", "version": "1.0.0"}


@app.get("/accounts", response_model=list[AccountSummary])
def list_accounts(
    tenant: Optional[str] = Query(None, description="Filter by tenant name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    account_category: Optional[str] = Query(None, description="Filter by account category (Execution or Analytics)"),
):
    """List all accounts with optional filters."""
    accounts = load_accounts()

    if tenant:
        accounts = [
            a for a in accounts if tenant.lower() in a["tenant"].lower()
        ]

    if status:
        accounts = [
            a for a in accounts if status.lower() == a["status"].lower()
        ]

    if environment:
        accounts = [
            a for a in accounts if environment.lower() in a["environment"].lower()
        ]

    if account_category:
        accounts = [
            a for a in accounts if account_category.lower() == a["accountCategory"].lower()
        ]

    return [
        AccountSummary(
            accountNumber=a["accountNumber"],
            tenant=a["tenant"],
            team=a["team"],
            environment=a["environment"],
            status=a["status"],
            region=a["region"],
            accountCategory=a["accountCategory"],
        )
        for a in accounts
    ]


@app.get("/accounts/{account_number}", response_model=Account)
def get_account(account_number: int):
    """Get detailed information about a specific account."""
    accounts = load_accounts()

    for account in accounts:
        if account["accountNumber"] == account_number:
            return Account(**account)

    raise HTTPException(status_code=404, detail="Account not found")


@app.get("/tenants", response_model=list[str])
def list_tenants():
    """List all unique tenant names."""
    accounts = load_accounts()
    tenants = sorted(set(a["tenant"] for a in accounts))
    return tenants


@app.get("/stats")
def get_stats():
    """Get statistics about accounts."""
    accounts = load_accounts()

    status_counts = {}
    tenant_counts = {}
    region_counts = {}
    env_counts = {}

    for a in accounts:
        status_counts[a["status"]] = status_counts.get(a["status"], 0) + 1
        tenant_counts[a["tenant"]] = tenant_counts.get(a["tenant"], 0) + 1
        region_counts[a["region"]] = region_counts.get(a["region"], 0) + 1
        env = a["environment"].split("(")[0].strip()
        env_counts[env] = env_counts.get(env, 0) + 1

    return {
        "total_accounts": len(accounts),
        "by_status": status_counts,
        "by_tenant": tenant_counts,
        "by_region": region_counts,
        "by_environment": env_counts,
    }