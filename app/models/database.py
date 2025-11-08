from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ORACLE_PLUS = "oracle_plus"

class BadgeType(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"

@dataclass
class User:
    id: str
    email: str
    hashed_password: str
    full_name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    stripe_customer_id: Optional[str] = None
    sports_dna: Dict = field(default_factory=dict)
    badges: List[BadgeType] = field(default_factory=list)

@dataclass
class Prediction:
    id: str
    user_id: str
    game_id: str
    sport: str
    predicted_winner: str
    confidence: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    actual_winner: Optional[str] = None
    was_correct: Optional[bool] = None

@dataclass
class Game:
    id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    scheduled_time: datetime
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = "scheduled"

@dataclass
class AIPrediction:
    game_id: str
    predicted_winner: str
    confidence: float
    dci_score: float
    analysis: str
    factors: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

class InMemoryDatabase:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.predictions: Dict[str, Prediction] = {}
        self.games: Dict[str, Game] = {}
        self.ai_predictions: Dict[str, AIPrediction] = {}
        self.user_emails: Dict[str, str] = {}
    
    def add_user(self, user: User):
        self.users[user.id] = user
        self.user_emails[user.email] = user.id
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        user_id = self.user_emails.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def add_prediction(self, prediction: Prediction):
        self.predictions[prediction.id] = prediction
    
    def get_user_predictions(self, user_id: str) -> List[Prediction]:
        return [p for p in self.predictions.values() if p.user_id == user_id]
    
    def add_game(self, game: Game):
        self.games[game.id] = game
    
    def get_games_by_sport(self, sport: str) -> List[Game]:
        return [g for g in self.games.values() if g.sport == sport]
    
    def add_ai_prediction(self, prediction: AIPrediction):
        self.ai_predictions[prediction.game_id] = prediction
    
    def get_ai_prediction(self, game_id: str) -> Optional[AIPrediction]:
        return self.ai_predictions.get(game_id)

db = InMemoryDatabase()
