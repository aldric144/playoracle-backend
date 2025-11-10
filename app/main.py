from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.routers import auth, predictions, sports, subscriptions, user, leaderboard, analytics, events, admin_events, rivalry, boxing, sports_intel
from app.database import init_db, SessionLocal
from app.services.sports_intel import SportsIntelAggregator

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

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

async def scheduled_sports_sync():
    """Background job to sync sports data daily"""
    logger.info("Starting scheduled sports data sync...")
    db = SessionLocal()
    try:
        aggregator = SportsIntelAggregator(db)
        results = await aggregator.sync_sports_data()
        logger.info(f"Sports sync completed: {results}")
    except Exception as e:
        logger.error(f"Sports sync failed: {e}")
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    init_db()
    
    scheduler.add_job(
        scheduled_sports_sync,
        CronTrigger(hour=4, minute=15),  # Run daily at 04:15 UTC
        id="sports_sync",
        name="Daily Sports Data Sync",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started for sports data sync")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(sports.router)
app.include_router(subscriptions.router)
app.include_router(user.router)
app.include_router(leaderboard.router)
app.include_router(analytics.router)
app.include_router(events.router)
app.include_router(admin_events.router)
app.include_router(rivalry.router)
app.include_router(boxing.router)
app.include_router(sports_intel.router)

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
