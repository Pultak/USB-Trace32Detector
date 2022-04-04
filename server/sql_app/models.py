from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, index=True, nullable=False)
    product_id = Column(Integer, index=True, nullable=False)
    serial_number = Column(String, index=True, nullable=False)

    logs = relationship("USBLog", back_populates="device")


class USBLog(Base):
    __tablename__ = "usb_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    hostname = Column(String, index=True, nullable=False)
    timestamp = Column(String, index=True, nullable=False)
    status = Column(String, index=True, nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))

    device = relationship("Device", back_populates="logs")
