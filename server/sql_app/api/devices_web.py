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
                                                           "statuses": statuses, "licenses": licenses, "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("devices_normal.html", {"request": request, "devs": len(devices), "devices": devices,
                                                                  "statuses": statuses, "licenses": licenses, "user": current_user})


@device_web.post("/devices-web", response_class=HTMLResponse)
async def filter_devices(request: Request, skip: int = 0, limit: int = 100, lic: str = Form("all"),
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Endpoint used for filtering devices by license. returns html template with only
    devices that has assigned license defined by user input
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
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
    if current_user == "admin":
        return templates.TemplateResponse("devices.html",
                                          {"request": request, "devs": len(def_devices), "devices": def_devices,
                                           "statuses": statuses, "licenses": licenses, "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("devices_normal.html",
                                          {"request": request, "devs": len(def_devices), "devices": def_devices,
                                           "statuses": statuses, "licenses": licenses, "user": current_user})


@device_web.get("/device-license/{device_id}", response_class=HTMLResponse)
async def connect_dev_lic(request: Request, device_id: int, db: Session = Depends(get_db),
                          Authorize: AuthJWT = Depends()):
    """
    Returns template with one device and all available licenses that can be assigned to it.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    device = crud.get_device(db, device_id)
    dev_licenses = crud.get_device_licenses(db, device_id)
    lic_names = []
    dev_lics = []
    for dev_lic in dev_licenses:
        dev_lics.append(dev_lic.licenses)
    for dev_lic in dev_licenses:
        lic_names.append(dev_lic.licenses.name)
    licenses = crud.get_licenses(db, 0, 100)
    lic_left = []
    for lic in licenses:
        if lic.name not in lic_names and lic not in lic_left:
            lic_left.append(lic)
    return templates.TemplateResponse("devicelicense.html",
                                      {"request": request, "device": device, "licenses": lic_left, "dev_lic": dev_lics})


@device_web.post("/devices-web/{device_id}")
async def connect_post(device_id: int, lic: str = Form(...), db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template for connecting device with license. Adds entry to devices_licenses
    table and redirects to devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.create_device_license(db, device_id, int(lic), datetime.now())
    return RedirectResponse(url=f"/devices-web", status_code=303)


@device_web.post("/devices-web-del/{device_id}")
async def delete_post(device_id: int, lic_del: str = Form(...), db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template for deleting device-license connection. Adds entry to bodydevices_licenses
    table and redirects to devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.delete_device_license(db, device_id, int(lic_del))
    return RedirectResponse(url=f"/devices-web", status_code=303)
