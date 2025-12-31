from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import UserHealthData
from app.utils.dependencies import get_current_user
from app.services.diet_recommender import DietRecommender
from app.services.workout_planner import WorkoutPlanner
from app.config import settings
import json
import os
import re

router = APIRouter()

# Initialize services
diet_recommender = DietRecommender()
workout_planner = WorkoutPlanner()

# Try to initialize FREE AI clients
gemini_model = None
groq_client = None

# Try Google Gemini (FREE - 15 requests/min, 1500/day)
try:
    import google.generativeai as genai
    api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        # Use the updated model name
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Google Gemini initialized (FREE)")
except Exception as e:
    print(f"ℹ️ Gemini not available: {e}")

# Try Groq (FREE - Fast inference)
try:
    from groq import Groq
    api_key = getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')
    if api_key:
        groq_client = Groq(api_key=api_key)
        print("✅ Groq initialized (FREE)")
except Exception as e:
    print(f"ℹ️ Groq not available: {e}")

def clean_json_response(text: str) -> str:
    """Extract JSON from markdown code blocks or other formatting"""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return text

def call_free_ai(prompt: str, system_prompt: str = None, max_tokens: int = 2000):
    """Universal FREE AI caller - tries Gemini, then Groq, then fallback"""
    
    # Try Google Gemini first (FREE)
    if gemini_model:
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = gemini_model.generate_content(full_prompt)
            cleaned = clean_json_response(response.text)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Gemini failed: {e}")
    
    # Try Groq if Gemini failed (FREE)
    if groq_client:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            chat_completion = groq_client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",  # Free model
                temperature=0.7,
                max_tokens=max_tokens,
            )
            
            cleaned = clean_json_response(chat_completion.choices[0].message.content)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Groq failed: {e}")
    
    # Both failed
    raise Exception("No AI service available")

