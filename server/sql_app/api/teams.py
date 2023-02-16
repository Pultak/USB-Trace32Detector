from typing import List

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# prefix used for all endpoints in this file
teams = APIRouter(prefix="/api/v1")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@teams.post("/team", response_model=schemas.Team)
def create_device(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    """
    Endpoint used for creating new pc
    """
    print(crud.create_team(db=db, name=team.name))


@teams.get("/teams", response_model=List[schemas.Device])
def read_devices(skip: int = 0, db: Session = Depends(get_db)):
    """
    Returns all pcs saved in database
    """
    teams = crud.get_teams(db, skip=skip)
    return teams


@teams.get("/team/{team_id}", response_model=schemas.Device)
def read_device(team_id: int, db: Session = Depends(get_db)):
    """
    Returns one specific team by given id
    """
    db_team = crud.get_team(db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_team