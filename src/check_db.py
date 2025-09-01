from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def check_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.mergington_high
    activities = await db.activities.find({}).to_list(length=None)
    print(f"Found {len(activities)} activities:")
    for activity in activities:
        print(f"\n{activity["name"]}:")
        print(f"  Description: {activity["description"]}")
        print(f"  Schedule: {activity["schedule"]}")
        print(f"  Max participants: {activity["max_participants"]}")
        print(f"  Current participants: {len(activity["participants"])}")

asyncio.run(check_db())
