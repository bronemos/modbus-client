from setuptools import setup, find_namespace_packages

setup(
    name='ModbusGuiClient',
    version='0.1',
    packages=find_namespace_packages(exclude=('venv', 'venv.*')),
    include_package_data=True,
    python_requires='>=3.8',
    entry_points={'console_scripts': ['modbus_client=modbus_client.main:main']},
    install_requires=['aiohttp~=3.6.2',
                      'pytest~=6.0.1',
                      'PySide2~=5.15.0',
                      'setuptools~=49.6.0'
                      ],
)
