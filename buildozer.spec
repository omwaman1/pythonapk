[app]
title = Anime Converter
package.name = anime_converter
package.domain = org.example
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy,opencv-python,numpy,tensorflow-lite
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.ndk = 23b
android.arch = arm64-v8a, armeabi-v7a
p4a.branch = stable
android.minapi = 21
android.sdk = 31
android.gradle_dependencies = "androidx.appcompat:appcompat:1.2.0"
android.ndk_path = $HOME/.android/ndk/23b
fullscreen = 1
orientation = portrait
