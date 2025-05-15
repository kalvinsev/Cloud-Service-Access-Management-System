from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
from app.db import get_database
from app.auth import get_current_user

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/{service_name}")
async def invoke_service(
    service_name: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # 1) Load subscription for this user
    user_id = current_user.get("_id")
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid user ID")

    sub = await db.subscriptions.find_one({"user_id": user_id})
    if not sub:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="No subscription found for user")

    # 2) Load plan and limits
    plan = await db.plans.find_one({"_id": sub["plan_id"]})
    if not plan:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Plan configuration missing")
    limits = plan.get("limits", {})
    if service_name not in limits:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"Service '{service_name}' not in your plan")
    limit = limits[service_name]

    # 3) Fetch or initialize usage record
    now = datetime.now(timezone.utc)
    usage = await db.usage.find_one({
        "user_id": user_id,
        "permission_name": service_name
    })
    if usage:
        last_reset = usage.get("last_reset")
        if last_reset and (last_reset.year != now.year or last_reset.month != now.month):
            # Reset monthly counter
            await db.usage.update_one({"_id": usage["_id"]}, {"$set": {"count": 0, "last_reset": now}})
            usage = None
    if not usage:
        # Create new usage doc
        usage_doc = {"user_id": user_id, "permission_name": service_name, "count": 0, "last_reset": now}
        res = await db.usage.insert_one(usage_doc)
        usage = await db.usage.find_one({"_id": res.inserted_id})

    # 4) Enforce quota
    used = usage.get("count", 0)
    if used >= limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Monthly quota exceeded for {service_name}")

    # 5) Increment and return
    await db.usage.update_one({"_id": usage["_id"]}, {"$inc": {"count": 1}})
    return {
        "service": service_name,
        "usage_this_month": used + 1,
        "data": f"🚀 Simulated result from {service_name}"
    }
