import sys
import modbus_client.gui.app
from threading import Thread
import tunnel.wstunnel


def main():
    #tunnel_thread = Thread(target=tunnel.wstunnel.WSTunnel)
    #tunnel_thread.start()
    modbus_client.gui.app.run_gui()


if __name__ == '__main__':
    sys.exit(main())
