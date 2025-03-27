import os
from dotenv import load_dotenv

load_dotenv()

USE_DOCKER = os.getenv("USE_DOCKER", "false").lower() == "true"
USE_LAPTOP = os.getenv("USE_LAPTOP", "false").lower() == "true"

if USE_DOCKER:
    DATABASE_URL = os.getenv("DATABASE_URL_DOCKER")
elif USE_LAPTOP:
    DATABASE_URL = os.getenv("DATABASE_URL_LAPTOP")
else:
    DATABASE_URL = os.getenv("DATABASE_URL_LOCAL")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")