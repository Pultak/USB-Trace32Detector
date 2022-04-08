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

For the Windows operating system, the user also needs to install the following tool.

- https://sourceforge.net/projects/libusb-win32/

Upon successful installation of this library, the following file should be created`C:\WINDOWS\system32\libusb0.dll`. The application uses this file to scan USB devices connected to the PC.

## Build

In order to create an executable file of the application, the user can use the `build.bat` file located in the root directory of the project structure. If everything goes well, a file called `licence_detector.exe` should be created in the same location. This file represents the executable file of the application.

## Execution

Before the very first start of the application, the user is required to execute the following command from the terminal in order to give the client access to all USB devices of the same vendor id and product id.

```
install-filter.exe install --device=USB\Vid_064f.Pid_2af9.Rev_0100
```

Vector Keyman: vendor id = **064f**, product id = **2af9**

After that, they can simply run the application by running the following command from the terminal.

```
licence_detector.exe --help
```