# ModbusGUI

GUI Client for Modbus protocol

## Usage

In order for client to work both diagslave and wstunnel must be running.

1. Run **diagslave** from simulator directory (windows version available at https://www.modbusdriver.com/diagslave.html)
2. Run **wstunnel.py** from tunnel directory
3. Run **main.py**

## Generating project documentation

rst files for generating project documentation are located in /docs/source\
Make sure sphinx is installed (run `pip install sphinx` if not)\
Run ```sphinx-build -b html sourcedir builddir```
