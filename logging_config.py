# logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import json

# Configure logging
log_formatter = logging.Formatter(
    json.dumps({
        "level": "%(levelname)s",
        "time": "%(asctime)s",
        "message": "%(message)s",
        "path": "%(pathname)s",
        "line": "%(lineno)d"
    })
)

log_handler = RotatingFileHandler("app.log", maxBytes=1000000, backupCount=3)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
