[app]

# (str) Title of your application
title = CorteÓptimo Pro

# (str) Package name
package.name = corteoptimopro

# (str) Package domain (needed for android packaging)
package.domain = com.corteoptimo

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (str) Application version
version = 1.0.0

# (list) Application requirements
# Solo lo necesario para tu main.py (KivyMD no parece usarse en los imports, solo Kivy estándar)
requirements = python3,kivy==2.2.1

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Aceptar licencias automáticamente (CRUCIAL)
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) Icon of the application
# Asegúrate de tener un icon.png en la raíz o comenta esta línea
icon.filename = %(source.dir)s/icon.png

[buildozer]

# (int) Log level (2 para ver errores detallados)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
