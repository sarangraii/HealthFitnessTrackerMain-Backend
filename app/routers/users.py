from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from app.utils.dependencies import get_current_user
from app.database import get_database
from bson import ObjectId

router = APIRouter()

@router.get("/stats/detailed")
async def get_detailed_user_stats(current_user: dict = Depends(get_current_user)):
    """Get comprehensive user statistics"""
    db = get_database()
    user_id = current_user["id"]
    
    # Calculate time ranges
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_start = today_start - timedelta(days=7)
    
    # Try both string and ObjectId for user_id queries
    # This handles cases where data might be stored inconsistently
    user_id_queries = [
        {"user_id": user_id},  # String format
        {"user_id": ObjectId(user_id)}  # ObjectId format
    ]
    
    # Function to count with fallback
    async def count_with_fallback(collection, date_filter=None):
        for query in user_id_queries:
            if date_filter:
                query.update(date_filter)
            count = await collection.count_documents(query)
            if count > 0:
                return count, query.get("user_id")
        return 0, user_id
    
    # Function to find with fallback
    async def find_with_fallback(collection, date_filter=None):
        for query in user_id_queries:
            if date_filter:
                query.update(date_filter)
            cursor = collection.find(query)
            items = await cursor.to_list(length=1000)
            if items:
                return items
        return []
    
    print(f"🔍 Fetching stats for user_id: {user_id} (type: {type(user_id)})")
    
    # TODAY's workouts
    today_workouts, _ = await count_with_fallback(
        db.workouts, 
        {"date": {"$gte": today_start, "$lt": today_end}}
    )
    
    # THIS WEEK's workouts (last 7 days)
    week_workouts, _ = await count_with_fallback(
        db.workouts,
        {"date": {"$gte": week_start, "$lt": today_end}}
    )
    
    # ALL TIME workouts
    total_workouts, workout_user_id = await count_with_fallback(db.workouts)
    print(f"✅ Total workouts: {total_workouts} (user_id format: {type(workout_user_id)})")
    
    # TODAY's meals
    today_meals, _ = await count_with_fallback(
        db.meals,
        {"date": {"$gte": today_start, "$lt": today_end}}
    )
    
    # ALL TIME meals
    total_meals, meal_user_id = await count_with_fallback(db.meals)
    print(f"✅ Total meals: {total_meals} (user_id format: {type(meal_user_id)})")
    
    # If still 0, let's check what's actually in the database
    if total_meals == 0:
        # Sample query to see what's there
        sample = await db.meals.find_one({})
        if sample:
            print(f"⚠️  Sample meal document found with user_id: {sample.get('user_id')} (type: {type(sample.get('user_id'))})")
            print(f"⚠️  Current user_id: {user_id} (type: {type(user_id)})")
        all_meals_count = await db.meals.count_documents({})
        print(f"⚠️  Total meals in database (all users): {all_meals_count}")
    
    # Calculate TODAY's calories consumed
    meals_today_list = await find_with_fallback(
        db.meals,
        {"date": {"$gte": today_start, "$lt": today_end}}
    )
    calories_consumed_today = sum(
        meal.get("total_calories", 0) for meal in meals_today_list
    )
    
    # Calculate TODAY's calories burned
    workouts_today_list = await find_with_fallback(
        db.workouts,
        {"date": {"$gte": today_start, "$lt": today_end}}
    )
    calories_burned_today = sum(
        workout.get("calories_burned", 0) for workout in workouts_today_list
    )
    
    # Calculate average calories per meal (today)
    avg_calories_today = (
        round(calories_consumed_today / today_meals) if today_meals > 0 else 0
    )
    
    return {
        "today": {
            "workouts": today_workouts,
            "meals": today_meals,
            "calories_consumed": calories_consumed_today,
            "calories_burned": calories_burned_today,
            "avg_calories_per_meal": avg_calories_today
        },
        "week": {
            "workouts": week_workouts
        },
        "all_time": {
            "total_workouts": total_workouts,
            "total_meals": total_meals
        },
        "debug_info": {
            "user_id": user_id,
            "user_id_type": type(user_id).__name__,
            "workout_user_id_type": type(workout_user_id).__name__ if total_workouts > 0 else "none",
            "meal_user_id_type": type(meal_user_id).__name__ if total_meals > 0 else "none"
        }
    }