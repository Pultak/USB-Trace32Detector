from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Device(Base):
    """
    Class defining database table devices
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String, index=True, nullable=False)
    product_id = Column(String, index=True, nullable=False)
    serial_number = Column(String, index=True, nullable=False)
    assigned = Column(Boolean, index=True, nullable=False)

    # relationships for foreign keys, thus connecting table with usb_logs and licenses
    # tables
    logs = relationship("USBLog", back_populates="device")
    licenses = relationship("DeviceLicense", back_populates="device_lic")


class USBLog(Base):
    """
    Class defining database table usb_logs
    """
    __tablename__ = "usb_logs"

    id = Column(Integer, primary_key=True, index=True)
    pc_id = Column(Integer, ForeignKey("pc.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, index=True, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))

    # relationships for foreign keys, thus connecting table with devices and pc
    # tables
    device = relationship("Device", back_populates="logs")
    pc = relationship("PC", back_populates="logs_pc")


class License(Base):
    """
    Class defining database table licenses
    """
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    expiration_date = Column(DateTime(timezone=True), server_default=func.now())

    # relationships for foreign keys, thus connecting table with devices table
    devices = relationship("DeviceLicense", back_populates="licenses")


class DeviceLicense(Base):
    """
    Class defining database table devices_licenses
    """
    __tablename__ = "devices_licenses"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    license_id = Column(Integer, ForeignKey("licenses.id"))
    assigned_datetime = Column(String, index=True, nullable=False)

    # relationships for foreign keys, thus connecting table with devices and licenses
    # tables
    device_lic = relationship("Device", back_populates="licenses")
    licenses = relationship("License", back_populates="devices")


class PC(Base):
    """
    Class defining database table pc
    """
    __tablename__ = "pc"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    hostname = Column(String, index=True, nullable=False)
    assigned = Column(Boolean, index=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))

    # relationships for foreign keys, thus connecting table with teams, usb_logs and ld_logs
    # tables
    team = relationship("Team", back_populates="pcs")
    logs_pc = relationship("USBLog", back_populates="pc")
    ld_pc = relationship("LDLog", back_populates="ldpc")


class Team(Base):
    """
    Class defining database table teams
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)

    # relationships for foreign keys, thus connecting table with pc table
    pcs = relationship("PC", back_populates="team")


class HeadDevice(Base):
    """
    Class defining database table head_devices
    """
    __tablename__ = "head_devices"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, index=True, nullable=False)

    # relationships for foreign keys, thus connecting table with ld_logs table
    h_logs = relationship("LDLog", back_populates="head_device")


class BodyDevice(Base):
    """
    Class defining database table body_devices
    """
    __tablename__ = "body_devices"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, index=True, nullable=False)

    # relationships for foreign keys, thus connecting table with ld_logs table
    b_logs = relationship("LDLog", back_populates="body_device")


class LDLog(Base):
    """
    Class defining database table ld_logs
    """
    __tablename__ = "ld_logs"

    id = Column(Integer, primary_key=True, index=True)
    pc_id = Column(Integer, ForeignKey("pc.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, index=True, nullable=False)
    head_id = Column(Integer, ForeignKey("head_devices.id"))
    body_id = Column(Integer, ForeignKey("body_devices.id"))

    # relationships for foreign keys, thus connecting table with pc, head_devices and body_devices
    # tables
    ldpc = relationship("PC", back_populates="ld_pc")
    head_device = relationship("HeadDevice", back_populates="h_logs")
    body_device = relationship("BodyDevice", back_populates="b_logs")
