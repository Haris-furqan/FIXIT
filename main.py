from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Database and Models
from database import engine, SessionLocal
import models

# Routers (Weeks 3-4 Only)
from auth import router as auth_router
from routers import jobs, workers

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Marketplace API")

# ─────────────────────────────────────────
#  DB DEPENDENCY
# ─────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────
#  ROUTERS
# ─────────────────────────────────────────
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(jobs.router)
app.include_router(workers.router)

# ─────────────────────────────────────────
#  SYSTEM ENDPOINTS
# ─────────────────────────────────────────
@app.get("/", tags=["System"])
def root():
    return {"message": "Service Marketplace API is running"}

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    return {"status": "success", "message": "Database connected successfully"}