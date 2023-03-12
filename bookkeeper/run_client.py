"""
Запуск основного клиента
"""
import sys
import os
from PySide6 import QtWidgets
from bookkeeper.client import Bookkeeper

app = QtWidgets.QApplication(sys.argv)
B = Bookkeeper(os.path.join(os.getcwd(), 'databases', 'bookkeeper.db'))
B.view.show()
app.exec()
