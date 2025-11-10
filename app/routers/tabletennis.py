"""
Table Tennis Router - Match schedules, results, and DCI analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.services.tabletennis_intel import TableTennisIntelligence
from app.services.thesportsdb_client import TheSportsDBClient
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tabletennis", tags=["tabletennis"])
settings = get_settings()


def get_tabletennis_service() -> TableTennisIntelligence:
    """Get TableTennisIntelligence instance"""
    return TableTennisIntelligence()


@router.get("/upcoming")
async def get_upcoming_matches(
    scope: str = Query("live", description="Data scope: 'live' or 'all'"),
    limit: int = Query(50, ge=1, le=100),
    service: TableTennisIntelligence = Depends(get_tabletennis_service)
):
    """
    Get upcoming table tennis matches
    
    - **scope**: 'live' for live+upcoming only, 'all' for historical+upcoming
    - **limit**: Maximum number of matches to return
    """
    try:
        if settings.thesportsdb_api_key:
            try:
                async with TheSportsDBClient(settings.thesportsdb_api_key) as client:
                    events = await client.get_table_tennis_events()
                    
                    if events:
                        matches = []
                        for event in events[:limit]:
                            match = {
                                "id": event.get("idEvent"),
                                "tournament": event.get("strLeague", "Unknown Tournament"),
                                "player1": {
                                    "name": event.get("strHomeTeam", "Player 1"),
                                    "dci": service.calculate_dci({
                                        "aces_per_game": 7.0,
                                        "errors_per_game": 2.5,
                                        "rally_efficiency": 0.75,
                                        "set_win_percentage": 0.70,
                                        "reflex_score": 0.80,
                                        "momentum": 0.75
                                    })
                                },
                                "player2": {
                                    "name": event.get("strAwayTeam", "Player 2"),
                                    "dci": service.calculate_dci({
                                        "aces_per_game": 6.5,
                                        "errors_per_game": 3.0,
                                        "rally_efficiency": 0.72,
                                        "set_win_percentage": 0.68,
                                        "reflex_score": 0.78,
                                        "momentum": 0.72
                                    })
                                },
                                "start_time": event.get("dateEvent"),
                                "venue": event.get("strVenue", "TBD"),
                                "status": event.get("strStatus", "Scheduled")
                            }
                            matches.append(match)
                        
                        return {
                            "sport": "tabletennis",
                            "scope": scope,
                            "count": len(matches),
                            "matches": matches,
                            "data_source": "thesportsdb"
                        }
            except Exception as e:
                logger.error(f"Failed to fetch live table tennis data: {e}")
        
        matches = service.get_mock_matches()
        
        return {
            "sport": "tabletennis",
            "scope": scope,
            "count": len(matches[:limit]),
            "matches": matches[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching table tennis matches: {e}")
        return {
            "sport": "tabletennis",
            "scope": scope,
            "count": 0,
            "matches": [],
            "error": str(e)
        }


@router.get("/match/{match_id}")
async def get_match_details(
    match_id: str,
    service: TableTennisIntelligence = Depends(get_tabletennis_service)
):
    """Get detailed information for a specific match"""
    try:
        if settings.thesportsdb_api_key:
            try:
                async with TheSportsDBClient(settings.thesportsdb_api_key) as client:
                    event = await client.get_event_details(match_id)
                    
                    if event:
                        match = {
                            "id": event.get("idEvent"),
                            "tournament": event.get("strLeague"),
                            "player1": {
                                "name": event.get("strHomeTeam"),
                                "score": event.get("intHomeScore"),
                                "dci": service.calculate_dci({
                                    "aces_per_game": 7.0,
                                    "errors_per_game": 2.5,
                                    "rally_efficiency": 0.75,
                                    "set_win_percentage": 0.70,
                                    "reflex_score": 0.80,
                                    "momentum": 0.75
                                })
                            },
                            "player2": {
                                "name": event.get("strAwayTeam"),
                                "score": event.get("intAwayScore"),
                                "dci": service.calculate_dci({
                                    "aces_per_game": 6.5,
                                    "errors_per_game": 3.0,
                                    "rally_efficiency": 0.72,
                                    "set_win_percentage": 0.68,
                                    "reflex_score": 0.78,
                                    "momentum": 0.72
                                })
                            },
                            "status": event.get("strStatus"),
                            "venue": event.get("strVenue"),
                            "date": event.get("dateEvent")
                        }
                        
                        return {
                            "match_id": match_id,
                            "match": match,
                            "data_source": "thesportsdb"
                        }
            except Exception as e:
                logger.error(f"Failed to fetch match details: {e}")
        
        matches = service.get_mock_matches()
        match = matches[0] if matches else {}
        
        return {
            "match_id": match_id,
            "match": match,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching match details: {e}")
        return {
            "match_id": match_id,
            "error": str(e)
        }


@router.get("/history")
async def get_match_history(
    limit: int = Query(20, ge=1, le=100),
    service: TableTennisIntelligence = Depends(get_tabletennis_service)
):
    """Get historical match results"""
    try:
        if settings.thesportsdb_api_key:
            try:
                async with TheSportsDBClient(settings.thesportsdb_api_key) as client:
                    results = await client.get_table_tennis_results()
                    
                    if results:
                        return {
                            "sport": "tabletennis",
                            "count": len(results[:limit]),
                            "history": results[:limit],
                            "data_source": "thesportsdb"
                        }
            except Exception as e:
                logger.error(f"Failed to fetch table tennis history: {e}")
        
        history = service.get_mock_history()
        
        return {
            "sport": "tabletennis",
            "count": len(history[:limit]),
            "history": history[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching table tennis history: {e}")
        return {
            "sport": "tabletennis",
            "count": 0,
            "history": [],
            "error": str(e)
        }


@router.get("/dci/{player_name}")
async def get_player_dci(
    player_name: str,
    service: TableTennisIntelligence = Depends(get_tabletennis_service)
):
    """Get DCI score for a specific player"""
    try:
        dci = service.calculate_dci({
            "aces_per_game": 7.0,
            "errors_per_game": 2.5,
            "rally_efficiency": 0.75,
            "set_win_percentage": 0.70,
            "reflex_score": 0.80,
            "momentum": 0.75
        })
        
        return {
            "player": player_name,
            "sport": "tabletennis",
            "dci": dci,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error calculating player DCI: {e}")
        return {
            "player": player_name,
            "error": str(e)
        }
