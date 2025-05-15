from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas import SubscriptionCreate, SubscriptionOut
from app.db import get_database
from app.auth import get_current_user, get_admin_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
async def subscribe(
    sub_in: SubscriptionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Customer subscribes themselves to a plan
    try:
        plan_obj_id = ObjectId(sub_in.plan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plan_id")
    plan = await db.plans.find_one({"_id": plan_obj_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    user_oid = current_user.get("_id")
    if not isinstance(user_oid, ObjectId):
        try:
            user_oid = ObjectId(user_oid)
        except:
            raise HTTPException(status_code=400, detail="Invalid user ID")

    existing = await db.subscriptions.find_one({"user_id": user_oid})
    now = datetime.now(timezone.utc)
    if existing:
        # update existing subscription
        await db.subscriptions.update_one(
            {"_id": existing["_id"]},
            {"$set": {"plan_id": plan_obj_id, "started_at": now}}
        )
        doc = await db.subscriptions.find_one({"_id": existing["_id"]})
    else:
        # create new subscription
        new_sub = {
            "user_id": user_oid,
            "plan_id": plan_obj_id,
            "started_at": now
        }
        res = await db.subscriptions.insert_one(new_sub)
        doc = await db.subscriptions.find_one({"_id": res.inserted_id})

    # Stringify ObjectIds for response
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    doc["plan_id"] = str(doc["plan_id"])
    doc["started_at"] = doc["started_at"].isoformat()

    return SubscriptionOut(**doc)

@router.get("/me", response_model=SubscriptionOut)
async def get_my_subscription(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    user_oid = current_user.get("_id")
    if not isinstance(user_oid, ObjectId):
        try:
            user_oid = ObjectId(user_oid)
        except:
            raise HTTPException(status_code=400, detail="Invalid user ID")
    sub = await db.subscriptions.find_one({"user_id": user_oid})
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found for user")
    sub["_id"] = str(sub["_id"])
    sub["user_id"] = str(sub["user_id"])
    sub["plan_id"] = str(sub["plan_id"])
    sub["started_at"] = sub["started_at"].isoformat()
    return SubscriptionOut(**sub)

# Admin-only endpoints
@router.get("", response_model=List[SubscriptionOut])
async def list_subscriptions(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    subs = []
    async for s in db.subscriptions.find():
        s["_id"] = str(s["_id"])
        s["user_id"] = str(s["user_id"])
        s["plan_id"] = str(s["plan_id"])
        s["started_at"] = s["started_at"].isoformat()
        subs.append(SubscriptionOut(**s))
    return subs

@router.put("/{user_id}", response_model=SubscriptionOut)
async def assign_plan_to_user(
    user_id: str,
    sub_in: SubscriptionCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    try:
        uid = ObjectId(user_id)
        plan_obj_id = ObjectId(sub_in.plan_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID provided")
    plan = await db.plans.find_one({"_id": plan_obj_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    existing = await db.subscriptions.find_one({"user_id": uid})
    now = datetime.now(timezone.utc)
    if existing:
        await db.subscriptions.update_one(
            {"_id": existing["_id"]},
            {"$set": {"plan_id": plan_obj_id, "started_at": now}}
        )
        doc = await db.subscriptions.find_one({"_id": existing["_id"]})
    else:
        new_sub = {"user_id": uid, "plan_id": plan_obj_id, "started_at": now}
        res = await db.subscriptions.insert_one(new_sub)
        doc = await db.subscriptions.find_one({"_id": res.inserted_id})
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    doc["plan_id"] = str(doc["plan_id"])
    doc["started_at"] = doc["started_at"].isoformat()
    return SubscriptionOut(**doc)
