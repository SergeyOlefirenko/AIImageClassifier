from setuptools import setup

APP = ['app.py']  # Указываем основной файл приложения
DATA_FILES = ['background.jpg', 'logo.png', 'ai_imageclassifier.keras']  # Перечисляем все дополнительные файлы, которые нужно упаковать
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tensorflow', 'Pillow', 'cv2', 'numpy'],
    'resources': DATA_FILES,
    'excludes': ['tkinter', 'PyQt5'],
    'iconfile': 'icon.icns'  
}

setup(
    name='AI Image Classifier & Enhancer',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)


