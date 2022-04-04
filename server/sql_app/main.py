from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
import uvicorn
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/device/", response_model=schemas.Device)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    print(crud.create_device(db=db, device=device))


@app.get("/devices/", response_model=List[schemas.Device])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = crud.get_devices(db, skip=skip, limit=limit)
    return devices


@app.get("/device/{device_id}", response_model=schemas.Device)
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


@app.post("/usb-logs/", response_model=schemas.USBLog)
def create_device_logs(log: schemas.USBTempBase, db: Session = Depends(get_db)):
    dev = crud.find_device(db, log.device)
    if dev is None:
        dev = crud.create_device(db=db, device=log.device)

    print(crud.create_device_logs(db=db, item=log, dev_id=dev.id))


@app.get("/logs/", response_model=List[schemas.USBLog])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_logs(db, skip=skip, limit=limit)
    return items


@app.get("/logs/{device_id}", response_model=List[schemas.USBLog])
def read_log(device_id: int, db: Session = Depends(get_db)):
    db_log = crud.get_log(db, device_id=device_id)
    if db_log is None:
        raise HTTPException(status_code=404, detail="Logs not found")
    return db_log


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.22", port=8000)
