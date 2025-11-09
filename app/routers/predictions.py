from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.schemas.predictions import (
    PredictionCreate, PredictionResponse, AIPredictionResponse,
    UserAccuracyResponse
)
from app.database import get_db, User, Prediction, AIPrediction, Game
from app.utils.auth import get_current_user
from app.ml.prediction_engine import prediction_engine

router = APIRouter(prefix="/api/predictions", tags=["predictions"])

@router.post("/user", response_model=PredictionResponse)
async def create_user_prediction(
    prediction_data: PredictionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a user prediction"""
    prediction = Prediction(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        game_id=prediction_data.game_id,
        sport=prediction_data.sport,
        predicted_winner=prediction_data.predicted_winner,
        confidence=prediction_data.confidence
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return PredictionResponse(
        id=prediction.id,
        user_id=prediction.user_id,
        game_id=prediction.game_id,
        sport=prediction.sport,
        predicted_winner=prediction.predicted_winner,
        confidence=prediction.confidence,
        created_at=prediction.created_at,
        actual_winner=prediction.actual_winner,
        was_correct=prediction.was_correct
    )

@router.get("/user/history", response_model=List[PredictionResponse])
async def get_user_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's prediction history"""
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()
    return [
        PredictionResponse(
            id=p.id,
            user_id=p.user_id,
            game_id=p.game_id,
            sport=p.sport,
            predicted_winner=p.predicted_winner,
            confidence=p.confidence,
            created_at=p.created_at,
            actual_winner=p.actual_winner,
            was_correct=p.was_correct
        )
        for p in predictions
    ]

@router.get("/user/accuracy", response_model=UserAccuracyResponse)
async def get_user_accuracy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's prediction accuracy stats"""
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()
    
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
    
    return UserAccuracyResponse(
        total_predictions=total,
        correct_predictions=correct,
        accuracy_percentage=round(accuracy, 2),
        by_sport=by_sport
    )

@router.get("/game/{game_id}", response_model=AIPredictionResponse)
async def get_ai_prediction_for_game(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI prediction for a specific game"""
    existing = db.query(AIPrediction).filter(AIPrediction.game_id == game_id).first()
    if existing:
        return AIPredictionResponse(
            game_id=existing.game_id,
            predicted_winner=existing.predicted_winner,
            confidence=existing.confidence,
            dci_score=existing.dci_score,
            analysis=existing.analysis,
            factors=existing.factors,
            created_at=existing.created_at
        )
    
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    prediction_data = prediction_engine.predict_game(
        game_id=game_id,
        home_team=game.home_team,
        away_team=game.away_team,
        sport=game.sport
    )
    
    ai_prediction = AIPrediction(
        game_id=prediction_data["game_id"],
        predicted_winner=prediction_data["predicted_winner"],
        confidence=prediction_data["confidence"],
        dci_score=prediction_data["dci_score"],
        analysis=prediction_data["analysis"],
        factors=prediction_data["factors"]
    )
    db.add(ai_prediction)
    db.commit()
    db.refresh(ai_prediction)
    
    return AIPredictionResponse(
        game_id=ai_prediction.game_id,
        predicted_winner=ai_prediction.predicted_winner,
        confidence=ai_prediction.confidence,
        dci_score=ai_prediction.dci_score,
        analysis=ai_prediction.analysis,
        factors=ai_prediction.factors,
        created_at=ai_prediction.created_at
    )

@router.get("/user/insights")
async def get_user_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized insights based on user's prediction history"""
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).all()
    
    history = [
        {
            "predicted_winner": p.predicted_winner,
            "was_correct": p.was_correct,
            "confidence": p.confidence
        }
        for p in predictions
    ]
    
    insights = prediction_engine.personalize_prediction(history)
    return insights
