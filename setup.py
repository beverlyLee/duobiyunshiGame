"""
躲避陨石游戏 - MacOS 打包配置

使用方式:
1. 使用 py2app 打包:
   pip install py2app pygame
   python setup.py py2app

2. 使用 PyInstaller 打包:
   pip install pyinstaller
   pyinstaller --onefile --windowed --name "躲避陨石" main.py
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame'],
    'includes': ['game', 'game.core', 'game.entities', 'game.ui'],
    'plist': {
        'CFBundleName': '躲避陨石',
        'CFBundleDisplayName': '躲避陨石',
        'CFBundleGetInfoString': '躲避陨石 - 经典小游戏',
        'CFBundleIdentifier': 'com.game.dodgemeteor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright 2026',
        'NSHighResolutionCapable': True,
    },
}

setup(
    name='躲避陨石',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    version='1.0.0',
    description='躲避陨石 - 经典小游戏',
    author='Game Developer',
)
