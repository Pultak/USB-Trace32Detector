from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy.orm import Session
from datetime import date
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates/licenses")

licenses = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@licenses.get("/licenses-web/", response_class=HTMLResponse)
async def read_pcs(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return templates.TemplateResponse("licenses.html", {"request": request, "licenses": licenses})


@licenses.post("/license/", response_model=schemas.License)
def create_license(license: schemas.LicenseCreate, db: Session = Depends(get_db)):
    print(crud.create_license(db=db, name=license.name, expdate=license.expiration_date))


@licenses.get("/licenses/", response_model=List[schemas.License])
def read_licenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return licenses


@licenses.post("/device-license/", response_model=schemas.DeviceLicense)
def create_device_license(device_license: schemas.DeviceLicenseCreate, db: Session = Depends(get_db)):
    print(crud.create_device_license(db=db, device_license=device_license))
