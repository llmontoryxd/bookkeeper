from bookkeeper.client import Bookkeeper
from PySide6 import QtWidgets

import sys

app = QtWidgets.QApplication(sys.argv)
B = Bookkeeper()
B.view.show()
app.exec()
