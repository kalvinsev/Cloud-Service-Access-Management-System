from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas import PlanCreate, PlanOut
from app.db import get_database
from app.auth import get_admin_user

router = APIRouter(prefix="/plans", tags=["plans"])

@router.post("", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_in: PlanCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user),
):
    # Prevent duplicate plan names
    if await db.plans.find_one({"name": plan_in.name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan name already exists")

    # Prepare document for insertion
    doc = plan_in.dict()
    # Convert permission IDs into ObjectId instances
    doc["permissions"] = [ObjectId(pid) for pid in doc.pop("permission_ids")]

    # Insert into database
    res = await db.plans.insert_one(doc)
    created = await db.plans.find_one({"_id": res.inserted_id})

    # Convert ObjectId fields to strings for Pydantic
    created["_id"] = str(created["_id"])
    created["permissions"] = [str(pid) for pid in created.get("permissions", [])]

    return PlanOut(**created)

@router.get("", response_model=List[PlanOut])
async def list_plans(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    plans = []
    async for p in db.plans.find():
        # stringify ObjectId fields
        p["_id"] = str(p["_id"])
        p["permissions"] = [str(pid) for pid in p.get("permissions", [])]
        plans.append(PlanOut(**p))
    return plans

@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(
    plan_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    plan = await db.plans.find_one({"_id": ObjectId(plan_id)})
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    plan["_id"] = str(plan["_id"])
    plan["permissions"] = [str(pid) for pid in plan.get("permissions", [])]
    return PlanOut(**plan)

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    res = await db.plans.delete_one({"_id": ObjectId(plan_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return
