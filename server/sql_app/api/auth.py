from fastapi import Depends, APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

# Path to html templates used in this file
templates = Jinja2Templates(directory="templates/auth")

# prefix used for all endpoints in this file
auth = APIRouter(prefix="")



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


@auth.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """
    return html template for login
    """
    return templates.TemplateResponse("login.html", {"request": request})


@auth.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...), Authorize: AuthJWT = Depends()):
    """
    Endpoint called from login template. Checks if given username and password aligns with admin
    username and password and returns token for browser according to given username and password
    """
    user_dict = fake_users_db.get(username)
    if user_dict != None:
        if user_dict["username"] == username and user_dict["password"] == password:
            access_token = Authorize.create_access_token(subject="admin", expires_time=False)
            refresh_token = Authorize.create_refresh_token(subject="admin", expires_time=False)
        else:
            access_token = Authorize.create_access_token(subject="host", expires_time=False)
            refresh_token = Authorize.create_refresh_token(subject="host", expires_time=False)
    else:
        access_token = Authorize.create_access_token(subject="host", expires_time=False)
        refresh_token = Authorize.create_refresh_token(subject="host", expires_time=False)

    # Set the JWT cookies in the response
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return """
    <html>
        <head>
            <title>Login</title>
        </head>
        <body>
            <h1>Logged in</h1>
            <form action="/logs-web" method="get">
                <input type="submit" value="Back" />
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