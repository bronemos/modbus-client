import sys
from threading import Thread

from modbus_client.gui import app
from modbus_client.state_manager.state_manager import StateManager


def main():
    state_manager = StateManager()
    state_manager_thread = Thread(target=state_manager.run_loop)
    state_manager_thread.start()
    app.run_gui(state_manager)


if __name__ == '__main__':
    sys.exit(main())
