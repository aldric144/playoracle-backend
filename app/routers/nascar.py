"""
NASCAR Router - Race schedules, standings, and DCI analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.services.nascar_intel import NASCARIntelligence
from app.services.sportsdata_client import SportsDataIOClient
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nascar", tags=["nascar"])
settings = get_settings()


def get_nascar_service() -> NASCARIntelligence:
    """Get NASCARIntelligence instance"""
    return NASCARIntelligence()


@router.get("/upcoming")
async def get_upcoming_races(
    scope: str = Query("live", description="Data scope: 'live' or 'all'"),
    limit: int = Query(50, ge=1, le=100),
    service: NASCARIntelligence = Depends(get_nascar_service)
):
    """
    Get upcoming NASCAR races
    
    - **scope**: 'live' for live+upcoming only, 'all' for historical+upcoming
    - **limit**: Maximum number of races to return
    """
    try:
        if settings.sportsdata_api_key and settings.sportsdata_api_key != "test":
            try:
                async with SportsDataIOClient(settings.sportsdata_api_key) as client:
                    races = await client.get_nascar_races()
                    
                    if races:
                        for race in races[:limit]:
                            if "Drivers" in race:
                                for driver in race["Drivers"][:5]:  # Top 5 drivers
                                    driver["dci"] = service.calculate_dci({
                                        "laps_completed": 0.85,
                                        "pit_stops": 0.75,
                                        "average_speed": 0.80,
                                        "consistency": 0.70,
                                        "overtakes": 0.65,
                                        "tire_wear": 0.75,
                                        "team_coordination": 0.80,
                                        "weather_impact": 0.70
                                    })
                        
                        return {
                            "sport": "nascar",
                            "scope": scope,
                            "count": len(races[:limit]),
                            "races": races[:limit],
                            "data_source": "sportsdata_io"
                        }
            except Exception as e:
                logger.error(f"Failed to fetch live NASCAR data: {e}")
        
        races = service.get_mock_races()
        
        return {
            "sport": "nascar",
            "scope": scope,
            "count": len(races[:limit]),
            "races": races[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching NASCAR races: {e}")
        return {
            "sport": "nascar",
            "scope": scope,
            "count": 0,
            "races": [],
            "error": str(e)
        }


@router.get("/standings")
async def get_driver_standings(
    service: NASCARIntelligence = Depends(get_nascar_service)
):
    """Get current NASCAR driver standings"""
    try:
        if settings.sportsdata_api_key and settings.sportsdata_api_key != "test":
            try:
                async with SportsDataIOClient(settings.sportsdata_api_key) as client:
                    standings = await client.get_nascar_standings()
                    
                    if standings and "Drivers" in standings:
                        for driver in standings["Drivers"]:
                            driver["dci"] = service.calculate_dci({
                                "laps_completed": 0.85,
                                "pit_stops": 0.75,
                                "average_speed": 0.80,
                                "consistency": 0.70,
                                "overtakes": 0.65,
                                "tire_wear": 0.75,
                                "team_coordination": 0.80,
                                "weather_impact": 0.70
                            })
                        
                        return {
                            "standings": standings,
                            "data_source": "sportsdata_io"
                        }
            except Exception as e:
                logger.error(f"Failed to fetch live standings: {e}")
        
        standings = service.get_mock_standings()
        
        return {
            "standings": standings,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching standings: {e}")
        return {
            "error": str(e)
        }


@router.get("/history")
async def get_race_history(
    limit: int = Query(20, ge=1, le=100),
    service: NASCARIntelligence = Depends(get_nascar_service)
):
    """Get historical race results"""
    try:
        races = service.get_mock_races()
        
        return {
            "sport": "nascar",
            "count": len(races[:limit]),
            "history": races[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching NASCAR history: {e}")
        return {
            "sport": "nascar",
            "count": 0,
            "history": [],
            "error": str(e)
        }


@router.get("/dci/{driver_name}")
async def get_driver_dci(
    driver_name: str,
    service: NASCARIntelligence = Depends(get_nascar_service)
):
    """Get DCI score for a specific driver"""
    try:
        dci = service.calculate_dci({
            "laps_completed": 0.85,
            "pit_stops": 0.75,
            "average_speed": 0.80,
            "consistency": 0.70,
            "overtakes": 0.65,
            "tire_wear": 0.75,
            "team_coordination": 0.80,
            "weather_impact": 0.70
        })
        
        return {
            "driver": driver_name,
            "sport": "nascar",
            "dci": dci,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error calculating driver DCI: {e}")
        return {
            "driver": driver_name,
            "error": str(e)
        }
