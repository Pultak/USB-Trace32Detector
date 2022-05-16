# Automatic detection and documentation of connected Lauterbach Debugger and its head device - LD Client - Bug Thugs

---

- [Description](#description)
- [Requirements](#requirements)
  * [Windows](#windows)
- [Build](#build)
- [Execution](#execution)

---

## Description

This client application periodically searches for running process of TRACE32 PowerView. 
Upon detection the application tries to execute t32rem.exe program with specific parameters which generates info file about currently connected Lauterbach Debbuger and its head device.
The serial numbers from the info file are then parsed and along with a timestamp and computer-related information, is sent to the server (API).
If the application fails to send the data, it will store the payload in a disk-based cache.
The client then periodically accesses the cache in order to resend the failed payloads to the server.   

## Requirements

In order to successfully run the application the user needs to have .NET 6.0 installed on their machine. 
It can be simply downloaded from the official site of the Microsoft (https://dotnet.microsoft.com/en-us/download/dotnet/6.0).

## Build/Publish

If you have .NET 6.0 installed on your machine and its binaries are included in the system variables, you can simply execute following command in the LDClient subfolder:
```
dotnet publish -c Release -o build -p:PublishSingleFile=true --self-contained true -r win-x86
```

If everything goes well, a file called `LDClient.exe` with all its needed dependencies and configuration files should be created under folder 'build'.

You can also build this application by opening the solution of this project in MSVC and using one of its build tools.

## Execution


After everything is successfully setup, you can simply run the application by running the following command from the terminal.

```
LDClient.exe
```