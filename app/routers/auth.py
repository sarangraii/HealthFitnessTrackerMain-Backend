from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from bson import ObjectId
from app.models.schemas import UserCreate, Token, UserUpdate
from app.services.auth_service import authenticate_user, create_user, create_user_token
from app.utils.dependencies import get_current_user
from app.database import get_database

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    user_dict = user.model_dump()
    user_dict["created_at"] = datetime.utcnow()
    user_dict["followers"] = []
    user_dict["following"] = []
    
    created_user = await create_user(user_dict)
    access_token = create_user_token(str(created_user["_id"]))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(created_user["_id"]),
            "name": created_user["name"],
            "email": created_user["email"]
        }
    }

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_user_token(str(user["_id"]))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "age": current_user.get("age"),
        "gender": current_user.get("gender"),
        "height": current_user.get("height"),
        "weight": current_user.get("weight"),
        "activity_level": current_user.get("activity_level"),
        "goal": current_user.get("goal"),
        "bio": current_user.get("bio")
    }

@router.put("/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    db = get_database()
    
    # Prepare update data (only fields that were provided)
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Only add updated_at if there's actually data to update
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Update user in database
    result = await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Fetch updated user
    updated_user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found after update"
        )
    
    return {
        "id": str(updated_user["_id"]),
        "name": updated_user["name"],
        "email": updated_user["email"],
        "age": updated_user.get("age"),
        "gender": updated_user.get("gender"),
        "height": updated_user.get("height"),
        "weight": updated_user.get("weight"),
        "activity_level": updated_user.get("activity_level"),
        "goal": updated_user.get("goal"),
        "bio": updated_user.get("bio")
    }