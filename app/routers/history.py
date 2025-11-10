from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/history", tags=["history"])

_season_cache: Dict[tuple, Dict[str, Any]] = {}
_accuracy_cache: Dict[tuple, Dict[str, Any]] = {}


class Milestone(BaseModel):
    date: str
    label: str
    type: str  # 'season_start' | 'playoffs' | 'finals' | 'championship' | 'highlight'
    note: Optional[str] = None


class TopDCITeam(BaseModel):
    team: str
    avg_dci: float


class SeasonHistory(BaseModel):
    sport: str
    year: int
    start: str
    end: str
    champion: str
    ai_champion_prediction: str
    top_dci: List[TopDCITeam]
    prediction_accuracy: int
    milestones: List[Milestone]


class YearAccuracy(BaseModel):
    year: int
    accuracy: int


class AccuracyTrend(BaseModel):
    sport: str
    from_year: int
    to_year: int
    total_seasons: int
    correct_count: int
    accuracy_percent: int
    trend: List[YearAccuracy]


MOCK_SEASON_DATA = {
    ("nfl", 2026): {
        "sport": "nfl",
        "year": 2026,
        "start": "2026-09-10",
        "end": "2027-02-13",
        "champion": "TBD",
        "ai_champion_prediction": "Chiefs",
        "top_dci": [
            {"team": "Chiefs", "avg_dci": 89.2},
            {"team": "49ers", "avg_dci": 87.5},
            {"team": "Bills", "avg_dci": 85.3}
        ],
        "prediction_accuracy": 0,
        "milestones": [
            {"date": "2026-09-10", "label": "Season Start", "type": "season_start"},
            {"date": "2027-01-11", "label": "Wild Card Round", "type": "playoffs"},
            {"date": "2027-01-18", "label": "Divisional Round", "type": "playoffs"},
            {"date": "2027-01-26", "label": "Conference Championships", "type": "playoffs"},
            {"date": "2027-02-13", "label": "Super Bowl LXI", "type": "championship"}
        ]
    },
    ("nfl", 2025): {
        "sport": "nfl",
        "year": 2025,
        "start": "2025-09-05",
        "end": "2026-02-08",
        "champion": "Chiefs",
        "ai_champion_prediction": "Chiefs",
        "top_dci": [
            {"team": "Chiefs", "avg_dci": 91.8},
            {"team": "49ers", "avg_dci": 88.2},
            {"team": "Ravens", "avg_dci": 86.7}
        ],
        "prediction_accuracy": 92,
        "milestones": [
            {"date": "2025-09-05", "label": "Season Start", "type": "season_start"},
            {"date": "2026-01-10", "label": "Wild Card Round", "type": "playoffs"},
            {"date": "2026-01-17", "label": "Divisional Round", "type": "playoffs"},
            {"date": "2026-01-25", "label": "Conference Championships", "type": "playoffs"},
            {"date": "2026-02-08", "label": "Super Bowl LX", "type": "championship", "note": "Chiefs defeated 49ers 31-28"}
        ]
    },
    ("nfl", 2024): {
        "sport": "nfl",
        "year": 2024,
        "start": "2024-09-05",
        "end": "2025-02-09",
        "champion": "Chiefs",
        "ai_champion_prediction": "49ers",
        "top_dci": [
            {"team": "49ers", "avg_dci": 90.5},
            {"team": "Chiefs", "avg_dci": 89.1},
            {"team": "Ravens", "avg_dci": 87.3}
        ],
        "prediction_accuracy": 85,
        "milestones": [
            {"date": "2024-09-05", "label": "Season Start", "type": "season_start"},
            {"date": "2025-01-11", "label": "Wild Card Round", "type": "playoffs"},
            {"date": "2025-01-18", "label": "Divisional Round", "type": "playoffs"},
            {"date": "2025-01-26", "label": "Conference Championships", "type": "playoffs"},
            {"date": "2025-02-09", "label": "Super Bowl LIX", "type": "championship", "note": "Chiefs defeated Eagles 38-35"}
        ]
    },
    ("nfl", 2023): {
        "sport": "nfl",
        "year": 2023,
        "start": "2023-09-07",
        "end": "2024-02-11",
        "champion": "Chiefs",
        "ai_champion_prediction": "Chiefs",
        "top_dci": [
            {"team": "Chiefs", "avg_dci": 92.3},
            {"team": "49ers", "avg_dci": 90.8},
            {"team": "Ravens", "avg_dci": 88.5}
        ],
        "prediction_accuracy": 88,
        "milestones": [
            {"date": "2023-09-07", "label": "Season Start", "type": "season_start"},
            {"date": "2024-01-13", "label": "Wild Card Round", "type": "playoffs"},
            {"date": "2024-01-20", "label": "Divisional Round", "type": "playoffs"},
            {"date": "2024-01-28", "label": "Conference Championships", "type": "playoffs"},
            {"date": "2024-02-11", "label": "Super Bowl LVIII", "type": "championship", "note": "Chiefs defeated 49ers 25-22 (OT)"}
        ]
    },
    ("nfl", 2022): {
        "sport": "nfl",
        "year": 2022,
        "start": "2022-09-08",
        "end": "2023-02-12",
        "champion": "Chiefs",
        "ai_champion_prediction": "Bills",
        "top_dci": [
            {"team": "Bills", "avg_dci": 91.2},
            {"team": "Chiefs", "avg_dci": 89.7},
            {"team": "Eagles", "avg_dci": 88.9}
        ],
        "prediction_accuracy": 82,
        "milestones": [
            {"date": "2022-09-08", "label": "Season Start", "type": "season_start"},
            {"date": "2023-01-14", "label": "Wild Card Round", "type": "playoffs"},
            {"date": "2023-01-21", "label": "Divisional Round", "type": "playoffs"},
            {"date": "2023-01-29", "label": "Conference Championships", "type": "playoffs"},
            {"date": "2023-02-12", "label": "Super Bowl LVII", "type": "championship", "note": "Chiefs defeated Eagles 38-35"}
        ]
    },
    
    ("nba", 2026): {
        "sport": "nba",
        "year": 2026,
        "start": "2026-10-15",
        "end": "2027-06-20",
        "champion": "TBD",
        "ai_champion_prediction": "Celtics",
        "top_dci": [
            {"team": "Celtics", "avg_dci": 92.1},
            {"team": "Bucks", "avg_dci": 88.7},
            {"team": "Nuggets", "avg_dci": 87.5}
        ],
        "prediction_accuracy": 0,
        "milestones": [
            {"date": "2026-10-15", "label": "Season Start", "type": "season_start"},
            {"date": "2027-04-19", "label": "Playoffs Begin", "type": "playoffs"},
            {"date": "2027-05-20", "label": "Conference Finals", "type": "playoffs"},
            {"date": "2027-06-01", "label": "NBA Finals", "type": "championship"}
        ]
    },
    ("nba", 2025): {
        "sport": "nba",
        "year": 2025,
        "start": "2025-10-15",
        "end": "2026-06-12",
        "champion": "Celtics",
        "ai_champion_prediction": "Celtics",
        "top_dci": [
            {"team": "Celtics", "avg_dci": 93.5},
            {"team": "Nuggets", "avg_dci": 89.2},
            {"team": "Bucks", "avg_dci": 87.8}
        ],
        "prediction_accuracy": 89,
        "milestones": [
            {"date": "2025-10-15", "label": "Season Start", "type": "season_start"},
            {"date": "2026-04-18", "label": "Playoffs Begin", "type": "playoffs"},
            {"date": "2026-05-19", "label": "Conference Finals", "type": "playoffs"},
            {"date": "2026-06-01", "label": "NBA Finals", "type": "championship", "note": "Celtics defeated Nuggets 4-2"}
        ]
    },
    ("nba", 2024): {
        "sport": "nba",
        "year": 2024,
        "start": "2024-10-22",
        "end": "2025-06-15",
        "champion": "Nuggets",
        "ai_champion_prediction": "Bucks",
        "top_dci": [
            {"team": "Bucks", "avg_dci": 91.3},
            {"team": "Nuggets", "avg_dci": 90.1},
            {"team": "Celtics", "avg_dci": 88.9}
        ],
        "prediction_accuracy": 84,
        "milestones": [
            {"date": "2024-10-22", "label": "Season Start", "type": "season_start"},
            {"date": "2025-04-15", "label": "Playoffs Begin", "type": "playoffs"},
            {"date": "2025-05-20", "label": "Conference Finals", "type": "playoffs"},
            {"date": "2025-06-01", "label": "NBA Finals", "type": "championship", "note": "Nuggets defeated Heat 4-1"}
        ]
    },
    ("nba", 2023): {
        "sport": "nba",
        "year": 2023,
        "start": "2023-10-24",
        "end": "2024-06-17",
        "champion": "Nuggets",
        "ai_champion_prediction": "Nuggets",
        "top_dci": [
            {"team": "Nuggets", "avg_dci": 94.2},
            {"team": "Celtics", "avg_dci": 90.5},
            {"team": "Bucks", "avg_dci": 89.3}
        ],
        "prediction_accuracy": 91,
        "milestones": [
            {"date": "2023-10-24", "label": "Season Start", "type": "season_start"},
            {"date": "2024-04-20", "label": "Playoffs Begin", "type": "playoffs"},
            {"date": "2024-05-21", "label": "Conference Finals", "type": "playoffs"},
            {"date": "2024-06-06", "label": "NBA Finals", "type": "championship", "note": "Nuggets defeated Heat 4-1"}
        ]
    },
    ("nba", 2022): {
        "sport": "nba",
        "year": 2022,
        "start": "2022-10-18",
        "end": "2023-06-12",
        "champion": "Warriors",
        "ai_champion_prediction": "Celtics",
        "top_dci": [
            {"team": "Celtics", "avg_dci": 92.7},
            {"team": "Warriors", "avg_dci": 90.8},
            {"team": "Bucks", "avg_dci": 89.1}
        ],
        "prediction_accuracy": 79,
        "milestones": [
            {"date": "2022-10-18", "label": "Season Start", "type": "season_start"},
            {"date": "2023-04-15", "label": "Playoffs Begin", "type": "playoffs"},
            {"date": "2023-05-16", "label": "Conference Finals", "type": "playoffs"},
            {"date": "2023-06-01", "label": "NBA Finals", "type": "championship", "note": "Warriors defeated Celtics 4-2"}
        ]
    }
}

