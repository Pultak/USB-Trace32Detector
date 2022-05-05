from datetime import datetime

from fastapi import Depends, APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sql_app.api.auth import fake_users_db
from sql_app import crud, models
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Path to html templates used in this file
templates = Jinja2Templates(directory="templates/devices")

# prefix used for all endpoints in this file
device_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@device_web.get("/devices-web", response_class=HTMLResponse)
async def read_devices(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Returns template with all devices and its current states
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()

    devices = crud.get_devices(db, skip=skip, limit=limit)
    statuses = []
    # adding state for each device in list
    for i in range(0, len(devices)):
        statuses.append(devices[i].logs[len(devices[i].logs) - 1].status)
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    if current_user == "admin":
        return templates.TemplateResponse("devices.html", {"request": request, "devs": len(devices), "devices": devices,
                                                           "statuses": statuses, "licenses": licenses})
    else:
        return templates.TemplateResponse("devices_normal.html", {"request": request, "devs": len(devices), "devices": devices,
                                                           "statuses": statuses, "licenses": licenses})


@device_web.post("/devices-web", response_class=HTMLResponse)
async def filter_devices(request: Request, skip: int = 0, limit: int = 100, lic: str = Form("all"),
                         db: Session = Depends(get_db)):
    """
    Endpoint used for filtering devices by license. returns html template with only
    devices that has assigned license defined by user input
    """
    devices = crud.get_devices(db, skip=skip, limit=limit)
    def_devices = []
    for dev in devices:
        for l in dev.licenses:
            if dev not in def_devices and l.licenses.name == lic:
                def_devices.append(dev)
    # if input was default all
    if lic == "all":
        def_devices = devices
    statuses = []
    for i in range(0, len(def_devices)):
        statuses.append(def_devices[i].logs[len(def_devices[i].logs) - 1].status)
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return templates.TemplateResponse("devices.html",
                                      {"request": request, "devs": len(def_devices), "devices": def_devices,
                                       "statuses": statuses, "licenses": licenses})


@device_web.get("/device-license/{device_id}", response_class=HTMLResponse)
async def connect_dev_lic(request: Request, device_id: int, db: Session = Depends(get_db)):
    """
    Returns template with one device and all available licenses that can be assigned to it.
    """
    device = crud.get_device(db, device_id)
    licenses = crud.get_licenses(db, 0, 100)
    return templates.TemplateResponse("devicelicense.html",
                                      {"request": request, "device": device, "licenses": licenses})


@device_web.post("/devices-web/{device_id}", response_class=HTMLResponse)
async def connect_post(device_id: int, lic: str = Form(...), db: Session = Depends(get_db)):
    """
    Endpoint called from template for connecting device with license. Adds entry to devices_licenses
    table and returns template with all devices in database
    """
    crud.create_device_license(db, device_id, int(lic), datetime.now())
    return RedirectResponse("/devices-web")
