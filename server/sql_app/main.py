import uvicorn
from sql_app.api.devices import device
from sql_app.api.devices_web import device_web
from sql_app.api.licenses import licenses
from sql_app.api.licenses_web import licenses_web
from sql_app.api.pcs import pcs
from sql_app.api.pcs_web import pcs_web
from sql_app.api.usb_logs import usblogs
from sql_app.api.usb_logs_web import usblogs_web
from sql_app.api.teams import teams
from sql_app.api.teams_web import teams_web
from sql_app.api.auth import auth
from sql_app.api.ld_logs_web import ldlogs_web
from sql_app.api.bodydevices_web import body_device_web
from sql_app.api.headdevices_web import head_device_web
from sql_app.api.users_web import users
from sql_app.api.licenses_names_web import lauterbach_types_web
from fastapi import FastAPI


app = FastAPI()

# including routers for endpoints used by clients
app.include_router(device)
app.include_router(licenses)
app.include_router(pcs)
app.include_router(usblogs)
app.include_router(teams)

# including routers for endpoints called from web
app.include_router(device_web)
app.include_router(licenses_web)
app.include_router(pcs_web)
app.include_router(teams_web)
app.include_router(usblogs_web)
app.include_router(ldlogs_web)
app.include_router(body_device_web)
app.include_router(users)
app.include_router(head_device_web)
app.include_router(auth)
app.include_router(lauterbach_types_web)

'''
if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.22", port=8000)
'''
