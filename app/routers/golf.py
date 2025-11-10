"""
Golf Router - Tournament schedules, leaderboards, and DCI analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.services.golf_intel import GolfIntelligence
from app.services.sportsdata_client import SportsDataIOClient
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/golf", tags=["golf"])
settings = get_settings()


def get_golf_service() -> GolfIntelligence:
    """Get GolfIntelligence instance"""
    return GolfIntelligence()


@router.get("/upcoming")
async def get_upcoming_tournaments(
    scope: str = Query("live", description="Data scope: 'live' or 'all'"),
    limit: int = Query(50, ge=1, le=100),
    service: GolfIntelligence = Depends(get_golf_service)
):
    """
    Get upcoming golf tournaments
    
    - **scope**: 'live' for live+upcoming only, 'all' for historical+upcoming
    - **limit**: Maximum number of tournaments to return
    """
    try:
        if settings.sportsdata_api_key and settings.sportsdata_api_key != "test":
            try:
                async with SportsDataIOClient(settings.sportsdata_api_key) as client:
                    tournaments = await client.get_golf_tournaments()
                    
                    if tournaments:
                        for tournament in tournaments[:limit]:
                            if "Players" in tournament:
                                for player in tournament["Players"][:5]:  # Top 5 players
                                    player["dci"] = service.calculate_dci({
                                        "driving_accuracy": 0.70,
                                        "strokes_gained": 1.5,
                                        "birdie_conversion": 0.25,
                                        "sand_saves": 0.60,
                                        "consistency": 0.75,
                                        "stamina": 0.80,
                                        "weather_impact": 0.75,
                                        "recent_form": 0.75
                                    })
                        
                        return {
                            "sport": "golf",
                            "scope": scope,
                            "count": len(tournaments[:limit]),
                            "tournaments": tournaments[:limit],
                            "data_source": "sportsdata_io"
                        }
            except Exception as e:
                logger.error(f"Failed to fetch live golf data: {e}")
        
        tournaments = service.get_mock_tournaments()
        
        return {
            "sport": "golf",
            "scope": scope,
            "count": len(tournaments[:limit]),
            "tournaments": tournaments[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching golf tournaments: {e}")
        return {
            "sport": "golf",
            "scope": scope,
            "count": 0,
            "tournaments": [],
            "error": str(e)
        }


@router.get("/leaderboard/{tournament_id}")
async def get_tournament_leaderboard(
    tournament_id: str,
    service: GolfIntelligence = Depends(get_golf_service)
):
    """Get live leaderboard for a specific tournament"""
    try:
        if settings.sportsdata_api_key and settings.sportsdata_api_key != "test":
            try:
                async with SportsDataIOClient(settings.sportsdata_api_key) as client:
                    leaderboard = await client.get_golf_leaderboard(int(tournament_id))
                    
                    if leaderboard and "Players" in leaderboard:
                        for player in leaderboard["Players"]:
                            player["dci"] = service.calculate_dci({
                                "driving_accuracy": 0.70,
                                "strokes_gained": 1.5,
                                "birdie_conversion": 0.25,
                                "sand_saves": 0.60,
                                "consistency": 0.75,
                                "stamina": 0.80,
                                "weather_impact": 0.75,
                                "recent_form": 0.75
                            })
                        
                        return {
                            "tournament_id": tournament_id,
                            "leaderboard": leaderboard,
                            "data_source": "sportsdata_io"
                        }
            except Exception as e:
                logger.error(f"Failed to fetch live leaderboard: {e}")
        
        leaderboard = service.get_mock_leaderboard(tournament_id)
        
        return {
            "tournament_id": tournament_id,
            "leaderboard": leaderboard,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return {
            "tournament_id": tournament_id,
            "error": str(e)
        }


@router.get("/history")
async def get_tournament_history(
    limit: int = Query(20, ge=1, le=100),
    service: GolfIntelligence = Depends(get_golf_service)
):
    """Get historical tournament results"""
    try:
        tournaments = service.get_mock_tournaments()
        
        return {
            "sport": "golf",
            "count": len(tournaments[:limit]),
            "history": tournaments[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching golf history: {e}")
        return {
            "sport": "golf",
            "count": 0,
            "history": [],
            "error": str(e)
        }


@router.get("/dci/{player_name}")
async def get_player_dci(
    player_name: str,
    service: GolfIntelligence = Depends(get_golf_service)
):
    """Get DCI score for a specific player"""
    try:
        dci = service.calculate_dci({
            "driving_accuracy": 0.70,
            "strokes_gained": 1.5,
            "birdie_conversion": 0.25,
            "sand_saves": 0.60,
            "consistency": 0.75,
            "stamina": 0.80,
            "weather_impact": 0.75,
            "recent_form": 0.75
        })
        
        return {
            "player": player_name,
            "sport": "golf",
            "dci": dci,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error calculating player DCI: {e}")
        return {
            "player": player_name,
            "error": str(e)
        }
