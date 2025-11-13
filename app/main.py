from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.routers import auth, predictions, sports, subscriptions, user, leaderboard, analytics, events, admin_events, rivalry, boxing, sports_intel, mma, tennis, hockey, volleyball, rugby, cricket, live_data, golf, tabletennis, nascar, motogp, cycling, history, ai_analytics
from app.database import init_db, SessionLocal
from app.services.sports_intel import SportsIntelAggregator
from app.services.sportsdata_client import LiveDataService
from app.config import get_settings

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
        "https://sports-iq-app-qy6on1ii.devinapps.com",
        "https://playoracle-frontend-1.onrender.com"
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

async def scheduled_live_data_sync():
    """Background job to sync live sports data every 15 minutes"""
    logger.info("Starting scheduled live data sync...")
    settings = get_settings()
    
    try:
        service = LiveDataService(api_key=settings.sportsdata_api_key)
        
        sports = ["nfl", "nba", "mlb", "nhl", "soccer", "golf", "tennis", 
                 "mma", "boxing", "college_football"]
        
        results = {}
        for sport in sports:
            try:
                games = await service.get_upcoming_games(sport)
                results[sport] = {
                    "count": len(games),
                    "status": "success"
                }
                logger.info(f"Synced {len(games)} games for {sport}")
            except Exception as e:
                results[sport] = {
                    "count": 0,
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"Failed to sync {sport}: {e}")
        
        logger.info(f"Live data sync completed: {results}")
    except Exception as e:
        logger.error(f"Live data sync failed: {e}")

@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Daily sports data sync at 04:15 UTC
    scheduler.add_job(
        scheduled_sports_sync,
        CronTrigger(hour=4, minute=15),
        id="sports_sync",
        name="Daily Sports Data Sync",
        replace_existing=True
    )
    
    scheduler.add_job(
        scheduled_live_data_sync,
        'interval',
        minutes=15,
        id="live_data_sync",
        name="Live Sports Data Sync (15 min)",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background scheduler started for sports data sync and live data sync")

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
app.include_router(mma.router)
app.include_router(tennis.router)
app.include_router(hockey.router)
app.include_router(volleyball.router)
app.include_router(rugby.router)
app.include_router(cricket.router)
app.include_router(sports_intel.router)
app.include_router(live_data.router)
app.include_router(golf.router)
app.include_router(tabletennis.router)
app.include_router(nascar.router)
app.include_router(motogp.router)
app.include_router(cycling.router)
app.include_router(history.router)
app.include_router(ai_analytics.router)

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
