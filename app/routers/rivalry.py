from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional
from datetime import datetime, date
import uuid

from app.database import get_db, RivalryHistory, RivalryMetrics, User, SubscriptionTierEnum
from app.utils.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/rivalry", tags=["rivalry"])

class RivalryHistoryResponse(BaseModel):
    id: str
    team_a: str
    team_b: str
    sport: str
    game_date: date
    score_a: int
    score_b: int
    winner: str
    summary: Optional[str]
    
    class Config:
        from_attributes = True

class RivalryMetricsResponse(BaseModel):
    team_a: str
    team_b: str
    sport: str
    total_meetings: int
    wins_a: int
    wins_b: int
    avg_margin: float
    current_streak: Optional[str]
    last_updated: datetime
    
    class Config:
        from_attributes = True

class RivalryDataResponse(BaseModel):
    history: List[RivalryHistoryResponse]
    metrics: Optional[RivalryMetricsResponse]
    has_access: bool

class RivalryInsightResponse(BaseModel):
    insight: str
    momentum_score: float
    trend: str

class AddGameRequest(BaseModel):
    team_a: str
    team_b: str
    sport: str
    game_date: date
    score_a: int
    score_b: int
    game_id: Optional[str] = None
    summary: Optional[str] = None

def check_premium_access(user: User) -> bool:
    """Check if user has premium access (Pro or Oracle Elite)"""
    return user.subscription_tier in [SubscriptionTierEnum.PRO, SubscriptionTierEnum.ORACLE_PLUS]

def normalize_team_names(team_a: str, team_b: str, score_a: int = None, score_b: int = None):
    """Normalize team names to ensure consistent ordering, swapping scores if needed"""
    teams = [(team_a.strip(), score_a), (team_b.strip(), score_b)]
    teams_sorted = sorted(teams, key=lambda x: x[0])
    
    if score_a is not None and score_b is not None:
        return teams_sorted[0][0], teams_sorted[1][0], teams_sorted[0][1], teams_sorted[1][1]
    else:
        return teams_sorted[0][0], teams_sorted[1][0]

def calculate_metrics(db: Session, team_a: str, team_b: str, sport: str) -> RivalryMetrics:
    """Calculate or update rivalry metrics"""
    norm_a, norm_b = normalize_team_names(team_a, team_b)
    
    games = db.query(RivalryHistory).filter(
        and_(
            RivalryHistory.sport == sport,
            or_(
                and_(RivalryHistory.team_a == norm_a, RivalryHistory.team_b == norm_b),
                and_(RivalryHistory.team_a == norm_b, RivalryHistory.team_b == norm_a)
            )
        )
    ).order_by(desc(RivalryHistory.game_date)).all()
    
    if not games:
        return None
    
    total_meetings = len(games)
    wins_a = sum(1 for g in games if g.winner == norm_a)
    wins_b = sum(1 for g in games if g.winner == norm_b)
    
    margins = []
    for game in games:
        if game.team_a == norm_a:
            margins.append(abs(game.score_a - game.score_b))
        else:
            margins.append(abs(game.score_b - game.score_a))
    avg_margin = sum(margins) / len(margins) if margins else 0.0
    
    current_streak = None
    if games:
        streak_team = games[0].winner
        streak_count = 1
        for game in games[1:]:
            if game.winner == streak_team:
                streak_count += 1
            else:
                break
        current_streak = f"{streak_team} {streak_count}"
    
    metrics = db.query(RivalryMetrics).filter(
        and_(
            RivalryMetrics.team_a == norm_a,
            RivalryMetrics.team_b == norm_b,
            RivalryMetrics.sport == sport
        )
    ).first()
    
    if metrics:
        metrics.total_meetings = total_meetings
        metrics.wins_a = wins_a
        metrics.wins_b = wins_b
        metrics.avg_margin = avg_margin
        metrics.current_streak = current_streak
        metrics.last_updated = datetime.utcnow()
    else:
        metrics = RivalryMetrics(
            id=str(uuid.uuid4()),
            team_a=norm_a,
            team_b=norm_b,
            sport=sport,
            total_meetings=total_meetings,
            wins_a=wins_a,
            wins_b=wins_b,
            avg_margin=avg_margin,
            current_streak=current_streak
        )
        db.add(metrics)
    
    db.commit()
    db.refresh(metrics)
    return metrics

