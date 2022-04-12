from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String, index=True, nullable=False)
    product_id = Column(String, index=True, nullable=False)
    serial_number = Column(String, index=True, nullable=False)
    assigned = Column(Boolean, index=True, nullable=False)

    logs = relationship("USBLog", back_populates="device")
    licenses = relationship("DeviceLicense", back_populates="device_lic")


class USBLog(Base):
    __tablename__ = "usb_logs"

    id = Column(Integer, primary_key=True, index=True)
    pc_id = Column(Integer, ForeignKey("pc.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, index=True, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))

    device = relationship("Device", back_populates="logs")
    pc = relationship("PC", back_populates="logs_pc")


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    expiration_date = Column(DateTime(timezone=True), server_default=func.now())

    devices = relationship("DeviceLicense", back_populates="licenses")


class DeviceLicense(Base):
    __tablename__ = "devices_licenses"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    license_id = Column(Integer, ForeignKey("licenses.id"))
    assigned_datetime = Column(String, index=True, nullable=False)

    device_lic = relationship("Device", back_populates="licenses")
    licenses = relationship("License", back_populates="devices")


class PC(Base):
    __tablename__ = "pc"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    hostname = Column(String, index=True, nullable=False)
    assigned = Column(Boolean, index=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))

    team = relationship("Team", back_populates="pcs")
    logs_pc = relationship("USBLog", back_populates="pc")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    pcs = relationship("PC", back_populates="team")
