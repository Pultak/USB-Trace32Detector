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
templates = Jinja2Templates(directory="templates/users")

# prefix used for all endpoints in this file
users = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@users.get("/users-web", response_class=HTMLResponse)
async def read_usrs(request: Request, skip: int = 0, db: Session = Depends(get_db),
                   Authorize: AuthJWT = Depends()):
    """
    Returns template with all users currently saved in database
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    users = crud.get_users(db, skip)
    if current_user == "admin":
        return templates.TemplateResponse("users.html", {"request": request, "users": users, "user": current_user})
    else:
        return RedirectResponse(url=f"/logs-web", status_code=303)


@users.get("/user-role/{usr_id}", response_class=HTMLResponse)
async def connect_pc_team(usr_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Changes role of user to either guest or admin depending on old role.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    user = crud.find_user_byid(db, usr_id)
    if user.role == "admin":
        crud.change_role(db, usr_id, "guest")
    else:
        crud.change_role(db, usr_id, "admin")
    return RedirectResponse(url=f"/users-web", status_code=303)