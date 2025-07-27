import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

def setup_logging(
    log_dir: str = "logs",
    log_file: str = "app.log",
    log_level: str = "INFO",
    max_bytes: int = 20 * 1024 * 1024,  # 20MB
    backup_count: int = 5
):
    """Set up logging with rotating file handler and stdout."""
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    log_path = path / log_file

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Disable uvicorn's duplicated logs
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.error").handlers.clear()
    logging.getLogger("uvicorn").handlers.clear()
