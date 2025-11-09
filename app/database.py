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
    is_admin = Column(Boolean, default=False, nullable=False)

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

class EventStatusEnum(str, enum.Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class PremiumEvent(Base):
    __tablename__ = "premium_events"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    status = Column(SQLEnum(EventStatusEnum), default=EventStatusEnum.UPCOMING)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    stripe_price_id_single = Column(String, nullable=True)
    stripe_price_id_season = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EventSubscription(Base):
    __tablename__ = "event_subscriptions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    event_slug = Column(String, index=True, nullable=False)
    stripe_price_id = Column(String, nullable=True)
    option_type = Column(String, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables and run migrations"""
    Base.metadata.create_all(bind=engine)
    
    run_migrations()

def run_migrations():
    """Run database migrations for schema updates"""
    from sqlalchemy import text
    import uuid
    
    db = SessionLocal()
    try:
        try:
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE
            """))
            db.commit()
            print("✓ Migration: Added is_admin column to users table")
        except Exception as e:
            db.rollback()
            print(f"Migration note: is_admin column may already exist - {e}")
        
        try:
            result = db.execute(text("""
                UPDATE users 
                SET is_admin = TRUE 
                WHERE email = 'admin@playoracle.com'
                RETURNING id
            """))
            db.commit()
            if result.rowcount > 0:
                print("✓ Migration: Set admin@playoracle.com as admin")
            else:
                print("Note: admin@playoracle.com user not found (will be created on signup)")
        except Exception as e:
            db.rollback()
            print(f"Migration note: Could not update admin user - {e}")
        
        seed_premium_events(db)
            
    finally:
        db.close()

def seed_premium_events(db):
    """Seed initial premium events data"""
    from datetime import datetime
    import uuid
    
    events = [
        {
            "id": str(uuid.uuid4()),
            "name": "March Madness 2025",
            "slug": "march-madness-2025",
            "description": "Unlock exclusive AI-powered bracket predictions, team analytics, and real-time upset alerts for the entire March Madness tournament.",
            "status": "upcoming",
            "start_date": datetime(2025, 3, 10),
            "end_date": datetime(2025, 4, 7),
            "expiration_date": datetime(2025, 5, 7),
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Super Bowl 2026",
            "slug": "super-bowl-2026",
            "description": "Get AI-driven predictions, player matchup analysis, and real-time game insights for Super Bowl LX.",
            "status": "upcoming",
            "start_date": datetime(2026, 1, 10),
            "end_date": datetime(2026, 2, 8),
            "expiration_date": datetime(2026, 3, 10),
        },
        {
            "id": str(uuid.uuid4()),
            "name": "World Series 2025",
            "slug": "world-series-2025",
            "description": "Access advanced baseball analytics, pitcher-batter matchup predictions, and AI-powered game forecasts for the entire World Series.",
            "status": "upcoming",
            "start_date": datetime(2025, 10, 10),
            "end_date": datetime(2025, 10, 30),
            "expiration_date": datetime(2025, 12, 30),
        },
        {
            "id": str(uuid.uuid4()),
            "name": "NBA Finals 2025",
            "slug": "nba-finals-2025",
            "description": "Unlock comprehensive NBA Finals analytics including player performance predictions, team matchup analysis, and AI-driven game forecasts.",
            "status": "upcoming",
            "start_date": datetime(2025, 6, 1),
            "end_date": datetime(2025, 6, 25),
            "expiration_date": datetime(2025, 7, 25),
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Racing Championship 2025",
            "slug": "racing-championship-2025",
            "description": "Get AI-powered race predictions, driver performance analytics, and track condition insights for the entire racing championship season.",
            "status": "upcoming",
            "start_date": datetime(2025, 11, 1),
            "end_date": datetime(2025, 11, 30),
            "expiration_date": datetime(2026, 1, 30),
        },
    ]
    
    try:
        for event_data in events:
            existing = db.query(PremiumEvent).filter(PremiumEvent.slug == event_data["slug"]).first()
            if not existing:
                event = PremiumEvent(**event_data)
                db.add(event)
        db.commit()
        print("✓ Migration: Seeded premium events data")
    except Exception as e:
        db.rollback()
        print(f"Migration note: Premium events may already exist - {e}")
