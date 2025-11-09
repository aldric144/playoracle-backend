from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid
from app.database import get_db, User, PremiumEvent, EventSubscription, EventStatusEnum
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/admin/events", tags=["admin-events"])

class EventCreate(BaseModel):
    name: str
    slug: str
    description: str
    status: str
    start_date: datetime
    end_date: datetime
    expiration_date: datetime
    stripe_price_id_single: Optional[str] = None
    stripe_price_id_season: Optional[str] = None

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    stripe_price_id_single: Optional[str] = None
    stripe_price_id_season: Optional[str] = None

def verify_admin(current_user: User):
    """Verify user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

@router.get("/events")
async def admin_list_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: List all premium events"""
    verify_admin(current_user)
    
    events = db.query(PremiumEvent).all()
    
    events_list = []
    for event in events:
        subscription_count = db.query(EventSubscription).filter(
            EventSubscription.event_slug == event.slug,
            EventSubscription.is_active == True
        ).count()
        
        events_list.append({
            "id": event.id,
            "name": event.name,
            "slug": event.slug,
            "description": event.description,
            "status": event.status,
            "start_date": event.start_date.isoformat(),
            "end_date": event.end_date.isoformat(),
            "expiration_date": event.expiration_date.isoformat(),
            "stripe_price_id_single": event.stripe_price_id_single,
            "stripe_price_id_season": event.stripe_price_id_season,
            "subscription_count": subscription_count,
            "created_at": event.created_at.isoformat(),
            "updated_at": event.updated_at.isoformat()
        })
    
    return {"events": events_list}

@router.post("/events")
async def admin_create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Create new premium event"""
    verify_admin(current_user)
    
    existing = db.query(PremiumEvent).filter(PremiumEvent.slug == event_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Event with this slug already exists")
    
    event = PremiumEvent(
        id=str(uuid.uuid4()),
        name=event_data.name,
        slug=event_data.slug,
        description=event_data.description,
        status=event_data.status,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        expiration_date=event_data.expiration_date,
        stripe_price_id_single=event_data.stripe_price_id_single,
        stripe_price_id_season=event_data.stripe_price_id_season
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return {
        "success": True,
        "event": {
            "id": event.id,
            "name": event.name,
            "slug": event.slug,
            "status": event.status
        }
    }

@router.put("/events/{event_id}")
async def admin_update_event(
    event_id: str,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Update premium event"""
    verify_admin(current_user)
    
    event = db.query(PremiumEvent).filter(PremiumEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event_data.name is not None:
        event.name = event_data.name
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.status is not None:
        event.status = event_data.status
    if event_data.start_date is not None:
        event.start_date = event_data.start_date
    if event_data.end_date is not None:
        event.end_date = event_data.end_date
    if event_data.expiration_date is not None:
        event.expiration_date = event_data.expiration_date
    if event_data.stripe_price_id_single is not None:
        event.stripe_price_id_single = event_data.stripe_price_id_single
    if event_data.stripe_price_id_season is not None:
        event.stripe_price_id_season = event_data.stripe_price_id_season
    
    event.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(event)
    
    return {
        "success": True,
        "event": {
            "id": event.id,
            "name": event.name,
            "slug": event.slug,
            "status": event.status
        }
    }

@router.delete("/events/{event_id}")
async def admin_delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Delete premium event"""
    verify_admin(current_user)
    
    event = db.query(PremiumEvent).filter(PremiumEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"success": True, "message": f"Event {event.name} deleted"}

@router.get("/subscriptions")
async def admin_list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: List all event subscriptions"""
    verify_admin(current_user)
    
    subscriptions = db.query(EventSubscription).all()
    
    subscription_list = []
    for sub in subscriptions:
        user = db.query(User).filter(User.id == sub.user_id).first()
        event = db.query(PremiumEvent).filter(PremiumEvent.slug == sub.event_slug).first()
        
        subscription_list.append({
            "id": sub.id,
            "user_email": user.email if user else "Unknown",
            "user_name": user.full_name if user else "Unknown",
            "event_name": event.name if event else sub.event_slug,
            "event_slug": sub.event_slug,
            "option_type": sub.option_type,
            "purchase_date": sub.purchase_date.isoformat(),
            "expiration_date": sub.expiration_date.isoformat(),
            "is_active": sub.is_active,
            "is_expired": sub.expiration_date < datetime.utcnow()
        })
    
    return {"subscriptions": subscription_list}

@router.post("/subscriptions/grant")
async def admin_grant_access(
    user_email: str,
    event_slug: str,
    option_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Manually grant event access to user"""
    verify_admin(current_user)
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    event = db.query(PremiumEvent).filter(PremiumEvent.slug == event_slug).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    existing_sub = db.query(EventSubscription).filter(
        EventSubscription.user_id == user.id,
        EventSubscription.event_slug == event_slug,
        EventSubscription.is_active == True
    ).first()
    
    if existing_sub:
        raise HTTPException(status_code=400, detail="User already has access to this event")
    
    subscription = EventSubscription(
        id=str(uuid.uuid4()),
        user_id=user.id,
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
        "message": f"Access granted to {user.email} for {event.name}",
        "subscription": {
            "id": subscription.id,
            "event_slug": subscription.event_slug,
            "expiration_date": subscription.expiration_date.isoformat()
        }
    }

@router.delete("/subscriptions/{subscription_id}")
async def admin_revoke_access(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Revoke event access"""
    verify_admin(current_user)
    
    subscription = db.query(EventSubscription).filter(EventSubscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = False
    db.commit()
    
    return {"success": True, "message": "Access revoked"}
