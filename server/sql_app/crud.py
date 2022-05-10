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
    returns all entries in devices_licenses table with given license_id
    """
    return db.query(models.DeviceLicense).filter(models.DeviceLicense.license_id == license_id).all()


def get_device_licenses(db: Session, device_id: int):
    """
    returns all entries in devices_licenses table with given license_id
    """
    return db.query(models.DeviceLicense).filter(models.DeviceLicense.device_id == device_id).all()


def get_devicelicense_by_devicelicense(db: Session, device_id: int, license_id: int):
    """
    returns entry in devices_licenses table with given device id and license id
    """
    return db.query(models.DeviceLicense).filter(and_(models.DeviceLicense.device_id == device_id,
                                                      models.DeviceLicense.license_id == license_id)).first()


def get_bodydevicelicense_by_bodydevicelicense(db: Session, device_id: int, license_id: int):
    """
    returns entry in bodydevices_licenses table with given body device id and license id
    """
    return db.query(models.BodyDeviceLicense).filter(and_(models.BodyDeviceLicense.bodydevice_id == device_id,
                                                          models.BodyDeviceLicense.license_id == license_id)).first()


def get_license_bodydevice(db: Session, license_id: int):
    """
    returns all entries in bodydevices_licenses with given license_id
    """
    return db.query(models.BodyDeviceLicense).filter(models.BodyDeviceLicense.license_id == license_id).all()


def get_bodydevice_license(db: Session, device_id: int):
    """
    returns all entries in bodydevices_licenses with given license_id
    """
    return db.query(models.BodyDeviceLicense).filter(models.BodyDeviceLicense.bodydevice_id == device_id).all()


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


def delete_device_license(db: Session, device: int, license: int):
    """
    deletes entry in devices_licenses table with device id, license id and time.
    """
    db_device_license = get_devicelicense_by_devicelicense(db, device, license)
    db_lic = db.delete(db_device_license)
    db.commit()
    return db_lic


def delete_bodydevice_license(db: Session, device: int, license: int):
    """
    deletes entry in devices_licenses table with device id, license id and time.
    """
    db_device_license = get_bodydevicelicense_by_bodydevicelicense(db, device, license)
    db_lic = db.delete(db_device_license)
    db.commit()
    return db_lic


def create_body_device_license(db: Session, device: int, license: int, time: datetime):
    """
    creates new entry in devices_licenses table with device id, license id and time.
    """
    db_device_license = models.BodyDeviceLicense(bodydevice_id=device, license_id=license,
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
    Updates team of one specific pc
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

def change_role(db: Session, usr_id: int, role: str):
    """
    Updates team of one specific pc
    """
    old_usr = find_user_byid(db, usr_id)
    new = {'id': old_usr.id, 'username': old_usr.username, 'password': old_usr.password, 'role': role}
    for key, value in new.items():
        setattr(old_usr, key, value)
    db.commit()
    db.refresh(old_usr)
    return old_usr


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
    return db.query(models.LDLog).order_by(desc(models.LDLog.timestamp)).offset(skip).limit(limit).all()


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


def find_filtered_ldlogs(db: Session, logs: []):
    """
    Returns all ld logs with ids in given id array.
    """
    return db.query(models.LDLog).filter(models.LDLog.id.in_(logs)).order_by(desc(models.LDLog.timestamp)).all()


def get_filtered_ldlogs(db: Session, pc: str, tema: str, lic: str):
    """
    Function creates query string used for filtering by pc username, team name and license name.
    Depending on selected filters assembles query string for database
    """
    execute_string = "SELECT * FROM ld_logs AS logs"
    pcs = find_pc_by_username(db, pc)
    if pc != "all":
        if pcs is not None:
            execute_string += "  WHERE logs.pc_id = " + str(pcs.id)
    if tema != "all":
        team = find_team(db, tema)
        if team is not None:
            pcst = get_pcs_by_team(db, team.id)
            pc_ids = "("
            for p in pcst:
                pc_ids += str(p.id) + ", "
            def_pc_ids = pc_ids[:-2] + ")"
            if pc != "all" and pcs is not None:
                if len(def_pc_ids) > 1:
                    execute_string += " AND logs.pc_id IN " + def_pc_ids
            else:
                if len(def_pc_ids) > 1:
                    execute_string += " WHERE logs.pc_id IN " + def_pc_ids
    if lic != "all":
        license = find_license(db, lic)
        if license is not None:
            device_licenses = get_license_bodydevice(db, license.id)
            dev_ids = "("
            for dev in device_licenses:
                dev_ids += str(dev.bodydevice_id) + ", "
            defin_ids = dev_ids[:-2] + ")"
            if pc != "all" or tema != "all":
                if len(defin_ids) > 1:
                    execute_string += " AND logs.body_id IN " + defin_ids
            else:
                if len(defin_ids) > 1:
                    execute_string += " WHERE logs.body_id IN " + defin_ids

    # executing assembled query string
    result = db.execute(execute_string)
    return result


def get_filtered_logs(db: Session, pc: str, tema: str, lic: str):
    """
    Function creates query string used for filtering by pc username, team name and license name.
    Depending on selected filters assembles query string for database
    """
    execute_string = "SELECT * FROM usb_logs AS logs"
    pcs = find_pc_by_username(db, pc)
    if pc != "all":
        if pcs is not None:
            execute_string += "  WHERE logs.pc_id = " + str(pcs.id)
    if tema != "all":
        team = find_team(db, tema)
        if team is not None:
            pcst = get_pcs_by_team(db, team.id)
            pc_ids = "("
            for p in pcst:
                pc_ids += str(p.id) + ", "
            def_pc_ids = pc_ids[:-2] + ")"
            if pc != "all" and pcs is not None:
                if len(def_pc_ids) > 1:
                    execute_string += " AND logs.pc_id IN " + def_pc_ids
            else:
                if len(def_pc_ids) > 1:
                    execute_string += " WHERE logs.pc_id IN " + def_pc_ids
    if lic != "all":
        license = find_license(db, lic)
        if license is not None:
            device_licenses = get_license_devices(db, license.id)
            dev_ids = "("
            for dev in device_licenses:
                dev_ids += str(dev.device_id) + ", "
            defin_ids = dev_ids[:-2] + ")"
            if pc != "all" or tema != "all":
                if len(defin_ids) > 1:
                    execute_string += " AND logs.device_id IN " + defin_ids
            else:
                if len(defin_ids) > 1:
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


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Returns all users saved in database
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def find_user(db: Session, name: str):
    """
    Finds one user by given username
    """
    return db.query(models.User).filter(models.User.username == name).first()


def find_user_byid(db: Session, id: int):
    """
    Finds one user by given id
    """
    return db.query(models.User).filter(models.User.id == id).first()


def create_user(db: Session, name: str, passw: str, rol: str):
    """
    Creates new user
    """
    db_user = models.User(username=name, password=passw, role=rol)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
