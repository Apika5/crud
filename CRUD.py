from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI()

MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["mydatabase"]
collection = database["items"]

class Item(BaseModel):
    name: str
    description: str = None
    id: str = None
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    result = await collection.insert_one(item.dict())
    item.id = str(result.inserted_id)
    return item

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    item = await collection.find_one({"_id": item_id})
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    updated_item = await collection.find_one_and_update(
        {"_id": item_id}, {"$set": item.dict()}, return_document=True
    )
    if updated_item:
        return Item(**updated_item)
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: str):
    deleted_item = await collection.find_one_and_delete({"_id": item_id})
    if deleted_item:
        return Item(**deleted_item)
    raise HTTPException(status_code=404, detail="Item not found")
