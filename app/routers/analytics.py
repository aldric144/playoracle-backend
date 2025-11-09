from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db, User, Game, AIPrediction
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/trends/{sport}")
async def get_sport_trends(
    sport: str,
    current_user: User = Depends(get_current_user)
):
    """Get trend data for a sport"""
    dates = [(datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7, 0, -1)]
    
    return {
        "sport": sport,
        "trends": {
            "prediction_accuracy": [
                {"date": dates[0], "accuracy": 72.5},
                {"date": dates[1], "accuracy": 75.0},
                {"date": dates[2], "accuracy": 78.3},
                {"date": dates[3], "accuracy": 76.8},
                {"date": dates[4], "accuracy": 80.2},
                {"date": dates[5], "accuracy": 82.1},
                {"date": dates[6], "accuracy": 81.5}
            ],
            "user_engagement": [
                {"date": dates[0], "predictions": 45},
                {"date": dates[1], "predictions": 52},
                {"date": dates[2], "predictions": 48},
                {"date": dates[3], "predictions": 61},
                {"date": dates[4], "predictions": 58},
                {"date": dates[5], "predictions": 67},
                {"date": dates[6], "predictions": 72}
            ]
        }
    }

@router.get("/team/{team_id}")
async def get_team_analytics(
    team_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get team analytics"""
    return {
        "team_id": team_id,
        "analytics": {
            "win_rate": 65.5,
            "home_win_rate": 72.3,
            "away_win_rate": 58.7,
            "avg_points_scored": 28.5,
            "avg_points_allowed": 22.1,
            "recent_form": [
                {"game": 1, "result": "W", "score": "31-24"},
                {"game": 2, "result": "W", "score": "28-17"},
                {"game": 3, "result": "L", "score": "20-27"},
                {"game": 4, "result": "W", "score": "35-21"},
                {"game": 5, "result": "W", "score": "24-20"}
            ],
            "key_stats": {
                "offensive_rating": 112.5,
                "defensive_rating": 98.3,
                "pace": 102.1,
                "efficiency": 1.15
            }
        }
    }

@router.get("/player/{player_id}")
async def get_player_analytics(
    player_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get player analytics"""
    return {
        "player_id": player_id,
        "analytics": {
            "ppg": 24.5,
            "rpg": 8.2,
            "apg": 5.7,
            "fg_percentage": 47.8,
            "three_point_percentage": 38.5,
            "recent_games": [
                {"date": "2024-11-07", "points": 28, "rebounds": 9, "assists": 6},
                {"date": "2024-11-05", "points": 22, "rebounds": 7, "assists": 5},
                {"date": "2024-11-03", "points": 31, "rebounds": 10, "assists": 8},
                {"date": "2024-11-01", "points": 19, "rebounds": 6, "assists": 4},
                {"date": "2024-10-30", "points": 26, "rebounds": 8, "assists": 7}
            ]
        }
    }

@router.get("/coach-corner/{game_id}")
async def get_coach_corner_analysis(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI Coach's Corner analysis for a game"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    ai_prediction = db.query(AIPrediction).filter(AIPrediction.game_id == game_id).first()
    
    analysis = {
        "game_id": game_id,
        "home_team": game.home_team,
        "away_team": game.away_team,
        "coach_analysis": ""
    }
    
    if ai_prediction:
        analysis["coach_analysis"] = ai_prediction.analysis
        analysis["key_factors"] = [
            f"Momentum: {ai_prediction.factors.get('home_momentum', 0):.1f} (Home) vs {ai_prediction.factors.get('away_momentum', 0):.1f} (Away)",
            f"Health: {ai_prediction.factors.get('home_health', 0):.1f} (Home) vs {ai_prediction.factors.get('away_health', 0):.1f} (Away)",
            f"Home advantage: +{ai_prediction.factors.get('home_advantage', 5)} points"
        ]
        analysis["prediction"] = {
            "winner": ai_prediction.predicted_winner,
            "confidence": ai_prediction.confidence,
            "dci_score": ai_prediction.dci_score
        }
    else:
        analysis["coach_analysis"] = f"This matchup between {game.home_team} and {game.away_team} presents an interesting challenge. Both teams have shown competitive form recently. Key factors to watch include home field advantage, recent momentum, and roster health. Make your prediction based on these analytical insights."
        analysis["key_factors"] = [
            "Home field advantage typically adds 3-5 points",
            "Recent form and momentum are critical indicators",
            "Injury reports can significantly impact outcomes"
        ]
    
    return analysis
