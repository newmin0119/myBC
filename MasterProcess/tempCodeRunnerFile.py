button.move(720, 10)
        button.resize(button.sizeHint())
        button.clicked.connect(QCoreApplication.instance().quit)