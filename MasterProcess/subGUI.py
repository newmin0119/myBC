import sys
from PyQt5.QtWidgets import *



class Mining_Block_tap(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        pass



class Snapshot_Blockchain_tap(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        lbl = QLabel(text='Snapshot myBC')
        lbl.move(60,20)

        qle = QLineEdit()
        qle.move(180,20)
        qle.resize(40,20)

        btn = QPushButton(text='GO!')
        btn.move(240,15)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.snapshot)

        lbl2 = QLabel(text='( Input \'ALL\' or <Fi> )')
        lbl2.move(320,20)

        hbox = QHBoxLayout()
        hbox.addStretch(20)
        hbox.addWidget(lbl)
        hbox.addWidget(qle)
        hbox.addWidget(btn)
        hbox.addWidget(lbl2)

        vbox = QVBoxLayout()
        vbox.addStretch(20)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def snapshot(self):
        print('snapshot')
        pass
        

class Verify_Transaction_tap(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        lbl = QLabel(text='verify-transaciton ')
        lbl.move(60,20)

        qle = QLineEdit()
        qle.move(180,20)
        qle.resize(40,20)

        btn = QPushButton(text='GO!')
        btn.move(240,15)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.verify_transaction)

        lbl2 = QLabel(text='( Input <Fi> )')
        lbl2.move(320,20)

        hbox = QHBoxLayout()
        hbox.addStretch(20)
        hbox.addWidget(lbl)
        hbox.addWidget(qle)
        hbox.addWidget(btn)
        hbox.addWidget(lbl2)

        vbox = QVBoxLayout()
        vbox.addStretch(20)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def verify_transaction(self):
        print('verify-transaction')
        pass
class Trace_Vid_tap(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        lbl = QLabel(text='trace')
        lbl.move(60,20)

        qle = QLineEdit()
        qle.move(180,20)
        qle.resize(40,20)

        btn = QPushButton(text='GO!')
        btn.move(240,15)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.trace_vehicle)

        lbl2 = QLabel(text='( Input <Fi> )')
        lbl2.move(320,20)

        hbox = QHBoxLayout()
        hbox.addStretch(20)
        hbox.addWidget(lbl)
        hbox.addWidget(qle)
        hbox.addWidget(btn)
        hbox.addWidget(lbl2)

        vbox = QVBoxLayout()
        vbox.addStretch(20)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def trace_vehicle(self):
        print('trace_vehicle')
        pass

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = Mining_Block_tap()
   sys.exit(app.exec_())