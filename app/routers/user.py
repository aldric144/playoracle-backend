from fastapi import APIRouter, Depends
from typing import List, Dict
from app.models.database import db, User, BadgeType
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/sports-dna")
async def get_sports_dna(current_user: User = Depends(get_current_user)):
    """Get user's sports DNA preferences"""
    return {
        "user_id": current_user.id,
        "sports_dna": current_user.sports_dna
    }

@router.put("/sports-dna")
async def update_sports_dna(
    sports_dna: Dict,
    current_user: User = Depends(get_current_user)
):
    """Update user's sports DNA preferences"""
    current_user.sports_dna = sports_dna
    return {
        "user_id": current_user.id,
        "sports_dna": current_user.sports_dna,
        "message": "Sports DNA updated successfully"
    }

@router.get("/badges")
async def get_user_badges(current_user: User = Depends(get_current_user)):
    """Get user's earned badges"""
    predictions = db.get_user_predictions(current_user.id)
    total = len(predictions)
    correct = sum(1 for p in predictions if p.was_correct)
    
    badges = []
    if total >= 10:
        badges.append(BadgeType.BRONZE)
    if total >= 50 and correct >= 25:
        badges.append(BadgeType.SILVER)
    if total >= 100 and correct >= 60:
        badges.append(BadgeType.GOLD)
    
    current_user.badges = badges
    
    return {
        "user_id": current_user.id,
        "badges": [badge.value for badge in badges],
        "next_badge": "silver" if BadgeType.BRONZE in badges and BadgeType.SILVER not in badges else "gold"
    }

@router.get("/progress")
async def get_user_progress(current_user: User = Depends(get_current_user)):
    """Get user's learning progress"""
    predictions = db.get_user_predictions(current_user.id)
    
    total = len(predictions)
    correct = sum(1 for p in predictions if p.was_correct)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    sports_covered = len(set(p.sport for p in predictions))
    
    return {
        "user_id": current_user.id,
        "total_predictions": total,
        "correct_predictions": correct,
        "accuracy_percentage": round(accuracy, 2),
        "sports_covered": sports_covered,
        "badges_earned": len(current_user.badges),
        "level": "Beginner" if total < 20 else "Intermediate" if total < 50 else "Advanced",
        "subscription_tier": current_user.subscription_tier.value
    }

@router.get("/report")
async def generate_user_report(current_user: User = Depends(get_current_user)):
    """Generate monthly progress report"""
    predictions = db.get_user_predictions(current_user.id)
    
    total = len(predictions)
    correct = sum(1 for p in predictions if p.was_correct)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    by_sport = {}
    for p in predictions:
        if p.sport not in by_sport:
            by_sport[p.sport] = {"total": 0, "correct": 0}
        by_sport[p.sport]["total"] += 1
        if p.was_correct:
            by_sport[p.sport]["correct"] += 1
    
    for sport in by_sport:
        sport_total = by_sport[sport]["total"]
        sport_correct = by_sport[sport]["correct"]
        by_sport[sport]["accuracy"] = (sport_correct / sport_total * 100) if sport_total > 0 else 0
    
    return {
        "user_id": current_user.id,
        "report_period": "Last 30 days",
        "overall_accuracy": round(accuracy, 2),
        "total_predictions": total,
        "correct_predictions": correct,
        "by_sport": by_sport,
        "badges": [badge.value for badge in current_user.badges],
        "insights": [
            "You're showing consistent improvement in prediction accuracy",
            "Consider exploring more sports to broaden your Sports IQ",
            "Your analytical skills are developing well"
        ]
    }