@router.post("/diet-recommendations")
async def get_diet_recommendations(
    user_data: UserHealthData,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered diet recommendations with actual meal plans"""
    
    # Calculate basic metrics
    bmr = diet_recommender.calculate_bmr(
        user_data.age, user_data.gender, user_data.height, user_data.weight
    )
    tdee = diet_recommender.calculate_tdee(bmr, user_data.activity_level)
    daily_calories = diet_recommender.get_calorie_target(tdee, user_data.goal)
    macros = diet_recommender.calculate_macros(daily_calories, user_data.goal)
    meals = diet_recommender.create_meal_breakdown(daily_calories)
    
    try:
        # Generate complete meal plan with AI
        prompt = f"""Create a complete daily meal plan for a client with these details:

Profile: Age {user_data.age}, Gender {user_data.gender}, Height {user_data.height}cm, Weight {user_data.weight}kg
Activity Level: {user_data.activity_level}, Goal: {user_data.goal}

Targets:
- Daily Calories: {daily_calories}
- Protein: {macros['protein']}g, Carbs: {macros['carbs']}g, Fats: {macros['fats']}g

Meal Distribution:
- Breakfast: {meals['breakfast']} cal
- Lunch: {meals['lunch']} cal  
- Dinner: {meals['dinner']} cal
- Snacks: {meals['snacks']} cal

For each meal, provide:
1. Creative meal name
2. 3-5 specific foods with exact gram quantities
3. For each food: name, quantity, calories, protein, carbs, fats
4. Brief preparation note

Also provide 5 personalized nutrition tips.

Return ONLY valid JSON (no markdown, no extra text):
{{
  "meals": [
    {{
      "type": "breakfast",
      "name": "Meal name",
      "target_calories": {meals['breakfast']},
      "foods": [
        {{"name": "Oatmeal", "quantity": 80, "unit": "g", "calories": 312, "protein": 13.5, "carbs": 53, "fats": 5.5}}
      ],
      "preparation": "How to prepare"
    }}
  ],
  "tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5"]
}}"""

        system_prompt = "You are a professional nutritionist. Create detailed meal plans with realistic food portions. Return ONLY valid JSON, no markdown formatting."
        
        ai_response = call_free_ai(prompt, system_prompt, max_tokens=2000)
        
        # Calculate totals from generated meals
        total_calories = sum(
            sum(food['calories'] for food in meal['foods']) 
            for meal in ai_response['meals']
        )
        total_protein = sum(
            sum(food['protein'] for food in meal['foods']) 
            for meal in ai_response['meals']
        )
        total_carbs = sum(
            sum(food['carbs'] for food in meal['foods']) 
            for meal in ai_response['meals']
        )
        total_fats = sum(
            sum(food['fats'] for food in meal['foods']) 
            for meal in ai_response['meals']
        )
        
        return {
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "daily_calories": daily_calories,
            "target_protein": macros["protein"],
            "target_carbs": macros["carbs"],
            "target_fats": macros["fats"],
            "actual_totals": {
                "calories": round(total_calories, 1),
                "protein": round(total_protein, 1),
                "carbs": round(total_carbs, 1),
                "fats": round(total_fats, 1)
            },
            "meals": ai_response['meals'],
            "recommendations": ai_response['tips']
        }
    except Exception as e:
        print(f"AI generation failed, using fallback: {e}")
        return get_fallback_diet_plan(user_data)

def get_fallback_diet_plan(user_data: UserHealthData):
    """Fallback diet plan when AI is unavailable"""
    bmr = diet_recommender.calculate_bmr(
        user_data.age, user_data.gender, user_data.height, user_data.weight
    )
    tdee = diet_recommender.calculate_tdee(bmr, user_data.activity_level)
    daily_calories = diet_recommender.get_calorie_target(tdee, user_data.goal)
    macros = diet_recommender.calculate_macros(daily_calories, user_data.goal)
    meals_breakdown = diet_recommender.create_meal_breakdown(daily_calories)
    
    # Create sample meals based on goal
    if user_data.goal == "lose_weight":
        sample_meals = get_weight_loss_meals(meals_breakdown)
    elif user_data.goal == "gain_muscle":
        sample_meals = get_muscle_gain_meals(meals_breakdown)
    else:
        sample_meals = get_maintenance_meals(meals_breakdown)
    
    # Calculate totals
    total_calories = sum(sum(f['calories'] for f in m['foods']) for m in sample_meals)
    total_protein = sum(sum(f['protein'] for f in m['foods']) for m in sample_meals)
    total_carbs = sum(sum(f['carbs'] for f in m['foods']) for m in sample_meals)
    total_fats = sum(sum(f['fats'] for f in m['foods']) for m in sample_meals)
    
    recommendations = diet_recommender.get_recommendations(user_data.goal)
    
    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "daily_calories": daily_calories,
        "target_protein": macros["protein"],
        "target_carbs": macros["carbs"],
        "target_fats": macros["fats"],
        "actual_totals": {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fats": round(total_fats, 1)
        },
        "meals": sample_meals,
        "recommendations": recommendations
    }

def get_weight_loss_meals(breakdown):
    return [
        {
            "type": "breakfast",
            "name": "Lean Protein Breakfast",
            "target_calories": breakdown["breakfast"],
            "foods": [
                {"name": "Egg Whites", "quantity": 150, "unit": "g", "calories": 78, "protein": 16.5, "carbs": 1.2, "fats": 0.3},
                {"name": "Oatmeal", "quantity": 50, "unit": "g", "calories": 195, "protein": 8.5, "carbs": 33, "fats": 3.5},
                {"name": "Blueberries", "quantity": 80, "unit": "g", "calories": 46, "protein": 0.6, "carbs": 11, "fats": 0.2}
            ],
            "preparation": "Scramble egg whites with herbs. Cook oatmeal with water. Top with fresh blueberries."
        },
        {
            "type": "lunch",
            "name": "Grilled Chicken Salad",
            "target_calories": breakdown["lunch"],
            "foods": [
                {"name": "Chicken Breast", "quantity": 120, "unit": "g", "calories": 198, "protein": 37, "carbs": 0, "fats": 4.3},
                {"name": "Mixed Greens", "quantity": 100, "unit": "g", "calories": 25, "protein": 2, "carbs": 5, "fats": 0.3},
                {"name": "Cherry Tomatoes", "quantity": 100, "unit": "g", "calories": 18, "protein": 0.9, "carbs": 4, "fats": 0.2},
                {"name": "Olive Oil", "quantity": 10, "unit": "ml", "calories": 88, "protein": 0, "carbs": 0, "fats": 10}
            ],
            "preparation": "Grill chicken with herbs. Toss greens and tomatoes with olive oil and lemon."
        },
        {
            "type": "dinner",
            "name": "Baked Fish with Vegetables",
            "target_calories": breakdown["dinner"],
            "foods": [
                {"name": "Tilapia", "quantity": 150, "unit": "g", "calories": 129, "protein": 26, "carbs": 0, "fats": 2.7},
                {"name": "Broccoli", "quantity": 150, "unit": "g", "calories": 51, "protein": 4.2, "carbs": 10.5, "fats": 0.6},
                {"name": "Cauliflower", "quantity": 100, "unit": "g", "calories": 25, "protein": 1.9, "carbs": 5, "fats": 0.3}
            ],
            "preparation": "Bake fish with lemon. Steam broccoli and cauliflower with garlic."
        },
        {
            "type": "snacks",
            "name": "Light Snacks",
            "target_calories": breakdown["snacks"],
            "foods": [
                {"name": "Greek Yogurt", "quantity": 100, "unit": "g", "calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
                {"name": "Cucumber", "quantity": 100, "unit": "g", "calories": 16, "protein": 0.7, "carbs": 3.6, "fats": 0.1}
            ],
            "preparation": "Enjoy plain Greek yogurt with cucumber slices."
        }
    ]

def get_muscle_gain_meals(breakdown):
    return [
        {
            "type": "breakfast",
            "name": "Power Breakfast",
            "target_calories": breakdown["breakfast"],
            "foods": [
                {"name": "Whole Eggs", "quantity": 150, "unit": "g", "calories": 233, "protein": 19.5, "carbs": 1.7, "fats": 16.5},
                {"name": "Oatmeal", "quantity": 80, "unit": "g", "calories": 312, "protein": 13.5, "carbs": 53, "fats": 5.5},
                {"name": "Banana", "quantity": 120, "unit": "g", "calories": 107, "protein": 1.3, "carbs": 27, "fats": 0.4}
            ],
            "preparation": "Scramble eggs with vegetables. Cook oatmeal with milk. Slice banana on top."
        },
        {
            "type": "lunch",
            "name": "Muscle Builder Plate",
            "target_calories": breakdown["lunch"],
            "foods": [
                {"name": "Beef Steak", "quantity": 150, "unit": "g", "calories": 271, "protein": 38, "carbs": 0, "fats": 12},
                {"name": "Brown Rice", "quantity": 200, "unit": "g", "calories": 246, "protein": 5.2, "carbs": 51, "fats": 2},
                {"name": "Sweet Potato", "quantity": 150, "unit": "g", "calories": 129, "protein": 2.4, "carbs": 30, "fats": 0.2}
            ],
            "preparation": "Grill steak to desired doneness. Cook brown rice. Roast sweet potato wedges."
        },
        {
            "type": "dinner",
            "name": "High-Protein Dinner",
            "target_calories": breakdown["dinner"],
            "foods": [
                {"name": "Salmon", "quantity": 180, "unit": "g", "calories": 374, "protein": 36, "carbs": 0, "fats": 23.4},
                {"name": "Quinoa", "quantity": 150, "unit": "g", "calories": 180, "protein": 6.6, "carbs": 32, "fats": 2.9},
                {"name": "Asparagus", "quantity": 100, "unit": "g", "calories": 20, "protein": 2.2, "carbs": 3.9, "fats": 0.1}
            ],
            "preparation": "Bake salmon with herbs. Cook quinoa. Roast asparagus with olive oil."
        },
        {
            "type": "snacks",
            "name": "Protein Snacks",
            "target_calories": breakdown["snacks"],
            "foods": [
                {"name": "Almonds", "quantity": 40, "unit": "g", "calories": 232, "protein": 8.4, "carbs": 8.8, "fats": 20},
                {"name": "Protein Shake", "quantity": 30, "unit": "g", "calories": 120, "protein": 24, "carbs": 3, "fats": 1.5}
            ],
            "preparation": "Mix protein powder with water or milk. Enjoy with raw almonds."
        }
    ]

def get_maintenance_meals(breakdown):
    return [
        {
            "type": "breakfast",
            "name": "Balanced Breakfast",
            "target_calories": breakdown["breakfast"],
            "foods": [
                {"name": "Oatmeal", "quantity": 80, "unit": "g", "calories": 312, "protein": 13.5, "carbs": 53, "fats": 5.5},
                {"name": "Greek Yogurt", "quantity": 150, "unit": "g", "calories": 88, "protein": 15, "carbs": 5.4, "fats": 0.6},
                {"name": "Berries", "quantity": 100, "unit": "g", "calories": 57, "protein": 0.7, "carbs": 14, "fats": 0.3}
            ],
            "preparation": "Cook oatmeal. Top with Greek yogurt and fresh berries."
        },
        {
            "type": "lunch",
            "name": "Mediterranean Lunch",
            "target_calories": breakdown["lunch"],
            "foods": [
                {"name": "Chicken Breast", "quantity": 150, "unit": "g", "calories": 248, "protein": 46.5, "carbs": 0, "fats": 5.4},
                {"name": "Brown Rice", "quantity": 150, "unit": "g", "calories": 185, "protein": 3.9, "carbs": 38.4, "fats": 1.5},
                {"name": "Mixed Vegetables", "quantity": 150, "unit": "g", "calories": 45, "protein": 2.5, "carbs": 9, "fats": 0.5}
            ],
            "preparation": "Grill chicken. Serve over brown rice with steamed mixed vegetables."
        },
        {
            "type": "dinner",
            "name": "Balanced Dinner",
            "target_calories": breakdown["dinner"],
            "foods": [
                {"name": "Salmon", "quantity": 120, "unit": "g", "calories": 250, "protein": 24, "carbs": 0, "fats": 15.6},
                {"name": "Quinoa", "quantity": 100, "unit": "g", "calories": 120, "protein": 4.4, "carbs": 21.3, "fats": 1.9},
                {"name": "Spinach", "quantity": 100, "unit": "g", "calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4}
            ],
            "preparation": "Bake salmon with lemon. Cook quinoa. Sauté spinach with garlic."
        },
        {
            "type": "snacks",
            "name": "Healthy Snacks",
            "target_calories": breakdown["snacks"],
            "foods": [
                {"name": "Apple", "quantity": 150, "unit": "g", "calories": 78, "protein": 0.5, "carbs": 21, "fats": 0.3},
                {"name": "Peanut Butter", "quantity": 20, "unit": "g", "calories": 118, "protein": 5, "carbs": 4, "fats": 10}
            ],
            "preparation": "Slice apple and enjoy with peanut butter."
        }
    ]

@router.post("/workout-plan")
async def get_workout_plan(
    user_data: UserHealthData,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered workout plan"""
    try:
        prompt = f"""Create a 4-day workout plan for someone:
- Age: {user_data.age}, Gender: {user_data.gender}
- Goal: {user_data.goal}
- Activity Level: {user_data.activity_level}

Return ONLY valid JSON (no markdown):
{{
  "plan_name": "Descriptive plan name",
  "goal": "Goal description",
  "duration_weeks": 10,
  "weekly_schedule": [
    {{
      "day": 1,
      "focus": "Upper Body Push",
      "type": "strength",
      "duration": 60,
      "exercises": [
        {{"name": "Bench Press", "sets": 4, "reps": "8-10", "rest": 120}},
        {{"name": "Overhead Press", "sets": 3, "reps": "10-12", "rest": 90}}
      ]
    }}
  ],
  "tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5"],
  "nutrition_guidelines": {{
    "protein": "2.0g per kg",
    "carbs": "4-5g per kg", 
    "fats": "1.0g per kg",
    "water": "3-4 liters"
  }}
}}"""
        
        system_prompt = "You are a fitness trainer. Create detailed workout plans. Return ONLY valid JSON."
        workout_plan = call_free_ai(prompt, system_prompt, max_tokens=2000)
        return workout_plan
    except Exception as e:
        print(f"AI workout failed, using fallback: {e}")
        return workout_planner.generate_plan(user_data.goal, user_data.activity_level, 4)

