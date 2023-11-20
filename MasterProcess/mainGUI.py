import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QFont
from subGUI import Mining_Block_tap,Snapshot_Blockchain_tap,Verify_Transaction_tap,Trace_Vid_tap

class MyBC(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        mining_tab= Mining_Block_tap()
        snapshot_tap = Snapshot_Blockchain_tap()
        verify_tab = Verify_Transaction_tap()
        trace_tap = Trace_Vid_tap()

        tabs = QTabWidget()
        tabs.addTab(mining_tab,'Latest_Block')
        tabs.addTab(snapshot_tap,'Snapshot_myBC')
        tabs.addTab(verify_tab,'Verifying_Transaction')
        tabs.addTab(trace_tap,'Tracing_Vehicle')

        vbox = QVBoxLayout()
        vbox.addWidget(tabs)

        self.setLayout(vbox)

        button = QPushButton('Quit',self)
        button.move(720, 10)
        button.resize(button.sizeHint())
        button.clicked.connect(QCoreApplication.instance().quit)
        
        self.setWindowTitle('myBC - Blockchain Project')
        self.resize(800, 500)
        self.center()
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyBC()
   ex.show()
   sys.exit(app.exec_())