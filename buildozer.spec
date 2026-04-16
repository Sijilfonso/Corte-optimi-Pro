[app]

# (str) Title of your application
title = Corte Optimo Pro

# (str) Package name
package.name = corteoptimo

# (str) Package domain (needed for android packaging)
package.domain = org.sijilfonso

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt

# (list) Application requirements
# NOTA: He añadido pandas, numpy y openpyxl que estaban en tu requirements.txt
requirements = python3,kivy==2.2.1,kivymd,pandas,numpy,openpyxl,et_xmlfile

# (str) Custom source folders for requirements
# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid any compiler version mismatch.
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# ESTO CORRIGE EL ERROR DE LICENCIAS QUE TENÍAS
android.accept_sdk_license = True

# (str) Android entry point, default is to use start.py
android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to white list for the libpcre merge
#android.whitelist =

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (int) overrides the version.code of the android package
android.numeric_version = 1

# (str) OS endpoint for the build (default is None)
# (list) List of service to declare
#services = NAME:ENDPOINT_CLASS

#
# Buildozer section
#

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
# LO HEMOS SUBIDO A 2 PARA VER ERRORES DETALLADOS
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1

# (str) Path to build artifacts (optional, defaults to <app.dir>/.buildozer)
#build_dir = ./.buildozer

# (str) Path to bin directory (optional, defaults to <app.dir>/bin)
#bin_dir = ./bin
