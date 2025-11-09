from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
import uuid
from sqlalchemy.orm import Session
from app.schemas.auth import UserSignup, UserLogin, Token, UserResponse, UserUpdate
from app.database import get_db, User, SubscriptionTierEnum, BadgeTypeEnum
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_current_user
from app.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])
settings = get_settings()

@router.post("/signup", response_model=Token)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    is_admin = user_data.email == "admin@playoracle.com"
    
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    badges = current_user.badges if isinstance(current_user.badges, list) else []
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier.value,
        sports_dna=current_user.sports_dna or {},
        badges=badges,
        created_at=current_user.created_at
    )

@router.put("/me", response_model=UserResponse)
async def update_me(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.sports_dna:
        current_user.sports_dna = user_update.sports_dna
    
    db.commit()
    db.refresh(current_user)
    
    badges = current_user.badges if isinstance(current_user.badges, list) else []
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_tier=current_user.subscription_tier.value,
        sports_dna=current_user.sports_dna or {},
        badges=badges,
        created_at=current_user.created_at
    )
