from typing import List, Dict
import random

class WorkoutPlanner:
    def __init__(self):
        self.exercises_db = {
            "strength": {
                "chest": [
                    "Barbell Bench Press", "Incline Dumbbell Press", "Decline Bench Press",
                    "Dumbbell Flyes", "Cable Crossovers", "Push-ups", "Dips",
                    "Incline Bench Press", "Pec Deck Machine", "Landmine Press"
                ],
                "back": [
                    "Deadlifts", "Pull-ups", "Bent Over Barbell Rows", "Lat Pulldowns",
                    "Seated Cable Rows", "T-Bar Rows", "Single-Arm Dumbbell Rows",
                    "Face Pulls", "Hyperextensions", "Inverted Rows"
                ],
                "legs": [
                    "Barbell Squats", "Front Squats", "Romanian Deadlifts", "Leg Press",
                    "Bulgarian Split Squats", "Walking Lunges", "Leg Curls", "Leg Extensions",
                    "Calf Raises", "Goblet Squats", "Step-ups", "Hack Squats"
                ],
                "shoulders": [
                    "Overhead Press", "Arnold Press", "Lateral Raises", "Front Raises",
                    "Rear Delt Flyes", "Face Pulls", "Shrugs", "Upright Rows",
                    "Cable Lateral Raises", "Dumbbell Shoulder Press"
                ],
                "arms": [
                    "Barbell Curls", "Hammer Curls", "Preacher Curls", "Concentration Curls",
                    "Tricep Dips", "Skull Crushers", "Overhead Tricep Extension",
                    "Cable Tricep Pushdowns", "Close-Grip Bench Press", "Cable Curls"
                ],
                "core": [
                    "Planks", "Side Planks", "Russian Twists", "Leg Raises",
                    "Bicycle Crunches", "Mountain Climbers", "Dead Bug", "Pallof Press",
                    "Ab Wheel Rollouts", "Hanging Knee Raises", "Cable Crunches"
                ]
            },
            "cardio": [
                "Running (Outdoor)", "Treadmill Running", "Cycling (Outdoor)", 
                "Stationary Bike", "Swimming", "Rowing Machine", "Jump Rope",
                "Elliptical Trainer", "Stair Climber", "Battle Ropes",
                "Box Jumps", "Burpees", "High Knees", "Jumping Jacks",
                "Mountain Climbers", "Sprint Intervals"
            ],
            "hiit": [
                "Burpees", "Jump Squats", "Mountain Climbers", "High Knees",
                "Box Jumps", "Jumping Lunges", "Battle Ropes", "Kettlebell Swings",
                "Sprint Intervals", "Jumping Jacks", "Plank Jacks", "Tuck Jumps"
            ],
            "flexibility": [
                "Yoga Flow", "Dynamic Stretching", "Static Stretching", 
                "Foam Rolling", "Pilates", "Tai Chi", "Mobility Drills"
            ]
        }
    
    def generate_plan(self, goal: str, activity_level: str, days_per_week: int = 4) -> Dict:
        """Generate personalized workout plan based on user goals"""
        if goal == "lose_weight":
            return self._weight_loss_plan(days_per_week)
        elif goal == "gain_muscle":
            return self._muscle_gain_plan(days_per_week)
        elif goal == "improve_endurance":
            return self._endurance_plan(days_per_week)
        else:
            return self._maintenance_plan(days_per_week)
    
    def _weight_loss_plan(self, days: int) -> Dict:
        schedule = [
            {
                "day": 1, 
                "focus": "Full Body HIIT", 
                "type": "hiit",
                "duration": 30,
                "exercises": self._get_hiit_workout()
            },
            {
                "day": 2, 
                "focus": "Upper Body Strength + Cardio", 
                "type": "strength",
                "duration": 45,
                "exercises": self._get_upper_body_workout()
            },
            {
                "day": 3, 
                "focus": "Cardio Intervals", 
                "type": "cardio",
                "duration": 35,
                "exercises": self._get_cardio_workout()
            },
            {
                "day": 4, 
                "focus": "Lower Body + Core", 
                "type": "strength",
                "duration": 45,
                "exercises": self._get_lower_body_workout()
            },
            {
                "day": 5, 
                "focus": "Full Body Circuit", 
                "type": "strength",
                "duration": 40,
                "exercises": self._get_full_body_workout()
            },
            {
                "day": 6, 
                "focus": "Active Recovery & Flexibility", 
                "type": "flexibility",
                "duration": 30,
                "exercises": self._get_flexibility_workout()
            }
        ]
        
        return {
            "plan_name": "Weight Loss Accelerator",
            "goal": "Burn fat and improve cardiovascular fitness",
            "duration_weeks": 8,
            "weekly_schedule": schedule[:days],
            "tips": [
                "Focus on compound movements for maximum calorie burn",
                "Keep rest periods short (30-60 seconds) between sets",
                "Combine strength training with cardio for optimal results",
                "Stay in a moderate caloric deficit (300-500 calories)",
                "Aim for 10,000+ steps daily outside of workouts"
            ],
            "nutrition_guidelines": {
                "protein": "1.6-2.0g per kg body weight",
                "carbs": "Moderate - focus on complex carbs",
                "fats": "0.8-1.0g per kg body weight",
                "water": "3+ liters per day"
            }
        }
    
    def _muscle_gain_plan(self, days: int) -> Dict:
        schedule = [
            {
                "day": 1, 
                "focus": "Chest & Triceps", 
                "type": "strength",
                "duration": 60,
                "exercises": self._get_chest_triceps_workout()
            },
            {
                "day": 2, 
                "focus": "Back & Biceps", 
                "type": "strength",
                "duration": 60,
                "exercises": self._get_back_biceps_workout()
            },
            {
                "day": 3, 
                "focus": "Rest or Light Cardio", 
                "type": "rest",
                "duration": 20,
                "exercises": []
            },
            {
                "day": 4, 
                "focus": "Legs & Glutes", 
                "type": "strength",
                "duration": 70,
                "exercises": self._get_legs_workout()
            },
            {
                "day": 5, 
                "focus": "Shoulders & Core", 
                "type": "strength",
                "duration": 55,
                "exercises": self._get_shoulders_core_workout()
            },
            {
                "day": 6, 
                "focus": "Full Body Power", 
                "type": "strength",
                "duration": 60,
                "exercises": self._get_full_body_workout()
            }
        ]
        
        return {
            "plan_name": "Muscle Building Program",
            "goal": "Build muscle mass and increase strength",
            "duration_weeks": 12,
            "weekly_schedule": schedule[:days],
            "tips": [
                "Focus on progressive overload - increase weight gradually",
                "Aim for 8-12 reps per set for hypertrophy",
                "Rest 2-3 minutes between heavy compound sets",
                "Get 7-9 hours of quality sleep for recovery",
                "Eat in a caloric surplus (300-500 calories above maintenance)"
            ],
            "nutrition_guidelines": {
                "protein": "2.0-2.2g per kg body weight",
                "carbs": "High - 4-6g per kg body weight",
                "fats": "1.0-1.2g per kg body weight",
                "water": "3-4 liters per day"
            }
        }
    
    def _endurance_plan(self, days: int) -> Dict:
        schedule = [
            {
                "day": 1, 
                "focus": "Long Steady Cardio", 
                "type": "cardio",
                "duration": 45,
                "exercises": [{"name": "Running (Outdoor)", "duration": 45, "intensity": "moderate"}]
            },
            {
                "day": 2, 
                "focus": "Strength Endurance Circuit", 
                "type": "strength",
                "duration": 40,
                "exercises": self._get_endurance_circuit()
            },
            {
                "day": 3, 
                "focus": "Interval Training", 
                "type": "hiit",
                "duration": 30,
                "exercises": self._get_hiit_workout()
            },
            {
                "day": 4, 
                "focus": "Cross Training", 
                "type": "cardio",
                "duration": 40,
                "exercises": [{"name": "Cycling (Outdoor)", "duration": 40, "intensity": "moderate"}]
            },
            {
                "day": 5, 
                "focus": "Tempo Run", 
                "type": "cardio",
                "duration": 35,
                "exercises": [{"name": "Treadmill Running", "duration": 35, "intensity": "high"}]
            }
        ]
        
        return {
            "plan_name": "Endurance Builder",
            "goal": "Improve cardiovascular endurance and stamina",
            "duration_weeks": 10,
            "weekly_schedule": schedule[:days],
            "tips": [
                "Gradually increase distance/duration each week",
                "Mix different types of cardio to prevent overuse injuries",
                "Include recovery days for adaptation",
                "Focus on proper breathing techniques"
            ]
        }
    
    def _maintenance_plan(self, days: int) -> Dict:
        schedule = [
            {
                "day": 1, 
                "focus": "Upper Body Strength", 
                "type": "strength",
                "duration": 45,
                "exercises": self._get_upper_body_workout()
            },
            {
                "day": 2, 
                "focus": "Cardio Session", 
                "type": "cardio",
                "duration": 30,
                "exercises": self._get_cardio_workout()
            },
            {
                "day": 3, 
                "focus": "Lower Body Strength", 
                "type": "strength",
                "duration": 45,
                "exercises": self._get_lower_body_workout()
            },
            {
                "day": 4, 
                "focus": "Flexibility & Mobility", 
                "type": "flexibility",
                "duration": 30,
                "exercises": self._get_flexibility_workout()
            },
            {
                "day": 5, 
                "focus": "Full Body Workout", 
                "type": "strength",
                "duration": 45,
                "exercises": self._get_full_body_workout()
            }
        ]
        
        return {
            "plan_name": "Balanced Fitness Plan",
            "goal": "Maintain overall fitness and health",
            "duration_weeks": 8,
            "weekly_schedule": schedule[:days],
            "tips": [
                "Mix strength and cardio throughout the week",
                "Focus on maintaining current fitness levels",
                "Listen to your body and adjust intensity as needed",
                "Enjoy varied activities to stay motivated"
            ]
        }
    
    # Workout generator methods
    def _get_chest_triceps_workout(self) -> List[Dict]:
        return [
            {"name": "Barbell Bench Press", "sets": 4, "reps": "8-10", "rest": 120},
            {"name": "Incline Dumbbell Press", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Cable Crossovers", "sets": 3, "reps": "12-15", "rest": 60},
            {"name": "Dips", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Tricep Dips", "sets": 3, "reps": "10-12", "rest": 60},
            {"name": "Skull Crushers", "sets": 3, "reps": "10-12", "rest": 60},
            {"name": "Cable Tricep Pushdowns", "sets": 3, "reps": "12-15", "rest": 60}
        ]
    
    def _get_back_biceps_workout(self) -> List[Dict]:
        return [
            {"name": "Deadlifts", "sets": 4, "reps": "6-8", "rest": 180},
            {"name": "Pull-ups", "sets": 4, "reps": "8-10", "rest": 120},
            {"name": "Bent Over Barbell Rows", "sets": 4, "reps": "8-10", "rest": 90},
            {"name": "Lat Pulldowns", "sets": 3, "reps": "10-12", "rest": 60},
            {"name": "Barbell Curls", "sets": 3, "reps": "10-12", "rest": 60},
            {"name": "Hammer Curls", "sets": 3, "reps": "10-12", "rest": 60},
            {"name": "Preacher Curls", "sets": 3, "reps": "12-15", "rest": 60}
        ]
    
    def _get_legs_workout(self) -> List[Dict]:
        return [
            {"name": "Barbell Squats", "sets": 4, "reps": "8-10", "rest": 180},
            {"name": "Romanian Deadlifts", "sets": 4, "reps": "8-10", "rest": 120},
            {"name": "Leg Press", "sets": 3, "reps": "12-15", "rest": 90},
            {"name": "Bulgarian Split Squats", "sets": 3, "reps": "10-12 each", "rest": 90},
            {"name": "Leg Curls", "sets": 3, "reps": "12-15", "rest": 60},
            {"name": "Leg Extensions", "sets": 3, "reps": "12-15", "rest": 60},
            {"name": "Calf Raises", "sets": 4, "reps": "15-20", "rest": 60}
        ]
    
    def _get_shoulders_core_workout(self) -> List[Dict]:
        return [
            {"name": "Overhead Press", "sets": 4, "reps": "8-10", "rest": 120},
            {"name": "Lateral Raises", "sets": 4, "reps": "12-15", "rest": 60},
            {"name": "Front Raises", "sets": 3, "reps": "12-15", "rest": 60},
            {"name": "Rear Delt Flyes", "sets": 3, "reps": "12-15", "rest": 60},
            {"name": "Shrugs", "sets": 3, "reps": "12-15", "rest": 60},
            {"name": "Planks", "sets": 3, "reps": "60 sec", "rest": 60},
            {"name": "Russian Twists", "sets": 3, "reps": "20 each side", "rest": 60},
            {"name": "Hanging Knee Raises", "sets": 3, "reps": "12-15", "rest": 60}
        ]
    
    def _get_upper_body_workout(self) -> List[Dict]:
        return [
            {"name": "Barbell Bench Press", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Pull-ups", "sets": 3, "reps": "8-10", "rest": 90},
            {"name": "Overhead Press", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Bent Over Barbell Rows", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Barbell Curls", "sets": 3, "reps": "10-12", "rest": 60},
            {"name": "Tricep Dips", "sets": 3, "reps": "10-12", "rest": 60}
        ]
    
    def _get_lower_body_workout(self) -> List[Dict]:
        return [
            {"name": "Barbell Squats", "sets": 4, "reps": "10-12", "rest": 120},
            {"name": "Romanian Deadlifts", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Walking Lunges", "sets": 3, "reps": "12 each leg", "rest": 90},
            {"name": "Leg Press", "sets": 3, "reps": "12-15", "rest": 90},
            {"name": "Leg Curls", "sets": 3, "reps": "12-15", "rest": 60},
            {"name": "Calf Raises", "sets": 4, "reps": "15-20", "rest": 60},
            {"name": "Planks", "sets": 3, "reps": "60 sec", "rest": 60}
        ]
    
    def _get_full_body_workout(self) -> List[Dict]:
        return [
            {"name": "Deadlifts", "sets": 3, "reps": "8-10", "rest": 120},
            {"name": "Barbell Bench Press", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Barbell Squats", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Pull-ups", "sets": 3, "reps": "8-10", "rest": 90},
            {"name": "Overhead Press", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Romanian Deadlifts", "sets": 3, "reps": "10-12", "rest": 90},
            {"name": "Planks", "sets": 3, "reps": "60 sec", "rest": 60}
        ]
    
    def _get_hiit_workout(self) -> List[Dict]:
        return [
            {"name": "Burpees", "sets": 4, "reps": "30 sec work, 30 sec rest"},
            {"name": "Jump Squats", "sets": 4, "reps": "30 sec work, 30 sec rest"},
            {"name": "Mountain Climbers", "sets": 4, "reps": "30 sec work, 30 sec rest"},
            {"name": "High Knees", "sets": 4, "reps": "30 sec work, 30 sec rest"},
            {"name": "Box Jumps", "sets": 4, "reps": "30 sec work, 30 sec rest"},
            {"name": "Battle Ropes", "sets": 4, "reps": "30 sec work, 30 sec rest"}
        ]
    
    def _get_cardio_workout(self) -> List[Dict]:
        options = [
            {"name": "Treadmill Running", "duration": 30, "intensity": "moderate", "notes": "Maintain 70-75% max heart rate"},
            {"name": "Cycling (Outdoor)", "duration": 35, "intensity": "moderate", "notes": "Steady pace"},
            {"name": "Rowing Machine", "duration": 25, "intensity": "moderate", "notes": "Focus on form"},
            {"name": "Swimming", "duration": 30, "intensity": "moderate", "notes": "Mix different strokes"}
        ]
        return [random.choice(options)]
    
    def _get_flexibility_workout(self) -> List[Dict]:
        return [
            {"name": "Dynamic Stretching", "duration": 10, "notes": "Leg swings, arm circles, hip rotations"},
            {"name": "Yoga Flow", "duration": 15, "notes": "Focus on breath and form"},
            {"name": "Static Stretching", "duration": 5, "notes": "Hold each stretch 30 seconds"}
        ]
    
    def _get_endurance_circuit(self) -> List[Dict]:
        return [
            {"name": "Push-ups", "sets": 3, "reps": "15-20", "rest": 30},
            {"name": "Squats", "sets": 3, "reps": "20-25", "rest": 30},
            {"name": "Planks", "sets": 3, "reps": "45 sec", "rest": 30},
            {"name": "Lunges", "sets": 3, "reps": "15 each leg", "rest": 30},
            {"name": "Mountain Climbers", "sets": 3, "reps": "30 sec", "rest": 30}
        ]
    
    def get_exercise_details(self, workout_type: str, muscle_group: str = None) -> List[Dict]:
        """Get specific exercise details for a given workout type and muscle group"""
        exercises = []
        
        if workout_type == "strength" and muscle_group:
            exercise_names = self.exercises_db["strength"].get(muscle_group, [])
            selected = random.sample(exercise_names, min(5, len(exercise_names)))
            
            for name in selected:
                exercises.append({
                    "name": name,
                    "sets": random.randint(3, 4),
                    "reps": f"{random.randint(8, 12)}-{random.randint(12, 15)}",
                    "rest": random.choice([60, 90, 120]),
                    "notes": "Focus on proper form and controlled movements"
                })
        
        elif workout_type == "cardio":
            exercise_names = random.sample(self.exercises_db["cardio"], min(3, len(self.exercises_db["cardio"])))
            for name in exercise_names:
                exercises.append({
                    "name": name,
                    "duration": random.randint(15, 30),
                    "intensity": random.choice(["low", "moderate", "high"]),
                    "notes": "Maintain steady pace"
                })
        
        elif workout_type == "hiit":
            exercise_names = random.sample(self.exercises_db["hiit"], min(6, len(self.exercises_db["hiit"])))
            for name in exercise_names:
                exercises.append({
                    "name": name,
                    "sets": 4,
                    "reps": "30 sec work, 30 sec rest",
                    "notes": "Maximum effort during work periods"
                })
        
        return exercises

