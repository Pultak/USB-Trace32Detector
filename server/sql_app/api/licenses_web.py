from typing import List
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from sqlalchemy.orm import Session
from datetime import date
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

# Path to html templates used in this file
templates = Jinja2Templates(directory="templates/licenses")
device_templates = Jinja2Templates(directory="templates/devices")

# prefix used for all endpoints in this file
licenses_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@licenses_web.get("/license-create", response_class=HTMLResponse)
async def licenses_create_web(request: Request, Authorize: AuthJWT = Depends()):
    """
    Returns template with Form for creating new license.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    return templates.TemplateResponse("license_create.html", {"request": request, "minimum_date": date.today()})


@licenses_web.get("/licenses-web", response_class=HTMLResponse)
async def read_licenses_web(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    """
    Returns template with all licenses currently saved in database
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    if current_user == "admin":
        return templates.TemplateResponse("licenses.html", {"request": request, "licenses": licenses,
                                                            "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("licenses_normal.html", {"request": request, "licenses": licenses,
                                                            "user": current_user})

@licenses_web.post("/licenses-web")
def create_license(name: Optional[str] = Form(""), lic_id: str = Form(...), expdate: Optional[date] = Form(None),
                   db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Endpoint called from create license form. Creates new license and redirects to devices-web endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    licenses = crud.get_licenses(db, 0, 100)
    licenses_ids = []
    for l in licenses:
        licenses_ids.append(l.license_id)
    if lic_id not in licenses_ids:
        db_license = crud.create_license(db, name, lic_id, expdate)
        if db_license is None:
            print("something went wrong")
    return RedirectResponse(url=f"/licenses-web", status_code=303)
