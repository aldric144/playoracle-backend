from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
from app.database import get_db, User, PremiumEvent, EventSubscription
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("/list")
async def get_events_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all premium events"""
    events = db.query(PremiumEvent).all()
    
    events_list = []
    for event in events:
        user_subscription = db.query(EventSubscription).filter(
            EventSubscription.user_id == current_user.id,
            EventSubscription.event_slug == event.slug,
            EventSubscription.is_active == True,
            EventSubscription.expiration_date > datetime.utcnow()
        ).first()
        
        has_access = user_subscription is not None or current_user.subscription_tier == "oracle_plus"
        
        events_list.append({
            "id": event.id,
            "name": event.name,
            "slug": event.slug,
            "description": event.description,
            "status": event.status,
            "start_date": event.start_date.isoformat(),
            "end_date": event.end_date.isoformat(),
            "expiration_date": event.expiration_date.isoformat(),
            "has_access": has_access,
            "price_single": 9.99,
            "price_season": 29.99
        })
    
    return {
        "events": events_list,
        "oracle_elite_price": 199.00
    }

@router.get("/verify-access/{event_slug}")
async def verify_event_access(
    event_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify if user has access to a specific event"""
    event = db.query(PremiumEvent).filter(PremiumEvent.slug == event_slug).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if current_user.subscription_tier == "oracle_plus":
        return {
            "has_access": True,
            "access_type": "oracle_elite",
            "event": {
                "name": event.name,
                "slug": event.slug,
                "status": event.status
            }
        }
    
    subscription = db.query(EventSubscription).filter(
        EventSubscription.user_id == current_user.id,
        EventSubscription.event_slug == event_slug,
        EventSubscription.is_active == True,
        EventSubscription.expiration_date > datetime.utcnow()
    ).first()
    
    if subscription:
        return {
            "has_access": True,
            "access_type": subscription.option_type,
            "expiration_date": subscription.expiration_date.isoformat(),
            "event": {
                "name": event.name,
                "slug": event.slug,
                "status": event.status
            }
        }
    
    return {
        "has_access": False,
        "event": {
            "name": event.name,
            "slug": event.slug,
            "status": event.status,
            "price_single": 9.99,
            "price_season": 29.99
        }
    }

@router.get("/my-subscriptions")
async def get_my_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active event subscriptions"""
    subscriptions = db.query(EventSubscription).filter(
        EventSubscription.user_id == current_user.id,
        EventSubscription.is_active == True
    ).all()
    
    subscription_list = []
    for sub in subscriptions:
        event = db.query(PremiumEvent).filter(PremiumEvent.slug == sub.event_slug).first()
        if event:
            subscription_list.append({
                "id": sub.id,
                "event_name": event.name,
                "event_slug": sub.event_slug,
                "option_type": sub.option_type,
                "purchase_date": sub.purchase_date.isoformat(),
                "expiration_date": sub.expiration_date.isoformat(),
                "is_active": sub.is_active and sub.expiration_date > datetime.utcnow(),
                "days_remaining": (sub.expiration_date - datetime.utcnow()).days if sub.expiration_date > datetime.utcnow() else 0
            })
    
    return {
        "subscriptions": subscription_list,
        "oracle_elite_active": current_user.subscription_tier == "oracle_plus"
    }

@router.post("/mock-checkout")
async def mock_checkout(
    event_slug: str,
    option_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock checkout endpoint for testing (no real Stripe integration)"""
    event = db.query(PremiumEvent).filter(PremiumEvent.slug == event_slug).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if option_type not in ["single", "season"]:
        raise HTTPException(status_code=400, detail="Invalid option type")
    
    existing_sub = db.query(EventSubscription).filter(
        EventSubscription.user_id == current_user.id,
        EventSubscription.event_slug == event_slug,
        EventSubscription.is_active == True
    ).first()
    
    if existing_sub:
        raise HTTPException(status_code=400, detail="You already have access to this event")
    
    subscription = EventSubscription(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        event_slug=event_slug,
        option_type=option_type,
        expiration_date=event.expiration_date,
        is_active=True
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return {
        "success": True,
        "message": "Mock checkout successful! (Stripe integration disabled)",
        "subscription": {
            "id": subscription.id,
            "event_slug": subscription.event_slug,
            "option_type": subscription.option_type,
            "expiration_date": subscription.expiration_date.isoformat()
        }
    }
