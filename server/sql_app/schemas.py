from typing import List, Optional
from datetime import datetime, date
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
    timestamp: datetime
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
    vendor_id: str
    product_id: str
    serial_number: str


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceCreate):
    id: int
    assigned: bool
    logs: List[USBLog] = []
    licenses: List[DeviceLicense] = []

    class Config:
        orm_mode = True


class LDLogBase(BaseModel):
    timestamp: datetime
    status: str


class LDLogCreate(LDLogBase):
    pass


class LDLog(LDLogCreate):
    id: int
    head_id: int
    body_id: int

    class Config:
        orm_mode = True


class BodyDeviceBase(BaseModel):
    serial_number: str


class BodyDeviceCreate(BodyDeviceBase):
    pass


class BodyDevice(BodyDeviceCreate):
    id: int
    logs: List[LDLog] = []

    class Config:
        orm_mode = True


class HeadDeviceBase(BaseModel):
    serial_number: str


class HeadDeviceCreate(HeadDeviceBase):
    pass


class HeadDevice(HeadDeviceCreate):
    id: int
    logs: List[LDLog] = []

    class Config:
        orm_mode = True


class PCBase(BaseModel):
    username: str
    hostname: str


class PCCreate(PCBase):
    pass


class PC(PCCreate):
    id: int
    assigned: bool
    logs_pc: List[USBLog] = []

    class Config:
        orm_mode = True


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class Team(TeamCreate):
    id: int
    pcs: List[PC] = []

    class Config:
        orm_mode = True


class LicenseBase(BaseModel):
    name: str
    expiration_date: date


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


class LDTempBase(BaseModel):
    username: str
    hostname: str
    timestamp: str
    head_device: HeadDeviceBase
    body_device: BodyDeviceBase
    status: str


class LDTempCreate(LDTempBase):
    pass


class LDTemp(LDTempCreate):
    id: int
    head_id: int
    body_id: int

    class Config:
        orm_mode = True
