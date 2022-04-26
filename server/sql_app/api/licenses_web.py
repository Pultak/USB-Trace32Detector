from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from sqlalchemy.orm import Session
from datetime import date
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

# Path to html templates used in this file
templates = Jinja2Templates(directory="../templates/licenses")
device_templates = Jinja2Templates(directory="../templates/devices")

# prefix used for all endpoints in this file
licenses_web = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@licenses_web.get("/license-create", response_class=HTMLResponse)
async def licenses_create_web(request: Request):
    """
    Returns template with Form for creating new license.
    """
    return templates.TemplateResponse("license_create.html", {"request": request})


@licenses_web.get("/licenses-web", response_class=HTMLResponse)
async def read_licenses_web(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns template with all licenses currently saved in database
    """
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return templates.TemplateResponse("licenses.html", {"request": request, "licenses": licenses})


@licenses_web.post("/licenses-web", response_class=HTMLResponse)
def create_license(request: Request, name: str = Form(...), expdate: date = Form(...), skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db)):
    """
    Endpoint called from create license form. Creates new license and returns template with all licenses in database
    """
    db_license = crud.create_license(db, name, expdate)
    if db_license is None:
        print("something went wrong")
    devices = crud.get_devices(db, skip=skip, limit=limit)
    statuses = []
    for i in range(0, len(devices)):
        statuses.append(devices[i].logs[len(devices[i].logs) - 1].status)
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return device_templates.TemplateResponse("devices.html", {"request": request, "devs": len(devices), "devices": devices,
                                                       "statuses": statuses, "licenses": licenses})