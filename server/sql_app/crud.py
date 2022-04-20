from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from . import models, schemas


def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()


def find_device(db: Session, device: schemas.DeviceBase):
    return db.query(models.Device).filter(and_(models.Device.product_id == device.product_id,
                                               models.Device.vendor_id == device.vendor_id,
                                               models.Device.serial_number == device.serial_number)).first()


def create_device(db: Session, device: schemas.DeviceBase):
    db_device = models.Device(vendor_id=device.vendor_id, product_id=device.product_id,
                              serial_number=device.serial_number, assigned=False)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_license(db: Session, license_id: int):
    return db.query(models.License).filter(models.License.id == license_id).first()


def get_licenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.License).offset(skip).limit(limit).all()


def find_license(db: Session, name: str):
    return db.query(models.License).filter(models.License.name == name).first()


def create_license(db: Session, name: str, expdate: date):
    db_license = models.License(name=name, expiration_date=expdate)
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


def get_license_devices(db: Session, license_id: int):
    return db.query(models.DeviceLicense).filter(models.DeviceLicense.license_id == license_id).all()


def create_device_license(db: Session, device: int, license: int, time: datetime):
    db_device_license = models.DeviceLicense(device_id=device, license_id=license,
                                             assigned_datetime=time)
    db.add(db_device_license)
    db.commit()
    db.refresh(db_device_license)
    return db_device_license


def find_pc_by_username(db: Session, name: str):
    return db.query(models.PC).filter(models.PC.username == name).first()


def get_pc(db: Session, pc_id: int):
    return db.query(models.PC).filter(models.PC.id == pc_id).first()


def update_pc(db: Session, pc_id: int, team: str):
    old_pc = get_pc(db, pc_id)
    team = get_team(db, int(team))
    new = {'id': old_pc.id, 'username': old_pc.username, 'hostname': old_pc.hostname, 'assigned': True,
           'team_id': team.id}
    for key, value in new.items():
        setattr(old_pc, key, value)
    db.commit()
    db.refresh(old_pc)
    return old_pc


def get_pcs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PC).offset(skip).limit(limit).all()


def find_pc(db: Session, username: str, hostname: str):
    return db.query(models.PC).filter(and_(models.PC.username == username,
                                           models.PC.hostname == hostname)).first()


def find_pc_by_name(db: Session, username: str):
    return db.query(models.PC).filter(models.PC.username == username).first()


def find_pc_by_name_all(db: Session, username: str):
    return db.query(models.PC).filter(models.PC.username == username).offset(0).limit(100).all()


def find_pcs(db: Session, pcs: []):
    return db.query(models.PC).filter(models.PC.id.in_(pcs)).all()


def get_pcs_by_team(db: Session, team_id: int):
    return db.query(models.PC).filter(models.PC.team_id == team_id).all()


def create_pc(db: Session, user: str, host: str):
    db_pc = models.PC(username=user, hostname=host, assigned=False)
    db.add(db_pc)
    db.commit()
    db.refresh(db_pc)
    return db_pc


def get_team(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()


def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Team).offset(skip).limit(limit).all()


def find_team(db: Session, name: str):
    return db.query(models.Team).filter(models.Team.name == name).first()


def create_team(db: Session, name: str):
    db_team = models.Team(name=name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.USBLog).order_by(desc(models.USBLog.timestamp)).offset(skip).limit(limit).all()


def get_log(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.USBLog).filter(models.USBLog.device_id == device_id).offset(skip).limit(limit).all()


def find_filtered_logs(db: Session, logs: []):
    return db.query(models.USBLog).filter(models.USBLog.id.in_(logs)).order_by(desc(models.USBLog.timestamp)).all()


def get_filtered_logs(db: Session, pc: str, tema: str, lic: str):
    execute_string = "SELECT * FROM usb_logs AS logs"
    if pc != "all":
        pcs = find_pc_by_username(db, pc)
        execute_string += "  WHERE logs.pc_id = " + str(pcs.id)
    if tema != "all":
        team = find_team(db, tema)
        pcs = get_pcs_by_team(db, team.id)
        pc_ids = "("
        for p in pcs:
            pc_ids += str(p.id) + ", "
        def_pc_ids = pc_ids[:-2] + ")"
        if pc != "all":
            execute_string += " AND logs.pc_id IN " + def_pc_ids
        else:
            execute_string += " WHERE logs.pc_id IN " + def_pc_ids
    if lic != "all":
        license = find_license(db, lic)
        device_licenses = get_license_devices(db, license.id)
        dev_ids = "("
        for dev in device_licenses:
            dev_ids += str(dev.device_id) + ", "
        defin_ids = dev_ids[:-2] + ")"
        if pc != "all" or tema != "all":
            execute_string += " AND logs.device_id IN " + defin_ids
        else:
            execute_string += " WHERE logs.device_id IN " + defin_ids

    result = db.execute(execute_string)
    return result


def create_device_logs(db: Session, item: schemas.USBTempBase, dev_id: int, pc_id: int, date: datetime):
    db_log = models.USBLog(pc_id=pc_id, timestamp=date, status=item.status, device_id=dev_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

