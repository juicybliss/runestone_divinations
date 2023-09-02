import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request

# to test for now...
CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL);"
)

# To use for realzies...
# CREATE_USERS_TABLE = (
#     "CREATE TABLE IF NOT EXSISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email VARCHAR UNIQUE NOT NULL, password TEXT NOT NULL);"
# )

CREATE_COLLECTIONS_TABLE = (
    "CREATE TABLE IF NOT EXISTS collections (id SERIAL PRIMARY KEY, title TEXT NOT NULL, description TEXT);"
)

# CREATE_DIVINATIONS_TABLE = (
#     "CREATE TABLE IF NOT EXISTS divinations (id SERIAL PRIMARY KEY, date_created DATE NOT NULL, question TEXT NOT NULL, spread_type_and_explanation TEXT NOT NULL, stone_type_and_explanation TEXT NOT NULL, spread JSON NOT NULL, spread_explanation JSON NOT NULL);"
# )

CREATE_USERS_COLLECTIONS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users_collections (user_id INT PRIMARY KEY, collection_id INT, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(collection_id) REFERENCES collections(id));"
)

# CREATE_COLLECTIONS_DIVINATIONS_TABLE = (
#     "CREATE TABLE IF NOT EXSISTS collections_divinations (collection_id INT PRIMARY KEY, divination_id INT PRIMARY KEY, FOREIGN KEY(divination_id) REFERENCES divination(id), FOREIGN KEY(collection_id) REFERENCES collections(id));"
# )

# CREATE_USERS_DIVINATIONS_TABLE = (
#     "CREATE TABLE IF NOT EXSISTS users_divinations (user_id INT PRIMARY KEY, divination_id INT PRIMARY KEY, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(divination_id) REFERENCES divinations(id));"
# )

INSERT_USER_RETURN_ID = "INSERT INTO users (username) VALUES (%s) RETURNING id;"

INSERT_COLLECTION_RETURN_ID = (
    "INSERT INTO collections (title, description) VALUES (%s, %s) RETURNING id;"
)
INSERT_USERS_COLLECTIONS = (
    "INSERT INTO users_collections (user_id, collection_id) VALUES (%s, %s);"
)

load_dotenv()

app = Flask(__name__)
url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)


@app.get("/")
def home():
    return "Hello Friend!"


@app.post("/api/user")
def create_user():
    data = request.get_json()
    username = data["username"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(INSERT_USER_RETURN_ID, (username,))
            room_id = cursor.fetchone()[0]
    return {"id": room_id, "message": f"User {username} created."}, 201


@app.post("/api/collection")
def create_collection():
    data = request.get_json()
    title = data["title"]
    description = data["description"]
    user_id = data["user_id"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_COLLECTIONS_TABLE)
            cursor.execute(CREATE_USERS_COLLECTIONS_TABLE)
            cursor.execute(INSERT_COLLECTION_RETURN_ID, (title, description))
            collection_id = cursor.fetchone()[0]
            cursor.execute(INSERT_USERS_COLLECTIONS, (user_id, collection_id))
    return {"id": collection_id, "message": f"User {title} created."}, 201
