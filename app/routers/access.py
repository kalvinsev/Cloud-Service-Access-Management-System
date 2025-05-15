from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.auth import get_current_user
from app.db import get_database

router = APIRouter(prefix="/access", tags=["access"])

@router.get("/{service_name}")
async def check_access(
    service_name: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Check if the current user has access to a given service and their usage stats.
    """
    # Convert user_id to ObjectId if it's a string
    user_id = current_user.get("_id")
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    # 1) Load subscription
    sub = await db.subscriptions.find_one({"user_id": user_id})
    if not sub:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No subscription found for user")

    # 2) Load plan
    plan = await db.plans.find_one({"_id": sub["plan_id"]})
    if not plan:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Plan configuration missing")

    # 3) Check permission inclusion
    limits = plan.get("limits", {})
    if service_name not in limits:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Service '{service_name}' not in your plan")

    # 4) Fetch usage (no increment)
    usage_record = await db.usage.find_one({
        "user_id": user_id,
        "permission_name": service_name
    })
    used = usage_record.get("count", 0) if usage_record else 0
    limit = limits[service_name]

    return {
        "service": service_name,
        "allowed": used < limit,
        "limit": limit,
        "used": used
    }
