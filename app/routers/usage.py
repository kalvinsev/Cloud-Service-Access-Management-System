from fastapi import APIRouter, Depends, HTTPException
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.db import get_database
from app.auth import get_current_user
from app.schemas import UsageOut

router = APIRouter(prefix="/usage", tags=["usage"])

@router.get("/me", response_model=List[UsageOut])
async def get_my_usage(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Convert user_id to ObjectId if needed
    user_id = current_user.get("_id")
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid user ID")

    # Fetch usage records for the current authenticated user
    cursor = db.usage.find({"user_id": user_id})
    results = []
    async for u in cursor:
        # Stringify ObjectIds and datetime for response
        u["_id"] = str(u["_id"])
        u["user_id"] = str(u["user_id"])
        u["last_reset"] = u["last_reset"].isoformat()
        results.append(UsageOut(**u))
    return results

@router.get("", response_model=List[UsageOut])
async def list_all_usage(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin: dict = Depends(get_current_user)
):
    # Admin-only: list all usage records
    # Note: if you have a separate get_admin_user, switch to that dependency
    cursor = db.usage.find()
    results = []
    async for u in cursor:
        u["_id"] = str(u["_id"])
        u["user_id"] = str(u["user_id"])
        u["last_reset"] = u["last_reset"].isoformat()
        results.append(UsageOut(**u))
    return results
