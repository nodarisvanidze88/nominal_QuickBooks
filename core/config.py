import os
from dotenv import load_dotenv
from intuitlib.client import AuthClient
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

ACCOUNT_API_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/query"

auth_client = AuthClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    environment=ENVIRONMENT,
    redirect_uri=REDIRECT_URI,
)
LOGGLY_TOKEN = os.getenv("LOGGLY_TOKEN")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
CELERY_REDIS_URL = f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_SCHEDULE_INTERVAL = int(os.getenv("CELERY_SCHEDULE_INTERVAL", 600))  # 10 minutes default