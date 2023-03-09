from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from . import models, schemas


def get_device(db: Session, device_id: int):
    """
    returns one specific devices by given id
    """
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_devices(db: Session, skip: int = 0):
    """
    returns all devices in database
    """
    return db.query(models.Device).offset(skip).all()


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


def get_bodydevices_with_ids(db: Session, ids: []):
    """
    returns all bodydevices with given ids
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.id.in_(ids)).all()


def get_headdevices_with_ids(db: Session, ids: []):
    """
    returns all headdevices with given ids
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.id.in_(ids)).all()


def find_headdevices_by_team(db: Session, team_id: int):
    """
    Returns all head devices in specific team
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.team_id == team_id).all()


def find_bodydevices_by_team(db: Session, team_id: int):
    """
    Returns all body devices in specific team
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.team_id == team_id).all()


def find_headdevices_by_license(db: Session, lic_id: int):
    """
    Returns all head devices with specific license
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.license_id == lic_id).all()


def find_bodydevices_by_license(db: Session, lic_id: int):
    """
    Returns all body devices with specific license
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.license_id == lic_id).all()


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


def get_licenses(db: Session, skip: int = 0):
    """
    returns all licenses in database
    """
    return db.query(models.License).offset(skip).all()


def find_license(db: Session, name: str):
    """
    finds one license by given string name
    """
    return db.query(models.License).filter(name == models.License.license_id).first()


def find_licenses_by_license_id(db: Session, license_id: str):
    """
    finds all licenses with license_id substring in license_id column
    """
    return db.query(models.License).filter(models.License.license_id.contains(license_id)).all()


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


def create_lauterbach_type(db: Session, name: str):
    """
    creates new lauterbach name with given name
    """
    db_l_name = models.LauterbachType(name=name)
    db.add(db_l_name)
    db.commit()
    db.refresh(db_l_name)
    return db_l_name


def get_lauterbach_types(db: Session):
    return db.query(models.LauterbachType).all()


def get_lauterbach_type(db: Session, lauterbach_type_id: int):
    return db.query(models.LauterbachType).filter(models.LauterbachType.id == lauterbach_type_id).first()


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


def get_pcs(db: Session, skip: int = 0):
    """
    returns all pcs in database
    """
    return db.query(models.PC).offset(skip).all()


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
    return db.query(models.PC).filter(models.PC.username == username).offset(0).all()


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


def get_teams(db: Session, skip: int = 0):
    """
    returns all teams currently saved in database
    """
    return db.query(models.Team).offset(skip).all()


def find_team(db: Session, name: str):
    """
    Finds one specific team by its name
    """
    return db.query(models.Team).filter(models.Team.name == name).first()


def find_teams_with_substring(db: Session, name: str):
    """
    Finds one specific team by its name
    """
    return db.query(models.Team).filter(models.Team.name.contains(name)).all()


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


def change_license(db: Session, license_id: int, name: str, lic_id: str, expdate: date):
    """
    Updates license information of license given by license_id
    """
    old_license = get_license(db, license_id)
    new = {'id': old_license.id, 'name': name, 'license_id': lic_id, 'expiration_date': expdate}
    for key, value in new.items():
        setattr(old_license, key, value)
    db.commit()
    db.refresh(old_license)
    return old_license


def change_lauterbach_type(db: Session, lauterbach_name_id: int, name: str):
    """
    Updates lauterbach name information of lauterbach name given by lauterbach_name_id
    """
    old_lname = get_lauterbach_type(db, lauterbach_name_id)
    new = {'id': old_lname.id, 'name': name}
    for key, value in new.items():
        setattr(old_lname, key, value)
    db.commit()
    db.refresh(old_lname)
    return old_lname


def get_head_device(db: Session, head_id: int):
    """
    Returns one specific head device by given id
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.id == head_id).first()


def get_head_devices(db: Session, skip: int = 0):
    """
    Returns all head devices saved in database
    """
    return db.query(models.HeadDevice).offset(skip).all()


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


def get_body_devices(db: Session, skip: int = 0):
    """
    Returns all body devices saved in database
    """
    return db.query(models.BodyDevice).offset(skip).all()


def find_body_device(db: Session, serial: schemas.BodyDeviceTemp):
    """
    Finds one body device by its serial number
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.serial_number == serial.serial_number).first()