MOCK_ACCURACY_TRENDS = {
    "nfl": {
        "total_seasons": 5,
        "correct_count": 4,
        "accuracy_percent": 80,
        "trend": [
            {"year": 2022, "accuracy": 82},
            {"year": 2023, "accuracy": 88},
            {"year": 2024, "accuracy": 85},
            {"year": 2025, "accuracy": 92},
            {"year": 2026, "accuracy": 0}
        ]
    },
    "nba": {
        "total_seasons": 5,
        "correct_count": 3,
        "accuracy_percent": 60,
        "trend": [
            {"year": 2022, "accuracy": 79},
            {"year": 2023, "accuracy": 91},
            {"year": 2024, "accuracy": 84},
            {"year": 2025, "accuracy": 89},
            {"year": 2026, "accuracy": 0}
        ]
    }
}


@router.get("/{sport}/{year}", response_model=SeasonHistory)
async def get_season_history(sport: str, year: int):
    """
    Get historical season data for a specific sport and year.
    Includes champion, predictions, top DCI teams, and milestones.
    """
    cache_key = (sport.lower(), year)
    
    if cache_key in _season_cache:
        return _season_cache[cache_key]
    
    if cache_key in MOCK_SEASON_DATA:
        data = MOCK_SEASON_DATA[cache_key]
        _season_cache[cache_key] = data
        return data
    
    raise HTTPException(
        status_code=404,
        detail=f"Season data not available for {sport} {year}"
    )