@router.post("/predict-calories")
async def predict_calories(
    user_data: UserHealthData,
    current_user: dict = Depends(get_current_user)
):
    """Calculate calorie needs with insights"""
    bmr = diet_recommender.calculate_bmr(
        user_data.age, user_data.gender, user_data.height, user_data.weight
    )
    tdee = diet_recommender.calculate_tdee(bmr, user_data.activity_level)
    
    try:
        prompt = f"""Provide 3 brief nutrition insights for someone with:
- BMR: {round(bmr)} calories
- TDEE: {round(tdee)} calories  
- Goal: {user_data.goal}
- Activity: {user_data.activity_level}

Return ONLY JSON array: ["Insight 1", "Insight 2", "Insight 3"]"""
        
        insights = call_free_ai(prompt, "You are a nutrition expert. Return only JSON array.", max_tokens=200)
        if not isinstance(insights, list):
            raise Exception("Invalid response")
    except:
        insights = [
            f"Your body burns {round(bmr)} calories at rest daily",
            f"With your activity level, you need {round(tdee)} calories to maintain weight",
            f"Adjust your intake based on your goal of {user_data.goal}"
        ]
    
    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "recommended_calories": {
            "lose_weight": int(tdee - 500),
            "maintain": int(tdee),
            "gain_muscle": int(tdee + 300)
        },
        "insights": insights
    }