def find_bodydevice_by_serial(db: Session, serial: str):
    """
    Finds one specific body device by given serial number
    """
    return db.query(models.BodyDevice).filter(models.BodyDevice.serial_number == serial).first()


def find_headdevice_by_serial(db: Session, serial: str):
    """
    Finds one specific head device by given serial number
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.serial_number == serial).first()


def find_headdevices_by_serial(db: Session, serial: str):
    """
    Finds head devices by given serial number as substring
    """
    return db.query(models.HeadDevice).filter(models.HeadDevice.serial_number.contains(serial)).all()


def create_body_device(db: Session, log: schemas.BodyDeviceTemp):
    """
    Creates new Body device
    """
    db_body = models.BodyDevice(serial_number=log.serial_number, inventory_number="", comment="")
    db.add(db_body)
    db.commit()
    db.refresh(db_body)
    return db_body


def update_bodydevice_license(db: Session, device_id: int, lic_id: int):
    """
    Updates body devices license with one given by user
    """
    old_dev = get_body_device(db, device_id)
    lic = get_license(db, lic_id)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': old_dev.comment, 'team_id': old_dev.team_id, 'license_id': lic.id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_bodydevice_team(db: Session, device_id: int, team_id: int):
    """
    Updates body devices team with one given by user
    """
    old_dev = get_body_device(db, device_id)
    team = get_team(db, team_id)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': old_dev.comment, 'team_id': team.id, 'license_id': old_dev.license_id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_bodydevice_inv(db: Session, device_id: int, dev_inv: str):
    """
    Updates body devices inventory number with new one given by user
    """
    old_dev = get_body_device(db, device_id)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': dev_inv,
           'comment': old_dev.comment, 'team_id': old_dev.team_id, 'license_id': old_dev.license_id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_bodydevice_comm(db: Session, device_id: int, comm: str):
    """
    Updates body devices comment with new one given by user
    """
    old_dev = get_body_device(db, device_id)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': comm, 'team_id': old_dev.team_id, 'license_id': old_dev.license_id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_headdevice_license(db: Session, device_id: int, l_type: int):
    """
    Updates head devices license with one given by user
    """
    old_dev = get_head_device(db, device_id)
    lbtype = get_lauterbach_type(db, l_type)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': old_dev.comment, 'team_id': old_dev.team_id, 'license_type_id': lbtype.id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_headdevice_team(db: Session, device_id: int, team_id: int):
    """
    Updates head devices team with one given by user
    """
    old_dev = get_head_device(db, device_id)
    team = get_team(db, team_id)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': old_dev.comment, 'team_id': team.id, 'license_type_id': old_dev.license_type_id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_headdevice_inv(db: Session, device_id: int, dev_inv: str):
    """
    Updates head devices inventory number with new one given by user
    """
    old_dev = get_head_device(db, device_id)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': dev_inv,
           'comment': old_dev.comment, 'team_id': old_dev.team_id, 'license_type_id': old_dev.license_type_id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def update_headdevice_comm(db: Session, device_id: int, comm: str):
    """
    Updates head devices comment with new one given by user
    """
    old_dev = get_head_device(db, device_id)
    new = {'id': old_dev.id, 'serial_number': old_dev.serial_number, 'inventory_number': old_dev.inventory_number,
           'comment': comm, 'team_id': old_dev.team_id, 'license_type_id': old_dev.license_type_id}
    for key, value in new.items():
        setattr(old_dev, key, value)
    db.commit()
    db.refresh(old_dev)
    return old_dev


def get_ld_logs(db: Session, skip: int = 0):
    """
    Returns all ld debugger logs in database
    """
    return db.query(models.LDLog).order_by(desc(models.LDLog.timestamp)).offset(skip).all()


def create_ld_logs(db: Session, item: schemas.LDTempBase, head_id: int, body_id: int, pc_id: int, date: datetime):
    """
    Creates new ld log for ld_logs database table
    """
    db_ld = models.LDLog(pc_id=pc_id, timestamp=date, status=item.status, head_id=head_id, body_id=body_id)
    db.add(db_ld)
    db.commit()
    db.refresh(db_ld)
    return db_ld


def get_logs(db: Session, skip: int = 0):
    """
    Returns all usb logs in database ordered by timestamp
    """
    return db.query(models.USBLog).order_by(desc(models.USBLog.timestamp)).offset(skip).all()


def get_log(db: Session, device_id: int, skip: int = 0):
    """
    Returns all usb logs in database sorted by id
    """
    return db.query(models.USBLog).filter(models.USBLog.device_id == device_id).offset(skip).all()


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
    execute_string = "SELECT * FROM ld_logs AS logs WHERE"
    before_me = False
    all_all = True
    if pc != "all":
        all_all = False
        pc = find_pc_by_username(db, pc)
        if pc != None:
            if before_me:
                execute_string += " AND logs.pc_id = " + str(pc.id)
            else:
                before_me = True
                execute_string += " logs.pc_id = " + str(pc.id)
        else:
            if before_me:
                execute_string += " AND logs.pc_id = -1"
            else:
                before_me = True
                execute_string += " logs.pc_id = -1"
    if tema != "all":
        all_all = False
        team = find_team(db, tema)
        if team != None:
            head_devices = find_headdevices_by_team(db, team.id)
            body_devices = find_bodydevices_by_team(db, team.id)
            if len(head_devices) > 0 and len(body_devices) > 0:
                h_ids = "("
                for h in head_devices:
                    h_ids += str(h.id) + ", "
                def_h_ids = h_ids[:-2] + ")"
                b_ids = "("
                for b in body_devices:
                    b_ids += str(b.id) + ", "
                def_b_ids = b_ids[:-2] + ")"
                if before_me:
                    execute_string += " AND (logs.head_id IN " + def_h_ids + " OR logs.body_id IN " + def_b_ids + ")"
                else:
                    before_me = True
                    execute_string += " (logs.head_id IN " + def_h_ids + " OR logs.body_id IN " + def_b_ids + ")"
            elif len(head_devices) == 0 and len(body_devices) > 0:
                b_ids = "("
                for b in body_devices:
                    b_ids += str(b.id) + ", "
                def_b_ids = b_ids[:-2] + ")"
                if before_me:
                    execute_string += " AND logs.body_id IN " + def_b_ids
                else:
                    before_me = True
                    execute_string += " logs.body_id IN " + def_b_ids
            elif len(head_devices) > 0 and len(body_devices) == 0:
                h_ids = "("
                for h in head_devices:
                    h_ids += str(h.id) + ", "
                def_h_ids = h_ids[:-2] + ")"
                if before_me:
                    execute_string += " AND logs.head_id IN " + def_h_ids
                else:
                    before_me = True
                    execute_string += " logs.head_id IN " + def_h_ids
            else:
                if before_me:
                    execute_string += " AND (logs.head_id = -1 OR logs.body_id = -1)"
                else:
                    before_me = True
                    execute_string += " (logs.head_id = -1 OR logs.body_id = -1)"
        else:
            if before_me:
                execute_string += " AND logs.pc_id = -1"
            else:
                before_me = True
                execute_string += " logs.pc_id = -1"
    if lic != "all":
        all_all = False
        license = find_license(db, lic)
        if license != None:
            head_devices = find_headdevices_by_license(db, license.id)
            body_devices = find_bodydevices_by_license(db, license.id)
            if len(head_devices) > 0 and len(body_devices) > 0:
                h_ids = "("
                for h in head_devices:
                    h_ids += str(h.id) + ", "
                def_h_ids = h_ids[:-2] + ")"
                b_ids = "("
                for b in body_devices:
                    b_ids += str(b.id) + ", "
                def_b_ids = b_ids[:-2] + ")"
                if before_me:
                    execute_string += " AND (logs.head_id IN " + def_h_ids + " OR logs.body_id IN " + def_b_ids + ")"
                else:
                    before_me = True
                    execute_string += " (logs.head_id IN " + def_h_ids + " OR logs.body_id IN " + def_b_ids + ")"
            elif len(head_devices) == 0 and len(body_devices) > 0:
                b_ids = "("
                for b in body_devices:
                    b_ids += str(b.id) + ", "
                def_b_ids = b_ids[:-2] + ")"
                if before_me:
                    execute_string += " AND logs.body_id IN " + def_b_ids
                else:
                    before_me = True
                    execute_string += " logs.body_id IN " + def_b_ids
            elif len(head_devices) > 0 and len(body_devices) == 0:
                h_ids = "("
                for h in head_devices:
                    h_ids += str(h.id) + ", "
                def_h_ids = h_ids[:-2] + ")"
                if before_me:
                    execute_string += " AND logs.head_id IN " + def_h_ids
                else:
                    before_me = True
                    execute_string += " logs.head_id IN " + def_h_ids
            else:
                if before_me:
                    execute_string += " AND (logs.head_id = -1 OR logs.body_id = -1)"
                else:
                    before_me = True
                    execute_string += " (logs.head_id = -1 OR logs.body_id = -1)"
        else:
            if before_me:
                execute_string += " AND logs.pc_id = -1"
            else:
                before_me = True
                execute_string += " logs.pc_id = -1"
    if all_all:
        before_me = True
        execute_string = "SELECT * FROM ld_logs AS logs"

    if not before_me:
        execute_string = "SELECT * FROM ld_logs AS logs WHERE logs.id = -1"
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
        else:
            execute_string += "  WHERE logs.pc_id = -1"
    if tema != "all":
        team = find_team(db, tema)
        if team is not None:
            devs = get_devices_by_team(db, team.id)
            d_ids = "("
            for p in devs:
                d_ids += str(p.id) + ", "
            def_d_ids = d_ids[:-2] + ")"
            if pc != "all":
                if len(def_d_ids) > 1:
                    execute_string += " AND logs.device_id IN " + def_d_ids
                else:
                    execute_string += " AND logs.device_id IN (-1)"
            else:
                if len(def_d_ids) > 1:
                    execute_string += " WHERE logs.device_id IN " + def_d_ids
                else:
                    execute_string += " WHERE logs.device_id IN (-1)"
        else:
            if pc != "all":
                execute_string += " AND logs.device_id IN (-1)"
            else:
                execute_string += " WHERE logs.device_id IN (-1)"
    if lic != "all":
        license = get_licenses_by_name(db, lic)
        if len(license) > 0:
            ids = []
            for l in license:
                ids.append(l.id)
            device_licenses = find_devicelicenses_by_licid_array(db, ids)
            dev_ids = "("
            for dev in device_licenses:
                dev_ids += str(dev.device_id) + ", "
            defin_ids = dev_ids[:-2] + ")"
            if pc != "all" or tema != "all":
                if len(defin_ids) > 1:
                    execute_string += " AND logs.device_id IN " + defin_ids
                else:
                    execute_string += " AND logs.device_id IN (-1)"
            else:
                if len(defin_ids) > 1:
                    execute_string += " WHERE logs.device_id IN " + defin_ids
                else:
                    execute_string += " WHERE logs.device_id IN (-1)"
        else:
            if pc != "all" or tema != "all":
                execute_string += " AND logs.device_id IN (-1)"
            else:
                execute_string += " WHERE logs.device_id IN (-1)"

    # executing assembled query string
    result = db.execute(execute_string)
    return result


def get_filtered_bodydevices(db: Session, body_id: str, license_id: str, team: str):
    """
    returns filtered body devices based on given attributes
    """
    execute_string = "SELECT * FROM body_devices AS device WHERE"
    before_me = False
    all_all = True
    if body_id != "all":
        all_all = False
        body_dev = find_bodydevice_by_serial(db, body_id)
        if body_dev != None:
            if before_me:
                execute_string += " AND device.id = " + str(body_dev.id)
            else:
                before_me = True
                execute_string += " device.id = " + str(body_dev.id)
        else:
            if before_me:
                execute_string += " AND device.id = -1"
            else:
                before_me = True
                execute_string += " device.id = -1"
    if license_id != "all":
        all_all = False
        license = find_license(db, license_id)
        if license != None:
            if before_me:
                execute_string += " AND device.license_id = " + str(license.id)
            else:
                before_me = True
                execute_string += " device.license_id = " + str(license.id)
        else:
            if before_me:
                execute_string += " AND device.id = -1"
            else:
                before_me = True
                execute_string += " device.id = -1"
    if team != "all":
        all_all = False
        tem = find_team(db, team)
        if tem != None:
            if before_me:
                execute_string += " AND device.team_id = " + str(tem.id)
            else:
                before_me = True
                execute_string += " device.team_id = " + str(tem.id)
        else:
            if before_me:
                execute_string += " AND device.id = -1"
            else:
                before_me = True
                execute_string += " device.id = -1"
    if all_all:
        before_me = True
        execute_string = "SELECT * FROM body_devices AS devices"

    if not before_me:
        execute_string = "SELECT * FROM body_devices AS devices WHERE devices.id = -1"
    result = db.execute(execute_string)
    return result


# def get_filtered_headdevices(db: Session, body_id: str, license_id: str, team: str):
#     """
#     returns filtered head devices based on given attributes
#     """
#     execute_string = "SELECT * FROM head_devices AS device WHERE"
#     before_me = False
#     all_all = True
#     if body_id != "all":
#         all_all = False
#         head_devs = find_headdevices_by_serial(db, body_id)
#         if len(head_devs) > 0:
#             dev_ids = "("
#             for dev in head_devs:
#                 dev_ids += str(dev.id) + ", "
#             defin_ids = dev_ids[:-2] + ")"
#             if before_me:
#                 execute_string += " AND device.id IN " + defin_ids
#             else:
#                 before_me = True
#                 execute_string += " device.id IN " + defin_ids
#         else:
#             if before_me:
#                 execute_string += " AND device.id = -1"
#             else:
#                 before_me = True
#                 execute_string += " device.id = -1"
#     if license_id != "all":
#         all_all = False
#         licenses = find_licenses_by_license_id(db, license_id)
#         if len(licenses) > 0:
#             lic_ids = "("
#             for lic in licenses:
#                 lic_ids += str(lic.id) + ", "
#             defin_ids = lic_ids[:-2] + ")"
#             if before_me:
#                 execute_string += " AND device.license_id IN " + defin_ids
#             else:
#                 before_me = True
#                 execute_string += " device.license_id IN " + defin_ids
#         else:
#             if before_me:
#                 execute_string += " AND device.id = -1"
#             else:
#                 before_me = True
#                 execute_string += " device.id = -1"
#     if team != "all":
#         all_all = False
#         teams = find_teams_with_substring(db, team)
#         if len(teams) > 0:
#             tem_ids = "("
#             for tem in teams:
#                 tem_ids += str(tem.id) + ", "
#             defin_ids = tem_ids[:-2] + ")"
#             if before_me:
#                 execute_string += " AND device.team_id IN " + defin_ids
#             else:
#                 before_me = True
#                 execute_string += " device.team_id IN " + defin_ids
#         else:
#             if before_me:
#                 execute_string += " AND device.id = -1"
#             else:
#                 before_me = True
#                 execute_string += " device.id = -1"
#     if all_all:
#         before_me = True
#         execute_string = "SELECT * FROM body_devices AS devices"
#
#     if not before_me:
#         execute_string = "SELECT * FROM body_devices AS devices WHERE devices.id = -1"
#     result = db.execute(execute_string)
#     return result


def get_filtered_devices(db: Session, keyman_id: str, license_name: str, license_id: str, team: str):
    """
    returns filtered keyman devices based on given attributes
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
        else:
            if before_me:
                execute_string += " AND device.id = -1"
            else:
                before_me = True
                execute_string += " device.id = -1"
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
            if len(def_lic_ids) <= 1:
                def_lic_ids = "(-1)"
            if before_me:
                execute_string += " AND device.id IN " + def_lic_ids
            else:
                before_me = True
                execute_string += " device.id IN " + def_lic_ids
        else:
            if before_me:
                execute_string += " AND device.id = -1"
            else:
                before_me = True
                execute_string += " device.id = -1"
    if license_id != "all":
        all_all = False
        license = find_license(db, license_id)
        if license != None:
            licen_devs = get_license_devices(db, license.id)
            ids = "("
            for lic in licen_devs:
                ids += str(lic.device_id) + ", "
            def_ids = ids[:-2] + ")"
            if len(def_ids) <= 1:
                def_ids = "(-1)"
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


def get_users(db: Session, skip: int = 0):
    """
    Returns all users saved in database
    """
    return db.query(models.User).offset(skip).all()


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
