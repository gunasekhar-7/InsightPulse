from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict
import uuid
from datetime import datetime
from core.config import get_settings
from services import cleaner, cache
from models import bundle, MODEL_VERSION
from api.deps import authenticate, create_access_token, get_current_user, init_rate_limiter, limiter
from structlog import get_logger
from sklearn.exceptions import NotFittedError
from starlette.websockets import WebSocket, WebSocketDisconnect
from core.logging_config import setup_logging


from core.logging_config import setup_logging
setup_logging()

settings = get_settings()
logger = get_logger()
app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION)

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Rate limiter -----
init_rate_limiter(app)

from datetime import datetime

import uuid
from starlette.requests import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    return response


# ----- Schemas -----
class AuthIn(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {"username": "user", "password": "password"}
        }

class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SentimentIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)

    class Config:
        json_schema_extra = {
            "example": {"text": "The service was quick and friendly!"}
        }

class Probabilities(BaseModel):
    positive: float
    negative: float
    neutral: float

class SentimentOut(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    probabilities: Probabilities
    cleaned_text: str
    model_version: str

# ----- Auth endpoints -----
@app.post(
    "/auth/login",
    response_model=AuthOut,
    tags=["auth"],
    summary="Authenticate and receive JWT token",
    description="Use your username and password to get a JWT for API access.",
)
async def login(payload: AuthIn):
    user = authenticate(payload.username, payload.password)
    if not user:
        logger.warning("login_failed", username=payload.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )
    token = create_access_token({"sub": payload.username})  # See deps.py for expiry
    logger.info("login_success", username=payload.username)
    return {"access_token": token, "token_type": "bearer"}

# ----- Sentiment analysis endpoint -----
@app.post(
    "/analyze",
    response_model=SentimentOut,
    tags=["inference"],
    summary="Analyze text sentiment",
    description="Submit text and receive its sentiment prediction and probabilities.",
)
@limiter.limit(settings.RATE_LIMIT)
async def analyze(
    payload: SentimentIn,
    user=Depends(get_current_user),
    request: Request = None,
):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info(
        "analyze_request",
        request_id=request_id,
        user=user,
        text_length=len(payload.text),
    )

    # Check cache first
    cached = cache.get(payload.text)
    if cached:
        logger.debug("cache_hit", request_id=request_id)
        return cached | {"model_version": MODEL_VERSION}

    cleaned = cleaner.clean(payload.text)

    # Model prediction
    try:
        vec = bundle.vectorizer.transform([cleaned])
        pred = bundle.model.predict(vec)[0]
        probs = bundle.model.predict_proba(vec)[0]
    except (NotFittedError, AttributeError) as e:
        logger.error("model_not_loaded", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded; please retry or contact support",
        )

    labels = ["positive", "negative", "neutral"]
    prob_map = {
        lab: round(float(p) * 100, 2)
        for lab, p in zip(bundle.model.classes_, probs)
    }
    # Ensure all sentiment keys exist
    for lab in labels:
        prob_map.setdefault(lab, 0.0)

    response = {
        "sentiment": pred,
        "probabilities": prob_map,
        "cleaned_text": cleaned,
        "model_version": MODEL_VERSION,
        "confidence": max(prob_map.values()),  # Optional: max probability as confidence
    }

    # Cache result
    cache.set(payload.text, response)

    logger.info(
        "analyze_success",
        request_id=request_id,
        sentiment=pred,
        confidence=max(prob_map.values()),
    )
    return response

# ----- Health & readiness endpoints -----
@app.get(
    "/health",
    tags=["misc"],
    summary="Service health status",
    description="Check if the service and its dependencies are healthy.",
)
async def health():
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "metrics": bundle.metadata,
    }

@app.get(
    "/readiness",
    tags=["misc"],
    summary="Service readiness",
    description="Check if the service is ready to serve requests (for CI/CD/k8s).",
)
async def readiness():
    # TODO: Add dependency checks (e.g., Redis, MongoDB)
    return JSONResponse({"status": "ready"})

@app.get(
    "/liveness",
    tags=["misc"],
    summary="Service liveness",
    description="Check if the service process is alive (for CI/CD/k8s).",
)
async def liveness():
    return JSONResponse({"status": "alive"})

# ----- Real-time (WebSocket) -----
connections: set[WebSocket] = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    request_id = str(uuid.uuid4())
    connections.add(websocket)
    logger.info("websocket_connected", request_id=request_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug("websocket_message", request_id=request_id, message=data)
            # Replace this with real-time sentiment, batch, or other features
            await websocket.send_text(f"pong: {data}")
    except WebSocketDisconnect:
        connections.remove(websocket)
        logger.info("websocket_disconnected", request_id=request_id)
