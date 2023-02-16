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
templates = Jinja2Templates(directory="templates/body-devices")

# prefix used for all endpoints in this file
body_device_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@body_device_web.get("/body-devices-web", response_class=HTMLResponse)
async def read_devices(request: Request, skip: int = 0, db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Returns template with all body devices and necessary attributes
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()

    device_dict = []
    devices = crud.get_body_devices(db, skip=skip)
    teams = crud.get_teams(db, skip=skip)
    for dev in devices:
        lic = crud.get_license(db, dev.license_id)
        device_dict.append({"device": dev, "license": lic, "log": dev.b_logs[len(dev.b_logs) - 1]})
    licenses = crud.get_licenses(db, skip=skip)
    if current_user == "admin":
        return templates.TemplateResponse("body_devices.html", {"request": request, "devices": device_dict,
                                                                "devs": devices, "teams": teams, "licenses": licenses,
                                                                "user": current_user, "body_val": "", "lic_val": "",
                                                                "team_val": ""})
    else:
        current_user = "guest"
        return templates.TemplateResponse("body_devices_normal.html", {"request": request, "devices": device_dict,
                                                                "devs": devices, "teams": teams, "licenses": licenses,
                                                                "user": current_user, "body_val": "", "lic_val": "",
                                                                "team_val": ""})


@body_device_web.post("/body-devices-web", response_class=HTMLResponse)
async def filter_devices(request: Request, skip: int = 0,
                         body_id: str = Form("all"), lic_id: str = Form("all"), team: str = Form("all"),
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Endpoint used for filtering body devices by user given inputs. returns html template with only
    body devices that has attributes defined by user input
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    device_dict = []
    devices_f = crud.get_filtered_bodydevices(db, body_id, lic_id, team)
    ids = []
    for d in devices_f:
        ids.append(d[0])
    devices = crud.get_bodydevices_with_ids(db, ids)
    teams = crud.get_teams(db, skip=skip)
    for dev in devices:
        lic = crud.get_license(db, dev.license_id)
        device_dict.append({"device": dev, "license": lic, "log": dev.b_logs[len(dev.b_logs) - 1]})
    licenses = crud.get_licenses(db, skip=skip)
    if body_id == "all":
        body_id = ""
    if lic_id == "all":
        lic_id = ""
    if team == "all":
        team = ""
    if current_user == "admin":
        return templates.TemplateResponse("body_devices.html", {"request": request, "devices": device_dict,
                                                                "devs": devices, "teams": teams, "licenses": licenses,
                                                                "user": current_user, "body_val": body_id, "lic_val": lic_id,
                                                                "team_val": team})
    else:
        current_user = "guest"
        return templates.TemplateResponse("body_devices_normal.html", {"request": request, "devices": device_dict,
                                                                       "devs": devices, "teams": teams,
                                                                       "licenses": licenses,
                                                                       "user": current_user, "body_val": body_id, "lic_val": lic_id,
                                                                       "team_val": team})


@body_device_web.get("/body-device-license/{device_id}", response_class=HTMLResponse)
async def connect_dev_lic(request: Request, device_id: int, db: Session = Depends(get_db),
                          Authorize: AuthJWT = Depends()):
    """
    Returns template with one body device and all available licenses that can be assigned to it. Plus available teams
    that can be assigned to device, inventory number and comment text input for this device.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    device = crud.get_body_device(db, device_id)
    licenses = crud.get_licenses(db, 0)
    lic_left = []
    for lic in licenses:
        if lic != device.license:
            lic_left.append(lic)
    teams = crud.get_teams(db, 0)
    return templates.TemplateResponse("body_device_license.html",
                                      {"request": request, "device": device, "licenses": lic_left, "teams": teams})


@body_device_web.post("/body-devices-web-lic/{device_id}")
async def connect_post(device_id: int, lic: str = Form(...), db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template from body_device_license.html template. Connects body device with license
    and redirects to body-devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_bodydevice_license(db, device_id, int(lic))
    return RedirectResponse(url=f"/body-devices-web", status_code=303)


@body_device_web.post("/body-devices-web-team/{device_id}")
async def delete_post(device_id: int, team_con: str = Form(...), db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template from body_device_license.html template, connects device with new team
    and redirects to body-devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_bodydevice_team(db, device_id, int(team_con))
    return RedirectResponse(url=f"/body-devices-web", status_code=303)


@body_device_web.post("/body-devices-inv/{device_id}")
async def device_inv(device_id: int, dev_inv: str = Form(...), db: Session = Depends(get_db),
                     Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template from body_device_license.html template, updates devices inventory number
    and redirects to body-devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_bodydevice_inv(db, device_id, dev_inv)
    return RedirectResponse(url=f"/body-devices-web", status_code=303)


@body_device_web.post("/body-devices-comm/{device_id}")
async def device_inv(device_id: int, dev_com: str = Form(...), db: Session = Depends(get_db),
                     Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template from body_device_license.html template, updates devices comment
    and redirects to body-devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_bodydevice_comm(db, device_id, dev_com)
    return RedirectResponse(url=f"/body-devices-web", status_code=303)
