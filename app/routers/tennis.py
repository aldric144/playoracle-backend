"""
Tennis Intelligence API Router
Endpoints for tennis matches, players, and DCI scoring
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.services.tennis_intel import TennisDCIService, get_mock_tennis_events
from app.routers.auth import get_current_user
from app.database import User

router = APIRouter(prefix="/api/tennis", tags=["tennis"])

@router.get("/upcoming")
async def get_upcoming_tennis_matches(
    db: Session = Depends(get_db)
):
    """Get upcoming tennis matches"""
    events = get_mock_tennis_events()
    
    for event in events:
        player_one = event.get("player_one", {})
        player_two = event.get("player_two", {})
        surface = event.get("surface", "hard")
        
        p1_dci, p2_dci = TennisDCIService.compute_dci(player_one, player_two, surface)
        
        event["dci_preview"] = {
            "player_one_score": p1_dci["dci_score"],
            "player_two_score": p2_dci["dci_score"],
            "classification": p1_dci["classification"]
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
    """Get detailed information for a specific tennis match"""
    events = get_mock_tennis_events()
    
    match = next((e for e in events if e["id"] == match_id), None)
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match

@router.get("/dci/{match_id}")
async def get_tennis_dci(
    match_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DCI (Dynamic Confidence Index) for a tennis match
    Requires authentication
    """
    events = get_mock_tennis_events()
    match = next((e for e in events if e["id"] == match_id), None)
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    player_one = match.get("player_one", {})
    player_two = match.get("player_two", {})
    surface = match.get("surface", "hard")
    
    p1_dci, p2_dci = TennisDCIService.compute_dci(player_one, player_two, surface)
    
    is_premium = current_user.subscription_tier in ["pro", "oracle_plus"]
    
    if not is_premium:
        return {
            "match_id": match_id,
            "dci_preview": {
                "player_one_score": p1_dci["dci_score"],
                "player_two_score": p2_dci["dci_score"],
                "classification": p1_dci["classification"]
            },
            "premium_required": True,
            "message": "Upgrade to Pro or Oracle Elite for full DCI analysis"
        }
    
    return {
        "match_id": match_id,
        "tournament": match.get("tournament"),
        "round": match.get("round"),
        "surface": surface,
        "player_one": {
            "name": player_one.get("name"),
            "ranking": player_one.get("ranking"),
            "dci": p1_dci
        },
        "player_two": {
            "name": player_two.get("name"),
            "ranking": player_two.get("ranking"),
            "dci": p2_dci
        },
        "prediction": p1_dci["classification"] if p1_dci["dci_score"] > p2_dci["dci_score"] else p2_dci["classification"],
        "confidence": max(p1_dci["dci_score"], p2_dci["dci_score"])
    }

@router.get("/player/{player_id}")
async def get_player_details(
    player_id: str,
    db: Session = Depends(get_db)
):
    """Get player details by ID"""
    events = get_mock_tennis_events()
    
    for event in events:
        if event.get("player_one", {}).get("id") == player_id:
            return {
                "player": event["player_one"],
                "upcoming_match": {
                    "tournament": event["tournament"],
                    "opponent": event["player_two"]["name"],
                    "date": event["date"],
                    "surface": event["surface"]
                }
            }
        if event.get("player_two", {}).get("id") == player_id:
            return {
                "player": event["player_two"],
                "upcoming_match": {
                    "tournament": event["tournament"],
                    "opponent": event["player_one"]["name"],
                    "date": event["date"],
                    "surface": event["surface"]
                }
            }
    
    raise HTTPException(status_code=404, detail="Player not found")
