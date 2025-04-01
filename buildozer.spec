[app]
title = AnimeGAN Video Converter
package.name = animegan_converter
package.domain = org.animegan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,tflite
version = 0.1
requirements = python3,kivy,numpy,opencv,tensorflow
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