@router.get("/{sport}/accuracy", response_model=AccuracyTrend)
async def get_accuracy_trend(sport: str, from_year: int = 2022, to_year: int = 2026):
    """
    Get AI prediction accuracy trend for a sport across multiple seasons.
    Returns aggregate accuracy and year-by-year breakdown.
    """
    cache_key = (sport.lower(), from_year, to_year)
    
    if cache_key in _accuracy_cache:
        return _accuracy_cache[cache_key]
    
    sport_lower = sport.lower()
    
    if sport_lower in MOCK_ACCURACY_TRENDS:
        trend_data = MOCK_ACCURACY_TRENDS[sport_lower]
        
        filtered_trend = [
            t for t in trend_data["trend"]
            if from_year <= t["year"] <= to_year and t["accuracy"] > 0
        ]
        
        total_seasons = len(filtered_trend)
        correct_count = sum(1 for t in filtered_trend if t["accuracy"] >= 50)
        accuracy_percent = trend_data["accuracy_percent"]
        
        result = {
            "sport": sport_lower,
            "from_year": from_year,
            "to_year": to_year,
            "total_seasons": total_seasons,
            "correct_count": correct_count,
            "accuracy_percent": accuracy_percent,
            "trend": filtered_trend
        }
        
        _accuracy_cache[cache_key] = result
        return result
    
    raise HTTPException(
        status_code=404,
        detail=f"Accuracy data not available for {sport}"
    )
