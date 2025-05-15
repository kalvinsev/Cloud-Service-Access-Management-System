from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db import get_database
from app.auth import get_admin_user
from app.models import PyObjectId
from app.schemas import UserCreate, UserOut

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    # admin=Depends(get_admin_user),
):
    if await db.users.find_one({"username": user_in.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    hashed = pwd_ctx.hash(user_in.password)
    doc = {
        "username": user_in.username,
        "hashed_password": hashed,
        "role": user_in.role
    }
    res = await db.users.insert_one(doc)
    created = await db.users.find_one({"_id": res.inserted_id})

    # *** key change here ***
    created["_id"] = str(created["_id"])

    return UserOut(**created)
