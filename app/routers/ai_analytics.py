from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai", tags=["ai_analytics"])

_accuracy_cache: Dict[str, Any] = {}


class SportAccuracy(BaseModel):
    accuracy: float
    seasons: int
    trend_r: float  # Correlation coefficient for trend
    delta: float  # Year-over-year improvement percentage


class AIAccuracyResponse(BaseModel):
    nfl: SportAccuracy
    nba: SportAccuracy
    mlb: SportAccuracy
    nhl: SportAccuracy
    soccer: SportAccuracy
    formula1: SportAccuracy
    college_football: SportAccuracy
    boxing: SportAccuracy
    mma: SportAccuracy
    tennis: SportAccuracy
    volleyball: SportAccuracy
    rugby: SportAccuracy
    cricket: SportAccuracy
    golf: SportAccuracy
    table_tennis: SportAccuracy
    nascar: SportAccuracy
    motogp: SportAccuracy
    cycling: SportAccuracy
    last_updated: str


MOCK_AI_ACCURACY_DATA = {
    "nfl": {
        "accuracy": 88.6,
        "seasons": 12,
        "trend_r": 0.91,
        "delta": 2.4
    },
    "nba": {
        "accuracy": 84.3,
        "seasons": 10,
        "trend_r": 0.89,
        "delta": 1.1
    },
    "mlb": {
        "accuracy": 79.2,
        "seasons": 15,
        "trend_r": 0.85,
        "delta": -0.3
    },
    "nhl": {
        "accuracy": 82.7,
        "seasons": 8,
        "trend_r": 0.88,
        "delta": 1.8
    },
    "soccer": {
        "accuracy": 76.5,
        "seasons": 6,
        "trend_r": 0.82,
        "delta": 0.7
    },
    "formula1": {
        "accuracy": 91.3,
        "seasons": 14,
        "trend_r": 0.94,
        "delta": 3.2
    },
    "college_football": {
        "accuracy": 73.8,
        "seasons": 9,
        "trend_r": 0.79,
        "delta": -1.2
    },
    "boxing": {
        "accuracy": 85.9,
        "seasons": 11,
        "trend_r": 0.87,
        "delta": 2.1
    },
    "mma": {
        "accuracy": 87.4,
        "seasons": 13,
        "trend_r": 0.90,
        "delta": 2.8
    },
    "tennis": {
        "accuracy": 89.1,
        "seasons": 16,
        "trend_r": 0.92,
        "delta": 1.9
    },
    "volleyball": {
        "accuracy": 71.2,
        "seasons": 5,
        "trend_r": 0.76,
        "delta": 0.4
    },
    "rugby": {
        "accuracy": 74.6,
        "seasons": 7,
        "trend_r": 0.81,
        "delta": 1.3
    },
    "cricket": {
        "accuracy": 78.9,
        "seasons": 8,
        "trend_r": 0.84,
        "delta": 0.9
    },
    "golf": {
        "accuracy": 68.3,
        "seasons": 12,
        "trend_r": 0.73,
        "delta": -0.8
    },
    "table_tennis": {
        "accuracy": 81.5,
        "seasons": 6,
        "trend_r": 0.86,
        "delta": 1.5
    },
    "nascar": {
        "accuracy": 83.7,
        "seasons": 10,
        "trend_r": 0.88,
        "delta": 2.3
    },
    "motogp": {
        "accuracy": 86.2,
        "seasons": 9,
        "trend_r": 0.89,
        "delta": 1.7
    },
    "cycling": {
        "accuracy": 75.4,
        "seasons": 7,
        "trend_r": 0.80,
        "delta": 0.6
    }
}


@router.get("/accuracy", response_model=AIAccuracyResponse)
async def get_ai_accuracy():
    """
    Get AI prediction accuracy aggregated across all sports.
    Returns accuracy percentage, total seasons analyzed, trend correlation,
    and year-over-year improvement delta for each sport.
    
    This endpoint powers the Predictive Accuracy Leaderboard in Coach's Corner.
    """
    cache_key = "ai_accuracy_all_sports"
    
    if cache_key in _accuracy_cache:
        return _accuracy_cache[cache_key]
    
    response = {
        **MOCK_AI_ACCURACY_DATA,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    _accuracy_cache[cache_key] = response
    return response


@router.get("/accuracy/{sport}", response_model=SportAccuracy)
async def get_sport_accuracy(sport: str):
    """
    Get AI prediction accuracy for a specific sport.
    """
    sport_lower = sport.lower().replace("-", "_").replace(" ", "_")
    
    if sport_lower in MOCK_AI_ACCURACY_DATA:
        return MOCK_AI_ACCURACY_DATA[sport_lower]
    
    raise HTTPException(
        status_code=404,
        detail=f"Accuracy data not available for {sport}"
    )
