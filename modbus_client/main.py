import sys

from modbus_client.gui import app
from modbus_client.state_manager import StateManager


def main():
    state_manager = StateManager()
    state_manager.run_loop()
    app.run_gui(state_manager)


if __name__ == '__main__':
    sys.exit(main())