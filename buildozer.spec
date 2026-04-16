[app]
# Información básica
title = CorteÓptimo Pro
package.name = corteoptimopro
package.domain = com.corteoptimo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0.0

# Requisitos (Kivy estándar para tu lógica de optimización)
requirements = python3,kivy==2.2.1

# Configuración de Android
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# API y NDK (Configuración específica para Kivy 2.2.1)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True

# Arquitectura recomendada para mayor compatibilidad
android.archs = arm64-v8a

# Icono (Asegúrate de tener un icon.png en la raíz o pon un # al inicio de la línea)
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
