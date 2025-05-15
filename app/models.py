from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Any, Annotated, Union, Optional, List, Dict
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema
from bson import ObjectId
from datetime import datetime, timezone

# --- Helper to validate and serialize MongoDB ObjectId ---
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

# Annotated type for Pydantic v2 supporting ObjectId
PyObjectId = Annotated[
    Union[str, ObjectId],
    AfterValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}),
]

# --- Models Definition ---

class PlanModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    name: str
    description: str
    permissions: List[PyObjectId]
    limits: Dict[str, int]

class PermissionModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    name: str
    endpoint: str
    description: Optional[str] = None

class UserModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    username: str
    hashed_password: str
    role: str  # "admin" or "customer"

class SubscriptionModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId
    plan_id: PyObjectId
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UsageModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId
    permission_name: str
    count: int
    last_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
