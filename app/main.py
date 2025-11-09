from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, predictions, sports, subscriptions, user, leaderboard, analytics
from app.database import init_db

app = FastAPI(
    title="PlayOracle API",
    description="AI-powered sports analytics and learning platform",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    init_db()

app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(sports.router)
app.include_router(subscriptions.router)
app.include_router(user.router)
app.include_router(leaderboard.router)
app.include_router(analytics.router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to PlayOracle API",
        "version": "1.0.0",
        "docs": "/docs",
        "disclaimer": "PlayOracle is an analytical and learning tool, not a gambling platform. Predictions are educational insights based on public data."
    }
