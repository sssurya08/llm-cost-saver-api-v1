from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Database setup ---
DATABASE_URL = "sqlite:///./requests.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class RequestLog(Base):
    __tablename__ = "requests"

    id               = Column(Integer, primary_key=True, index=True)
    api_key          = Column(String)
    model_used       = Column(String)
    tokens           = Column(Integer)
    estimated_cost   = Column(Float)
    estimated_savings = Column(Float)
    timestamp        = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

# --- App setup ---
app = FastAPI()

VALID_KEYS = ["testkey123"]

PRICING = {
    "cheap-model": 0.001,
    "expensive-model": 0.01,
}


class ChatRequest(BaseModel):
    prompt: str
    mode: str


class ChatResponse(BaseModel):
    response: str
    model_used: str
    tokens: int
    estimated_cost: float
    estimated_savings: float


# --- Logic functions ---
def choose_model(prompt: str, mode: str) -> str:
    if mode == "cheap" and len(prompt) < 200:
        return "cheap-model"
    return "expensive-model"


def call_model(model_name: str, prompt: str) -> str:
    return f"fake response from {model_name}"


def calculate_cost(model_name: str, prompt: str) -> tuple[float, float, int]:
    tokens = len(prompt.split())
    rate = PRICING[model_name]
    estimated_cost = (tokens / 1000) * rate
    cost_if_expensive = (tokens / 1000) * 0.01
    estimated_savings = cost_if_expensive - estimated_cost
    return estimated_cost, estimated_savings, tokens


# --- Routes ---
@app.get("/")
async def root():
    return {"message": "Chat API is running. POST to /chat to use it."}


@app.get("/chat/demo")
async def chat_demo():
    model = choose_model("Hello world this is a test", "cheap")
    estimated_cost, estimated_savings, tokens = calculate_cost(model, "Hello world this is a test")
    return ChatResponse(
        response=call_model(model, "Hello world this is a test"),
        model_used=model,
        tokens=tokens,
        estimated_cost=estimated_cost,
        estimated_savings=estimated_savings,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": "Unauthorized"})

    api_key = authorization.removeprefix("Bearer ")

    if api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail={"error": "Unauthorized"})

    model = choose_model(request.prompt, request.mode)
    estimated_cost, estimated_savings, tokens = calculate_cost(model, request.prompt)

    # Log to database
    db = SessionLocal()
    try:
        log = RequestLog(
            api_key=api_key,
            model_used=model,
            tokens=tokens,
            estimated_cost=estimated_cost,
            estimated_savings=estimated_savings,
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

    return ChatResponse(
        response=call_model(model, request.prompt),
        model_used=model,
        tokens=tokens,
        estimated_cost=estimated_cost,
        estimated_savings=estimated_savings,
    )
    
@app.get("/logs")
async def get_logs():
    db = SessionLocal()
    try:
        logs = db.query(RequestLog).all()
        return [
            {
                "id": log.id,
                "api_key": log.api_key,
                "model_used": log.model_used,
                "tokens": log.tokens,
                "estimated_cost": log.estimated_cost,
                "estimated_savings": log.estimated_savings,
                "timestamp": log.timestamp,
            }
            for log in logs
        ]
    finally:
        db.close()

