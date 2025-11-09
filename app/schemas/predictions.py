from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class PredictionCreate(BaseModel):
    game_id: str
    sport: str
    predicted_winner: str
    confidence: float

class PredictionResponse(BaseModel):
    id: str
    user_id: str
    game_id: str
    sport: str
    predicted_winner: str
    confidence: float
    created_at: datetime
    actual_winner: Optional[str] = None
    was_correct: Optional[bool] = None

class AIPredictionResponse(BaseModel):
    game_id: str
    predicted_winner: str
    confidence: float
    dci_score: float
    analysis: str
    factors: Dict
    created_at: datetime

class GameResponse(BaseModel):
    id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    scheduled_time: datetime
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str

class UserAccuracyResponse(BaseModel):
    total_predictions: int
    correct_predictions: int
    accuracy_percentage: float
    by_sport: Dict[str, Dict]
