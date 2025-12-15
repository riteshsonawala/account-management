from pydantic import BaseModel
from typing import Optional


class AccessInfo(BaseModel):
    readOnlyAD: str
    writeAD: str


class Account(BaseModel):
    accountType: str
    tenant: str
    team: str
    accountNumber: int
    type: str
    region: str
    barclaysOu: str
    accountLimit: Optional[int] = None
    environment: str
    adGroupCoreRoles: str
    serviceFirstItba: str
    serviceFirstItbs: str
    status: str
    accountCategory: str
    access: AccessInfo


class AccountSummary(BaseModel):
    accountNumber: int
    tenant: str
    team: str
    environment: str
    status: str
    region: str
    accountCategory: str