# app/schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

# === Plan schemas ===

class PlanCreate(BaseModel):
    name: str
    description: str
    permission_ids: List[str]
    limits: Dict[str, int]

class PlanOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    description: str
    permissions: List[str]
    limits: Dict[str, int]


# === Permission schemas ===

class PermissionCreate(BaseModel):
    name: str
    endpoint: str
    description: Optional[str] = None

class PermissionOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    endpoint: str
    description: Optional[str] = None


# === Subscription schemas ===

class SubscriptionCreate(BaseModel):
    plan_id: str

class SubscriptionOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    plan_id: str
    started_at: str


# === Usage schemas ===

class UsageOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    permission_name: str
    count: int
    last_reset: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["admin", "customer"]

class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    username: str
    role: str