from setuptools import setup, find_packages

setup(
    name="animegan_converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "kivy==2.1.0",
        "numpy==1.22.4",
        "opencv-python==4.6.0.66",
        "tensorflow==2.9.1",
        "psutil==5.9.4",
    ],
    python_requires=">=3.8",
)
