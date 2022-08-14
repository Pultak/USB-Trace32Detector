@echo off

del licence_detector.exe || VER>NUL
rmdir /s /q dist || VER>NUL
pyinstaller -F --additional-hooks-dir=hooks src/licence_detector.py
copy  dist\licence_detector.exe .
del licence_detector.spec
rmdir /s /q dist || VER>NUL