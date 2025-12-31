from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from app.models.schemas import MealCreate, MealUpdate
from app.utils.dependencies import get_current_user
from app.database import get_database
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_meal(
    meal: MealCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new meal entry"""
    db = get_database()
    
    try:
        meal_dict = meal.model_dump()
        meal_dict["user_id"] = current_user["id"]
        meal_dict["created_at"] = datetime.utcnow()
        
        # Set date to current time if not provided
        if meal_dict.get("date") is None:
            meal_dict["date"] = datetime.utcnow()
        
        # Calculate totals
        meal_dict["total_calories"] = sum(food["calories"] for food in meal_dict["foods"])
        meal_dict["total_protein"] = sum(food.get("protein", 0) for food in meal_dict["foods"])
        meal_dict["total_carbs"] = sum(food.get("carbs", 0) for food in meal_dict["foods"])
        meal_dict["total_fats"] = sum(food.get("fats", 0) for food in meal_dict["foods"])
        
        print(f"✅ Creating meal:")
        print(f"   User ID: {meal_dict['user_id']}")
        print(f"   Type: {meal_dict['type']}")
        print(f"   Date: {meal_dict['date']}")
        print(f"   Calories: {meal_dict['total_calories']}")
        
        result = await db.meals.insert_one(meal_dict)
        created_meal = await db.meals.find_one({"_id": result.inserted_id})
        
        print(f"   Saved with ID: {result.inserted_id}")
        
        created_meal["id"] = str(created_meal["_id"])
        del created_meal["_id"]
        
        # Convert datetime to ISO string
        if isinstance(created_meal.get("date"), datetime):
            created_meal["date"] = created_meal["date"].isoformat()
        if isinstance(created_meal.get("created_at"), datetime):
            created_meal["created_at"] = created_meal["created_at"].isoformat()
        
        return created_meal
    except Exception as e:
        print(f"❌ Error creating meal: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
@router.get("/")
async def get_meals(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get all meals for the current user"""
    db = get_database()
    
    try:
        query = {"user_id": current_user["id"]}
        
        print(f"\n🔍 Fetching meals:")
        print(f"   User ID: {current_user['id']}")
        print(f"   Start date: {start_date}")
        print(f"   End date: {end_date}")
        
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                query["date"]["$gte"] = start_dt
                print(f"   From: {start_dt}")
            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                query["date"]["$lte"] = end_dt
                print(f"   To: {end_dt}")
        
        print(f"   Query: {query}")
        
        cursor = db.meals.find(query).sort("date", -1)
        meals = await cursor.to_list(length=100)
        
        print(f"   ✅ Found {len(meals)} meals")
        
        if len(meals) == 0:
            # Check if user has ANY meals
            total_meals = await db.meals.count_documents({"user_id": current_user["id"]})
            print(f"   📊 User has {total_meals} total meals in database")
            
            if total_meals > 0:
                # Show a sample meal
                sample = await db.meals.find_one({"user_id": current_user["id"]})
                print(f"   Sample meal date: {sample.get('date')}")
        
        for meal in meals:
            meal["id"] = str(meal["_id"])
            del meal["_id"]
            if isinstance(meal.get("date"), datetime):
                meal["date"] = meal["date"].isoformat()
            if isinstance(meal.get("created_at"), datetime):
                meal["created_at"] = meal["created_at"].isoformat()
        
        return meals
    except Exception as e:
        print(f"❌ Error fetching meals: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/all")
async def debug_all_meals(current_user: dict = Depends(get_current_user)):
    """Debug endpoint - get ALL meals"""
    db = get_database()
    
    print(f"\n🐛 DEBUG - All meals for user: {current_user['id']}")
    
    cursor = db.meals.find({"user_id": current_user["id"]})
    meals = await cursor.to_list(length=100)
    
    print(f"   Found {len(meals)} total meals")
    
    for i, meal in enumerate(meals):
        print(f"   Meal {i+1}: {meal.get('type')} - {meal.get('date')}")
        meal["id"] = str(meal["_id"])
        del meal["_id"]
        if isinstance(meal.get("date"), datetime):
            meal["date"] = meal["date"].isoformat()
        if isinstance(meal.get("created_at"), datetime):
            meal["created_at"] = meal["created_at"].isoformat()
    
    return {
        "user_id": current_user["id"],
        "total_meals": len(meals),
        "meals": meals
    }

@router.get("/{meal_id}")
async def get_meal(
    meal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific meal by ID"""
    db = get_database()
    
    try:
        meal = await db.meals.find_one({
            "_id": ObjectId(meal_id),
            "user_id": current_user["id"]
        })
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        meal["id"] = str(meal["_id"])
        del meal["_id"]
        if isinstance(meal.get("date"), datetime):
            meal["date"] = meal["date"].isoformat()
        if isinstance(meal.get("created_at"), datetime):
            meal["created_at"] = meal["created_at"].isoformat()
        
        return meal
    except Exception as e:
        print(f"Error fetching meal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{meal_id}")
async def update_meal(
    meal_id: str,
    meal_update: MealUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a meal"""
    db = get_database()
    
    try:
        update_data = {k: v for k, v in meal_update.model_dump().items() if v is not None}
        
        if "foods" in update_data:
            update_data["total_calories"] = sum(food["calories"] for food in update_data["foods"])
            update_data["total_protein"] = sum(food.get("protein", 0) for food in update_data["foods"])
            update_data["total_carbs"] = sum(food.get("carbs", 0) for food in update_data["foods"])
            update_data["total_fats"] = sum(food.get("fats", 0) for food in update_data["foods"])
        
        if update_data:
            result = await db.meals.update_one(
                {"_id": ObjectId(meal_id), "user_id": current_user["id"]},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Meal not found")
        
        meal = await db.meals.find_one({"_id": ObjectId(meal_id)})
        meal["id"] = str(meal["_id"])
        del meal["_id"]
        if isinstance(meal.get("date"), datetime):
            meal["date"] = meal["date"].isoformat()
        if isinstance(meal.get("created_at"), datetime):
            meal["created_at"] = meal["created_at"].isoformat()
        
        return meal
    except Exception as e:
        print(f"Error updating meal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a meal"""
    db = get_database()
    
    try:
        result = await db.meals.delete_one({
            "_id": ObjectId(meal_id),
            "user_id": current_user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        print(f"✅ Deleted meal {meal_id}")
        
        return {"message": "Meal deleted successfully"}
    except Exception as e:
        print(f"Error deleting meal: {e}")
        raise HTTPException(status_code=500, detail=str(e))