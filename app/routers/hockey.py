"""
Hockey Intelligence API Router
Endpoints for NHL/International hockey games and DCI scoring
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.services.hockey_intel import HockeyDCIService, get_mock_hockey_events
from app.routers.auth import get_current_user
from app.database import User

router = APIRouter(prefix="/api/hockey", tags=["hockey"])

@router.get("/upcoming")
async def get_upcoming_hockey_games(
    db: Session = Depends(get_db)
):
    """Get upcoming hockey games"""
    events = get_mock_hockey_events()
    
    for event in events:
        home_team = event.get("home_team", {})
        away_team = event.get("away_team", {})
        
        h_dci, a_dci = HockeyDCIService.compute_dci(home_team, away_team, is_team_one_home=True)
        
        event["dci_preview"] = {
            "home_team_score": h_dci["dci_score"],
            "away_team_score": a_dci["dci_score"],
            "classification": h_dci["classification"]
        }
    
    return {
        "events": events,
        "count": len(events),
        "sources_used": ["mock_data"],
        "premium_data_available": False
    }

@router.get("/game/{game_id}")
async def get_game_details(
    game_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific hockey game"""
    events = get_mock_hockey_events()
    
    game = next((e for e in events if e["id"] == game_id), None)
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game

@router.get("/dci/{game_id}")
async def get_hockey_dci(
    game_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DCI (Dynamic Confidence Index) for a hockey game
    Requires authentication
    """
    events = get_mock_hockey_events()
    game = next((e for e in events if e["id"] == game_id), None)
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    home_team = game.get("home_team", {})
    away_team = game.get("away_team", {})
    
    h_dci, a_dci = HockeyDCIService.compute_dci(home_team, away_team, is_team_one_home=True)
    
    is_premium = current_user.subscription_tier in ["pro", "oracle_plus"]
    
    if not is_premium:
        return {
            "game_id": game_id,
            "dci_preview": {
                "home_team_score": h_dci["dci_score"],
                "away_team_score": a_dci["dci_score"],
                "classification": h_dci["classification"]
            },
            "premium_required": True,
            "message": "Upgrade to Pro or Oracle Elite for full DCI analysis"
        }
    
    return {
        "game_id": game_id,
        "league": game.get("league"),
        "venue": game.get("venue"),
        "home_team": {
            "name": home_team.get("name"),
            "abbreviation": home_team.get("abbreviation"),
            "dci": h_dci
        },
        "away_team": {
            "name": away_team.get("name"),
            "abbreviation": away_team.get("abbreviation"),
            "dci": a_dci
        },
        "prediction": h_dci["classification"] if h_dci["dci_score"] > a_dci["dci_score"] else a_dci["classification"],
        "confidence": max(h_dci["dci_score"], a_dci["dci_score"])
    }

@router.get("/team/{team_id}")
async def get_team_details(
    team_id: str,
    db: Session = Depends(get_db)
):
    """Get team details by ID"""
    events = get_mock_hockey_events()
    
    for event in events:
        if event.get("home_team", {}).get("id") == team_id:
            return {
                "team": event["home_team"],
                "upcoming_game": {
                    "opponent": event["away_team"]["name"],
                    "date": event["date"],
                    "venue": event["venue"],
                    "is_home": True
                }
            }
        if event.get("away_team", {}).get("id") == team_id:
            return {
                "team": event["away_team"],
                "upcoming_game": {
                    "opponent": event["home_team"]["name"],
                    "date": event["date"],
                    "venue": event["venue"],
                    "is_home": False
                }
            }
    
    raise HTTPException(status_code=404, detail="Team not found")
