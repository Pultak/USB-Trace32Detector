from typing import List
from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy.orm import Session
from ...sql_app import crud, models, schemas
from ..database import SessionLocal, engine
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="../templates/pcs")

pcs = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pcs.get("/pcs-web/", response_class=HTMLResponse)
async def read_pcs(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pcs = crud.get_pcs(db, skip=skip, limit=limit)
    return templates.TemplateResponse("pcs.html", {"request": request, "pcs": pcs})


@pcs.post("/pc/", response_model=schemas.PC)
def create_pc(pc: schemas.PCCreate, db: Session = Depends(get_db)):
    print(crud.create_pc(db=db, user=pc.username, host=pc.hostname))


@pcs.get("/pcs/", response_model=List[schemas.PC])
def read_pcs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pcs = crud.get_pcs(db, skip=skip, limit=limit)
    return pcs


@pcs.get("/pc/{pc_id}", response_model=schemas.PC)
def read_pc(pc_id: int, db: Session = Depends(get_db)):
    db_pc = crud.get_pc(db, pc_id=pc_id)
    if db_pc is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_pc
