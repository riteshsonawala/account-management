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

# Default values for account fields
DEFAULT_ACCOUNT_CATEGORY = "Execution"


def normalize_account(account: dict) -> dict:
    """Normalize account data by applying defaults for missing/empty fields."""
    normalized = account.copy()

    # Default accountCategory to "Execution" if missing or empty
    if not normalized.get("accountCategory"):
        normalized["accountCategory"] = DEFAULT_ACCOUNT_CATEGORY

    # Ensure string fields have at least empty string defaults
    string_fields = [
        "accountType", "tenant", "team", "type", "region", "barclaysOu",
        "environment", "adGroupCoreRoles", "serviceFirstItba", "serviceFirstItbs", "status"
    ]
    for field in string_fields:
        if normalized.get(field) is None:
            normalized[field] = ""

    # Ensure access info exists with defaults
    if not normalized.get("access"):
        normalized["access"] = {"readOnlyAD": "", "writeAD": ""}
    else:
        if normalized["access"].get("readOnlyAD") is None:
            normalized["access"]["readOnlyAD"] = ""
        if normalized["access"].get("writeAD") is None:
            normalized["access"]["writeAD"] = ""

    return normalized


def load_accounts() -> list[dict]:
    with open(DATA_FILE) as f:
        accounts = json.load(f)
    return [normalize_account(a) for a in accounts]


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
    # Filter out empty tenant names
    tenants = sorted(set(a.get("tenant") or "" for a in accounts if a.get("tenant")))
    return tenants


@app.get("/stats")
def get_stats():
    """Get statistics about accounts."""
    accounts = load_accounts()

    status_counts = {}
    tenant_counts = {}
    region_counts = {}
    env_counts = {}
    category_counts = {}

    for a in accounts:
        # Handle potentially empty fields with defaults
        status = a.get("status") or "Unknown"
        tenant = a.get("tenant") or "Unknown"
        region = a.get("region") or "Unknown"
        environment = a.get("environment") or ""
        category = a.get("accountCategory") or "Execution"

        status_counts[status] = status_counts.get(status, 0) + 1
        tenant_counts[tenant] = tenant_counts.get(tenant, 0) + 1
        region_counts[region] = region_counts.get(region, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1

        # Safely parse environment
        env = environment.split("(")[0].strip() if environment else "Unknown"
        env_counts[env] = env_counts.get(env, 0) + 1

    return {
        "total_accounts": len(accounts),
        "by_status": status_counts,
        "by_tenant": tenant_counts,
        "by_region": region_counts,
        "by_environment": env_counts,
        "by_category": category_counts,
    }