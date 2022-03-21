from sqlalchemy.orm import Session

from . import models, schemas


def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()

def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()


def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = models.Device(vendor_id=device.vendor_id, product_id=device.product_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.USBLog).offset(skip).limit(limit).all()

def get_log(db: Session, device_id: int, skip: int=0, limit: int=100):
    return db.query(models.USBLog).filter(models.USBLog.device_id == device_id).offset(skip).limit(limit).all()

def create_device_logs(db: Session, item: schemas.USBLogCreate, dev_id: int):
    db_log = models.USBLog(**item.dict(), device_id=dev_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

