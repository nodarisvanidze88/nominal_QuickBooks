from celery import Celery
from utils.logger import get_logger
from services.token_service import get_latest_token
from services.quickbooks_service import fetch_accounts_from_qbo, save_accounts_to_db
from core.config import CELERY_REDIS_URL, CELERY_SCHEDULE_INTERVAL
from database.session import SessionLocal


celery_logger = get_logger("celery.task")

celery_app = Celery(
    "worker",
    broker=CELERY_REDIS_URL,
    backend=CELERY_REDIS_URL
)

celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        'update-qbo-accounts-every-minute': {
            'task': 'tasks.tasks.update_qbo_accounts',
            'schedule': CELERY_SCHEDULE_INTERVAL,
        },
    },
    broker_pool_limit=5,
    broker_connection_timeout=10,
    broker_heartbeat=0
)
# celery_app.conf.timezone = 'UTC'
# DB session


@celery_app.task
def update_qbo_accounts():
    celery_logger.info("🚀 Background task started: Checking token and updating accounts")
    db = SessionLocal()

    token = get_latest_token(db)
    if not token or token.is_token_expired():
        celery_logger.warning("⚠️ No valid token found. Please refresh the token.")
        db.close()
        return
    try:
        response = fetch_accounts_from_qbo(token)
        if response.status_code == 200:
            accounts_data = response.json().get("QueryResponse", {}).get("Account", [])
            save_accounts_to_db(db, accounts_data)
            celery_logger.info("✅ Accounts updated successfully.")
        else:
            celery_logger.warning(f"⚠️ Failed to update accounts. Status: {response.status_code}")
    except Exception as e:
        celery_logger.exception(f"💥 Exception during account update: {str(e)}")
    finally:
        db.close()
