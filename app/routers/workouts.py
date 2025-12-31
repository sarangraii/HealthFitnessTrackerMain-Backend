from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.models.schemas import WorkoutCreate, WorkoutUpdate
from app.utils.dependencies import get_current_user
from app.database import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/")
async def create_workout(
    workout: WorkoutCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    workout_dict = workout.model_dump()
    workout_dict["user_id"] = current_user["id"]
    workout_dict["created_at"] = datetime.utcnow()
    
    if workout_dict.get("date") is None:
        workout_dict["date"] = datetime.utcnow()
    
    result = await db.workouts.insert_one(workout_dict)
    
    # Fetch the created workout from database
    created_workout = await db.workouts.find_one({"_id": result.inserted_id})
    
    # Convert ObjectIds to strings
    created_workout["id"] = str(created_workout["_id"])
    del created_workout["_id"]
    
    # Convert user_id if it's an ObjectId
    if isinstance(created_workout.get("user_id"), ObjectId):
        created_workout["user_id"] = str(created_workout["user_id"])
    
    return created_workout

@router.get("/")
async def get_workouts(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    query = {"user_id": current_user["id"]}
    
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    cursor = db.workouts.find(query).sort("date", -1)
    workouts = await cursor.to_list(length=100)
    
    for workout in workouts:
        workout["id"] = str(workout["_id"])
        del workout["_id"]
        
        # Convert user_id if it's an ObjectId
        if isinstance(workout.get("user_id"), ObjectId):
            workout["user_id"] = str(workout["user_id"])
    
    return workouts

@router.get("/{workout_id}")
async def get_workout(
    workout_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    workout = await db.workouts.find_one({
        "_id": ObjectId(workout_id),
        "user_id": current_user["id"]
    })
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    workout["id"] = str(workout["_id"])
    del workout["_id"]
    
    # Convert user_id if it's an ObjectId
    if isinstance(workout.get("user_id"), ObjectId):
        workout["user_id"] = str(workout["user_id"])
    
    return workout

@router.put("/{workout_id}")
async def update_workout(
    workout_id: str,
    workout_update: WorkoutUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    update_data = {k: v for k, v in workout_update.model_dump().items() if v is not None}
    
    if update_data:
        result = await db.workouts.update_one(
            {"_id": ObjectId(workout_id), "user_id": current_user["id"]},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Workout not found")
    
    workout = await db.workouts.find_one({"_id": ObjectId(workout_id)})
    workout["id"] = str(workout["_id"])
    del workout["_id"]
    
    # Convert user_id if it's an ObjectId
    if isinstance(workout.get("user_id"), ObjectId):
        workout["user_id"] = str(workout["user_id"])
    
    return workout

@router.delete("/{workout_id}")
async def delete_workout(
    workout_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    result = await db.workouts.delete_one({
        "_id": ObjectId(workout_id),
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    return {"message": "Workout deleted successfully"}