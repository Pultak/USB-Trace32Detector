from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# prefix used for all endpoints in this file
device = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@device.post("/device", response_model=schemas.Device)
def create_device(device: schemas.DeviceTemp, db: Session = Depends(get_db)):
    """
    Endpoint used for creating new device
    """
    print(crud.create_device(db=db, device=device))


@device.get("/devices", response_model=List[schemas.Device])
def read_devices(skip: int = 0, db: Session = Depends(get_db)):
    """
    Endpoint returns all devices in database
    """
    devices = crud.get_devices(db, skip=skip)
    return devices


@device.get("/device/{device_id}", response_model=schemas.Device)
def read_device(device_id: int, db: Session = Depends(get_db)):
    """
    Returns one specific device by given id
    """
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device
