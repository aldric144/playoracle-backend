"""
Sports Intelligence API Router
Endpoints for hybrid sports data aggregation and sync
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.sports_intel import SportsIntelAggregator
from app.routers.auth import get_current_user
from app.database import User

router = APIRouter(prefix="/api/sports-intel", tags=["sports-intel"])

@router.post("/sync")
async def sync_sports_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger sports data sync
    Requires admin access
    """
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    aggregator = SportsIntelAggregator(db)
    
    async def run_sync():
        await aggregator.sync_sports_data()
    
    background_tasks.add_task(run_sync)
    
    return {
        "message": "Sports data sync initiated",
        "status": "running"
    }

@router.get("/schedule/{sport}")
async def get_sport_schedule(
    sport: str,
    use_cache: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get schedule for a specific sport
    Supports: nfl, nba, mlb, nhl, premier_league, formula1, ncaa_football
    """
    aggregator = SportsIntelAggregator(db)
    events = await aggregator.fetch_schedule(sport, use_cache=use_cache)
    
    return {
        "sport": sport,
        "events": events,
        "count": len(events),
        "cached": use_cache,
        "sources_used": events[0].get("sources_used", []) if events else [],
        "premium_data_available": events[0].get("premium_data_available", False) if events else False
    }

@router.get("/game/{game_id}")
async def get_game_details(
    game_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific game/event
    """
    from app.database import SportsEvent
    
    event = db.query(SportsEvent).filter(SportsEvent.id == game_id).first()
    
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {
        "id": event.id,
        "sport_type": event.sport_type,
        "league": event.league,
        "start_time": event.start_time.isoformat() if event.start_time else None,
        "home_team": event.home_team,
        "away_team": event.away_team,
        "dci_score": event.dci_score,
        "dci_class": event.dci_class,
        "analysis": event.analysis_text,
        "computed_at": event.computed_at.isoformat() if event.computed_at else None,
        "sources": event.source_ids,
        "merged_data": event.merged_payload
    }

@router.get("/status")
async def get_sync_status(
    db: Session = Depends(get_db)
):
    """
    Get status of sports data sync and cache
    """
    from app.database import SportsCache
    from datetime import datetime
    
    cache_entries = db.query(SportsCache).all()
    
    active_caches = []
    expired_caches = []
    
    now = datetime.utcnow()
    
    for cache in cache_entries:
        cache_info = {
            "key": cache.cache_key,
            "created_at": cache.created_at.isoformat() if cache.created_at else None,
            "expires_at": cache.expires_at.isoformat() if cache.expires_at else None,
            "expired": cache.expires_at < now if cache.expires_at else True
        }
        
        if cache.expires_at and cache.expires_at > now:
            active_caches.append(cache_info)
        else:
            expired_caches.append(cache_info)
    
    return {
        "active_caches": len(active_caches),
        "expired_caches": len(expired_caches),
        "cache_details": active_caches,
        "last_sync": active_caches[0]["created_at"] if active_caches else None
    }
