"""
Rugby Intelligence API Router
Endpoints for rugby events, teams, and DCI scoring
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.services.rugby_intel import RugbyDCIService, get_mock_rugby_events
from app.routers.auth import get_current_user
from app.database import User

router = APIRouter(prefix="/api/rugby", tags=["rugby"])

@router.get("/upcoming")
async def get_upcoming_rugby_events(
    db: Session = Depends(get_db)
):
    """Get upcoming rugby events"""
    events = get_mock_rugby_events()
    
    for event in events:
        team_one = event.get("team_one", {})
        team_two = event.get("team_two", {})
        
        t1_dci, t2_dci = RugbyDCIService.compute_dci(team_one, team_two)
        
        event["dci_preview"] = {
            "team_one_score": t1_dci["dci_score"],
            "team_two_score": t2_dci["dci_score"],
            "classification": t1_dci["classification"]
        }
    
    return {
        "events": events,
        "count": len(events),
        "sources_used": ["mock_data"],
        "premium_data_available": False
    }

@router.get("/match/{match_id}")
async def get_match_details(
    match_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific rugby match"""
    events = get_mock_rugby_events()
    
    match = next((e for e in events if e["id"] == match_id), None)
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match

@router.get("/dci/{match_id}")
async def get_rugby_dci(
    match_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DCI (Dynamic Confidence Index) for a rugby match
    Requires authentication
    """
    events = get_mock_rugby_events()
    match = next((e for e in events if e["id"] == match_id), None)
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    team_one = match.get("team_one", {})
    team_two = match.get("team_two", {})
    
    t1_dci, t2_dci = RugbyDCIService.compute_dci(team_one, team_two)
    
    is_premium = current_user.subscription_tier in ["pro", "oracle_plus"]
    
    if not is_premium:
        return {
            "match_id": match_id,
            "dci_preview": {
                "team_one_score": t1_dci["dci_score"],
                "team_two_score": t2_dci["dci_score"],
                "classification": t1_dci["classification"]
            },
            "premium_required": True,
            "message": "Upgrade to Pro or Oracle Elite for full DCI analysis"
        }
    
    return {
        "match_id": match_id,
        "event_name": match.get("event_name"),
        "league": match.get("league"),
        "team_one": {
            "name": team_one.get("name"),
            "country": team_one.get("country"),
            "dci": t1_dci
        },
        "team_two": {
            "name": team_two.get("name"),
            "country": team_two.get("country"),
            "dci": t2_dci
        },
        "prediction": t1_dci["classification"] if t1_dci["dci_score"] > t2_dci["dci_score"] else t2_dci["classification"],
        "confidence": max(t1_dci["dci_score"], t2_dci["dci_score"])
    }

@router.get("/team/{team_id}")
async def get_team_details(
    team_id: str,
    db: Session = Depends(get_db)
):
    """Get team details by ID"""
    events = get_mock_rugby_events()
    
    for event in events:
        if event.get("team_one", {}).get("id") == team_id:
            return {
                "team": event["team_one"],
                "upcoming_match": {
                    "event_name": event["event_name"],
                    "opponent": event["team_two"]["name"],
                    "date": event["date"]
                }
            }
        if event.get("team_two", {}).get("id") == team_id:
            return {
                "team": event["team_two"],
                "upcoming_match": {
                    "event_name": event["event_name"],
                    "opponent": event["team_one"]["name"],
                    "date": event["date"]
                }
            }
    
    raise HTTPException(status_code=404, detail="Team not found")
