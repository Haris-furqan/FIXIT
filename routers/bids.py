from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import json

import models, schemas
from database import SessionLocal
from models import JobStatus, BidStatus
from firebase import verify_firebase_token
from redis_client import get_redis

router = APIRouter(prefix="/bids", tags=["Bids"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{job_id}")
def submit_bid(job_id: int, bid: schemas.BidCreate, authorization: str = Header(...), db: Session = Depends(get_db)):
    # Step 1 - verify token and get user
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token["uid"]
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2 - get worker record
    worker = db.query(models.Worker).filter(models.Worker.user_id == user.user_id).first()
    if not worker:
        raise HTTPException(status_code=403, detail="Only workers can submit bids")

    # Step 3 - check job exists and is active
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.active:
        raise HTTPException(status_code=400, detail="Job is not active")

    # Step 4 - store bid in Redis with 10 minute expiry
    redis = get_redis()
    bid_key = f"bid:{job_id}:{worker.worker_id}"
    bid_data = {
        "worker_id": worker.worker_id,
        "job_id": job_id,
        "bid_amount": str(bid.bid_amount)
    }
    redis.setex(bid_key, 600, json.dumps(bid_data))

    return {"message": "Bid submitted successfully", "expires_in": "10 minutes"}


@router.get("/{job_id}")
def get_bids_for_job(job_id: int, authorization: str = Header(...), db: Session = Depends(get_db)):
    # Step 1 - verify token
    token = authorization.replace("Bearer ", "")
    decoded_token = verify_firebase_token(token)
    firebase_uid = decoded_token["uid"]
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2 - check job belongs to this customer
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="You can only view bids on your own jobs")

    # Step 3 - get all bids from Redis for this job
    redis = get_redis()
    bid_keys = redis.keys(f"bid:{job_id}:*")
    bids = []
    for key in bid_keys:
        bid_data = json.loads(redis.get(key))
        bids.append(bid_data)

    return {"job_id": job_id, "bids": bids}