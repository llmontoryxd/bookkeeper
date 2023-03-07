from PySide6 import QtWidgets, QtGui

categories = ['Продукты', 'Мясо', 'Игрушки']


class CategoryTab(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.cat_table = CategoryTable()
        self.layout.addWidget(self.cat_table)


class CategoryTable(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QtWidgets.QLabel('<b>Категории</b>')
        self.cat_table = QtWidgets.QTableWidget()
        self.cat_table.setColumnCount(1)
        self.cat_table.setRowCount(20)
        self.cat_table.setHorizontalHeaderLabels(
            "Категория".split()
        )
        self.header = self.cat_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.cat_table.verticalHeader().hide()

        self._set_data()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.cat_table)

    def _set_data(self):
        for i in range(len(categories)):
            self.cat_table.setItem(i, 0, QtWidgets.QTableWidgetItem(categories[i]))

    def contextMenuEvent(self, event):
        context = QtWidgets.QMenu(self)
        add_row = QtGui.QAction('Добавить категорию', self)
        delete_row = QtGui.QAction('Удалить категорию', self)
        context.addAction(add_row)
        context.addAction(delete_row)

        action = context.exec(event.globalPos())
        if action == add_row:
            self._add_row()
        elif action == delete_row:
            self._delete_row()

    def _add_row(self):
        self.cat_table.insertRow(0)
        self.add_menu = AddMenu()
        self.add_menu.setWindowTitle('Добавление категории')
        self.add_menu.show()

    def _delete_row(self):
        self.cat_table.removeRow(self.cat_table.currentRow())


class AddMenu(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.cat_widget = AddCategory()
        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self._submit)

        self.layout.addWidget(self.cat_widget)
        self.layout.addWidget(self.submit_button)

    def _submit(self):
        self.close()


class AddCategory(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.cat_label = QtWidgets.QLabel('Категория')
        self.cat_line = QtWidgets.QLineEdit()
        self.layout.addWidget(self.cat_label)
        self.layout.addWidget(self.cat_line)
