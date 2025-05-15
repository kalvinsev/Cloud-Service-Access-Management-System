from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.schemas import PermissionCreate, PermissionOut
from app.db import get_database
from app.auth import get_admin_user, get_current_user

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("", response_model=PermissionOut, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    existing = await db.permissions.find_one({"name": permission.name})
    if existing:
        raise HTTPException(status_code=400, detail="Permission name already exists")
    doc = permission.dict()
    res = await db.permissions.insert_one(doc)
    created = await db.permissions.find_one({"_id": res.inserted_id})
    # Convert ObjectId to string for Pydantic validation
    created["_id"] = str(created["_id"])
    return PermissionOut(**created)

@router.get("", response_model=List[PermissionOut])
async def list_permissions(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    perms = []
    async for p in db.permissions.find():
        p["_id"] = str(p["_id"])
        perms.append(PermissionOut(**p))
    return perms

@router.get("/{permission_id}", response_model=PermissionOut)
async def get_permission(
    permission_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    perm = await db.permissions.find_one({"_id": ObjectId(permission_id)})
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    perm["_id"] = str(perm["_id"])
    return PermissionOut(**perm)

@router.put("/{permission_id}", response_model=PermissionOut)
async def update_permission(
    permission_id: str,
    permission: PermissionCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    update_data = permission.dict()
    res = await db.permissions.update_one(
        {"_id": ObjectId(permission_id)},
        {"$set": update_data}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Permission not found")
    updated = await db.permissions.find_one({"_id": ObjectId(permission_id)})
    updated["_id"] = str(updated["_id"])
    return PermissionOut(**updated)

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin=Depends(get_admin_user)
):
    res = await db.permissions.delete_one({"_id": ObjectId(permission_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Permission not found")
    return
