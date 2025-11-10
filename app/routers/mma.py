"""
MMA/UFC Intelligence API Router
Endpoints for MMA events, fighters, and DCI scoring
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.services.mma_intel import MMADCIService, get_mock_mma_events
from app.routers.auth import get_current_user
from app.database import User

router = APIRouter(prefix="/api/mma", tags=["mma"])

@router.get("/upcoming")
async def get_upcoming_mma_events(
    db: Session = Depends(get_db)
):
    """Get upcoming MMA/UFC events"""
    events = get_mock_mma_events()
    
    for event in events:
        fighter_one = event.get("fighter_one", {})
        fighter_two = event.get("fighter_two", {})
        
        f1_dci, f2_dci = MMADCIService.compute_dci(fighter_one, fighter_two)
        
        event["dci_preview"] = {
            "fighter_one_score": f1_dci["dci_score"],
            "fighter_two_score": f2_dci["dci_score"],
            "classification": f1_dci["classification"]
        }
    
    return {
        "events": events,
        "count": len(events),
        "sources_used": ["mock_data"],
        "premium_data_available": False
    }

@router.get("/fight/{fight_id}")
async def get_fight_details(
    fight_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific MMA fight"""
    events = get_mock_mma_events()
    
    fight = next((e for e in events if e["id"] == fight_id), None)
    
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    return fight

@router.get("/dci/{fight_id}")
async def get_mma_dci(
    fight_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DCI (Dynamic Confidence Index) for an MMA fight
    Requires authentication
    """
    events = get_mock_mma_events()
    fight = next((e for e in events if e["id"] == fight_id), None)
    
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    fighter_one = fight.get("fighter_one", {})
    fighter_two = fight.get("fighter_two", {})
    
    f1_dci, f2_dci = MMADCIService.compute_dci(fighter_one, fighter_two)
    
    is_premium = current_user.subscription_tier in ["pro", "oracle_plus"]
    
    if not is_premium:
        return {
            "fight_id": fight_id,
            "dci_preview": {
                "fighter_one_score": f1_dci["dci_score"],
                "fighter_two_score": f2_dci["dci_score"],
                "classification": f1_dci["classification"]
            },
            "premium_required": True,
            "message": "Upgrade to Pro or Oracle Elite for full DCI analysis"
        }
    
    return {
        "fight_id": fight_id,
        "event_name": fight.get("event_name"),
        "weight_class": fight.get("weight_class"),
        "fighter_one": {
            "name": fighter_one.get("name"),
            "record": fighter_one.get("record"),
            "dci": f1_dci
        },
        "fighter_two": {
            "name": fighter_two.get("name"),
            "record": fighter_two.get("record"),
            "dci": f2_dci
        },
        "prediction": f1_dci["classification"] if f1_dci["dci_score"] > f2_dci["dci_score"] else f2_dci["classification"],
        "confidence": max(f1_dci["dci_score"], f2_dci["dci_score"])
    }

@router.get("/fighter/{fighter_id}")
async def get_fighter_details(
    fighter_id: str,
    db: Session = Depends(get_db)
):
    """Get fighter details by ID"""
    events = get_mock_mma_events()
    
    for event in events:
        if event.get("fighter_one", {}).get("id") == fighter_id:
            return {
                "fighter": event["fighter_one"],
                "upcoming_fight": {
                    "event_name": event["event_name"],
                    "opponent": event["fighter_two"]["name"],
                    "date": event["date"]
                }
            }
        if event.get("fighter_two", {}).get("id") == fighter_id:
            return {
                "fighter": event["fighter_two"],
                "upcoming_fight": {
                    "event_name": event["event_name"],
                    "opponent": event["fighter_one"]["name"],
                    "date": event["date"]
                }
            }
    
    raise HTTPException(status_code=404, detail="Fighter not found")
