from typing import List, Optional

from pydantic import BaseModel


class USBLogBase(BaseModel):
    username: str
    hostname: str
    timestamp: str
    status: str


class USBLogCreate(USBLogBase):
    pass


class USBLog(USBLogBase):
    id: int
    device_id: int

    class Config:
        orm_mode = True
        
class DeviceBase(BaseModel):
    vendor_id: int
    product_id: int


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int
    logs: List[USBLog] = []
    class Config:
        orm_mode = True

