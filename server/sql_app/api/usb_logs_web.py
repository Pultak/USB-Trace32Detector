from typing import List
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from datetime import datetime
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

# Path to html templates used in this file
templates = Jinja2Templates(directory="templates/usb-logs")

# prefix used for all endpoints in this file
usblogs_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@usblogs_web.get("/logs-web", response_class=HTMLResponse)
async def read_logs(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    """
    Returns template with all usb logs currently saved in database with its pcs, teams and licenses.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    logs = crud.get_logs(db, skip=skip, limit=limit)
    pcs = []
    for log in logs:
        if log.pc_id not in pcs:
            pcs.append(log.pc_id)
    pc_obj = crud.find_pcs(db, pcs)
    teams = crud.get_teams(db, skip=skip, limit=limit)
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    if current_user == "admin":
        return templates.TemplateResponse("logs.html", {"request": request, "logs": logs, "pcs": pc_obj, "teams": teams,
                                                        "licenses": licenses, "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("logs_normal.html", {"request": request, "logs": logs, "pcs": pc_obj, "teams": teams,
                                                        "licenses": licenses, "user": current_user})


@usblogs_web.post("/logs-web", response_class=HTMLResponse)
async def filter_logs(request: Request, pc: str = Form("all"), team: str = Form("all"), lic: str = Form("all"),
                      skip: int = 0, limit: int = 100,
                      db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Endpoint used for filtering usb logs by user given form inputs.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    log = crud.get_filtered_logs(db, pc, team, lic)
    logs_ids = []
    for l in log:
        logs_ids.append(l[0])
    logs = crud.find_filtered_logs(db, logs_ids)
    pc_obj = crud.get_pcs(db, skip=skip, limit=limit)
    teams = crud.get_teams(db, skip=skip, limit=limit)
    licenses = crud.get_licenses(db, skip=skip, limit=limit)
    if current_user == "admin":
        return templates.TemplateResponse("logs.html", {"request": request, "logs": logs, "pcs": pc_obj, "teams": teams,
                                                        "licenses": licenses, "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("logs_normal.html", {"request": request, "logs": logs, "pcs": pc_obj, "teams": teams,
                                                        "licenses": licenses, "user": current_user})


@usblogs_web.get("/", response_class=HTMLResponse)
async def crossroad(request: Request):
    return templates.TemplateResponse("crossroad.html", {"request": request})