@router.get("/history", response_model=RivalryDataResponse)
async def get_rivalry_history(
    team_a: str,
    team_b: str,
    sport: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get rivalry history between two teams"""
    has_access = check_premium_access(current_user)
    
    norm_a, norm_b = normalize_team_names(team_a, team_b)
    
    history = db.query(RivalryHistory).filter(
        and_(
            RivalryHistory.sport == sport,
            or_(
                and_(RivalryHistory.team_a == norm_a, RivalryHistory.team_b == norm_b),
                and_(RivalryHistory.team_a == norm_b, RivalryHistory.team_b == norm_a)
            )
        )
    ).order_by(desc(RivalryHistory.game_date)).limit(limit).all()
    
    metrics = db.query(RivalryMetrics).filter(
        and_(
            RivalryMetrics.team_a == norm_a,
            RivalryMetrics.team_b == norm_b,
            RivalryMetrics.sport == sport
        )
    ).first()
    
    if not metrics and history:
        metrics = calculate_metrics(db, norm_a, norm_b, sport)
    
    return RivalryDataResponse(
        history=history if has_access else [],
        metrics=metrics if has_access else None,
        has_access=has_access
    )

@router.post("/update")
async def add_game_result(
    game_data: AddGameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new game result to rivalry history (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add game results"
        )
    
    norm_a, norm_b, norm_score_a, norm_score_b = normalize_team_names(
        game_data.team_a, game_data.team_b, game_data.score_a, game_data.score_b
    )
    
    winner = norm_a if norm_score_a > norm_score_b else norm_b
    
    existing = db.query(RivalryHistory).filter(
        and_(
            RivalryHistory.team_a == norm_a,
            RivalryHistory.team_b == norm_b,
            RivalryHistory.sport == game_data.sport,
            RivalryHistory.game_date == game_data.game_date
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game result already exists for this date"
        )
    
    history_entry = RivalryHistory(
        id=str(uuid.uuid4()),
        team_a=norm_a,
        team_b=norm_b,
        sport=game_data.sport,
        game_date=game_data.game_date,
        score_a=norm_score_a,
        score_b=norm_score_b,
        winner=winner,
        summary=game_data.summary,
        game_id=game_data.game_id
    )
    
    db.add(history_entry)
    db.commit()
    
    metrics = calculate_metrics(db, norm_a, norm_b, game_data.sport)
    
    return {
        "message": "Game result added successfully",
        "game_id": history_entry.id,
        "metrics_updated": True
    }

@router.get("/insight", response_model=RivalryInsightResponse)
async def get_rivalry_insight(
    team_a: str,
    team_b: str,
    sport: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI insight for a rivalry"""
    has_access = check_premium_access(current_user)
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required for rivalry insights"
        )
    
    norm_a, norm_b = normalize_team_names(team_a, team_b)
    
    recent_games = db.query(RivalryHistory).filter(
        and_(
            RivalryHistory.sport == sport,
            or_(
                and_(RivalryHistory.team_a == norm_a, RivalryHistory.team_b == norm_b),
                and_(RivalryHistory.team_a == norm_b, RivalryHistory.team_b == norm_a)
            )
        )
    ).order_by(desc(RivalryHistory.game_date)).limit(10).all()
    
    if not recent_games:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rivalry history found"
        )
    
    metrics = db.query(RivalryMetrics).filter(
        and_(
            RivalryMetrics.team_a == norm_a,
            RivalryMetrics.team_b == norm_b,
            RivalryMetrics.sport == sport
        )
    ).first()
    
    wins_a = sum(1 for g in recent_games if g.winner == norm_a)
    wins_b = len(recent_games) - wins_a
    
    avg_score_a = sum(g.score_a if g.team_a == norm_a else g.score_b for g in recent_games) / len(recent_games)
    avg_score_b = sum(g.score_b if g.team_b == norm_b else g.score_a for g in recent_games) / len(recent_games)
    
    momentum_score = 0.0
    for i, game in enumerate(recent_games[:5]):
        weight = 1.0 - (i * 0.15)
        if game.winner == norm_a:
            momentum_score += weight
        else:
            momentum_score -= weight
    
    if momentum_score > 1.5:
        trend = f"{norm_a} Dominant"
    elif momentum_score > 0.5:
        trend = f"{norm_a} Momentum"
    elif momentum_score < -1.5:
        trend = f"{norm_b} Dominant"
    elif momentum_score < -0.5:
        trend = f"{norm_b} Momentum"
    else:
        trend = "Evenly Matched"
    
    insight = f"In their last {len(recent_games)} meetings, {norm_a} has won {wins_a} times ({wins_a/len(recent_games)*100:.0f}%) with an average score of {avg_score_a:.1f} points. {norm_b} has won {wins_b} times ({wins_b/len(recent_games)*100:.0f}%) averaging {avg_score_b:.1f} points. "
    
    if metrics and metrics.current_streak:
        insight += f"Current streak: {metrics.current_streak} game(s). "
    
    if abs(avg_score_a - avg_score_b) < 3:
        insight += "These teams are extremely competitive with close scoring margins."
    elif avg_score_a > avg_score_b:
        insight += f"{norm_a} has been the more dominant offensive team in recent matchups."
    else:
        insight += f"{norm_b} has been the more dominant offensive team in recent matchups."
    
    return RivalryInsightResponse(
        insight=insight,
        momentum_score=momentum_score,
        trend=trend
    )
