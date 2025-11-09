from fastapi import APIRouter, Depends
from typing import List, Dict
from app.models.database import db, User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])

@router.get("/global")
async def get_global_leaderboard(current_user: User = Depends(get_current_user)):
    """Get global leaderboard"""
    leaderboard = []
    
    for user in db.users.values():
        predictions = db.get_user_predictions(user.id)
        total = len(predictions)
        correct = sum(1 for p in predictions if p.was_correct)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        if total >= 5:  # Only include users with at least 5 predictions
            leaderboard.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "accuracy": round(accuracy, 2),
                "total_predictions": total,
                "correct_predictions": correct,
                "badges": len(user.badges)
            })
    
    leaderboard.sort(key=lambda x: (x["accuracy"], x["total_predictions"]), reverse=True)
    
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    
    return {
        "leaderboard": leaderboard[:50],  # Top 50
        "total_users": len(leaderboard)
    }

@router.get("/{sport}")
async def get_sport_leaderboard(
    sport: str,
    current_user: User = Depends(get_current_user)
):
    """Get sport-specific leaderboard"""
    leaderboard = []
    
    for user in db.users.values():
        predictions = [p for p in db.get_user_predictions(user.id) if p.sport == sport]
        total = len(predictions)
        correct = sum(1 for p in predictions if p.was_correct)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        if total >= 3:  # Only include users with at least 3 predictions in this sport
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
        "leaderboard": leaderboard[:25],  # Top 25
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
