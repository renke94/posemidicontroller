import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from pyquantum.ui import *
from src.camera_ui import CameraUI

from src.mapping import MidiMappingTableView

class MainView(View):
    def __init__(self):
        super(MainView, self).__init__()
        mapping_table = MidiMappingTableView(self)

        self.setLayout(Column(
            children=[
                TabView(
                    parent=self,
                    tabs={
                        'Camera': CameraUI(self, mapping_table.send_midi),
                        'Midi Mapping': mapping_table,
                    }
                )
            ],
            stretch=1
        ))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(640, 600)
        self.setWindowTitle("Pose MIDI Controller")

        widget = MainView()
        self.setCentralWidget(widget)

    # def closeEvent(self, a0):
    #     pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
