class CaloriePredictor:
    def __init__(self):
        self.activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        # Exercise calorie burn rates (calories per minute for 70kg person)
        self.exercise_calories = {
            "Running (Outdoor)": 11.4,
            "Treadmill Running": 11.0,
            "Cycling (Outdoor)": 7.5,
            "Stationary Bike": 6.8,
            "Swimming": 9.0,
            "Jump Rope": 12.3,
            "Rowing Machine": 8.5,
            "Elliptical Trainer": 7.0,
            "Stair Climber": 9.0,
            "HIIT": 12.0,
            "Weight Training": 6.0,
            "Strength Training": 6.0,
            "Yoga": 3.0,
            "Pilates": 4.0,
            "Walking": 4.0,
            "Burpees": 10.0,
            "Box Jumps": 9.5,
            "Battle Ropes": 10.5,
            "Kettlebell Swings": 9.8
        }
    
    def calculate_bmr(self, age: int, gender: str, height: float, weight: float) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
        
        Args:
            age: Age in years
            gender: 'male' or 'female'
            height: Height in centimeters
            weight: Weight in kilograms
        
        Returns:
            BMR in calories per day
        """
        if gender.lower() == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
        return round(bmr, 2)
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure
        
        Args:
            bmr: Basal Metabolic Rate
            activity_level: Activity level (sedentary, light, moderate, active, very_active)
        
        Returns:
            TDEE in calories per day
        """
        multiplier = self.activity_multipliers.get(activity_level.lower(), 1.55)
        return round(bmr * multiplier, 2)
    
    def predict(self, age: int, gender: str, height: float, weight: float, activity_level: str) -> dict:
        """
        Predict comprehensive calorie needs and macronutrient breakdown
        
        Args:
            age: Age in years
            gender: 'male' or 'female'
            height: Height in centimeters
            weight: Weight in kilograms
            activity_level: Activity level
        
        Returns:
            Dictionary containing BMR, TDEE, calorie recommendations, and macros
        """
        bmr = self.calculate_bmr(age, gender, height, weight)
        tdee = self.calculate_tdee(bmr, activity_level)
        
        return {
            "bmr": bmr,
            "tdee": tdee,
            "recommended_calories": {
                "maintenance": int(tdee),
                "weight_loss": int(tdee - 500),
                "moderate_weight_loss": int(tdee - 300),
                "extreme_weight_loss": int(tdee - 750),
                "muscle_gain": int(tdee + 300),
                "lean_bulk": int(tdee + 200)
            },
            "macronutrients": {
                "weight_loss": {
                    "protein_g": round(weight * 2.0, 1),
                    "protein_calories": round(weight * 2.0 * 4, 0),
                    "carbs_g": round((tdee - 500) * 0.40 / 4, 1),
                    "carbs_calories": round((tdee - 500) * 0.40, 0),
                    "fats_g": round((tdee - 500) * 0.30 / 9, 1),
                    "fats_calories": round((tdee - 500) * 0.30, 0),
                    "ratio": "40% Protein / 40% Carbs / 20% Fats"
                },
                "muscle_gain": {
                    "protein_g": round(weight * 2.2, 1),
                    "protein_calories": round(weight * 2.2 * 4, 0),
                    "carbs_g": round((tdee + 300) * 0.50 / 4, 1),
                    "carbs_calories": round((tdee + 300) * 0.50, 0),
                    "fats_g": round((tdee + 300) * 0.25 / 9, 1),
                    "fats_calories": round((tdee + 300) * 0.25, 0),
                    "ratio": "30% Protein / 50% Carbs / 20% Fats"
                },
                "maintenance": {
                    "protein_g": round(weight * 1.8, 1),
                    "protein_calories": round(weight * 1.8 * 4, 0),
                    "carbs_g": round(tdee * 0.45 / 4, 1),
                    "carbs_calories": round(tdee * 0.45, 0),
                    "fats_g": round(tdee * 0.30 / 9, 1),
                    "fats_calories": round(tdee * 0.30, 0),
                    "ratio": "25% Protein / 45% Carbs / 30% Fats"
                }
            },
            "guidelines": {
                "min_calories": 1200 if gender.lower() == "female" else 1500,
                "max_deficit": 1000,
                "water_liters": round(weight * 0.033, 1),
                "water_oz": round(weight * 0.033 * 33.814, 0),
                "protein_per_kg": "1.6-2.2g",
                "meal_frequency": "3-5 meals per day",
                "weekly_weight_loss": "0.5-1kg (safe range)",
                "weekly_weight_gain": "0.25-0.5kg (lean bulk)"
            }
        }
    
    def estimate_workout_calories(self, exercise_type: str, duration: int, weight: float) -> dict:
        """
        Estimate calories burned during a specific workout
        
        Args:
            exercise_type: Type of exercise
            duration: Duration in minutes
            weight: Body weight in kilograms
        
        Returns:
            Dictionary with calorie estimates and details
        """
        base_rate = self.exercise_calories.get(exercise_type, 6.0)
        # Adjust for body weight (base rate is for 70kg person)
        adjusted_rate = base_rate * (weight / 70)
        calories = adjusted_rate * duration
        
        return {
            "exercise": exercise_type,
            "duration_minutes": duration,
            "calories_burned": int(calories),
            "calories_per_minute": round(adjusted_rate, 2),
            "intensity": self._get_intensity_level(base_rate),
            "equivalent": {
                "walking_minutes": int(calories / (4.0 * weight / 70)),
                "running_minutes": int(calories / (11.4 * weight / 70))
            }
        }
    
    def _get_intensity_level(self, cal_per_min: float) -> str:
        """Determine exercise intensity based on calorie burn rate"""
        if cal_per_min >= 10:
            return "High Intensity"
        elif cal_per_min >= 7:
            return "Moderate-High Intensity"
        elif cal_per_min >= 5:
            return "Moderate Intensity"
        else:
            return "Low-Moderate Intensity"
    
    def calculate_meal_calories(self, tdee: float, goal: str, meals_per_day: int) -> dict:
        """
        Calculate recommended calories per meal based on goal
        
        Args:
            tdee: Total Daily Energy Expenditure
            goal: Fitness goal (maintenance, weight_loss, muscle_gain)
            meals_per_day: Number of meals per day
        
        Returns:
            Dictionary with meal calorie breakdown
        """
        calorie_adjustments = {
            "maintenance": 0,
            "weight_loss": -500,
            "moderate_weight_loss": -300,
            "muscle_gain": 300,
            "lean_bulk": 200
        }
        
        adjustment = calorie_adjustments.get(goal, 0)
        daily_target = tdee + adjustment
        
        # Standard meal distribution (breakfast, lunch, dinner)
        if meals_per_day == 3:
            distribution = [0.30, 0.35, 0.35]  # 30% breakfast, 35% lunch, 35% dinner
        elif meals_per_day == 4:
            distribution = [0.25, 0.30, 0.25, 0.20]  # Add snack
        elif meals_per_day == 5:
            distribution = [0.20, 0.15, 0.30, 0.15, 0.20]  # 5 smaller meals
        else:
            distribution = [1.0 / meals_per_day] * meals_per_day
        
        meals = []
        meal_names = ["Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner", "Evening Snack"]
        
        for i, percent in enumerate(distribution):
            meals.append({
                "meal": meal_names[i] if i < len(meal_names) else f"Meal {i+1}",
                "calories": int(daily_target * percent),
                "percentage": f"{int(percent * 100)}%"
            })
        
        return {
            "daily_target": int(daily_target),
            "meals_per_day": meals_per_day,
            "meal_breakdown": meals,
            "pre_workout_snack": int(daily_target * 0.10),
            "post_workout_meal": int(daily_target * 0.25)
        }
    
    def get_food_recommendations(self, goal: str) -> dict:
        """
        Get food recommendations based on fitness goal
        
        Args:
            goal: Fitness goal
        
        Returns:
            Dictionary with food recommendations
        """
        recommendations = {
            "weight_loss": {
                "proteins": ["Chicken breast", "Turkey", "Fish (salmon, tuna)", "Egg whites", "Greek yogurt", "Tofu"],
                "carbs": ["Oatmeal", "Brown rice", "Sweet potato", "Quinoa", "Whole grain bread", "Vegetables"],
                "fats": ["Avocado", "Nuts (almonds, walnuts)", "Olive oil", "Fatty fish", "Seeds"],
                "avoid": ["Sugary drinks", "Processed foods", "Fried foods", "Excessive alcohol", "White bread"],
                "tips": [
                    "Eat protein with every meal",
                    "Fill half your plate with vegetables",
                    "Drink water before meals",
                    "Avoid late-night snacking"
                ]
            },
            "muscle_gain": {
                "proteins": ["Chicken", "Beef", "Fish", "Eggs", "Milk", "Protein powder", "Greek yogurt"],
                "carbs": ["Rice", "Pasta", "Oats", "Potatoes", "Bread", "Fruits", "Quinoa"],
                "fats": ["Nuts", "Nut butter", "Avocado", "Olive oil", "Whole eggs", "Fatty fish"],
                "supplements": ["Whey protein", "Creatine", "BCAAs (optional)", "Multivitamin"],
                "tips": [
                    "Eat every 3-4 hours",
                    "Consume protein within 30 min after workout",
                    "Don't skip post-workout meal",
                    "Get 1g protein per lb body weight"
                ]
            },
            "maintenance": {
                "proteins": ["Chicken", "Fish", "Eggs", "Legumes", "Greek yogurt", "Lean beef"],
                "carbs": ["Whole grains", "Fruits", "Vegetables", "Oats", "Rice", "Pasta"],
                "fats": ["Nuts", "Olive oil", "Avocado", "Fish", "Seeds"],
                "tips": [
                    "Balance your macronutrients",
                    "Eat a variety of foods",
                    "Stay hydrated",
                    "Practice portion control"
                ]
            }
        }
        
        return recommendations.get(goal, recommendations["maintenance"])