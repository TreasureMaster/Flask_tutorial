"""Файл описывает проект и принадлежащие ему файлы."""

from setuptools import find_packages, setup

setup(
    name='flaskr',                              # определяет имя пакета, отображаемое в PyPI
    version='1.0.2.dev5',                       # определяет номер версии пакета
    packages=find_packages(where='flaskr'),     # список строк, определяющих пакеты, которыми управляет setuptools
                                                # find_packages() возвращает список всех пакетов, найденных в указанном каталоге (по умолчанию - текущий)
    package_dir={'': 'flaskr'},
    include_package_data=True,                  # True указывает автоматически включать любый файлы данных, описанных в файле MANIFEST.in
    zip_safe=False,                             # False указывает, что нельзя установить и запустить проект из zip-файла
    install_requires=[                          # список строк, указывающий какие другие дистрибутивы надо установить
        'flask',
        'python-dotenv'
    ],
    python_requires='>=3.6, <4',                # строка, соответствующая спецификатору используемой версии Python
)