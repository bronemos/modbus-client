from threading import Thread

from modbus_client.communication import serializer


class StateManager:

    def __init__(self):
        serializer_thread = Thread(target=serializer.start)
        serializer_thread.start()

    def start(self):
        pass