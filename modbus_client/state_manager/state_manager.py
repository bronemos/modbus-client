import asyncio
from queue import Queue

from PySide2.QtCore import QObject, Signal

from modbus_client.communication import serializer


class StateManager(QObject):
    update = Signal(dict)
    current_state = dict()

    def __init__(self):
        QObject.__init__()
        self.req_queue = Queue()

    def run_loop(self):
        print("started state manager")
        asyncio.new_event_loop().run_until_complete(self._state_manager_loop())

    async def _state_manager_loop(self):

        pass



