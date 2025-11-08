from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum
from app.config import get_settings

settings = get_settings()

DATABASE_URL = settings.database_url if hasattr(settings, 'database_url') else "sqlite:///./playoracle.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class SubscriptionTierEnum(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ORACLE_PLUS = "oracle_plus"

class BadgeTypeEnum(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription_tier = Column(SQLEnum(SubscriptionTierEnum), default=SubscriptionTierEnum.FREE)
    stripe_customer_id = Column(String, nullable=True)
    sports_dna = Column(JSON, default={})
    badges = Column(JSON, default=[])

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    game_id = Column(String, index=True, nullable=False)
    sport = Column(String, nullable=False)
    predicted_winner = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    actual_winner = Column(String, nullable=True)
    was_correct = Column(Boolean, nullable=True)

class Game(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True, index=True)
    sport = Column(String, index=True, nullable=False)
    league = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    status = Column(String, default="scheduled")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    
    game_id = Column(String, primary_key=True, index=True)
    predicted_winner = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    dci_score = Column(Float, nullable=False)
    analysis = Column(String, nullable=False)
    factors = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
