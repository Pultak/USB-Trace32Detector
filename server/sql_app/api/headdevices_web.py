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
templates = Jinja2Templates(directory="templates/head_devices")

# prefix used for all endpoints in this file
head_device_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@head_device_web.get("/head-devices-web", response_class=HTMLResponse)
async def read_devices(request: Request, skip: int = 0, db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Returns template with all head devices and necessary attributes
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()

    device_dict = []
    devices = crud.get_head_devices(db, skip=skip)
    for dev in devices:
        ltype = crud.get_lauterbach_type(db, dev.license_type_id)
        device_dict.append({"device": dev, "ltype": ltype, "log": dev.h_logs[len(dev.h_logs) - 1]})
    if current_user == "admin":
        return templates.TemplateResponse("head_devices.html", {"request": request, "devices": device_dict})
    else:
        current_user = "guest"
        return templates.TemplateResponse("head_devices_normal.html", {"request": request, "devices": device_dict})


# @head_device_web.post("/head-devices-web", response_class=HTMLResponse)
# async def filter_devices(request: Request, skip: int = 0,
#                          body_id: str = Form("all"), lic_id: str = Form("all"), team: str = Form("all"),
#                          db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     """
#     Endpoint used for filtering head devices by user given inputs. returns html template with only
#     head devices that has attributes defined by user input
#     """
#     Authorize.jwt_optional()
#     current_user = Authorize.get_jwt_subject()
#     device_dict = []
#     devices_f = crud.get_filtered_headdevices(db, body_id, lic_id, team)
#     ids = []
#     for d in devices_f:
#         ids.append(d[0])
#     devices = crud.get_headdevices_with_ids(db, ids)
#     teams = crud.get_teams(db, skip=skip)
#     for dev in devices:
#         lic = crud.get_license(db, dev.license_id)
#         device_dict.append({"device": dev, "license": lic, "log": dev.h_logs[len(dev.h_logs) - 1]})
#     licenses = crud.get_licenses(db, skip=skip)
#     if body_id == "all":
#         body_id = ""
#     if lic_id == "all":
#         lic_id = ""
#     if team == "all":
#         team = ""
#     if current_user == "admin":
#         return templates.TemplateResponse("head_devices.html", {"request": request, "devices": device_dict,
#                                                                 "devs": devices, "teams": teams, "licenses": licenses,
#                                                                 "user": current_user, "body_val": body_id, "lic_val": lic_id,
#                                                                 "team_val": team})
#     else:
#         current_user = "guest"
#         return templates.TemplateResponse("head_devices_normal.html", {"request": request, "devices": device_dict,
#                                                                        "devs": devices, "teams": teams,
#                                                                        "licenses": licenses,
#                                                                        "user": current_user, "body_val": body_id, "lic_val": lic_id,
#                                                                        "team_val": team})


@head_device_web.get("/head-device-lbtype/{device_id}", response_class=HTMLResponse)
async def connect_dev_lic(request: Request, device_id: int, db: Session = Depends(get_db),
                          Authorize: AuthJWT = Depends()):
    """
    Returns template with one head device and all available licenses that can be assigned to it, plus team and comment
    and inventory number inputs.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    device = crud.get_head_device(db, device_id)
    ltypes = crud.get_lauterbach_types(db)
    teams = crud.get_teams(db, 0)
    return templates.TemplateResponse("head_device_lbtype.html",
                                      {"request": request, "device": device, "ltypes": ltypes, "teams": teams})


@head_device_web.post("/head-devices-web-lbt/{device_id}")
async def connect_post(device_id: int, ltype: str = Form(...), db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template for connecting head device with license and redirects to head-devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_headdevice_lbtype(db, device_id, int(ltype))
    return RedirectResponse(url=f"/head-devices-web", status_code=303)


@head_device_web.post("/head-devices-web-team/{device_id}")
async def delete_post(device_id: int, team_con: str = Form(...), db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template for connecting head device with team and redirects to body-devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_headdevice_team(db, device_id, int(team_con))
    return RedirectResponse(url=f"/head-devices-web", status_code=303)


@head_device_web.post("/head-devices-inv/{device_id}")
async def device_inv(device_id: int, dev_inv: str = Form(...), db: Session = Depends(get_db),
                     Authorize: AuthJWT = Depends()):
    """
    Endpoint called from within from headlicense.html template. Changes head devices inventory number with new one
    given from user
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_headdevice_inv(db, device_id, dev_inv)
    return RedirectResponse(url=f"/head-devices-web", status_code=303)


@head_device_web.post("/head-devices-comm/{device_id}")
async def device_inv(device_id: int, dev_com: str = Form(...), db: Session = Depends(get_db),
                     Authorize: AuthJWT = Depends()):
    """
    Endpoint called from within from headlicense.html template. Changes head devices comment with new one
    given from user
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_headdevice_comm(db, device_id, dev_com)
    return RedirectResponse(url=f"/head-devices-web", status_code=303)