from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from datetime import datetime
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="../templates/devices")

device_web = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@device_web.get("/devices-web", response_class=HTMLResponse)
async def read_devices(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = crud.get_devices(db, skip=skip, limit=limit)
    return templates.TemplateResponse("devices.html", {"request": request, "devs": devices})


@device_web.post("/devices-web", response_class=HTMLResponse)
async def filter_devices(request: Request, skip: int = 0, limit: int = 100, lic: str = Form("all"),
                         db: Session = Depends(get_db)):
    devices = crud.get_devices(db, skip=skip, limit=limit)
    def_devices = []
    for dev in devices:
        for l in dev.licenses:
            if dev not in def_devices and l.licenses.name == lic:
                def_devices.append(dev)
    if lic == "all":
        def_devices = devices
    return templates.TemplateResponse("devices.html", {"request": request, "devs": def_devices})
