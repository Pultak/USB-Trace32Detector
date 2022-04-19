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
templates = Jinja2Templates(directory="templates/licenses")

licenses = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@licenses.get("/license-create", response_class=HTMLResponse)
async def licenses_create_web(request: Request):
    return templates.TemplateResponse("license_create.html", {"request": request})


@licenses.get("/licenses-web", response_class=HTMLResponse)
async def licenses_web(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return templates.TemplateResponse("licenses.html", {"request": request, "licenses": licenses})


@licenses.post("/licenses-web", response_class=HTMLResponse)
def create_license(request: Request, name: str = Form(...), expdate: date = Form(...), skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db)):
    db_license = crud.create_license(db, name, expdate)
    if db_license is None:
        print("something went wrong")
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return templates.TemplateResponse("licenses.html", {"request": request, "licenses": licenses})


@licenses.get("/licenses", response_model=List[schemas.License])
def read_licenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    return licenses


@licenses.post("/device-license", response_model=schemas.DeviceLicense)
def create_device_license(device_license: schemas.DeviceLicenseCreate, db: Session = Depends(get_db)):
    print(crud.create_device_license(db=db, device_license=device_license))
