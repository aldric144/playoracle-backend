"""
Live Data Router - Real-time sports data endpoints
Provides /api/live/{sport}/upcoming, /api/live/{sport}/scores, /api/live/{sport}/standings
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.database import get_db
from app.services.sportsdata_client import LiveDataService
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/live", tags=["live-data"])
settings = get_settings()


def get_live_service() -> LiveDataService:
    """Get LiveDataService instance"""
    api_key = getattr(settings, 'sportsdata_api_key', None)
    return LiveDataService(api_key=api_key)


@router.get("/{sport}/upcoming")
async def get_upcoming_games(
    sport: str,
    service: LiveDataService = Depends(get_live_service)
):
    """
    Get upcoming games for any sport
    
    Supported sports: nfl, nba, mlb, nhl, soccer, golf, tennis, mma, boxing, 
                     college_football, volleyball, rugby, cricket
    """
    try:
        games = await service.get_upcoming_games(sport)
        
        return {
            "sport": sport,
            "count": len(games),
            "games": games,
            "data_source": "mock" if service.use_mock else "sportsdata_io",
            "cached": False
        }
    except Exception as e:
        logger.error(f"Error fetching upcoming games for {sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch upcoming games: {str(e)}")


@router.get("/{sport}/scores")
async def get_live_scores(
    sport: str,
    service: LiveDataService = Depends(get_live_service)
):
    """
    Get live scores for any sport
    
    Returns current and recent game scores with live status indicators
    """
    try:
        scores = await service.get_scores(sport)
        
        return {
            "sport": sport,
            "count": len(scores),
            "scores": scores,
            "data_source": "mock" if service.use_mock else "sportsdata_io",
            "cached": False
        }
    except Exception as e:
        logger.error(f"Error fetching scores for {sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scores: {str(e)}")


@router.get("/{sport}/standings")
async def get_standings(
    sport: str,
    service: LiveDataService = Depends(get_live_service)
):
    """
    Get standings for any sport
    
    Returns current season standings with win/loss records
    """
    try:
        standings = await service.get_standings(sport)
        
        return {
            "sport": sport,
            "count": len(standings),
            "standings": standings,
            "data_source": "mock" if service.use_mock else "sportsdata_io",
            "cached": False
        }
    except Exception as e:
        logger.error(f"Error fetching standings for {sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch standings: {str(e)}")


@router.get("/status")
async def get_live_data_status(
    service: LiveDataService = Depends(get_live_service)
):
    """
    Get status of live data service
    
    Returns information about API connectivity and data sources
    """
    return {
        "status": "operational",
        "data_source": "mock" if service.use_mock else "sportsdata_io",
        "api_key_configured": bool(service.api_key and service.api_key != "test"),
        "supported_sports": [
            "nfl", "nba", "mlb", "nhl", "soccer", "golf", "tennis", 
            "mma", "boxing", "college_football", "volleyball", "rugby", "cricket"
        ]
    }
