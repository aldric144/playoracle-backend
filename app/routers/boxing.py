"""
Boxing Intelligence API Router
Endpoints for boxing events, fighters, and DCI scoring
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.database import get_db, Fighter, SportsEvent, FightHistory
from app.services.sports_intel import SportsIntelAggregator
from app.routers.auth import get_current_user
from app.database import User

router = APIRouter(prefix="/api/boxing", tags=["boxing"])

@router.get("/upcoming")
async def get_upcoming_boxing_events(
    db: Session = Depends(get_db)
):
    """Get upcoming boxing events"""
    aggregator = SportsIntelAggregator(db)
    events = await aggregator.fetch_upcoming_boxing(use_cache=True)
    
    return {
        "events": events,
        "count": len(events),
        "sources_used": ["thesportsdb"] if events else [],
        "premium_data_available": False
    }

@router.get("/fighter/{fighter_id}")
async def get_fighter_details(
    fighter_id: str,
    db: Session = Depends(get_db)
):
    """Get fighter details by ID"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    
    fight_history = db.query(FightHistory).filter(
        FightHistory.fighter_id == fighter_id
    ).order_by(FightHistory.fight_date.desc()).limit(5).all()
    
    return {
        "fighter": {
            "id": fighter.id,
            "name": fighter.name,
            "age": fighter.age,
            "stance": fighter.stance,
            "nationality": fighter.nationality,
            "weight_class": fighter.weight_class,
            "reach_cm": fighter.reach_cm,
            "height_cm": fighter.height_cm,
            "record": {
                "wins": fighter.record_wins,
                "losses": fighter.record_losses,
                "draws": fighter.record_draws
            },
            "stats": {
                "ko_pct": fighter.ko_pct,
                "ko_wins": fighter.ko_wins,
                "ko_losses": fighter.ko_losses,
                "power_idx": fighter.power_idx,
                "speed_idx": fighter.speed_idx,
                "stamina_idx": fighter.stamina_idx,
                "defense_idx": fighter.defense_idx,
                "win_streak": fighter.win_streak
            }
        },
        "last_5_fights": [
            {
                "opponent": fight.opponent_name,
                "result": fight.result,
                "method": fight.method,
                "date": fight.fight_date.isoformat() if fight.fight_date else None,
                "rounds": fight.rounds
            }
            for fight in fight_history
        ]
    }

@router.get("/dci/{fight_id}")
async def get_boxing_dci(
    fight_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DCI (Dynamic Confidence Index) for a boxing match
    Requires authentication
    """
    aggregator = SportsIntelAggregator(db)
    dci_result = await aggregator.compute_boxing_dci(fight_id)
    
    if not dci_result:
        raise HTTPException(status_code=404, detail="Fight not found or DCI computation failed")
    
    is_premium = current_user.subscription_tier in ["pro", "oracle_plus"]
    
    if not is_premium:
        return {
            "fight_id": fight_id,
            "dci_preview": {
                "fighter_one_score": dci_result["fighter_one"]["dci"]["dci_score"],
                "fighter_two_score": dci_result["fighter_two"]["dci"]["dci_score"],
                "classification": dci_result["prediction"]
            },
            "premium_required": True,
            "message": "Upgrade to Pro or Oracle Elite for full DCI analysis"
        }
    
    return dci_result

@router.get("/history/{fighter_id}")
async def get_fighter_history(
    fighter_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get fighter's fight history with DCI evolution
    Requires Pro or Oracle Elite subscription
    """
    if current_user.subscription_tier not in ["pro", "oracle_plus"]:
        raise HTTPException(
            status_code=403,
            detail="This feature requires Pro or Oracle Elite subscription"
        )
    
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    
    fight_history = db.query(FightHistory).filter(
        FightHistory.fighter_id == fighter_id
    ).order_by(FightHistory.fight_date.desc()).limit(limit).all()
    
    return {
        "fighter": {
            "id": fighter.id,
            "name": fighter.name,
            "current_record": {
                "wins": fighter.record_wins,
                "losses": fighter.record_losses,
                "draws": fighter.record_draws
            }
        },
        "fight_history": [
            {
                "id": fight.id,
                "opponent": fight.opponent_name,
                "result": fight.result,
                "method": fight.method,
                "date": fight.fight_date.isoformat() if fight.fight_date else None,
                "rounds": fight.rounds,
                "judges": fight.judges
            }
            for fight in fight_history
        ],
        "dci_evolution": {
            "current_power_idx": fighter.power_idx,
            "current_speed_idx": fighter.speed_idx,
            "current_stamina_idx": fighter.stamina_idx,
            "current_defense_idx": fighter.defense_idx,
            "win_streak": fighter.win_streak
        }
    }

@router.post("/fighter")
async def create_fighter(
    fighter_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new fighter profile (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    fighter = Fighter(
        id=str(uuid.uuid4()),
        name=fighter_data.get("name"),
        age=fighter_data.get("age"),
        stance=fighter_data.get("stance"),
        nationality=fighter_data.get("nationality"),
        weight_class=fighter_data.get("weight_class"),
        reach_cm=fighter_data.get("reach_cm"),
        height_cm=fighter_data.get("height_cm"),
        record_wins=fighter_data.get("record_wins", 0),
        record_losses=fighter_data.get("record_losses", 0),
        record_draws=fighter_data.get("record_draws", 0),
        ko_pct=fighter_data.get("ko_pct"),
        ko_wins=fighter_data.get("ko_wins", 0),
        ko_losses=fighter_data.get("ko_losses", 0),
        power_idx=fighter_data.get("power_idx"),
        speed_idx=fighter_data.get("speed_idx"),
        stamina_idx=fighter_data.get("stamina_idx"),
        defense_idx=fighter_data.get("defense_idx"),
        win_streak=fighter_data.get("win_streak", 0)
    )
    
    db.add(fighter)
    db.commit()
    db.refresh(fighter)
    
    return {
        "message": "Fighter created successfully",
        "fighter_id": fighter.id
    }
