from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import random

router = APIRouter(prefix="/api/ai", tags=["ai_analytics"])

_accuracy_cache: Dict[str, Any] = {}
_commentary_cache: Dict[str, Any] = {}
_commentary_log: List[Dict[str, Any]] = []


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


class AICommentary(BaseModel):
    sport: str
    season: int
    commentary: str
    trust_index: str  # "verified" | "high" | "moderate" | "low"
    confidence: float
    accuracy: float
    delta: float
    key_factors: List[str]
    data_sources: List[str]
    last_updated: str
    timestamp: str


def generate_commentary(sport: str, season: int, accuracy: float, delta: float, trend_r: float) -> str:
    """
    Generate AI self-commentary based on prediction accuracy and performance metrics.
    """
    sport_display = sport.upper() if len(sport) <= 4 else sport.replace("_", " ").title()
    
    if accuracy >= 85:
        templates = [
            f"I predicted the {season} {sport_display} season with {accuracy:.1f}% confidence — my defensive weighting update proved crucial.",
            f"My {sport_display} model achieved {accuracy:.1f}% accuracy by factoring in momentum shifts and injury impact analysis.",
            f"The {season} {sport_display} predictions hit {accuracy:.1f}% accuracy after I refined my playoff probability algorithms.",
            f"I correctly forecasted {int(accuracy)}% of {sport_display} outcomes by emphasizing late-season form and head-to-head records."
        ]
    elif accuracy >= 70:
        templates = [
            f"I achieved {accuracy:.1f}% accuracy in {sport_display} — next season I'll weight bench depth more heavily.",
            f"My {sport_display} model hit {accuracy:.1f}% by analyzing roster changes, though I underestimated coaching impact.",
            f"The {season} {sport_display} season taught me to factor in home-field advantage more precisely ({accuracy:.1f}% accuracy).",
            f"I reached {accuracy:.1f}% accuracy in {sport_display} but missed key upset predictions due to weather variables."
        ]
    else:
        templates = [
            f"I missed the {sport_display} season predictions by {100 - accuracy:.1f}% — adjusting my injury recovery timeline model for next year.",
            f"My {sport_display} accuracy was {accuracy:.1f}% due to underestimating bench momentum — recalibrating for {season + 1}.",
            f"The {season} {sport_display} season exposed gaps in my playoff seeding algorithm ({accuracy:.1f}% accuracy) — improvements incoming.",
            f"I achieved {accuracy:.1f}% in {sport_display} but learned to better weight mid-season trades and roster chemistry."
        ]
    
    if delta > 2.0:
        templates.append(f"My {sport_display} model improved {delta:.1f}% year-over-year by incorporating advanced momentum metrics.")
    elif delta < -1.0:
        templates.append(f"My {sport_display} accuracy dropped {abs(delta):.1f}% this season — analyzing variance patterns for next year.")
    
    return random.choice(templates)


def get_trust_index(confidence: float) -> str:
    """
    Determine trust index tier based on confidence level.
    """
    if confidence >= 90:
        return "verified"
    elif confidence >= 75:
        return "high"
    elif confidence >= 60:
        return "moderate"
    else:
        return "low"


MOCK_KEY_FACTORS = {
    "nfl": ["Defensive line pressure", "Red zone efficiency", "Turnover differential", "Playoff experience"],
    "nba": ["Bench depth scoring", "Three-point percentage", "Defensive rating", "Clutch performance"],
    "mlb": ["Bullpen consistency", "On-base percentage", "Starting rotation ERA", "Home run rate"],
    "nhl": ["Goaltender save %", "Power play efficiency", "Shot differential", "Penalty kill rate"],
    "soccer": ["Possession control", "Shot accuracy", "Defensive organization", "Set piece conversion"],
    "formula1": ["Qualifying pace", "Tire strategy", "Pit stop efficiency", "Weather adaptation"],
    "college_football": ["Recruiting class rank", "Offensive line strength", "Turnover margin", "Special teams"],
    "boxing": ["Punch accuracy", "Ring control", "Stamina endurance", "Counter-punching"],
    "mma": ["Ground control time", "Striking accuracy", "Takedown defense", "Cardio conditioning"],
    "tennis": ["First serve %", "Break point conversion", "Unforced errors", "Court coverage"],
    "volleyball": ["Block efficiency", "Service aces", "Dig success rate", "Attack percentage"],
    "rugby": ["Scrum dominance", "Lineout success", "Tackle completion", "Territory control"],
    "cricket": ["Bowling economy", "Batting strike rate", "Fielding efficiency", "Partnership building"],
    "golf": ["Driving accuracy", "Greens in regulation", "Putting average", "Scrambling ability"],
    "table_tennis": ["Service variation", "Forehand consistency", "Footwork speed", "Rally endurance"],
    "nascar": ["Pit crew speed", "Fuel strategy", "Drafting efficiency", "Track position"],
    "motogp": ["Cornering speed", "Braking precision", "Tire management", "Overtaking skill"],
    "cycling": ["Climbing power", "Sprint speed", "Team tactics", "Aerodynamic positioning"]
}


@router.get("/commentary/{sport}/{season}", response_model=AICommentary)
async def get_ai_commentary(sport: str, season: int):
    """
    Get AI self-commentary for a specific sport and season.
    Generates dynamic reflections based on prediction accuracy, DCI variance, and model factors.
    """
    cache_key = f"{sport}_{season}"
    
    if cache_key in _commentary_cache:
        cached = _commentary_cache[cache_key]
        cached_time = datetime.fromisoformat(cached["timestamp"])
        if (datetime.utcnow() - cached_time).total_seconds() < 86400:
            return cached
    
    sport_lower = sport.lower().replace("-", "_").replace(" ", "_")
    
    if sport_lower not in MOCK_AI_ACCURACY_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Commentary not available for {sport}"
        )
    
    accuracy_data = MOCK_AI_ACCURACY_DATA[sport_lower]
    accuracy = accuracy_data["accuracy"]
    delta = accuracy_data["delta"]
    trend_r = accuracy_data["trend_r"]
    
    commentary_text = generate_commentary(sport_lower, season, accuracy, delta, trend_r)
    
    confidence = min(100, accuracy + (trend_r * 10))
    
    trust_index = get_trust_index(confidence)
    
    key_factors = MOCK_KEY_FACTORS.get(sport_lower, ["Performance metrics", "Historical data", "Team dynamics", "Statistical analysis"])
    
    data_sources = ["SportsDataIO", "Sportradar", "Historical DCI Database"]
    
    commentary_obj = {
        "sport": sport_lower,
        "season": season,
        "commentary": commentary_text,
        "trust_index": trust_index,
        "confidence": round(confidence, 1),
        "accuracy": accuracy,
        "delta": delta,
        "key_factors": key_factors,
        "data_sources": data_sources,
        "last_updated": datetime.utcnow().isoformat(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    _commentary_cache[cache_key] = commentary_obj
    
    _commentary_log.append({
        **commentary_obj,
        "logged_at": datetime.utcnow().isoformat()
    })
    
    return commentary_obj


@router.get("/commentary/{sport}")
async def get_latest_commentary(sport: str):
    """
    Get the latest AI commentary for a sport (current season).
    """
    current_season = 2026
    return await get_ai_commentary(sport, current_season)


@router.get("/commentary-log")
async def get_commentary_log(limit: int = 50):
    """
    Get recent AI commentary log entries for analysis and email digests.
    """
    return {
        "total": len(_commentary_log),
        "entries": _commentary_log[-limit:] if _commentary_log else [],
        "last_updated": datetime.utcnow().isoformat()
    }
