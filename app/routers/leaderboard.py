from fastapi import APIRouter, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database import get_db, User, Prediction
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

@router.get("/global")
async def get_global_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get global leaderboard"""
    leaderboard = []
    
    users = db.query(User).all()
    for user in users:
        predictions = db.query(Prediction).filter(Prediction.user_id == user.id).all()
        total = len(predictions)
        correct = sum(1 for p in predictions if p.was_correct)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        if total >= 5:
            badges = user.badges if isinstance(user.badges, list) else []
            leaderboard.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "accuracy": round(accuracy, 2),
                "total_predictions": total,
                "correct_predictions": correct,
                "badges": len(badges)
            })
    
    leaderboard.sort(key=lambda x: (x["accuracy"], x["total_predictions"]), reverse=True)
    
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    
    return {
        "leaderboard": leaderboard[:50],
        "total_users": len(leaderboard)
    }

@router.get("/{sport}")
async def get_sport_leaderboard(
    sport: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sport-specific leaderboard"""
    leaderboard = []
    
    users = db.query(User).all()
    for user in users:
        predictions = db.query(Prediction).filter(
            Prediction.user_id == user.id,
            Prediction.sport == sport
        ).all()
        total = len(predictions)
        correct = sum(1 for p in predictions if p.was_correct)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        if total >= 3:
            leaderboard.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "accuracy": round(accuracy, 2),
                "total_predictions": total,
                "correct_predictions": correct
            })
    
    leaderboard.sort(key=lambda x: (x["accuracy"], x["total_predictions"]), reverse=True)
    
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    
    return {
        "sport": sport,
        "leaderboard": leaderboard[:25],
        "total_users": len(leaderboard)
    }

@router.get("/challenges")
async def get_weekly_challenges(current_user: User = Depends(get_current_user)):
    """Get weekly challenges"""
    return {
        "challenges": [
            {
                "id": "challenge_1",
                "title": "Perfect Week",
                "description": "Make 7 correct predictions in a row",
                "reward": "Gold Star Badge",
                "progress": 0,
                "target": 7,
                "active": True
            },
            {
                "id": "challenge_2",
                "title": "Multi-Sport Master",
                "description": "Make predictions in 5 different sports",
                "reward": "Versatility Badge",
                "progress": 0,
                "target": 5,
                "active": True
            },
            {
                "id": "challenge_3",
                "title": "High Confidence",
                "description": "Achieve 80%+ accuracy on 10 predictions",
                "reward": "Analyst Pro Badge",
                "progress": 0,
                "target": 10,
                "active": True
            }
        ],
        "weekly_reset": "Every Monday at 00:00 UTC"
    }
