from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy.orm import Session
from ...sql_app import crud, models, schemas
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

licenses = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@licenses.post("/license/", response_model=schemas.License)
def create_license(license: schemas.LicenseCreate, db: Session = Depends(get_db)):
    print(crud.create_license(db=db, license=license))


@licenses.get("/licenses/", response_model=List[schemas.License])
def read_licenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return licenses


@licenses.post("/device_license/", response_model=schemas.DeviceLicense)
def create_device_license(device_license: schemas.DeviceLicenseCreate, db: Session = Depends(get_db)):
    print(crud.create_device_license(db=db, device_license=device_license))
