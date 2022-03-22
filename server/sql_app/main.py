from fastapi import FastAPI
import fastapi
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

class Device(BaseModel):
	vendor_id: int
	product_id: int
	serial_number: str

class USBLog(BaseModel):
	username: str
	hostname: str
	timestamp: str
	device: Device
	status:str

@app.post("/api/v1/usb-logs/")
async def root_post(usb_log: USBLog):
	print(usb_log)
	return {"message": "Sucess"}
	
@app.get("/")
async def root_read():
	print("Hello")
	return {"message":"Hello World"}
