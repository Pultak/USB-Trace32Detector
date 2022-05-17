from fastapi import Depends, APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from sql_app import crud
from passlib.context import CryptContext
from pydantic import BaseModel
from ..database import SessionLocal, engine

# Path to html templates used in this file
templates = Jinja2Templates(directory="templates/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# prefix used for all endpoints in this file
auth = APIRouter(prefix="")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False


@AuthJWT.load_config
def get_config():
    return Settings()


# admin username and password
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "admin"
    }
}


def verify_password(plain_password, hashed_password):
    """
    Verifies plain text password with hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_hash_password(password):
    """
    Returns hashed password
    """
    return pwd_context.hash(password)


def auth_user(db, username: str, password: str):
    """
    Determines if given password belongs to user with given username
    """
    user = crud.find_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


@auth.get("/signup", response_class=HTMLResponse)
async def signup_get(request: Request):
    """
    return html template for signup
    """
    return templates.TemplateResponse("signup.html", {"request": request})


@auth.post("/signup", response_class=HTMLResponse)
async def signup(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Endpoint called form signup template. Creates new user with role guest that can be changed by admin user
    """
    users = crud.get_users(db, 0, 100)
    users_names = []
    for u in users:
        users_names.append(u.username)
    if username not in users_names:
        new_user = crud.create_user(db, username, get_hash_password(password), "guest")
        if new_user is None:
            print("something went wrong")
        return """
            <html>
                <head>
                    <title>Signup</title>
                </head>
                <body>
                    <h1>New user created. You can go back to previous page.</h1>
                    <form action="/logs-web" method="get">
                        <input type="submit" value="Home Page" />
                    </form>
                </body>
            </html>
            """
    else:
        return """
                    <html>
                        <head>
                            <title>Signup</title>
                        </head>
                        <body>
                            <h1>Username taken. Try to choose different username.</h1>
                            <form action="/logs-web" method="get">
                                <input type="submit" value="Home Page" />
                            </form>
                        </body>
                    </html>
                    """

@auth.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """
    return html template for login
    """
    return templates.TemplateResponse("login.html", {"request": request})


@auth.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db),
                Authorize: AuthJWT = Depends()):
    """
    Endpoint called from login template. Checks if given username and password aligns with admin
    username and password and returns token for browser according to given username and password
    """
    user = auth_user(db, username, password)
    if user != None:
        if user.role == "admin":
            access_token = Authorize.create_access_token(subject="admin", expires_time=False)
            refresh_token = Authorize.create_refresh_token(subject="admin", expires_time=False)
        else:
            access_token = Authorize.create_access_token(subject="guest", expires_time=False)
            refresh_token = Authorize.create_refresh_token(subject="guest", expires_time=False)
    else:
        usr = fake_users_db.get(username)
        if usr != None:
            if usr["username"] == username and usr["password"] == password:
                access_token = Authorize.create_access_token(subject="admin", expires_time=False)
                refresh_token = Authorize.create_refresh_token(subject="admin", expires_time=False)
        else:
            return """
                <html>
                    <head>
                        <title>Login</title>
                    </head>
                    <body>
                        <h1>Wrong Username or Password</h1>
                        <form action="/login" method="get">
                            <input type="submit" value="Log again" />
                        </form>
                        <form action="/login" method="get">
                            <input type="submit" value="Home Page" />
                        </form>
                    </body>
                </html>
                """

    # Set the JWT cookies in the response
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return """
    <html>
        <head>
            <title>Login</title>
        </head>
        <body>
            <h1>Now you are logged in, you can continue to previous page.</h1>
            <form action="/logs-web" method="get">
                <input type="submit" value="Home Page" />
            </form>
        </body>
    </html>
    """


@auth.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
    endpoint for refreshing browser token. Not used at the moment since lifetime of given tokens are
    unlimited.
    """
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    # Set the JWT cookies in the response
    Authorize.set_access_cookies(new_access_token)
    return {"msg": "The token has been refresh"}


@auth.get('/logout', response_class=HTMLResponse)
def logout(Authorize: AuthJWT = Depends()):
    """
    Endpoint for deleting cookie token with acces role.
    """
    Authorize.jwt_optional()

    Authorize.unset_jwt_cookies()
    return """
        <html>
            <head>
                <title>Logout</title>
            </head>
            <body>
                <h1>Logged Out</h1>
                <form action="/logs-web" method="get">
                    <input type="submit" value="Back" />
                </form>
            </body>
        </html>
        """
