from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import SessionLocal
from models import JobStatus
from firebase import verify_firebase_token

router = APIRouter(prefix="/workers", tags=["Workers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/profile", response_model=schemas.WorkerResponse)
def create_worker_profile(profile: schemas.WorkerCreate, authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token["uid"]
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_worker = models.Worker(
        user_id=user.user_id,
        profession=profile.profession
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return new_worker


@router.patch("/{worker_id}/availability", response_model=schemas.WorkerResponse)
def update_availability(worker_id: int, body: schemas.AvailabilityUpdate, authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token["uid"]
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
    worker = db.query(models.Worker).filter(models.Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    if worker.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="You can only update your own availability")
    worker.is_available = body.is_available
    db.commit()
    db.refresh(worker)
    return worker


@router.get("/nearby-jobs", response_model=List[schemas.JobResponse])
def get_nearby_jobs(db: Session = Depends(get_db)):
    active_jobs = db.query(models.Job).filter(models.Job.status == JobStatus.active).all()
    return active_jobs