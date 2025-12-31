from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime

# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    age: int
    gender: Literal["male", "female", "other"]
    height: float
    weight: float
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"] = "moderate"
    goal: Literal["lose_weight", "maintain", "gain_muscle"] = "maintain"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal["male", "female", "other"]] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    activity_level: Optional[Literal["sedentary", "light", "moderate", "active", "very_active"]] = None
    goal: Optional[Literal["lose_weight", "maintain", "gain_muscle"]] = None
    bio: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    age: int
    gender: str
    height: float
    weight: float
    activity_level: str
    goal: str
    bio: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# ============================================================================
# WORKOUT SCHEMAS
# ============================================================================

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    weight: Optional[float] = None
    duration: Optional[int] = None

class WorkoutCreate(BaseModel):
    title: str
    type: Literal["strength", "cardio", "flexibility", "sports", "other"]
    exercises: List[Exercise] = []
    duration: int
    calories_burned: Optional[int] = 0
    notes: Optional[str] = None
    date: Optional[datetime] = None

class WorkoutUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[Literal["strength", "cardio", "flexibility", "sports", "other"]] = None
    exercises: Optional[List[Exercise]] = None
    duration: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None

class WorkoutResponse(BaseModel):
    id: str
    user_id: str
    title: str
    type: str
    exercises: List[Exercise]
    duration: int
    calories_burned: int
    notes: Optional[str] = None
    date: datetime
    created_at: datetime

# ============================================================================
# MEAL SCHEMAS
# ============================================================================

class FoodItem(BaseModel):
    name: str
    quantity: float
    unit: str
    calories: int
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fats: Optional[float] = 0

class MealCreate(BaseModel):
    type: Literal["breakfast", "lunch", "dinner", "snack"]
    foods: List[FoodItem]
    notes: Optional[str] = None
    date: Optional[datetime] = None

class MealUpdate(BaseModel):
    type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = None
    foods: Optional[List[FoodItem]] = None
    notes: Optional[str] = None

class MealResponse(BaseModel):
    id: str
    user_id: str
    type: str
    foods: List[FoodItem]
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fats: float
    notes: Optional[str] = None
    date: datetime
    created_at: datetime

# ============================================================================
# WATER SCHEMAS
# ============================================================================

class WaterCreate(BaseModel):
    amount_ml: int = Field(..., gt=0, description="Amount of water in milliliters")
    timestamp: Optional[datetime] = None

class WaterUpdate(BaseModel):
    amount_ml: Optional[int] = Field(None, gt=0)

class WaterResponse(BaseModel):
    id: str
    user_id: str
    amount_ml: int
    timestamp: datetime
    date: datetime

# ============================================================================
# SOCIAL SCHEMAS
# ============================================================================

class PostCreate(BaseModel):
    content: str
    type: Literal["workout", "meal", "achievement", "general"] = "general"

class PostResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    content: str
    type: str
    likes: int
    comments: List[dict]
    created_at: datetime

class CommentCreate(BaseModel):
    text: str

# ============================================================================
# AI SCHEMAS
# ============================================================================

class AIUserData(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    activity_level: str
    goal: str

class UserHealthData(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    activity_level: str
    goal: str

class DietRecommendation(BaseModel):
    daily_calories: int
    protein_grams: int
    carbs_grams: int
    fats_grams: int
    meals_breakdown: dict
    recommendations: List[str]

class WorkoutPlan(BaseModel):
    plan_name: str
    duration_weeks: int
    weekly_schedule: List[dict]
    tips: List[str]

class CalorieResponse(BaseModel):
    bmr: float
    tdee: float
    recommended_calories: dict

class FoodDatabaseItem(BaseModel):
    name: str
    calories: int
    protein: float
    carbs: float
    fats: float
    serving_size: str

class MealSuggestion(BaseModel):
    meal_type: str
    target_calories: int
    suggested_foods: List[dict]
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fats: float
    tips: List[str]

class TrainerChatResponse(BaseModel):
    question: str
    answer: str
    category: str
    tips: Optional[List[str]] = None

# ============================================================================
# STATS SCHEMAS
# ============================================================================

class DailyStats(BaseModel):
    workouts: int
    meals: int
    calories_consumed: int
    calories_burned: int
    avg_calories_per_meal: int

class WeeklyStats(BaseModel):
    workouts: int

class AllTimeStats(BaseModel):
    total_workouts: int
    total_meals: int

class DetailedStatsResponse(BaseModel):
    today: DailyStats
    week: WeeklyStats
    all_time: AllTimeStats
    debug_info: Optional[dict] = None

class UserStats(BaseModel):
    total_workouts: int
    total_meals: int
    avg_calories: int
    total_calories_burned: int
    streak_days: int
