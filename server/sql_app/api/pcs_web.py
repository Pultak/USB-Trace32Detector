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
templates = Jinja2Templates(directory="templates/pcs")

# prefix used for all endpoints in this file
pcs_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pcs_web.get("/pcs-web", response_class=HTMLResponse)
async def read_pcs(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   Authorize: AuthJWT = Depends()):
    """
    Returns template with all pcs currently saved in database
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    pcs = crud.get_pcs(db, skip=skip, limit=limit)
    if current_user == "admin":
        return templates.TemplateResponse("pcs.html", {"request": request, "pcs": pcs, "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("pcs_normal.html", {"request": request, "pcs": pcs, "user": current_user})

