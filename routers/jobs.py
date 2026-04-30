from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import SessionLocal
from models import JobStatus
from firebase import verify_firebase_token

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.JobResponse)
def create_job(job: schemas.JobCreate, authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token["uid"]
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_job = models.Job(
        user_id=user.user_id,
        job_title=job.job_title,
        job_description=job.job_description,
        x_coords=job.x_coords,
        y_coords=job.y_coords,
        status=JobStatus.active
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.get("/", response_model=List[schemas.JobResponse])
def get_all_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(models.Job).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_single_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}/cancel", response_model=schemas.JobResponse)
def cancel_job(job_id: int, authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token["uid"]
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="You can only cancel your own jobs")
    if job.status in [JobStatus.completed, JobStatus.cancelled]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a job that is {job.status}")
    job.status = JobStatus.cancelled
    db.commit()
    db.refresh(job)
    return job