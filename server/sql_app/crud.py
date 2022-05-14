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


def find_device(db: Session, device: schemas.DeviceTemp):
    """
    finds one device with  serial_number same as in given DeviceBase object
    """
    return db.query(models.Device).filter(and_(models.Device.serial_number == device.serial_number)).first()


def find_device_by_serial(db: Session, ser: str):
    """
    finds one device with serial_number same as in given DeviceBase object
    """
    return db.query(models.Device).filter(and_(models.Device.serial_number == ser)).first()

def get_devices_with_ids(db: Session, ids: []):
    """
    returns all devices with given ids
    """
    return db.query(models.Device).filter(models.Device.id.in_(ids)).all()

def get_devices_by_team(db: Session, team: int):
    """
    returns all devices with same team
    """
    return db.query(models.Device).filter(models.Device.team_id == team).all()

def create_device(db: Session, device: schemas.DeviceTemp):
    """
    creates new device with data from given DeviceBase object
    """
    db_device = models.Device(vendor_id=device.vendor_id, product_id=device.product_id,
                              serial_number=device.serial_number, inventory_number="", comment="")
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
    return db.query(models.License).filter(models.License.license_id == name).first()


def get_licenses_by_name(db: Session, name: str):
    return db.query(models.License).filter(models.License.name == name).all()


def create_license(db: Session, name: str, lic_id: str, expdate: date):
    """
    creates new license with given name and expiration date
    """
    db_license = models.License(name=name, license_id=lic_id, expiration_date=expdate)
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


def get_license_devices(db: Session, license_id: int):
    """
    returns all entries in devices_licenses table with given license_id
    """
    return db.query(models.DeviceLicense).filter(models.DeviceLicense.license_id == license_id).all()


def find_devicelicenses_by_licid_array(db: Session, lcs: []):
    """
    Finds all device_licenses with license_id in given id array
    """
    return db.query(models.DeviceLicense).filter(models.DeviceLicense.license_id.in_(lcs)).all()


def get_device_licenses(db: Session, device_id: int):
    """
    returns all entries in devices_licenses table with given device_id
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


def update_device(db: Session, device_id: int, team: str):
    """
    Updates team of one specific pc
    """
    old_dev = get_device(db, device_id)
    team = get_team(db, int(team))
    new = {'id': old_dev.id, 'vendor_id': old_dev.vendor_id, 'product_id': old_dev.product_id,
           'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': old_dev.comment, 'team_id': team.id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_device_inv(db: Session, device_id: int, inv: str):
    """
    Updates inventory number of one specific pc
    """
    old_dev = get_device(db, device_id)
    if old_dev.team_id != None:
        team = get_team(db, int(old_dev.team_id))
        teamid = team.id
    else:
        teamid = None
    new = {'id': old_dev.id, 'vendor_id': old_dev.vendor_id, 'product_id': old_dev.product_id,
           'serial_number': old_dev.serial_number, 'inventory_number': inv,
           'comment': old_dev.comment, 'team_id': teamid}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_device_com(db: Session, device_id: int, comm: str):
    """
    Updates team of one specific pc
    """
    old_dev = get_device(db, device_id)
    if old_dev.team_id != None:
        team = get_team(db, int(old_dev.team_id))
        teamid = team.id
    else:
        teamid = None
    new = {'id': old_dev.id, 'vendor_id': old_dev.vendor_id, 'product_id': old_dev.product_id,
           'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': comm, 'team_id': teamid}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


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


def create_pc(db: Session, user: str, host: str):
    """
    creates new pc with given username and hostname
    """
    db_pc = models.PC(username=user, hostname=host)
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


def change_team(db: Session, team_id: int, name: str):
    """
    Updates name of one specific team
    """
    old_team = get_team(db, team_id)
    new = {'id': old_team.id, 'name': name}
    for key, value in new.items():
        setattr(old_team, key, value)
    db.commit()
    db.refresh(old_team)
    return old_team


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


def find_head_device(db: Session, serial: schemas.HeadDeviceTemp):
    """
    Finds one head device by its serial number
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.serial_number == serial.serial_number).first()


def create_head_device(db: Session, log: schemas.HeadDeviceTemp):
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


def find_body_device(db: Session, serial: schemas.BodyDeviceTemp):
    """
    Finds one body device by its serial number
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.serial_number == serial.serial_number).first()


def create_body_device(db: Session, log: schemas.BodyDeviceTemp):
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
            devs = get_devices_by_team(db, team.id)
            d_ids = "("
            for p in devs:
                d_ids += str(p.id) + ", "
            def_d_ids = d_ids[:-2] + ")"
            if pc != "all" and pcs is not None:
                if len(def_d_ids) > 1:
                    execute_string += " AND logs.device_id IN " + def_d_ids
            else:
                if len(def_d_ids) > 1:
                    execute_string += " WHERE logs.device_id IN " + def_d_ids
    if lic != "all":
        license = get_licenses_by_name(db, lic)
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
            devs = get_devices_by_team(db, team.id)
            d_ids = "("
            for p in devs:
                d_ids += str(p.id) + ", "
            def_d_ids = d_ids[:-2] + ")"
            if pc != "all" and pcs is not None:
                if len(def_d_ids) > 1:
                    execute_string += " AND logs.device_id IN " + def_d_ids
            else:
                if len(def_d_ids) > 1:
                    execute_string += " WHERE logs.device_id IN " + def_d_ids
    if lic != "all":
        license = get_licenses_by_name(db, lic)
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


def get_filtered_devices(db: Session, keyman_id: str, license_name: str, license_id: str, team: str):
    """
    returns filtered devices based on given atributes
    """
    execute_string = "SELECT * FROM devices AS device WHERE"
    before_me = False
    all_all = True
    if keyman_id != "all":
        all_all = False
        keyman_dev = find_device_by_serial(db, keyman_id)
        if keyman_dev != None:
            if before_me:
                execute_string += " AND device.id = " + str(keyman_dev.id)
            else:
                before_me = True
                execute_string += " device.id = " + str(keyman_dev.id)
    if license_name != "all":
        all_all = False
        license = get_licenses_by_name(db, license_name)
        if len(license) > 0:
            lic_ids = []
            for l in license:
                lic_ids.append(l.id)
            dev_lics = find_devicelicenses_by_licid_array(db, lic_ids)
            lic_ids = "("
            for l in dev_lics:
                lic_ids += str(l.device_id) + ", "
            def_lic_ids = lic_ids[:-2] + ")"
            if before_me:
                execute_string += " AND device.id IN " + def_lic_ids
            else:
                before_me = True
                execute_string += " device.id IN " + def_lic_ids
    if license_id != "all":
        all_all = False
        license = find_license(db, license_id)
        licen_devs = get_license_devices(db, license.id)
        ids = "("
        for lic in licen_devs:
            ids += str(lic.device_id) + ", "
        def_ids = ids[:-2] + ")"
        if license != None:
            if before_me:
                execute_string += " AND device.id IN " + def_ids
            else:
                before_me = True
                execute_string += " device.id IN " + def_ids
    if team != "all":
        all_all = False
        tem = find_team(db, team)
        if tem != None:
            if before_me:
                execute_string += " AND device.team_id = " + str(tem.id)
            else:
                before_me = True
                execute_string += " device.team_id = " + str(tem.id)
    if all_all:
        before_me = True
        execute_string = "SELECT * FROM devices AS devices"

    if not before_me:
        execute_string = "SELECT * FROM devices AS devices WHERE devices.id = -1"
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
