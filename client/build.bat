@echo off

del licence_detector || VER>NUL
rmdir /s /q dist || VER>NUL
pyinstaller -F --add-binary "C:\WINDOWS\system32\libusb0.dll;." --additional-hooks-dir=hooks src/licence_detector.py
copy  dist\licence_detector .
del licence_detector.spec
rmdir /s /q dist || VER>NUL