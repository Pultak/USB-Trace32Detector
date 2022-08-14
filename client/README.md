# Automatic detection and documentation of connected USB devices - Client - Bug Thugs

---

- [Description](#description)
- [Requirements](#requirements)
  * [Windows](#windows)
- [Build](#build)
- [Execution](#execution)

---

## Description

This client application periodically scans all USB devices connected to the computer. For each device, it tries to retrieve its **vendor id**, **product id**, and **serial number**, which is believed to be unique for all devices from the same vendor. This data, along with a timestamp and computer-related information, is sent to the server (API). If the application fails to send the data, it will store the payload in a disk-based cache. The client then periodically accesses the cache in order to resend the failed payloads to the server.   

## Requirements

As required, the application was written in Python. In order to successfully run the application, the user needs to have Python 3 installed on their machine. Furthermore, they are required to run the following command to install all dependencies the application takes advantage of.

```
pip install -r requirements.txt
```

### Windows
The new detection method doesn't require installation of the LibUSB. Only requirement is to have functional powershell that can output connected USB devices via command Get-PnpDevice. 

You can try the command by inserting the following line into the powershell:

```
Get-PnpDevice -Class 'HIDClass' -Status 'OK' -FriendlyName 'USB Input Device' | Select-Object InstanceId | ConvertTo-Json
```

The output should look similarly to the following output:
```
[
    {
        "InstanceId":  "USB\\VID_A123\u0026PID_455E\u0026MI_00\\7\u002611EE4411\u00261\u00260000"
    },
    {
        "InstanceId":  "USB\\VID_12A2\u0026PID_4455\u0026MI_01\\7\u002699EEFF11\u00261\u00260001"
    },
    {
        "InstanceId":  "USB\\VID_00D4\u0026PID_1256\u0026MI_02\\7\u0026C2B1B16\u00260\u00260002"
    }
]
```
<del>
For the Windows operating system, the user also needs to install the LibUSB-Win32 library. The installer can be found over at: https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/libusb-win32-devel-filter-1.2.6.0.exe~~

Upon successful installation of this library, the following file should be created`C:\WINDOWS\system32\libusb0.dll`. The application uses this dynamic library to scan USB devices connected to the PC. The default installation folder of this library is `C:\Program Files\LibUSB-Win32\`. 

Before the very first start of the application, the user is required to execute following command as an administrator in order to give the client access to all USB devices of the same vendor id and product id.

```
install-filter.exe install --device=USB\Vid_064f.Pid_2af9.Rev_0100
```

Vector Keyman: vendor id = **064f**, product id = **2af9**

The `install-filter.exe` executable file can be found in the default LibUSB-Win32 installation folder in sub-folder `bin`, or it can be downloaded from the following link https://sourceforge.net/projects/libusb-win32/. 

</del>

## Build

In order to create an executable file of the application, the user can use the `build.bat` file located in the root directory of the project structure. If everything goes well, a file called `licence_detector.exe` should be created in the same location. This file represents the executable file of the application.

## Execution


After everything is successfully setup, you can simply run the application by running the following command from the terminal.

```
licence_detector.exe --help
```