from dotenv import load_dotenv
from pathlib import Path
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables from project root .env, overriding any existing values
project_root = Path(__file__).parent.parent
load_dotenv(dotenv_path=project_root / ".env", override=True)

# Retrieve and validate the MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")
print("→ MONGO_URI =", repr(MONGO_URI))
if not MONGO_URI or not MONGO_URI.startswith(("mongodb://", "mongodb+srv://")):
    raise RuntimeError(f"Invalid or missing MONGO_URI: {MONGO_URI!r}")

# Initialize Motor client and select the database explicitly
client = AsyncIOMotorClient(MONGO_URI)
db = client["cloud_gateway_proj"]  # replace with your target database name

# FastAPI dependency to provide the database instance to routes

def get_database():
    """Return the MongoDB database instance."""
    return db
