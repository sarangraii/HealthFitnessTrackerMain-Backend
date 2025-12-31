from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.schemas import PostCreate
from app.utils.dependencies import get_current_user
from app.database import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/posts")
async def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    post_dict = post.model_dump()
    post_dict["user_id"] = current_user["id"]
    post_dict["user_name"] = current_user["name"]
    post_dict["likes"] = []
    post_dict["comments"] = []
    post_dict["created_at"] = datetime.utcnow()
    
    result = await db.social_posts.insert_one(post_dict)
    post_dict["id"] = str(result.inserted_id)
    del post_dict["_id"]
    
    return post_dict

@router.get("/feed")
async def get_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    skip = (page - 1) * limit
    
    cursor = db.social_posts.find().sort("created_at", -1).skip(skip).limit(limit)
    posts = await cursor.to_list(length=limit)
    
    for post in posts:
        post["id"] = str(post["_id"])
        del post["_id"]
    
    total = await db.social_posts.count_documents({})
    
    return {
        "posts": posts,
        "current_page": page,
        "total_pages": (total + limit - 1) // limit,
        "total": total
    }

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    post = await db.social_posts.find_one({"_id": ObjectId(post_id)})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    user_id = current_user["id"]
    likes = post.get("likes", [])
    
    if user_id in likes:
        await db.social_posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$pull": {"likes": user_id}}
        )
    else:
        await db.social_posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"likes": user_id}}
        )
    
    updated_post = await db.social_posts.find_one({"_id": ObjectId(post_id)})
    updated_post["id"] = str(updated_post["_id"])
    del updated_post["_id"]
    
    return updated_post

@router.post("/posts/{post_id}/comment")
async def add_comment(
    post_id: str,
    comment: dict,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    post = await db.social_posts.find_one({"_id": ObjectId(post_id)})
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = {
        "user_id": current_user["id"],
        "user_name": current_user["name"],
        "text": comment.get("text"),
        "created_at": datetime.utcnow()
    }
    
    await db.social_posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": new_comment}}
    )
    
    updated_post = await db.social_posts.find_one({"_id": ObjectId(post_id)})
    updated_post["id"] = str(updated_post["_id"])
    del updated_post["_id"]
    
    return updated_post