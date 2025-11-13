import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

sys.path.insert(0, os.path.dirname(__file__))

from app.database import User, Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_users():
    import uuid
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        dr_aldric = db.query(User).filter(User.email == "dr.aldric@playoracle.com").first()
        if dr_aldric:
            print("Dr. Aldric Marshall admin user already exists, updating password...")
            dr_aldric.hashed_password = hash_password("DrAldric123!")
            dr_aldric.full_name = "Dr. Aldric Marshall"
            dr_aldric.is_admin = True
            dr_aldric.subscription_tier = "pro"
        else:
            print("Creating Dr. Aldric Marshall admin user...")
            dr_aldric = User(
                id=str(uuid.uuid4()),
                email="dr.aldric@playoracle.com",
                hashed_password=hash_password("DrAldric123!"),
                full_name="Dr. Aldric Marshall",
                is_admin=True,
                subscription_tier="pro"
            )
            db.add(dr_aldric)
        
        admin = db.query(User).filter(User.email == "admin@playoracle.com").first()
        if admin:
            print("Admin user already exists, updating password...")
            admin.hashed_password = hash_password("Admin123!")
        else:
            print("Creating admin user...")
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@playoracle.com",
                hashed_password=hash_password("Admin123!"),
                full_name="Admin User",
                is_admin=True,
                subscription_tier="pro"
            )
            db.add(admin)
        
        test = db.query(User).filter(User.email == "test@playoracle.com").first()
        if test:
            print("Test user already exists, updating password...")
            test.hashed_password = hash_password("Test123!")
        else:
            print("Creating test user...")
            test = User(
                id=str(uuid.uuid4()),
                email="test@playoracle.com",
                hashed_password=hash_password("Test123!"),
                full_name="Test User",
                is_admin=False,
                subscription_tier="free"
            )
            db.add(test)
        
        db.commit()
        print("\n✅ Users created/updated successfully!")
        print("\nCredentials:")
        print("Dr. Aldric Marshall: dr.aldric@playoracle.com / DrAldric123!")
        print("Admin: admin@playoracle.com / Admin123!")
        print("Test: test@playoracle.com / Test123!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_users()
