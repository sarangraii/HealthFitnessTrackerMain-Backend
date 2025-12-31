from typing import Dict, List

class DietRecommender:
    def __init__(self):
        self.activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
    
    def calculate_bmr(self, age: int, gender: str, height: float, weight: float) -> float:
        if gender.lower() == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        multiplier = self.activity_multipliers.get(activity_level, 1.55)
        return bmr * multiplier
    
    def get_calorie_target(self, tdee: float, goal: str) -> int:
        if goal == "lose_weight":
            return int(tdee - 500)
        elif goal == "gain_muscle":
            return int(tdee + 300)
        else:
            return int(tdee)
    
    def calculate_macros(self, calories: int, goal: str) -> Dict[str, int]:
        if goal == "lose_weight":
            protein_ratio = 0.35
            carbs_ratio = 0.35
            fats_ratio = 0.30
        elif goal == "gain_muscle":
            protein_ratio = 0.30
            carbs_ratio = 0.45
            fats_ratio = 0.25
        else:
            protein_ratio = 0.30
            carbs_ratio = 0.40
            fats_ratio = 0.30
        
        return {
            "protein": int((calories * protein_ratio) / 4),
            "carbs": int((calories * carbs_ratio) / 4),
            "fats": int((calories * fats_ratio) / 9)
        }
    
    def create_meal_breakdown(self, total_calories: int) -> Dict[str, int]:
        return {
            "breakfast": int(total_calories * 0.25),
            "lunch": int(total_calories * 0.35),
            "dinner": int(total_calories * 0.30),
            "snacks": int(total_calories * 0.10)
        }
    
    def get_recommendations(self, goal: str) -> List[str]:
        base = [
            "Drink at least 8 glasses of water daily",
            "Include vegetables in every meal",
            "Choose whole grains over refined grains"
        ]
        
        if goal == "lose_weight":
            base.extend([
                "Focus on high-protein, low-calorie foods",
                "Increase fiber intake to stay full longer",
                "Limit processed foods and added sugars"
            ])
        elif goal == "gain_muscle":
            base.extend([
                "Consume protein within 30 minutes after workout",
                "Eat frequent smaller meals throughout the day",
                "Include healthy fats like nuts and avocados"
            ])
        else:
            base.extend([
                "Maintain balanced portions",
                "Include variety in your diet",
                "Listen to your hunger cues"
            ])
        
        return base