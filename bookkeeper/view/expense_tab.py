from PySide6 import QtWidgets, QtGui, QtCore
import datetime


class ExpenseTab(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.categories = None
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expense_table = ExpenseTable()
        self.layout.addWidget(self.expense_table)


class ExpenseTable(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = None
        self.expenses = None
        self.expense_adder = None
        self.expense_deleter = None
        self.expense_updater = None
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
        self.v_header = self.expenses_table.verticalHeader()
        self.v_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.expenses_table.verticalHeader().hide()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.expenses_table)

    def set_categories(self, categories):
        self.categories = categories

    def set_data(self, expenses):
        self.expenses = expenses
        self.expenses_table.setRowCount(len(expenses))
        for i in range(len(expenses)):
            date = expenses[i].expense_date.split('.')[0]
            self.expenses_table.setItem(i, 0, QtWidgets.QTableWidgetItem(date))
            self.expenses_table.setItem(i, 1, QtWidgets.QTableWidgetItem(expenses[i].amount))
            self.expenses_table.setItem(i, 2, QtWidgets.QTableWidgetItem(expenses[i].category))
            self.expenses_table.setItem(i, 3, QtWidgets.QTableWidgetItem(expenses[i].comment))

    def contextMenuEvent(self, event):
        context = QtWidgets.QMenu(self)
        add_row = QtGui.QAction('Добавить расход', self)
        delete_row = QtGui.QAction('Удалить расход', self)
        update_row = QtGui.QAction('Изменить расход', self)
        context.addAction(update_row)
        context.addAction(add_row)
        context.addAction(delete_row)

        action = context.exec(event.globalPos())
        if action == add_row:
            self._add_row()
        elif action == delete_row:
            self._delete_row()
        elif action == update_row:
            self._update_row()

    def _update_row(self):
        upd_obj_pk = self.expenses[self.expenses_table.currentRow()].pk
        self.update_menu = UpdateMenu(upd_obj_pk, self.categories)
        self.update_menu.sum_widget.sum_line.setText(self.expenses[self.expenses_table.currentRow()].amount)
        self.update_menu.com_widget.comment_line.setText(self.expenses[self.expenses_table.currentRow()].comment)
        date = QtCore.QDateTime.fromString(self.expenses[self.expenses_table.currentRow()].expense_date,
                                           'yyyy-MM-dd HH:mm:ss')
        self.update_menu.date_widget.date_box.setDateTime(date)
        placeholder_cat = self.expenses[self.expenses_table.currentRow()].category
        for i in range(self.update_menu.cat_widget.cat_box.count()):
            if self.update_menu.cat_widget.cat_box.itemText(i) == placeholder_cat:
                self.update_menu.cat_widget.cat_box.setCurrentIndex(i)
        self.update_menu.submitClicked.connect(self._on_update_menu_submit)
        self.update_menu.show()

    def _add_row(self):
        self.add_menu = AddMenu(self.categories)
        self.add_menu.submitClicked.connect(self._on_add_menu_submit)
        self.add_menu.show()

    def _delete_row(self):
        self.delete_warning = DeleteWarning()
        self.delete_warning.exec()
        if self.delete_warning.clickedButton() == self.delete_warning.yes_btn:
            self.expense_deleter(self.expenses[self.expenses_table.currentRow()])

    def _on_add_menu_submit(self, date, summ, cat, comment):
        self.expense_adder(date, summ, cat, comment)

    def _on_update_menu_submit(self, pk, new_date, new_summ, new_cat, new_com):
        self.expense_updater(pk, new_date, new_summ, new_cat, new_com)

    def register_expense_adder(self, handler):
        self.expense_adder = handler

    def register_expense_deleter(self, handler):
        self.expense_deleter = handler

    def register_expense_updater(self, handler):
        self.expense_updater = handler


class UpdateMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(int, str, str, object, str)

    def __init__(self, pk, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pk = pk
        self.categories = categories
        self.layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle('Изменение расхода')
        self.setLayout(self.layout)
        self.sum_widget = AddSum()
        self.cat_widget = AddCategory(self.categories)
        self.com_widget = AddComment()
        self.date_widget = AddDate()
        self.submit_button = QtWidgets.QPushButton('Изменить')
        self.submit_button.clicked.connect(self._submit)

        self.layout.addWidget(self.date_widget)
        self.layout.addWidget(self.sum_widget)
        self.layout.addWidget(self.cat_widget)
        self.layout.addWidget(self.com_widget)
        self.layout.addWidget(self.submit_button)

    def _submit(self):
        self.date = self.date_widget.date_box.dateTime()
        self.date = self.date.toString('yyyy-MM-dd HH:mm:ss')
        self.sum = self.sum_widget.sum_line.text()
        self.cat_text = self.cat_widget.cat_box.currentText()
        self.com = self.com_widget.comment_line.toPlainText()
        self.submitClicked.emit(self.pk, self.date, self.sum, self.cat_text, self.com)
        self.close()


class AddMenu(QtWidgets.QWidget):
    submitClicked = QtCore.Signal(str, str, object, str)

    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = categories
        self.layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle('Добавление расхода')
        self.setLayout(self.layout)
        self.sum_widget = AddSum()
        self.cat_widget = AddCategory(self.categories)
        self.com_widget = AddComment()
        self.date_widget = AddDate()
        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self._submit)

        self.layout.addWidget(self.date_widget)
        self.layout.addWidget(self.sum_widget)
        self.layout.addWidget(self.cat_widget)
        self.layout.addWidget(self.com_widget)
        self.layout.addWidget(self.submit_button)

    def _submit(self):
        self.date = self.date_widget.date_box.dateTime()
        self.date = self.date.toString('yyyy-MM-dd HH:mm:ss')
        self.sum = self.sum_widget.sum_line.text()
        self.cat_text = self.cat_widget.cat_box.currentText()
        self.com = self.com_widget.comment_line.toPlainText()
        self.submitClicked.emit(self.date, self.sum, self.cat_text, self.com)
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
    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = categories
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.cat_label = QtWidgets.QLabel('Категория')
        self.cat_box = QtWidgets.QComboBox()
        for i in range(len(self.categories)):
            self.cat_box.addItem(self.categories[i].name)
        self.layout.addWidget(self.cat_label)
        self.layout.addWidget(self.cat_box)


class AddComment(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.comment_label = QtWidgets.QLabel('Комментарий')
        self.comment_line = QtWidgets.QTextEdit()
        self.layout.addWidget(self.comment_label)
        self.layout.addWidget(self.comment_line)


class AddDate(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.date_label = QtWidgets.QLabel('Дата')
        self.date_box = QtWidgets.QDateTimeEdit()
        self.date_box.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_box)


class DeleteWarning(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Удаление расхода')
        self.setText('Вы действительно'
            +' хотите удалить строку? Запись о расходе будет удалена.')
        self.yes_btn = self.addButton('Да', QtWidgets.QMessageBox.ButtonRole.YesRole)
        self.no_btn = self.addButton('Нет', QtWidgets.QMessageBox.ButtonRole.NoRole)
        self.setIcon(QtWidgets.QMessageBox.Icon.Question)

