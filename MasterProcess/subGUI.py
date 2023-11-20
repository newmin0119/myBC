import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


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
        qle = QLineEdit()
        qle.resize(40,20)

        btn = QPushButton(text='GO!')
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.snapshot)

        lbl2 = QLabel(text='( Input \'ALL\' or <Fi> )')
        self.hbox = QHBoxLayout()
        self.hbox.addStretch(20)
        self.hbox.addWidget(lbl)
        self.hbox.addWidget(qle)
        self.hbox.addWidget(btn)
        self.hbox.addWidget(lbl2)
        self.Blockchains = []
        self.scrollareas = []
        self.wholes_chains_layout = QFormLayout()
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
    def snapshot(self,Blockchains_str):
        for i in len(Blockchains_str):
            self.Blockchains.append(QLabel(text=Blockchains_str[i]))
            self.scrollareas.append(QScrollArea())
            self.scrollareas[i].setWidget(self.Blockchains[i])
            
            self.vbox.addWidget(self.scrollareas[i])
        

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

    def verify_transaction(self,res):
        
        pass
class Trace_Vid_tap(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        lbl = QLabel(text='trace')
        lbl.move(60,20)

        self.qle = QLineEdit()
        self.qle.move(180,20)
        self.qle.resize(40,20)

        btn = QPushButton(text='GO!')
        btn.move(240,15)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.trace_vehicle)

        lbl2 = QLabel(text='( Input <Fi> )')
        lbl2.move(320,20)

        hbox = QHBoxLayout()
        hbox.addStretch(20)
        hbox.addWidget(lbl)
        hbox.addWidget(self.qle)
        hbox.addWidget(btn)
        hbox.addWidget(lbl2)

        vbox = QVBoxLayout()
        vbox.addStretch(20)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def trace_vehicle(self):
        print(self.qle.text())
        pass

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = Mining_Block_tap()
   sys.exit(app.exec_())