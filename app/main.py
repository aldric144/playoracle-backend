from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, predictions, sports, subscriptions, user, leaderboard, analytics, events, admin_events
from app.database import init_db

app = FastAPI(
    title="PlayOracle API",
    description="AI-powered sports analytics and learning platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sports-iq-app-qy6on1ii.devinapps.com"
    ],
    allow_credentials=False,  # We use Bearer tokens, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(events.router)
app.include_router(admin_events.router)

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
