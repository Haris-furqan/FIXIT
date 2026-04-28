from pydantic import BaseModel
<<<<<<< HEAD
from datetime import datetime
from decimal import Decimal
from typing import Optional
from models import JobStatus, UserRole


# --- JOB SCHEMAS ---
class JobBase(BaseModel):
    job_title: str
    job_description: str
    x_coords: Decimal
    y_coords: Decimal

class JobCreate(JobBase):
    user_id: int

class JobResponse(JobBase):
    job_id: int
    user_id: int
    status: JobStatus
    created_at: datetime

    class Config:
        from_attributes = True


# --- WORKER SCHEMAS ---
class WorkerBase(BaseModel):
    profession: str

class WorkerCreate(WorkerBase):
    user_id: int

class WorkerResponse(WorkerBase):
    worker_id: int
    user_id: int
    is_available: bool  # Added Week 3-4

    class Config:
        from_attributes = True

class AvailabilityUpdate(BaseModel):  # Added Week 3-4
    is_available: bool
=======
from models import UserRole
from typing import Optional
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    cnic: str
    role: UserRole
    profession: Optional[str] = None
>>>>>>> b562721380bec5e60263a4abfd84ca0d59eae70c
