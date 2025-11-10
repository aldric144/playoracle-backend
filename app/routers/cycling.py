"""
Cycling Router - Race schedules, standings, and DCI analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.services.cycling_intel import CyclingIntelligence
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cycling", tags=["cycling"])
settings = get_settings()


def get_cycling_service() -> CyclingIntelligence:
    """Get CyclingIntelligence instance"""
    return CyclingIntelligence()


@router.get("/upcoming")
async def get_upcoming_races(
    scope: str = Query("live", description="Data scope: 'live' or 'all'"),
    limit: int = Query(50, ge=1, le=100),
    service: CyclingIntelligence = Depends(get_cycling_service)
):
    """
    Get upcoming cycling races
    
    - **scope**: 'live' for live+upcoming only, 'all' for historical+upcoming
    - **limit**: Maximum number of races to return
    """
    try:
        races = service.get_mock_races()
        
        return {
            "sport": "cycling",
            "scope": scope,
            "count": len(races[:limit]),
            "races": races[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching cycling races: {e}")
        return {
            "sport": "cycling",
            "scope": scope,
            "count": 0,
            "races": [],
            "error": str(e)
        }


@router.get("/standings")
async def get_rider_standings(
    service: CyclingIntelligence = Depends(get_cycling_service)
):
    """Get current cycling general classification standings"""
    try:
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
    service: CyclingIntelligence = Depends(get_cycling_service)
):
    """Get historical race results"""
    try:
        races = service.get_mock_races()
        
        return {
            "sport": "cycling",
            "count": len(races[:limit]),
            "history": races[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching cycling history: {e}")
        return {
            "sport": "cycling",
            "count": 0,
            "history": [],
            "error": str(e)
        }


@router.get("/dci/{rider_name}")
async def get_rider_dci(
    rider_name: str,
    service: CyclingIntelligence = Depends(get_cycling_service)
):
    """Get DCI score for a specific rider"""
    try:
        dci = service.calculate_dci({
            "climb_percentage": 0.75,
            "time_gap": 0.80,
            "heart_rate_stability": 0.70,
            "cadence": 0.75,
            "endurance": 0.85,
            "descent_control": 0.70,
            "team_pacing": 0.80,
            "terrain_adaptation": 0.75
        })
        
        return {
            "rider": rider_name,
            "sport": "cycling",
            "dci": dci,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error calculating rider DCI: {e}")
        return {
            "rider": rider_name,
            "error": str(e)
        }
