from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserRegister
from firebase import verify_firebase_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user_data: UserRegister, authorization: str = Header(...), db: Session = Depends(get_db)):
    
    # Step 1 - verify the firebase token from the header
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    
    # Step 2 - extract phone number and firebase_uid from token
    firebase_uid = decoded_token["uid"]
    phone_number = decoded_token["phone_number"]
    
    # Step 3 - check if user already exists
    existing_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if existing_user:
        return {"message": "User already exists", "user_id": existing_user.user_id}
    
    # Step 4 - create new user
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        cnic=user_data.cnic,
        role=user_data.role,
        firebase_uid=firebase_uid,
        phone_number=phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.user_id}

@router.post("/login")
def login(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token["uid"]
    existing_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not existing_user:
        return {"message":"User does not exist.Register First"}
    else:
        return {
            "user_id": existing_user.user_id,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "phone_number": existing_user.phone_number,
            "role": existing_user.role
            }