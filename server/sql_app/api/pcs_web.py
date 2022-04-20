from typing import List
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="../templates/pcs")

pcs_web = APIRouter(prefix="/api/v1")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pcs_web.get("/pcs-web", response_class=HTMLResponse)
async def read_pcs(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pcs = crud.get_pcs(db, skip=skip, limit=limit)
    return templates.TemplateResponse("pcs.html", {"request": request, "pcs": pcs})
