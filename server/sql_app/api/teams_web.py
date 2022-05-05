from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

# Path to html templates used in this file
templates = Jinja2Templates(directory="templates/teams")

# prefix used for all endpoints in this file
teams_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@teams_web.get("/teams-web", response_class=HTMLResponse)
async def read_devices(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       Authorize: AuthJWT = Depends()):
    """
    Returns template with all teams currently saved in database
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    teams = crud.get_teams(db, skip=skip, limit=limit)
    if current_user == "admin":
        return templates.TemplateResponse("teams.html", {"request": request, "teams": teams})
    else:
        return templates.TemplateResponse("teams_normal.html", {"request": request, "teams": teams})


@teams_web.get("/team-create", response_class=HTMLResponse)
async def team_create_web(request: Request):
    """
    Returns template with form for creating new team
    """
    return templates.TemplateResponse("team_create.html", {"request": request})


@teams_web.post("/teams-web", response_class=HTMLResponse)
def create_team(name: str = Form(...), db: Session = Depends(get_db)):
    """
    Endpoint called from within form for creating new team. Creates new team and returns all teams in database
    """
    team = crud.create_team(db, name)
    if team is None:
        print("something went wrong")
    RedirectResponse("/teams-web")
