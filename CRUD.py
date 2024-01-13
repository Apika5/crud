from fastapi import FastAPI, HTTPException  #Здесь импортируется класс FastAPI из библиотеки, который предоставляет основные функции
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import List

app = FastAPI()

# тут подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["library"]
collection = db["movies"]

class Movie(BaseModel):
    title: str
    director: str
    release_year: int

@app.post("/movies", response_model=Movie)
def create_movie(movie: Movie):
    # Дальше добавление фильма в базу данных
    movie_data = {
        "title": movie.title,
        "director": movie.director,
        "release_year": movie.release_year
    }
    result = collection.insert_one(movie_data)
    movie_id = result.inserted_id

    return {"title": movie.title, "director": movie.director, "release_year": movie.release_year, "_id": str(movie_id)}

@app.get("/movies", response_model=List[Movie])
def read_movies():
    # Потом получение списка фильмов из базы данных
    movies = list(collection.find({}, {"_id": 0}))
    return movies

@app.get("/movies/{movie_id}", response_model=Movie)
def read_movie(movie_id: str):
    # Тут получение конкретного фильма по идентификатору из БД
    movie = collection.find_one({"_id": ObjectId(movie_id)}, {"_id": 0})
    if movie:
        return movie
    raise HTTPException(status_code=404, detail="Movie not found")

@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: str, movie: Movie):
    # Обновление фильма в БД
    result = collection.update_one(
        {"_id": ObjectId(movie_id)},
        {"$set": {
            "title": movie.title,
            "director": movie.director,
            "release_year": movie.release_year
        }}
    )

    if result.modified_count == 1:
        return {"title": movie.title, "director": movie.director, "release_year": movie.release_year}
    raise HTTPException(status_code=404, detail="Movie not found")

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: str):
    # И удаление фильма
    result = collection.delete_one({"_id": ObjectId(movie_id)})

    if result.deleted_count == 1:
        return {"message": "Movie deleted"}
    raise HTTPException(status_code=404, detail="Movie not found")
