from datetime import datetime

from fastapi import Depends, APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sql_app import crud, models
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Path to html templates used in this file
templates = Jinja2Templates(directory="templates/devices")

# prefix used for all endpoints in this file
device_web = APIRouter(prefix="")



class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False


@AuthJWT.load_config
def get_config():
    return Settings()


fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "admin"
    },
    "editor": {
        "username": "editor",
        "password": "editor"
    },
}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@device_web.get("/token", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@device_web.post("/token", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...), Authorize: AuthJWT = Depends()):
    user_dict = fake_users_db.get(username)

    access_token = Authorize.create_access_token(subject=username, expires_time=False)
    refresh_token = Authorize.create_refresh_token(subject=username, expires_time=False)

    # Set the JWT cookies in the response
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
            <form action="/devices-web" method="get">
                <input type="submit" value="Login" />
            </form>
        </body>
    </html>
    """


@device_web.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    # Set the JWT cookies in the response
    Authorize.set_access_cookies(new_access_token)
    return {"msg": "The token has been refresh"}


@device_web.get('/logout', response_class=HTMLResponse)
def logout(Authorize: AuthJWT = Depends()):
    """
    Because the JWT are stored in an httponly cookie now, we cannot
    log the user out by simply deleting the cookies in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    Authorize.jwt_required()

    Authorize.unset_jwt_cookies()
    return """
        <html>
            <head>
                <title>Some HTML in here</title>
            </head>
            <body>
                <h1>Look ma! HTML!</h1>
                <form action="/devices-web" method="get">
                    <input type="submit" value="Login" />
                </form>
            </body>
        </html>
        """


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
    return templates.TemplateResponse("devices.html", {"request": request, "devs": len(devices), "devices": devices,
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
async def connect_post(request: Request, device_id: int, lic: str = Form(...), skip: int = 0, limit: int = 100,
                       db: Session = Depends(get_db)):
    """
    Endpoint called from template for connecting device with license. Adds entry to devices_licenses
    table and returns template with all devices in database
    """
    crud.create_device_license(db, device_id, int(lic), datetime.now())
    devices = crud.get_devices(db, skip=skip, limit=limit)
    statuses = []
    # adding state for each device in list
    for i in range(0, len(devices)):
        statuses.append(devices[i].logs[len(devices[i].logs) - 1].status)
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return templates.TemplateResponse("devices.html", {"request": request, "devs": len(devices), "devices": devices,
                                                       "statuses": statuses, "licenses": licenses})
