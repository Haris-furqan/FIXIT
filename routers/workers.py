from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import SessionLocal
from models import JobStatus

router = APIRouter(prefix="/workers", tags=["Workers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/profile", response_model=schemas.WorkerResponse)
def create_worker_profile(profile: schemas.WorkerCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == profile.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_worker = models.Worker(**profile.model_dump())
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return new_worker


@router.patch("/{worker_id}/availability", response_model=schemas.WorkerResponse)
def update_availability(worker_id: int, body: schemas.AvailabilityUpdate, db: Session = Depends(get_db)):
    worker = db.query(models.Worker).filter(models.Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_available = body.is_available
    db.commit()
    db.refresh(worker)
    return worker


@router.get("/nearby-jobs", response_model=List[schemas.JobResponse])
def get_nearby_jobs(db: Session = Depends(get_db)):
    # Placeholder: returns all active jobs.
    # Will be updated in Weeks 7-8 once Person A adds PostGIS + GPS columns.
    active_jobs = db.query(models.Job).filter(models.Job.status == JobStatus.active).all()
    return active_jobs