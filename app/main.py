from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, users, workouts, meals, social, ai, water  # ADD water here

app = FastAPI(
    title="Fitness Tracker API",
    description="Complete fitness tracking application with AI features",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000",
    #     "https://health-fitness-tracker-frontend.vercel.app"],
    
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://health-fitness-tracker-main-fronten.vercel.app",  # Your Vercel frontend
        "https://healthfitnesstrackermain-backend.onrender.com",  # Backend itself (optional)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include routers - VERIFY THIS ORDER
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(workouts.router, prefix="/workouts", tags=["Workouts"])
app.include_router(meals.router, prefix="/meals", tags=["Meals"])
app.include_router(water.router, prefix="/water", tags=["Water"])  # ADD this line
app.include_router(social.router, prefix="/social", tags=["Social"])
app.include_router(ai.router, prefix="/ai", tags=["AI Features"])

@app.get("/")
async def root():
    return {
        "message": "Fitness Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}