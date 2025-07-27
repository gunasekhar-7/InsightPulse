"""Load and manage the latest trained sentiment analysis model and vectorizer.

This module automatically loads the most recently trained model (by timestamped folder)
from disk, including its vectorizer and metrics, and makes it available globally.

Usage Example:
    from models import bundle, MODEL_VERSION
    print(bundle.model, bundle.vectorizer, bundle.metadata)
"""

import json
import os
import time
from pathlib import Path
from threading import Lock
from typing import Optional
from sklearn.base import BaseEstimator
from core.config import get_settings
from loguru import logger
import joblib  # <--- This was missing


settings = get_settings()
MODEL_DIR = Path(settings.MODEL_DIR).resolve()
_LOAD_LOCK = Lock()  # Thread-safe singleton loading

class ModelBundle:
    """Container for the latest model, vectorizer, and training metrics.

    Automatically loads the most recent model from a timestamped directory.
    Thread-safe, singleton pattern—only one instance exists per Python process.
    """

    def __init__(self):
        self.vectorizer: Optional[BaseEstimator] = None
        self.model: Optional[BaseEstimator] = None
        self.metadata: dict = {}
        self.loaded_at: float = 0.0
        self.loaded_version: str = ""
        self.has_model: bool = False  # Health/readiness flag

    def load_latest(self) -> Optional[str]:
        """Load the latest model from a timestamped directory under MODEL_DIR."""
        candidates = sorted(MODEL_DIR.glob("*"), key=os.path.getmtime, reverse=True)
        if not candidates:
            logger.critical("No model folders found in %s. Please run `python train_model.py` first!", str(MODEL_DIR))
            return None

        latest = candidates[0]
        logger.info("Loading model from {}", latest)

        load_start = time.time()
        with _LOAD_LOCK:
            try:
                self.vectorizer = joblib.load(latest / "tfidf_vectorizer.pkl")
                self.model = joblib.load(latest / "sentiment_model.pkl")
                metrics_file = latest / "metrics.json"
                if metrics_file.exists():
                    with open(metrics_file, "r") as f:
                        self.metadata = json.load(f)
                else:
                    logger.warning("metrics.json missing in {}", latest)
                    self.metadata = {}

                # Validate that both model and vectorizer exist and are usable
                if not hasattr(self.model, "predict") or not hasattr(self.vectorizer, "transform"):
                    raise AttributeError("Model or vectorizer is invalid (missing predict/transform method).")

                self.loaded_version = latest.name
                self.loaded_at = time.time()
                self.has_model = True
                logger.success(
                    "Loaded model {}. Took {:.2f}s",
                    latest.name,
                    time.time() - load_start,
                )
                return self.loaded_version
            except Exception as e:
                logger.error("Failed to load model from {}: {}", latest, e)
                self.has_model = False
                return None  # Return None instead of raising

    def is_ready(self) -> bool:
        """Returns True if model and vectorizer are loaded and valid."""
        return self.has_model

bundle = ModelBundle()
MODEL_VERSION = bundle.load_latest()
if not MODEL_VERSION:
    logger.critical("Aborting: could not load any model. Please train a model first (python train_model.py) and restart the server.")
    # Optionally, raise SystemExit to abort startup:
    # raise SystemExit("No model available. Please train a model first.")
