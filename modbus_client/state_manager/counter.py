from time import sleep

from PySide2.QtCore import QThread, Signal


class Counter(QThread):
    update_counter = Signal(float)
    update_live_view = Signal()

    def run(self):
        cnt = 0
        while cnt < 100 and not QThread.isInterruptionRequested(self):
            cnt += 1
            sleep(0.03)
            if cnt == 100:
                cnt = 0
                self.update_live_view.emit()
            self.update_counter.emit(cnt)
        self.update_counter.emit(None)
