import uvicorn
from sql_app.api.devices import device
from sql_app.api.licenses import licenses
from sql_app.api.pcs import pcs
from sql_app.api.usb_logs import usblogs
from sql_app.api.teams import teams
from fastapi import FastAPI


app = FastAPI(root_path="/api/v1")
app.include_router(device)
app.include_router(licenses)
app.include_router(pcs)
app.include_router(usblogs)
app.include_router(teams)

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.22", port=8000)