@router.get("/food-database")
async def get_food_database(current_user: dict = Depends(get_current_user)):
    """Get food database for meal logging"""
    foods = [
        {"name": "Chicken Breast", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
        {"name": "Brown Rice", "calories": 123, "protein": 2.6, "carbs": 25.6, "fats": 1.0},
        {"name": "Broccoli", "calories": 34, "protein": 2.8, "carbs": 7, "fats": 0.4},
        {"name": "Salmon", "calories": 208, "protein": 20, "carbs": 0, "fats": 13},
        {"name": "Sweet Potato", "calories": 86, "protein": 1.6, "carbs": 20, "fats": 0.1},
        {"name": "Eggs", "calories": 155, "protein": 13, "carbs": 1.1, "fats": 11},
        {"name": "Oatmeal", "calories": 389, "protein": 16.9, "carbs": 66.3, "fats": 6.9},
        {"name": "Banana", "calories": 89, "protein": 1.1, "carbs": 23, "fats": 0.3},
        {"name": "Almonds", "calories": 579, "protein": 21, "carbs": 22, "fats": 50},
        {"name": "Greek Yogurt", "calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
        {"name": "Spinach", "calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4},
        {"name": "Avocado", "calories": 160, "protein": 2, "carbs": 8.5, "fats": 14.7},
        {"name": "Quinoa", "calories": 120, "protein": 4.4, "carbs": 21.3, "fats": 1.9},
        {"name": "Tuna", "calories": 132, "protein": 28, "carbs": 0, "fats": 1.3},
        {"name": "Whole Wheat Bread", "calories": 247, "protein": 13, "carbs": 41, "fats": 3.4},
        {"name": "Apple", "calories": 52, "protein": 0.3, "carbs": 14, "fats": 0.2},
        {"name": "Peanut Butter", "calories": 588, "protein": 25, "carbs": 20, "fats": 50},
        {"name": "Cottage Cheese", "calories": 98, "protein": 11, "carbs": 3.4, "fats": 4.3},
        {"name": "Turkey Breast", "calories": 135, "protein": 30, "carbs": 0, "fats": 0.7},
        {"name": "Lentils", "calories": 116, "protein": 9, "carbs": 20, "fats": 0.4}
    ]
    return {"foods": foods}

@router.post("/chat-with-trainer")
async def chat_with_trainer(
    question: str,
    current_user: dict = Depends(get_current_user)
):
    """Chat with AI trainer - returns plain text response"""
    try:
        prompt = f"As a fitness and nutrition expert, answer this question briefly (2-3 sentences): {question}"
        
        # Try Gemini first
        if gemini_model:
            try:
                response = gemini_model.generate_content(prompt)
                return {"question": question, "answer": response.text}
            except Exception as e:
                print(f"Gemini failed: {e}")
        
        # Try Groq if Gemini failed
        if groq_client:
            try:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a professional fitness trainer and nutritionist. Give concise, helpful advice in 2-3 sentences."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=300,
                )
                return {"question": question, "answer": chat_completion.choices[0].message.content}
            except Exception as e:
                print(f"Groq failed: {e}")
        
        # Both failed
        raise Exception("No AI service available")
        
    except Exception as e:
        print(f"Chat failed: {e}")
        return {
            "question": question,
            "answer": "I'm currently unavailable. Please try again later or check your AI service configuration."
        }