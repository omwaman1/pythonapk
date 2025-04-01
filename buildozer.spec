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
android.archs = arm64-v8a, armeabi-v7a

# Uncomment these to explicitly specify the Android API level
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 26b

# Increased build timeout and more memory for Java
android.gradle_parameters = -Dorg.gradle.jvmargs="-Xmx2048m -XX:MaxPermSize=512m -XX:+HeapDumpOnOutOfMemoryError" -Dorg.gradle.daemon=true -Dorg.gradle.parallel=true -Dorg.gradle.configureondemand=true

[buildozer]
log_level = 2
warn_on_root = 1

# Android NDK/SDK setup

android.skip_update = False
