"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from typing import List

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# MongoDB connection
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.mergington_high

# Dependency to get database collection
async def get_activities_collection():
    return db.activities

# Keeping this commented out as reference
_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    # Sports activities
    "Soccer Team": {
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    # Artistic activities
    "Drama Club": {
        "description": "Act, direct, and participate in school theater productions",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    # Intellectual activities
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 10,
        "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["james@mergington.edu", "harper@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
async def get_activities(collection = Depends(get_activities_collection)):
    """Get all activities"""
    cursor = collection.find({}, {'_id': 0})  # Exclude MongoDB _id field
    activities_list = await cursor.to_list(length=None)
    
    # Convert to the expected format with activity name as key
    return {activity["name"]: {k: v for k, v in activity.items() if k != "name"} 
            for activity in activities_list}


@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(
    activity_name: str, 
    email: str, 
    collection = Depends(get_activities_collection)
):
    """Sign up a student for an activity"""
    # Find the activity
    activity = await collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    # Validate activity is not full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    
    # Add student to participants array
    result = await collection.update_one(
        {"name": activity_name},
        {"$push": {"participants": email}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update activity")
    
    return {"message": f"Signed up {email} for {activity_name}"}

@app.delete("/activities/{activity_name}/unregister")
async def unregister_from_activity(
    activity_name: str,
    email: str,
    collection = Depends(get_activities_collection)
):
    """Unregister a student from an activity"""
    # Find and update the activity
    result = await collection.update_one(
        {"name": activity_name},
        {"$pull": {"participants": email}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Activity not found")
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Student not registered for this activity")
    
    return {"message": f"Unregistered {email} from {activity_name}"}
