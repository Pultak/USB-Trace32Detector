from sqlalchemy.orm import Session

from . import models, schemas


def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()


def find_device(db: Session, device: schemas.DeviceBase):
    return db.query(models.Device).filter(models.Device.product_id == device.product_id and
                                          models.Device.vendor_id == device.vendor_id and
                                          models.Device.serial_number == device.serial_number).first()


def create_device(db: Session, device: schemas.DeviceBase):
    db_device = models.Device(vendor_id=device.vendor_id, product_id=device.product_id,
                              serial_number=device.serial_number)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_license(db: Session, license_id: int):
    return db.query(models.License).filter(models.License.id == license_id).first()


def get_licenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.License).offset(skip).limit(limit).all()


def create_license(db: Session, license: schemas.LicenseBase):
    db_license = models.License(name=license.name, expiration_date=license.expiration_date)
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


def create_device_license(db: Session, device_license: schemas.DeviceLicenseBase):
    db_device_license = models.DeviceLicense(device_id=device_license.device_id, license_id=device_license.license_id,
                                             assigned_datetime=device_license.assigned_datetime)
    db.add(db_device_license)
    db.commit()
    db.refresh(db_device_license)
    return db_device_license


def get_pc(db: Session, pc_id: int):
    return db.query(models.PC).filter(models.PC.id == pc_id).first()


def get_pcs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PC).offset(skip).limit(limit).all()


def find_pc(db: Session, username: str, hostname: str):
    return db.query(models.PC).filter(models.PC.username == username and
                                      models.PC.hostname == hostname).first()


def create_pc(db: Session, user: str, host: str):
    db_pc = models.PC(username=user, hostname=host)
    db.add(db_pc)
    db.commit()
    db.refresh(db_pc)
    return db_pc


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.USBLog).offset(skip).limit(limit).all()


def get_log(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.USBLog).filter(models.USBLog.device_id == device_id).offset(skip).limit(limit).all()


def create_device_logs(db: Session, item: schemas.USBTempBase, dev_id: int, pc_id: int):
    db_log = models.USBLog(pc_id=pc_id, timestamp=item.timestamp, status=item.status, device_id=dev_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
