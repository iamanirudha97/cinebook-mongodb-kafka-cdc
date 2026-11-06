import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.environ["MONGODB_URI"]
db_name = os.getenv("MONGODB_DB", "cinebook")

client = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    client.admin.command("ping")
    print("MongoDB Atlas connection successful!")
    print(f"Database selected: {db_name}")
finally:
    client.close()
