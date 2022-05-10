# Automatic detection and documentation of connected USB devices - Server - Bug Thugs

---

- [Description](#description)
- [Build](#build)
- [Execution](#execution)

---

## Description

This server application provides data via endpoints defined in **sql_app.api** package. Files in this package are divided by their respetive funcionality. File **usb_logs_web.py** provides endpoints and methods for main web view **/api/v1/logs-web**, file **usb_logs.py** provides endpoints and methods for client applications.

**sql_app** package contains files for database communication. **models.py** and **schemas.py** provides classes for mapping objects to database table entries, **database.py** defines database communication session and **crud.py**  contains methods with database queries for reading, updating and saving data from client applications and web interfaces.  


## Build

Server application comes with dockerFile and docker compose file so build is quite simple. In the server folder run command

```bash
docker-compose up
```

And docker will create image for server application and postgresql database. Database files are stored in own folder, so saved data will be persistent even if docker daemon would unexpectedly shut down.

## Web Views

Data from database are easily accesibly from web browser. Main web views url is

```bash
http://localhost:8000/api/v1/logs-web
```

On this page there is select box at the top of the page for accessing different views on other data in database as well as creating new ones

