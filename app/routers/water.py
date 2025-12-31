from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, Field
from app.utils.dependencies import get_current_user
from app.database import get_database
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter()

class WaterCreate(BaseModel):
    amount: float = Field(..., gt=0, le=10)
    date: Optional[str] = None
    time: Optional[str] = None
    notes: Optional[str] = ""

class WaterUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, le=10)
    date: Optional[str] = None
    time: Optional[str] = None
    notes: Optional[str] = None

@router.post("/")
async def create_water(water: WaterCreate, current_user: dict = Depends(get_current_user)):
    db = get_database()
    
    water_date = datetime.utcnow()
    if water.date:
        try:
            water_date = datetime.fromisoformat(water.date.replace('Z', '+00:00'))
        except:
            water_date = datetime.utcnow()
    
    water_time = datetime.utcnow()
    if water.time:
        try:
            water_time = datetime.fromisoformat(water.time.replace('Z', '+00:00'))
        except:
            water_time = datetime.utcnow()
    
    water_dict = {
        "user_id": current_user["id"],
        "amount": water.amount,
        "date": water_date,
        "time": water_time,
        "notes": water.notes or "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.water.insert_one(water_dict)
    created_water = await db.water.find_one({"_id": result.inserted_id})
    
    created_water["id"] = str(created_water["_id"])
    del created_water["_id"]
    if isinstance(created_water.get("user_id"), ObjectId):
        created_water["user_id"] = str(created_water["user_id"])
    
    return {"success": True, "data": created_water, "message": "Water intake logged successfully"}

@router.get("/")
async def get_water_records(start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None), current_user: dict = Depends(get_current_user)):
    db = get_database()
    query = {"user_id": current_user["id"]}
    
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    cursor = db.water.find(query).sort("date", -1).sort("time", -1)
    water_records = await cursor.to_list(length=100)
    
    for record in water_records:
        record["id"] = str(record["_id"])
        del record["_id"]
        if isinstance(record.get("user_id"), ObjectId):
            record["user_id"] = str(record["user_id"])
    
    total = sum(record["amount"] for record in water_records)
    return {"success": True, "data": water_records, "total": round(total, 2)}

@router.get("/today")
async def get_today_water(current_user: dict = Depends(get_current_user)):
    db = get_database()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    query = {"user_id": current_user["id"], "date": {"$gte": today, "$lt": tomorrow}}
    cursor = db.water.find(query).sort("time", -1)
    water_records = await cursor.to_list(length=100)
    
    for record in water_records:
        record["id"] = str(record["_id"])
        del record["_id"]
        if isinstance(record.get("user_id"), ObjectId):
            record["user_id"] = str(record["user_id"])
    
    total = sum(record["amount"] for record in water_records)
    return {"success": True, "data": water_records, "total": round(total, 2), "goal": 3.0}

@router.get("/stats")
async def get_water_stats(start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None), current_user: dict = Depends(get_current_user)):
    db = get_database()
    query = {"user_id": current_user["id"]}
    
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    cursor = db.water.find(query)
    water_records = await cursor.to_list(length=1000)
    
    total = sum(record["amount"] for record in water_records)
    count = len(water_records)
    average = total / count if count > 0 else 0
    goal = 3.0
    goal_percentage = (total / goal) * 100 if goal > 0 else 0
    
    return {"success": True, "stats": {"total": round(total, 2), "average": round(average, 2), "count": count, "goal": goal, "goal_percentage": round(goal_percentage, 2)}}

@router.get("/{water_id}")
async def get_water(water_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    water = await db.water.find_one({"_id": ObjectId(water_id), "user_id": current_user["id"]})
    
    if not water:
        raise HTTPException(status_code=404, detail="Water record not found")
    
    water["id"] = str(water["_id"])
    del water["_id"]
    if isinstance(water.get("user_id"), ObjectId):
        water["user_id"] = str(water["user_id"])
    
    return water

@router.put("/{water_id}")
async def update_water(water_id: str, water_update: WaterUpdate, current_user: dict = Depends(get_current_user)):
    db = get_database()
    update_data = {}
    
    if water_update.amount is not None:
        update_data["amount"] = water_update.amount
    if water_update.date is not None:
        try:
            update_data["date"] = datetime.fromisoformat(water_update.date.replace('Z', '+00:00'))
        except:
            pass
    if water_update.time is not None:
        try:
            update_data["time"] = datetime.fromisoformat(water_update.time.replace('Z', '+00:00'))
        except:
            pass
    if water_update.notes is not None:
        update_data["notes"] = water_update.notes
    
    update_data["updated_at"] = datetime.utcnow()
    
    if update_data:
        result = await db.water.update_one({"_id": ObjectId(water_id), "user_id": current_user["id"]}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Water record not found")
    
    water = await db.water.find_one({"_id": ObjectId(water_id)})
    water["id"] = str(water["_id"])
    del water["_id"]
    if isinstance(water.get("user_id"), ObjectId):
        water["user_id"] = str(water["user_id"])
    
    return {"success": True, "data": water, "message": "Water intake updated successfully"}

@router.delete("/{water_id}")
async def delete_water(water_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    result = await db.water.delete_one({"_id": ObjectId(water_id), "user_id": current_user["id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Water record not found")
    
    return {"success": True, "message": "Water deleted successfully"}

@router.delete("/today/reset")
async def reset_today_water(current_user: dict = Depends(get_current_user)):
    db = get_database()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    result = await db.water.delete_many({
        "user_id": current_user["id"],
        "date": {"$gte": today, "$lt": tomorrow}
    })
    
    return {"success": True, "message": f"Reset {result.deleted_count} water records for today", "deleted_count": result.deleted_count}