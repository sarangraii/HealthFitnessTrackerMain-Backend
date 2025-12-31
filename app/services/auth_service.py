from datetime import timedelta
from fastapi import HTTPException, status
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.database import get_database
from app.config import settings

async def authenticate_user(email: str, password: str):
    db = get_database()
    user = await db.users.find_one({"email": email})
    
    if not user:
        return None
    
    if not verify_password(password, user["password"]):
        return None
    
    return user

async def create_user(user_data: dict):
    db = get_database()
    
    existing_user = await db.users.find_one({"email": user_data["email"]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_data["password"] = get_password_hash(user_data["password"])
    result = await db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    return user_data

def create_user_token(user_id: str):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    return access_token
