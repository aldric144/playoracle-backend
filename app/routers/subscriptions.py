from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict
import stripe
from app.models.database import db, User, SubscriptionTier
from app.utils.auth import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/api/subscription", tags=["subscriptions"])
settings = get_settings()

stripe.api_key = settings.stripe_api_key

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free Scout",
                "price": 0,
                "interval": "month",
                "features": [
                    "1 sport access",
                    "Weekly forecasts",
                    "Basic analytics",
                    "Community leaderboard"
                ]
            },
            {
                "id": "pro",
                "name": "Pro Analyst",
                "price": 14.99,
                "interval": "month",
                "features": [
                    "Multi-sport access",
                    "Daily forecasts",
                    "Advanced analytics",
                    "Custom AI model",
                    "Coach's Corner insights",
                    "Priority support"
                ]
            },
            {
                "id": "oracle_plus",
                "name": "Oracle+ Lifetime",
                "price": 99,
                "interval": "year",
                "features": [
                    "All Pro features",
                    "Historical data archive",
                    "Trend analysis tools",
                    "Export reports (PDF)",
                    "Early access to new features",
                    "Dedicated support"
                ]
            }
        ]
    }

@router.post("/checkout")
async def create_checkout_session(
    plan_id: str,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session"""
    try:
        price_map = {
            "pro": 1499,  # $14.99 in cents
            "oracle_plus": 9900  # $99.00 in cents
        }
        
        if plan_id not in price_map:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": price_map[plan_id],
                        "product_data": {
                            "name": f"PlayOracle {plan_id.replace('_', ' ').title()}",
                        },
                        "recurring": {
                            "interval": "month" if plan_id == "pro" else "year"
                        }
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url="http://localhost:5173/subscription/success",
            cancel_url="http://localhost:5173/subscription/cancel",
            metadata={
                "user_id": current_user.id,
                "plan_id": plan_id
            }
        )
        
        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """Get user's current subscription status"""
    return {
        "user_id": current_user.id,
        "subscription_tier": current_user.subscription_tier.value,
        "stripe_customer_id": current_user.stripe_customer_id,
        "active": True
    }

@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user)
):
    """Cancel user's subscription"""
    if current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")
    
    current_user.subscription_tier = SubscriptionTier.FREE
    current_user.stripe_customer_id = None
    
    return {"message": "Subscription cancelled successfully"}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        plan_id = session["metadata"]["plan_id"]
        
        user = db.get_user_by_id(user_id)
        if user:
            if plan_id == "pro":
                user.subscription_tier = SubscriptionTier.PRO
            elif plan_id == "oracle_plus":
                user.subscription_tier = SubscriptionTier.ORACLE_PLUS
            user.stripe_customer_id = session.get("customer")
    
    return {"status": "success"}
