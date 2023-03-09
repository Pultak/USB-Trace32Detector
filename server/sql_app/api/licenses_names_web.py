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
templates = Jinja2Templates(directory="templates/lauterbach_type")

# prefix used for all endpoints in this file
lauterbach_types_web = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lauterbach_types_web.get("/lauterbach-types-create", response_class=HTMLResponse)
async def licenses_create_web(request: Request, Authorize: AuthJWT = Depends()):
    """
    Returns template with Form for creating new lauterbach name.
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    return templates.TemplateResponse("lauterbach_type_create.html", {"request": request})


@lauterbach_types_web.get("/lauterbach-types-web", response_class=HTMLResponse)
async def read_licenses_web(request: Request, skip: int = 0, db: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    """
    Returns template with all lauterbach names currently saved in database
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    ltypes = crud.get_lauterbach_types(db)
    if current_user == "admin":
        return templates.TemplateResponse("lauterbach_type.html", {"request": request, "lauterbachs": ltypes,
                                                                   "user": current_user})
    else:
        current_user = "guest"
        return templates.TemplateResponse("lauterbach_type_normal.html", {"request": request, "lauterbachs": ltypes,
                                                                          "user": current_user})


@lauterbach_types_web.post("/lauterbach-types-web")
def create_license(name: Optional[str] = Form(""), db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    Endpoint called from create lauterbach name form. Creates new lauterbach name and redirects to lauterbach names endpoint
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/logs-web", status_code=303)
    l_types = crud.get_lauterbach_types(db)
    l_types_values = []
    for l in l_types:
        l_types_values.append(l.name)
    if name not in l_types_values:
        db_lname = crud.create_lauterbach_type(db, name)
        if db_lname is None:
            print("something went wrong")
    return RedirectResponse(url=f"/lauterbach-types-web", status_code=303)


@lauterbach_types_web.get("/lauterbach-web-change/{lauterbach_id}", response_class=HTMLResponse)
def change_license(request: Request, lauterbach_id: int, db: Session = Depends(get_db),
                   Authorize: AuthJWT = Depends()):
    """
    Returns template with form to change a lauterbach
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/lauterbach-types-web", status_code=303)
    lbach = crud.get_lauterbach_type(db, lauterbach_id)
    return templates.TemplateResponse("lauterbach_type_change.html", {"request": request, "lauterbach": lbach})


@lauterbach_types_web.post("/lauterbach-web-change-process/{lauterbach_id}")
def change_license(lauterbach_id: int, name: Optional[str] = Form(""), db: Session = Depends(get_db),
                   Authorize: AuthJWT = Depends()):
    """
    Changes a lauterbach_name
    """
    Authorize.jwt_optional()
    current_user = Authorize.get_jwt_subject()
    if current_user != "admin":
        return RedirectResponse(url=f"/lauterbach-types-web", status_code=303)

    l_names = crud.get_lauterbach_types(db)
    l_names_values = []
    for l in l_names:
        l_names_values.append(l.name)
    if name not in l_names_values:
        ln = crud.change_lauterbach_type(db, lauterbach_id, name)

    return RedirectResponse(url=f"/lauterbach-types-web", status_code=303)
