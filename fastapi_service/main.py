#MAIN
import json
import logging
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# MongoDB connection
MONGO_URL = "mongodb://admin:admin@mongodb:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["spotify"]
collection = db["myList"]

#endpoint status OK 
@app.get("/", tags=["home"])
async def root():
    return {'status':'ok 👍🐍 '}

# Endpoint to create a new database named "spotify"
@app.post("/create_database", tags=["database"])
async def create_database():
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        # Create the "spotify" database
        await client.admin.command("create", "spotify")
        return {"message": "Database 'spotify' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating database: {e}")
    
# Endpoint to create a new collection named "myList" in the "spotify" database
@app.post("/create_collection", tags=["database"])
async def create_collection():
    try:
        # Connect to the "spotify" database
        db = client["spotify"]
        # Create the "myList" collection
        await db.create_collection("myList")
        return {"message": "Collection 'myList' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collection: {e}")
    
# Endpoint to create a new song
@app.post("/create_songs", tags=["songs"])
async def create_song(song_data: dict):
    try:
        # Exclude the _id field from the song data
        song_data.pop("_id", None)
    
        # Insert the new song document into the collection
        result = await collection.insert_one(song_data)
        
        # Retrieve the inserted document
        inserted_song = await collection.find_one({"_id": result.inserted_id})
        inserted_song.pop('_id', None)
        return inserted_song
    except Exception as e:
        logger.error(f"Error creating song: {e}")
        raise HTTPException(status_code=500, detail="Error creating song")


# Endpoint to retrieve all students
@app.get("/songs")
async def get_all_songs():
    songs = []
    async for song in collection.find({}):  # Retrieve all documents in the collection
        # Remove the '_id' field from each song document
        song.pop('_id', None)
        songs.append(song)
    return songs




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
