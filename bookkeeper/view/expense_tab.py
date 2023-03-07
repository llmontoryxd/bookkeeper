from PySide6 import QtWidgets, QtGui

categories = ['Продукты', 'Мясо', 'Игрушки']


class ExpenseTab(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expense_table = ExpenseTable()
        self.layout.addWidget(self.expense_table)


class ExpenseTable(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QtWidgets.QLabel('<b>Последние расходы</b>')
        self.expenses_table = QtWidgets.QTableWidget()
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        self.header = self.expenses_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)
        self.expenses_table.verticalHeader().hide()

        self._set_data()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.expenses_table)

    def _set_data(self):
        for i in range(self.expenses_table.rowCount()):
            for j in range(self.expenses_table.columnCount()):
                self.expenses_table.setItem(i, j, QtWidgets.QTableWidgetItem('10'))

    def contextMenuEvent(self, event):
        context = QtWidgets.QMenu(self)
        add_row = QtGui.QAction('Добавить строку', self)
        delete_row = QtGui.QAction('Удалить строку', self)
        context.addAction(add_row)
        context.addAction(delete_row)

        action = context.exec(event.globalPos())
        if action == add_row:
            self._add_row()
        elif action == delete_row:
            self._delete_row()

    def _add_row(self):
        self.expenses_table.insertRow(0)
        self.add_menu = AddMenu()
        self.add_menu.setWindowTitle('Добавление строки')
        self.add_menu.show()

    def _delete_row(self):
        self.expenses_table.removeRow(self.expenses_table.currentRow())


class AddMenu(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.sum_widget = AddSum()
        self.cat_widget = AddCategory()
        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self._submit)

        self.layout.addWidget(self.sum_widget)
        self.layout.addWidget(self.cat_widget)
        self.layout.addWidget(self.submit_button)

    def _submit(self):
        self.close()


class AddSum(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.sum_label = QtWidgets.QLabel('Сумма')
        self.sum_line = QtWidgets.QLineEdit()
        self.layout.addWidget(self.sum_label)
        self.layout.addWidget(self.sum_line)


class AddCategory(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.cat_label = QtWidgets.QLabel('Категория')
        self.cat_box = QtWidgets.QComboBox()
        self.cat_box.addItems(categories)
        self.layout.addWidget(self.cat_label)
        self.layout.addWidget(self.cat_box)