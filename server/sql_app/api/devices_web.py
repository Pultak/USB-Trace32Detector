from datetime import datetime

from fastapi import Depends, APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sql_app.api.auth import fake_users_db
from sql_app import crud, models, schemas
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
async def read_devices(request: Request, skip: int = 0, db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Returns template with all devices and its necessary attributes
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()

    device_dict = []
    devices = crud.get_devices(db, skip=skip)
    teams = crud.get_teams(db, skip=skip)
    # adding dictionary entry with all inforamtions needed in template
    for dev in devices:
        if len(dev.licenses) > 0:
            for lic in dev.licenses:
                device_dict.append({"device": dev, "license": lic.licenses, "log": dev.logs[len(dev.logs) - 1]})
        else:
            device_dict.append({"device": dev, "license": dev.licenses, "log": dev.logs[len(dev.logs) - 1]})
    licenses = crud.get_licenses(db, skip=skip)
    if current_user == "admin":
        return templates.TemplateResponse("devices.html", {"request": request, "devices": device_dict,
                                                           "licenses": licenses, "devs": devices, "keyman_val": "",
                                                           "licn_val": "", "lici_val": "", "team_val": "",
                                                           "teams": teams, "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("devices_normal.html", {"request": request, "devices": device_dict,
                                                                  "licenses": licenses, "devs": devices, "keyman_val": "",
                                                                  "licn_val": "", "lici_val": "", "team_val": "",
                                                                  "teams": teams, "user": current_user})


@device_web.post("/devices-web", response_class=HTMLResponse)
async def filter_devices(request: Request, skip: int = 0,
                         keyman_id: str = Form("all"), lic_name: str = Form("all"),
                         lic_id: str = Form("all"), team: str = Form("all"),
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Endpoint used for filtering devices by user given inputs. returns html template with only
    devices that has assigned license defined by user input
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    device_dict = []
    devices_f = crud.get_filtered_devices(db, keyman_id, lic_name, lic_id, team)
    ids = []
    for d in devices_f:
        ids.append(d[0])
    devices = crud.get_devices_with_ids(db, ids)
    teams = crud.get_teams(db, skip=skip)
    # adding dictionary entry with all inforamtions needed in template
    for dev in devices:
        if len(dev.licenses) > 0:
            for lic in dev.licenses:
                device_dict.append({"device": dev, "license": lic.licenses, "log": dev.logs[len(dev.logs) - 1]})
        else:
            device_dict.append({"device": dev, "license": dev.licenses, "log": dev.logs[len(dev.logs) - 1]})
    licenses = crud.get_licenses(db, skip=skip)
    if keyman_id == "all":
        keyman_id = ""
    if lic_name == "all":
        lic_name = ""
    if lic_id == "all":
        lic_id = ""
    if team == "all":
        team = ""
    if current_user == "admin":
        return templates.TemplateResponse("devices.html", {"request": request, "devices": device_dict,
                                                           "licenses": licenses, "devs": devices, "keyman_val": keyman_id,
                                                           "licn_val": lic_name, "lici_val": lic_id, "team_val": team,
                                                           "teams": teams, "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("devices_normal.html", {"request": request, "devices": device_dict,
                                                                  "licenses": licenses, "devs": devices, "keyman_val": keyman_id,
                                                                  "licn_val": lic_name, "lici_val": lic_id, "team_val": team,
                                                                  "teams": teams, "user": current_user})


@device_web.get("/device-license/{device_id}", response_class=HTMLResponse)
async def connect_dev_lic(request: Request, device_id: int, db: Session = Depends(get_db),
                          Authorize: AuthJWT = Depends()):
    """
    Returns template with one device and all available licenses that can be assigned to it. Plus all teams that can
    be assigned to device, inventory number text input and comment text input
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    device = crud.get_device(db, device_id)
    dev_licenses = crud.get_device_licenses(db, device_id)
    lic_ids = []
    dev_lics = []
    for dev_lic in dev_licenses:
        dev_lics.append(dev_lic.licenses)
    for dev_lic in dev_licenses:
        lic_ids.append(dev_lic.licenses.license_id)
    licenses = crud.get_licenses(db, 0)
    lic_left = []
    for lic in licenses:
        if lic.license_id not in lic_ids and lic not in lic_left:
            lic_left.append(lic)
    teams = crud.get_teams(db, 0)
    return templates.TemplateResponse("devicelicense.html",
                                      {"request": request, "device": device, "licenses": lic_left, "dev_lic": dev_lics,
                                       "teams": teams})


@device_web.post("/devices-web/{device_id}")
async def connect_post(device_id: int, lic: str = Form(...), db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Endpoint called from devicelicense.html template. Adds entry to devices_licenses
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
    Endpoint called from devicelicense.html template for deleting device-license connection. Deletes entry in
    bodydevices_licenses table and redirects to devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.delete_device_license(db, device_id, int(lic_del))
    return RedirectResponse(url=f"/devices-web", status_code=303)


@device_web.post("/devices-web-team/{device_id}")
async def dev_team_con(device_id: int, team_con: str = Form(...), db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Endpoint called from devicelicense.html template, connects device with team and redirects to devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_device(db, device_id, team_con)
    return RedirectResponse(url=f"/devices-web", status_code=303)


@device_web.post("/devices-web-inv/{device_id}")
async def dev_inv_new(device_id: int, dev_inv: str = Form(...), db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template devicelicense.html, updates inventory number of device and redirects to devices-web
    endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_device_inv(db, device_id, dev_inv)
    return RedirectResponse(url=f"/devices-web", status_code=303)


@device_web.post("/devices-web-comment/{device_id}")
async def dev_comm_new(device_id: int, dev_com: str = Form(...), db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Endpoint called from template devicelicense.html, updates comment of device and redirects to devices-web
    endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    crud.update_device_com(db, device_id, dev_com)
    return RedirectResponse(url=f"/devices-web", status_code=303)
