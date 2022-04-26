from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from . import models, schemas


def get_device(db: Session, device_id: int):
    """
    returns one specific devices by given id
    """
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    """
    returns all devices in database
    """
    return db.query(models.Device).offset(skip).limit(limit).all()


def find_device(db: Session, device: schemas.DeviceBase):
    """
    finds one device with product_id, vendor_id and serial_number same as in given DeviceBase object
    """
    return db.query(models.Device).filter(and_(models.Device.product_id == device.product_id,
                                               models.Device.vendor_id == device.vendor_id,
                                               models.Device.serial_number == device.serial_number)).first()


def create_device(db: Session, device: schemas.DeviceBase):
    """
    creates new device with data from given DeviceBase object
    """
    db_device = models.Device(vendor_id=device.vendor_id, product_id=device.product_id,
                              serial_number=device.serial_number, assigned=False)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_license(db: Session, license_id: int):
    """
    returns one specific license by given id
    """
    return db.query(models.License).filter(models.License.id == license_id).first()


def get_licenses(db: Session, skip: int = 0, limit: int = 100):
    """
    returns all licenses in database
    """
    return db.query(models.License).offset(skip).limit(limit).all()


def find_license(db: Session, name: str):
    """
    finds one license by given string name
    """
    return db.query(models.License).filter(models.License.name == name).first()


def create_license(db: Session, name: str, expdate: date):
    """
    creates new license with given name and expiration date
    """
    db_license = models.License(name=name, expiration_date=expdate)
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


def get_license_devices(db: Session, license_id: int):
    """
    returns all entries in devices_licenses table
    """
    return db.query(models.DeviceLicense).filter(models.DeviceLicense.license_id == license_id).all()


def create_device_license(db: Session, device: int, license: int, time: datetime):
    """
    creates new entry in devices_licenses table with device id, license id and time.
    """
    db_device_license = models.DeviceLicense(device_id=device, license_id=license,
                                             assigned_datetime=time)
    db.add(db_device_license)
    db.commit()
    db.refresh(db_device_license)
    return db_device_license


def find_pc_by_username(db: Session, name: str):
    """
    Finds one pc by given username
    """
    return db.query(models.PC).filter(models.PC.username == name).first()


def get_pc(db: Session, pc_id: int):
    """
    returns one specific pc by given id
    """
    return db.query(models.PC).filter(models.PC.id == pc_id).first()


def update_pc(db: Session, pc_id: int, team: str):
    """
    Function updates team of one specific pc
    """
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
    """
    returns all pcs in database
    """
    return db.query(models.PC).offset(skip).limit(limit).all()


def find_pc(db: Session, username: str, hostname: str):
    """
    Finds one pc with given username and hostname
    """
    return db.query(models.PC).filter(and_(models.PC.username == username,
                                           models.PC.hostname == hostname)).first()


def find_pc_by_name(db: Session, username: str):
    """
    Finds one pc by its username
    """
    return db.query(models.PC).filter(models.PC.username == username).first()


def find_pc_by_name_all(db: Session, username: str):
    """
    Finds all pcs with same username
    """
    return db.query(models.PC).filter(models.PC.username == username).offset(0).limit(100).all()


def find_pcs(db: Session, pcs: []):
    """
    Finds all pcs with ids in given id array
    """
    return db.query(models.PC).filter(models.PC.id.in_(pcs)).all()


def get_pcs_by_team(db: Session, team_id: int):
    """
    returns all pcs in given team by team id
    """
    return db.query(models.PC).filter(models.PC.team_id == team_id).all()


def create_pc(db: Session, user: str, host: str):
    """
    creates new pc with given username and hostname
    """
    db_pc = models.PC(username=user, hostname=host, assigned=False)
    db.add(db_pc)
    db.commit()
    db.refresh(db_pc)
    return db_pc


def get_team(db: Session, team_id: int):
    """
    returns one specific team wit given id
    """
    return db.query(models.Team).filter(models.Team.id == team_id).first()


def get_teams(db: Session, skip: int = 0, limit: int = 100):
    """
    returns all teams currently saved in database
    """
    return db.query(models.Team).offset(skip).limit(limit).all()


def find_team(db: Session, name: str):
    """
    Finds one specific team by its name
    """
    return db.query(models.Team).filter(models.Team.name == name).first()


def create_team(db: Session, name: str):
    """
    Creates new team with given name
    """
    db_team = models.Team(name=name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def get_head_device(db: Session, head_id: int):
    """
    Returns one specific head device by given id
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.id == head_id).first()


def get_head_devices(db: Session, skip: int = 0, limit: int = 100):
    """
    Returns all head devices saved in database
    """
    return db.query(models.HeadDevice).offset(skip).limit(limit).all()


def find_head_device(db: Session, serial: schemas.HeadDeviceBase):
    """
    Finds one head device by its serial number
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.serial_number == serial.serial_number).first()


def create_head_device(db: Session, log: schemas.HeadDeviceBase):
    """
    Creates new head device
    """
    db_head = models.HeadDevice(serial_number=log.serial_number)
    db.add(db_head)
    db.commit()
    db.refresh(db_head)
    return db_head


def get_body_device(db: Session, body_id: int):
    """
    Returns one specific body device by given id
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.id == body_id).first()


def get_body_devices(db: Session, skip: int = 0, limit: int = 100):
    """
    Returns all body devices saved in database
    """
    return db.query(models.BodyDevice).offset(skip).limit(limit).all()


def find_body_device(db: Session, serial: schemas.BodyDeviceBase):
    """
    Finds one body device by its serial number
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.serial_number == serial.serial_number).first()


def create_body_device(db: Session, log: schemas.BodyDeviceBase):
    """
    Creates new Body device
    """
    db_body = models.BodyDevice(serial_number=log.serial_number)
    db.add(db_body)
    db.commit()
    db.refresh(db_body)
    return db_body


def get_ld_logs(db: Session, skip: int = 0, limit: int = 100):
    """
    Returns all ld debugger logs in database
    """
    return db.query(models.LDLog).offset(skip).limit(limit).all()


def create_ld_logs(db: Session, item: schemas.LDTempBase, head_id: int, body_id: int, pc_id: int, date: datetime):
    """
    Creates new ld log for ld_logs database table
    """
    db_ld = models.LDLog(pc_id=pc_id, timestamp=date, status=item.status, head_id=head_id, body_id=body_id)
    db.add(db_ld)
    db.commit()
    db.refresh(db_ld)
    return db_ld


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    """
    Returns all usb logs in database ordered by timestamp
    """
    return db.query(models.USBLog).order_by(desc(models.USBLog.timestamp)).offset(skip).limit(limit).all()


def get_log(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    """
    Returns all usb logs in database sorted by id
    """
    return db.query(models.USBLog).filter(models.USBLog.device_id == device_id).offset(skip).limit(limit).all()


def find_filtered_logs(db: Session, logs: []):
    """
    Returns all usb logs with ids in given id array.
    """
    return db.query(models.USBLog).filter(models.USBLog.id.in_(logs)).order_by(desc(models.USBLog.timestamp)).all()


def get_filtered_logs(db: Session, pc: str, tema: str, lic: str):
    """
    Function creates query string used for filtering by pc username, team name and license name.
    Depending on selected filters assembles query string for database
    """
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

    # executing assembled query string
    result = db.execute(execute_string)
    return result


def create_device_logs(db: Session, item: schemas.USBTempBase, dev_id: int, pc_id: int, date: datetime):
    """
    Creates new USB log for usb_logs database table
    """
    db_log = models.USBLog(pc_id=pc_id, timestamp=date, status=item.status, device_id=dev_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
