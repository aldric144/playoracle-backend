"""
MotoGP Router - Race schedules, standings, and DCI analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.services.motogp_intel import MotoGPIntelligence
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/motogp", tags=["motogp"])
settings = get_settings()


def get_motogp_service() -> MotoGPIntelligence:
    """Get MotoGPIntelligence instance"""
    return MotoGPIntelligence()


@router.get("/upcoming")
async def get_upcoming_races(
    scope: str = Query("live", description="Data scope: 'live' or 'all'"),
    limit: int = Query(50, ge=1, le=100),
    service: MotoGPIntelligence = Depends(get_motogp_service)
):
    """
    Get upcoming MotoGP races
    
    - **scope**: 'live' for live+upcoming only, 'all' for historical+upcoming
    - **limit**: Maximum number of races to return
    """
    try:
        races = service.get_mock_races()
        
        return {
            "sport": "motogp",
            "scope": scope,
            "count": len(races[:limit]),
            "races": races[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching MotoGP races: {e}")
        return {
            "sport": "motogp",
            "scope": scope,
            "count": 0,
            "races": [],
            "error": str(e)
        }


@router.get("/standings")
async def get_rider_standings(
    service: MotoGPIntelligence = Depends(get_motogp_service)
):
    """Get current MotoGP rider standings"""
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
    service: MotoGPIntelligence = Depends(get_motogp_service)
):
    """Get historical race results"""
    try:
        races = service.get_mock_races()
        
        return {
            "sport": "motogp",
            "count": len(races[:limit]),
            "history": races[:limit],
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error fetching MotoGP history: {e}")
        return {
            "sport": "motogp",
            "count": 0,
            "history": [],
            "error": str(e)
        }


@router.get("/dci/{rider_name}")
async def get_rider_dci(
    rider_name: str,
    service: MotoGPIntelligence = Depends(get_motogp_service)
):
    """Get DCI score for a specific rider"""
    try:
        dci = service.calculate_dci({
            "lap_time_delta": 0.80,
            "top_speed": 0.85,
            "braking_efficiency": 0.75,
            "rider_form": 0.80,
            "track_adaptation": 0.70,
            "tire_management": 0.75,
            "experience": 0.85,
            "reaction_time": 0.80
        })
        
        return {
            "rider": rider_name,
            "sport": "motogp",
            "dci": dci,
            "data_source": "mock"
        }
        
    except Exception as e:
        logger.error(f"Error calculating rider DCI: {e}")
        return {
            "rider": rider_name,
            "error": str(e)
        }
