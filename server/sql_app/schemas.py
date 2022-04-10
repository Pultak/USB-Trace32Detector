from typing import List, Optional

from pydantic import BaseModel



class DeviceLicenseBase(BaseModel):
    device_id: int
    license_id: int
    assigned_datetime: str


class DeviceLicenseCreate(DeviceLicenseBase):
    pass


class DeviceLicense(DeviceLicenseCreate):
    id: int

    class Config:
        orm_mode = True


class USBLogBase(BaseModel):
    timestamp: str
    status: str


class USBLogCreate(USBLogBase):
    pass


class USBLog(USBLogBase):
    id: int
    device_id: int
    pc_id: int

    class Config:
        orm_mode = True


class DeviceBase(BaseModel):
    vendor_id: int
    product_id: int
    serial_number: str


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int
    logs: List[USBLog] = []
    licenses: List[DeviceLicense] = []

    class Config:
        orm_mode = True


class PCBase(BaseModel):
    username: str
    hostname: str


class PCCreate(PCBase):
    pass


class PC(PCCreate):
    id: int
    logs_pc: List[USBLog] = []

    class Config:
        orm_mode = True


class LicenseBase(BaseModel):
    name: str
    expiration_date: str


class LicenseCreate(LicenseBase):
    pass


class License(LicenseCreate):
    id: int
    devices: List[DeviceLicense] = []

    class Config:
        orm_mode = True


class USBTempBase(BaseModel):
    username: str
    hostname: str
    timestamp: str
    device: DeviceBase
    status: str


class USBTempCreate(USBTempBase):
    pass


class USBTemp(USBTempBase):
    id: int
    device_id: int

    class Config:
        orm_mode = True
