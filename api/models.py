from pydantic import BaseModel, field_validator
from typing import Optional


class AccessInfo(BaseModel):
    readOnlyAD: str = ""
    writeAD: str = ""

    @field_validator("readOnlyAD", "writeAD", mode="before")
    @classmethod
    def default_empty_string(cls, v):
        if v is None or v == "":
            return ""
        return v


class Account(BaseModel):
    accountType: str = ""
    tenant: str = ""
    team: str = ""
    accountNumber: int
    type: str = ""
    region: str = ""
    barclaysOu: str = ""
    accountLimit: Optional[int] = None
    environment: str = ""
    adGroupCoreRoles: str = ""
    serviceFirstItba: str = ""
    serviceFirstItbs: str = ""
    status: str = ""
    accountCategory: str = "Execution"
    access: Optional[AccessInfo] = None

    @field_validator("accountCategory", mode="before")
    @classmethod
    def default_execution_category(cls, v):
        if v is None or v == "":
            return "Execution"
        return v

    @field_validator("access", mode="before")
    @classmethod
    def default_access_info(cls, v):
        if v is None:
            return AccessInfo()
        return v


class AccountSummary(BaseModel):
    accountNumber: int
    tenant: str = ""
    team: str = ""
    environment: str = ""
    status: str = ""
    region: str = ""
    accountCategory: str = "Execution"

    @field_validator("accountCategory", mode="before")
    @classmethod
    def default_execution_category(cls, v):
        if v is None or v == "":
            return "Execution"
        return v