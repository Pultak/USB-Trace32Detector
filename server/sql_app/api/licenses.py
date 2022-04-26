from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from sqlalchemy.orm import Session
from datetime import datetime
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# prefix used for all endpoints in this file
licenses = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@licenses.get("/licenses", response_model=List[schemas.License])
def read_licenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns all licenses currently saved in database.
    """
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return licenses


@licenses.post("/device-license", response_model=schemas.DeviceLicense)
def create_device_license(device_license: schemas.DeviceLicenseCreate, db: Session = Depends(get_db)):
    """
    Creates entry for devices_licenses table thus connecting device with its license.
    """
    print(crud.create_device_license(db=db, device=device_license.device_id, license=device_license.license_id,
                                     time=datetime.now()))
