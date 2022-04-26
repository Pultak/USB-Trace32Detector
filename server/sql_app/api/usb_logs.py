from typing import List
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from datetime import datetime
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# prefix used for all endpoints in this file
usblogs = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@usblogs.post("/usb-logs", response_model=schemas.USBLog)
def create_device_logs(log: schemas.USBTempBase, db: Session = Depends(get_db)):
    """
    Endpoint called from keyman detecting client. Parses timestamp into datetime object.
    Finds if device and pc defined in message already exists and creates them if necessary.
    Saves log into database
    """
    dev = crud.find_device(db, log.device)
    dat = datetime.strptime(log.timestamp, '%Y-%m-%d %H:%M:%S')
    if dev is None:
        dev = crud.create_device(db=db, device=log.device)
    pc = crud.find_pc(db, log.username, log.hostname)
    if pc is None:
        pc = crud.create_pc(db=db, user=log.username, host=log.hostname)

    print(crud.create_device_logs(db=db, item=log, dev_id=dev.id, pc_id=pc.id, date=dat))


@usblogs.post("/ld-logs", response_model=schemas.LDLog)
def create_ld_logs(log: schemas.LDTempBase, db: Session = Depends(get_db)):
    """
    Endpoint called from debugger detecting client. Parses timestamp into datetime object.
    Finds if head device and body device defined in message already exists and creates them if necessary.
    Saves log into database
    """
    head_dev = crud.find_head_device(db, log.head_device)
    body_dev = crud.find_body_device(db, log.body_device)
    if head_dev is None:
        crud.create_head_device(db, log.head_device)
    if body_dev is None:
        crud.create_body_device(db, log.body_device)

    pc = crud.find_pc(db, log.username, log.hostname)
    if pc is None:
        pc = crud.create_pc(db=db, user=log.username, host=log.hostname)
    dat = datetime.strptime(log.timestamp, '%Y-%m-%d %H:%M:%S')
    print(crud.create_ld_logs(db=db, item=log, head_id=head_dev.id, body_id=body_dev.id, pc_id=pc.id, date=dat))


@usblogs.get("/logs", response_model=List[schemas.USBLog])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns all usb logs saved in database
    """
    items = crud.get_logs(db, skip=skip, limit=limit)
    return items


@usblogs.get("/logs/{device_id}", response_model=List[schemas.USBLog])
def read_log(device_id: int, db: Session = Depends(get_db)):
    """
    Returns one specific log by given id
    """
    db_log = crud.get_log(db, device_id=device_id)
    if db_log is None:
        raise HTTPException(status_code=404, detail="Logs not found")
    return db_log
