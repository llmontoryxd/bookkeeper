from bookkeeper.client import Bookkeeper
from PySide6 import QtWidgets

import sys
import os

app = QtWidgets.QApplication(sys.argv)
B = Bookkeeper(os.path.join(os.getcwd(), 'databases', 'bookkeeper.db'))
B.view.show()
app.exec()
