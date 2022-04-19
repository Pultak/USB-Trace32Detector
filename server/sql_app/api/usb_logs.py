from typing import List
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from datetime import datetime
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates/usb-logs")

usblogs = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@usblogs.get("/logs-web", response_class=HTMLResponse)
async def read_logs(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = crud.get_logs(db, skip=skip, limit=limit)
    pcs = []
    for log in logs:
        if log.pc_id not in pcs:
            pcs.append(log.pc_id)
    pc_obj = crud.find_pcs(db, pcs)
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs, "pcs": pc_obj})


@usblogs.post("/logs-web", response_class=HTMLResponse)
async def filter_logs(request: Request, pc: str = Form(...), skip: int = 0, limit: int = 100,
                      db: Session = Depends(get_db)):
    logs_temp = crud.get_logs(db, skip=skip, limit=limit)
    pcs = []
    logs = []
    for log in logs_temp:
        if log.pc_id not in pcs:
            pcs.append(log.pc_id)
        if pc != "all":
            if log.pc_id == int(pc):
                logs.append(log)
    if pc == "all":
        logs = logs_temp
    pc_obj = crud.find_pcs(db, pcs)
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs, "pcs": pc_obj})


@usblogs.post("/usb-logs", response_model=schemas.USBLog)
def create_device_logs(log: schemas.USBTempBase, db: Session = Depends(get_db)):
    dev = crud.find_device(db, log.device)
    dat = datetime.strptime(log.timestamp, '%Y-%m-%d %H:%M:%S')
    if dev is None:
        dev = crud.create_device(db=db, device=log.device)
    pc = crud.find_pc(db, log.username, log.hostname)
    if pc is None:
        pc = crud.create_pc(db=db, user=log.username, host=log.hostname)

    print(crud.create_device_logs(db=db, item=log, dev_id=dev.id, pc_id=pc.id, date=dat))


@usblogs.get("/logs", response_model=List[schemas.USBLog])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_logs(db, skip=skip, limit=limit)
    return items


@usblogs.get("/logs/{device_id}", response_model=List[schemas.USBLog])
def read_log(device_id: int, db: Session = Depends(get_db)):
    db_log = crud.get_log(db, device_id=device_id)
    if db_log is None:
        raise HTTPException(status_code=404, detail="Logs not found")
    return db_log
