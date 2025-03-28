import logging
from loggly.handlers import HTTPSHandler
from core.config import LOGGLY_TOKEN


def get_logger(name: str):
    """
    Create a logger that sends logs to Loggly."
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        https_handler = HTTPSHandler(url=f"https://logs-01.loggly.com/inputs/{LOGGLY_TOKEN}/tag/python")
        formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(name)s | %(message)s")
        https_handler.setFormatter(formatter)
        logger.addHandler(https_handler)
    return logger
