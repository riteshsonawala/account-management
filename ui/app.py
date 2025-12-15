import requests
import streamlit as st
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Account Management",
    page_icon="☁️",
    layout="wide",
)

# Initialize session state
if "view" not in st.session_state:
    st.session_state.view = "list"
if "selected_account" not in st.session_state:
    st.session_state.selected_account = None


def navigate_to_details(account_number: int):
    st.session_state.selected_account = account_number
    st.session_state.view = "details"


def navigate_to_list():
    st.session_state.view = "list"
    st.session_state.selected_account = None


@st.cache_data(ttl=60)
def fetch_accounts(tenant: str = None, status: str = None, environment: str = None, account_category: str = None):
    params = {}
    if tenant:
        params["tenant"] = tenant
    if status:
        params["status"] = status
    if environment:
        params["environment"] = environment
    if account_category:
        params["account_category"] = account_category

    response = requests.get(f"{API_URL}/accounts", params=params)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60)
def fetch_account_details(account_number: int):
    response = requests.get(f"{API_URL}/accounts/{account_number}")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60)
def fetch_tenants():
    response = requests.get(f"{API_URL}/tenants")
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60)
def fetch_stats():
    response = requests.get(f"{API_URL}/stats")
    response.raise_for_status()
    return response.json()


def render_details_view():
    """Render the account details screen."""
    if st.button("← Back to Accounts", type="secondary"):
        navigate_to_list()
        st.rerun()

    if st.session_state.selected_account is None:
        st.warning("No account selected.")
        return

    try:
        details = fetch_account_details(st.session_state.selected_account)
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to load account details: {e}")
        return

    st.title(f"Account Details")
    st.markdown(f"### {details['tenant']} - {details['accountNumber']}")

    st.divider()

    # Basic Information
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Basic Information")
        info_data = {
            "Account Type": details["accountType"],
            "Account Number": details["accountNumber"],
            "Tenant": details["tenant"],
            "Team": details["team"],
            "Type": details["type"],
            "Region": details["region"],
            "Status": details["status"],
            "Account Category": details["accountCategory"],
        }
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")

    with col2:
        st.markdown("#### Configuration")
        config_data = {
            "Barclays OU": details["barclaysOu"],
            "Environment": details["environment"],
            "AD Group Core Roles": details["adGroupCoreRoles"],
            "Service First ITBA": details["serviceFirstItba"],
            "Service First ITBS": details["serviceFirstItbs"],
        }
        if details.get("accountLimit"):
            config_data["Account Limit"] = details["accountLimit"]
        for key, value in config_data.items():
            st.write(f"**{key}:** {value}")

    st.divider()

    # Access Information
    st.markdown("#### Access Information")
    access_col1, access_col2 = st.columns(2)
    with access_col1:
        st.write(f"**Read-Only AD:** {details['access']['readOnlyAD']}")
    with access_col2:
        st.write(f"**Write AD:** {details['access']['writeAD']}")


def render_list_view():
    """Render the accounts list view with table."""
    st.title("AWS Account Management")

    try:
        stats = fetch_stats()
        tenants = fetch_tenants()
    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to the API. Please make sure the API server is running on http://localhost:8000"
        )
        st.code("cd ~/Projects/account-management/api && uvicorn main:app --reload")
        return

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Accounts", stats["total_accounts"])
    with col2:
        active = stats["by_status"].get("Active", 0)
        st.metric("Active Accounts", active)
    with col3:
        decom = stats["by_status"].get("Decom", 0)
        st.metric("Decommissioned", decom)
    with col4:
        st.metric("Unique Tenants", len(tenants))

    st.divider()

    # Filters
    st.subheader("Filter Accounts")
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        tenant_filter = st.selectbox(
            "Filter by Tenant",
            options=["All"] + tenants,
            index=0,
        )

    with filter_col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Active", "Decom"],
            index=0,
        )

    with filter_col3:
        env_filter = st.selectbox(
            "Filter by Environment",
            options=["All", "prod", "UAT", "DEV"],
            index=0,
        )

    with filter_col4:
        category_filter = st.selectbox(
            "Filter by Account Category",
            options=["All", "Execution", "Analytics"],
            index=0,
        )

    tenant_param = None if tenant_filter == "All" else tenant_filter
    status_param = None if status_filter == "All" else status_filter
    env_param = None if env_filter == "All" else env_filter
    category_param = None if category_filter == "All" else category_filter

    accounts = fetch_accounts(
        tenant=tenant_param, status=status_param, environment=env_param, account_category=category_param
    )

    st.subheader(f"Accounts ({len(accounts)} found)")
    st.caption("Double-click on a row to view account details")

    if accounts:
        df = pd.DataFrame(accounts)
        df = df.rename(
            columns={
                "accountNumber": "Account Number",
                "tenant": "Tenant",
                "team": "Team",
                "environment": "Environment",
                "status": "Status",
                "region": "Region",
                "accountCategory": "Account Category",
            }
        )

        # Display table with row selection
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Account Number": st.column_config.NumberColumn(format="%d"),
            },
            on_select="rerun",
            selection_mode="single-row",
            key="accounts_table",
        )

        # Handle row selection (double-click behavior)
        if event.selection and event.selection.rows:
            selected_row_index = event.selection.rows[0]
            selected_account_number = accounts[selected_row_index]["accountNumber"]
            navigate_to_details(selected_account_number)
            st.rerun()

    else:
        st.info("No accounts found matching the filters.")


# Main app logic
try:
    if st.session_state.view == "details":
        render_details_view()
    else:
        render_list_view()
except requests.exceptions.ConnectionError:
    st.error(
        "Cannot connect to the API. Please make sure the API server is running on http://localhost:8000"
    )
    st.code("cd ~/Projects/account-management/api && uvicorn main:app --reload")