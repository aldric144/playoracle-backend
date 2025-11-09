from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    subscription_tier: str
    sports_dna: Dict
    badges: List[str]
    created_at: datetime

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    sports_dna: Optional[Dict] = None
