[app]
title = CorteÓptimo Pro
package.name = corteoptimopro
package.domain = com.corteoptimo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0.0
requirements = python3,kivy==2.2.1
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
icon.filename = %(source.dir)s/icon.png
[buildozer]
log_level = 2
warn_on_root = 1
