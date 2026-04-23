from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, SessionLocal

import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Marketplace API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "FastAPI server is up and running!"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "success", "message": "Database connected successfully!"}